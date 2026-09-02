// docs/<教材>/exercises/*.md の演習ページを、その場で解答できる UI に変換する。
// Markdown を唯一の原本とするため、ページの書式（「## 問題」「## 解答と解説」、
// 設問「### 問N」、選択肢「- A. 」、解答「**解答**：X」）を描画後の DOM から
// 読み取って組み立てる。書式が読み取れないページでは何もせず、素の表示のまま残す。
// 全問に解答すると成績（全 N 問中 M 問正解）とやり直しボタンを表示する。
(function () {
  "use strict";

  // 見出しのテキストを、toc の permalink アンカー（¶）を除いて取り出す
  function headingText(heading) {
    var clone = heading.cloneNode(true);
    var anchors = clone.querySelectorAll("a.headerlink");
    Array.prototype.forEach.call(anchors, function (a) {
      a.parentNode.removeChild(a);
    });
    return clone.textContent.trim();
  }

  function findSectionHeading(article, text) {
    var headings = article.querySelectorAll("h2");
    for (var i = 0; i < headings.length; i++) {
      if (headingText(headings[i]) === text) return headings[i];
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
        current = headingText(node);
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

  // 設問を解答 UI にし、状態（解答済みか、正解したか）とやり直し用の
  // reset を持つオブジェクトを返す
  function setupQuestion(ul, answer, onAnswered) {
    var items = Array.prototype.slice.call(ul.children);
    var state = {
      answered: false,
      correct: false,
      reset: function () {
        state.answered = false;
        state.correct = false;
        ul.classList.remove("quiz-answered");
        items.forEach(function (li) {
          li.classList.remove("quiz-correct");
          li.classList.remove("quiz-incorrect");
        });
        var next = ul.nextElementSibling;
        if (next && next.classList.contains("quiz-feedback")) {
          next.parentNode.removeChild(next);
        }
      },
    };
    items.forEach(function (li) {
      var m = li.textContent.match(/^\s*([A-D])[.．]/);
      if (!m) return;
      var letter = m[1];
      li.classList.add("quiz-option");
      li.setAttribute("role", "button");
      li.tabIndex = 0;
      var choose = function () {
        if (state.answered) return;
        state.answered = true;
        ul.classList.add("quiz-answered");
        var correct = letter === answer.letter;
        state.correct = correct;
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
        onAnswered();
      };
      li.addEventListener("click", choose);
      li.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          choose();
        }
      });
    });
    return state;
  }

  // 全問に解答した時点で、成績とやり直しボタンをページ末尾に出す
  function buildSummary(states, container, insertBeforeNode) {
    var correctCount = states.filter(function (s) {
      return s.correct;
    }).length;
    var summary = document.createElement("div");
    summary.className = "quiz-summary";
    var score = document.createElement("p");
    score.className = "quiz-verdict";
    score.textContent = "全 " + states.length + " 問中 " + correctCount + " 問正解";
    summary.appendChild(score);
    var retry = document.createElement("button");
    retry.type = "button";
    retry.className = "md-button quiz-retry";
    retry.textContent = "もう一度解く";
    retry.addEventListener("click", function () {
      states.forEach(function (s) {
        s.reset();
      });
      summary.parentNode.removeChild(summary);
    });
    summary.appendChild(retry);
    container.insertBefore(summary, insertBeforeNode);
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
    var states = [];
    var question = null;
    var onAnswered = function () {
      var done = states.every(function (s) {
        return s.answered;
      });
      if (done) buildSummary(states, answerHeading.parentNode, answerHeading);
    };
    sectionNodes(problemHeading).forEach(function (node) {
      if (node === answerHeading) return;
      if (node.tagName === "H3") {
        question = answers[headingText(node)] || null;
        return;
      }
      if (node.tagName === "UL" && question && question.letter) {
        states.push(setupQuestion(node, question, onAnswered));
        question = null;
      }
    });

    // 一問も変換できなければ、解答の節を隠さず素のページのまま残す
    if (states.length === 0) return;
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
