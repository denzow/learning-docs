// docs/exercises/*.md の演習ページを、その場で解答できる UI に変換する。
// Markdown を唯一の原本とするため、ページの書式（「## 問題」「## 解答と解説」、
// 設問「### 問N」、選択肢「- A. 」、解答「**解答**：X」）を描画後の DOM から
// 読み取って組み立てる。書式が読み取れないページでは何もせず、素の表示のまま残す。
(function () {
  "use strict";

  function findSectionHeading(article, text) {
    var headings = article.querySelectorAll("h2");
    for (var i = 0; i < headings.length; i++) {
      if (headings[i].textContent.trim() === text) return headings[i];
    }
    return null;
  }

  // 見出しの次要素から、次の h2 の手前までを節の本体として集める
  function sectionNodes(heading) {
    var nodes = [];
    for (var n = heading.nextElementSibling; n && n.tagName !== "H2"; n = n.nextElementSibling) {
      nodes.push(n);
    }
    return nodes;
  }

  // 解答と解説の節から、設問名 → { letter, notes } の対応を作る
  function collectAnswers(nodes) {
    var answers = {};
    var current = null;
    nodes.forEach(function (node) {
      if (node.tagName === "H3") {
        current = node.textContent.trim();
        answers[current] = { letter: null, notes: [] };
        return;
      }
      if (!current) return;
      var entry = answers[current];
      if (!entry.letter) {
        var m = node.textContent.match(/解答[^A-DＡ-Ｄ]*([A-D])/);
        if (m) {
          entry.letter = m[1];
          return;
        }
      }
      entry.notes.push(node);
    });
    return answers;
  }

  function buildFeedback(correct, letter, notes) {
    var feedback = document.createElement("div");
    feedback.className = "quiz-feedback " + (correct ? "quiz-ok" : "quiz-ng");
    var verdict = document.createElement("p");
    verdict.className = "quiz-verdict";
    verdict.textContent = correct ? "正解" : "不正解（正解は " + letter + "）";
    feedback.appendChild(verdict);
    notes.forEach(function (n) {
      var clone = n.cloneNode(true);
      clone.style.display = "";
      feedback.appendChild(clone);
    });
    return feedback;
  }

  function setupQuestion(ul, answer) {
    var items = Array.prototype.slice.call(ul.children);
    var answered = false;
    items.forEach(function (li) {
      var m = li.textContent.match(/^\s*([A-D])[.．]/);
      if (!m) return;
      var letter = m[1];
      li.classList.add("quiz-option");
      li.setAttribute("role", "button");
      li.tabIndex = 0;
      var choose = function () {
        if (answered) return;
        answered = true;
        ul.classList.add("quiz-answered");
        var correct = letter === answer.letter;
        li.classList.add(correct ? "quiz-correct" : "quiz-incorrect");
        if (!correct) {
          items.forEach(function (other) {
            var om = other.textContent.match(/^\s*([A-D])[.．]/);
            if (om && om[1] === answer.letter) other.classList.add("quiz-correct");
          });
        }
        ul.parentNode.insertBefore(
          buildFeedback(correct, answer.letter, answer.notes),
          ul.nextSibling
        );
      };
      li.addEventListener("click", choose);
      li.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          choose();
        }
      });
    });
  }

  function init() {
    if (!/\/exercises\//.test(window.location.pathname)) return;
    var article = document.querySelector("article");
    if (!article) return;

    var problemHeading = findSectionHeading(article, "問題");
    var answerHeading = findSectionHeading(article, "解答と解説");
    if (!problemHeading || !answerHeading) return;

    var answerNodes = sectionNodes(answerHeading);
    var answers = collectAnswers(answerNodes);

    // 設問ごとに、見出し（### 問N）に続く選択肢リストを解答 UI にする
    var wired = 0;
    var question = null;
    sectionNodes(problemHeading).forEach(function (node) {
      if (node === answerHeading) return;
      if (node.tagName === "H3") {
        question = answers[node.textContent.trim()] || null;
        return;
      }
      if (node.tagName === "UL" && question && question.letter) {
        setupQuestion(node, question);
        wired++;
        question = null;
      }
    });

    // 一問も変換できなければ、解答の節を隠さず素のページのまま残す
    if (wired === 0) return;
    answerHeading.style.display = "none";
    answerNodes.forEach(function (n) {
      n.style.display = "none";
    });

    // ページ内目次にも解答の節を出さない
    document.querySelectorAll(".md-nav--secondary a").forEach(function (link) {
      if (link.textContent.trim() === "解答と解説") {
        var li = link.closest("li");
        if (li) li.style.display = "none";
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
