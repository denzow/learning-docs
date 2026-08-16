// 読み上げ原稿ページで、再生中の一文をハイライトし、その文が画面から出るときは
// 自動でスクロールする。文をクリックすると、その文の先頭へ再生位置を移す。
//
// 文の区切りと開始時刻は docs/audio/<章>.timing.json から読む。この JSON は
// scripts/generate-audio.sh が edge-tts の字幕から作ったもので、各文のテキストは
// 原稿本文と一致する。ページの段落と突き合わせて文単位の <span> に包み、
// 突き合わせに失敗した章や JSON を置いていない章では何もせず素の表示のまま残す。
(function () {
  "use strict";

  var FOLLOW_KEY = "audioFollow";
  // ハイライトの上下にこれだけ余白があれば「見えている」と見なす
  var VISIBLE_MARGIN_PX = 24;
  // スクロールするとき、ハイライトを使える領域の上から何割の位置に置くか。
  // 手前の文も見えるようにして、文が変わるたびにスクロールしないようにする
  var SCROLL_ANCHOR_RATIO = 0.25;

  function isSpace(ch) {
    return /\s/.test(ch);
  }

  function strip(text) {
    return text.replace(/\s+/g, "");
  }

  function timingUrl(audio) {
    var src = audio.currentSrc || audio.src || "";
    if (!/\.mp3(\?|#|$)/.test(src)) return null;
    return src.replace(/\.mp3(\?[^#]*)?(#.*)?$/, ".timing.json");
  }

  function loadFollow() {
    try {
      return localStorage.getItem(FOLLOW_KEY) !== "off";
    } catch (e) {
      return true;
    }
  }

  function saveFollow(on) {
    try {
      localStorage.setItem(FOLLOW_KEY, on ? "on" : "off");
    } catch (e) {
      // 保存できなくてもハイライト自体は動く
    }
  }

  // 本文の段落だけを集める。プレイヤーや案内テキストを含む <p> は、
  // 子がテキストノード 1 つだけという条件から外れるので自然に除かれる
  function scriptParagraphs(article) {
    var paragraphs = [];
    Array.prototype.forEach.call(article.querySelectorAll("p"), function (p) {
      if (p.childNodes.length !== 1) return;
      if (p.firstChild.nodeType !== 3) return;
      if (!p.textContent.trim()) return;
      paragraphs.push(p);
    });
    return paragraphs;
  }

  // 段落の文字列を、文の並びと順に突き合わせて [開始, 終了) の位置に変換する。
  // 空白の入り方は無視して比較し、一文字でも食い違えば null を返して機能ごと諦める
  function alignCues(paragraphs, cues) {
    var plans = [];
    var ci = 0;
    for (var pi = 0; pi < paragraphs.length; pi++) {
      var s = paragraphs[pi].textContent;
      var ranges = [];
      var pos = 0;
      while (ci < cues.length) {
        while (pos < s.length && isSpace(s.charAt(pos))) pos++;
        if (pos >= s.length) break;
        var text = strip(cues[ci].text);
        var j = pos;
        var k = 0;
        while (j < s.length && k < text.length) {
          if (isSpace(s.charAt(j))) {
            j++;
            continue;
          }
          if (s.charAt(j) !== text.charAt(k)) return null;
          j++;
          k++;
        }
        // 段落をまたぐ文は想定していない。原稿と JSON がずれた印なので諦める
        if (k < text.length) return null;
        ranges.push({ start: pos, end: j, cue: ci });
        ci++;
        pos = j;
      }
      plans.push(ranges);
    }
    if (ci < cues.length) return null;
    return plans;
  }

  // 段落のテキストノードを、文ごとの <span> と間の文字列に置き換える
  function wrapParagraph(p, ranges, spans) {
    var s = p.textContent;
    var frag = document.createDocumentFragment();
    var pos = 0;
    ranges.forEach(function (r) {
      if (r.start > pos) frag.appendChild(document.createTextNode(s.slice(pos, r.start)));
      var span = document.createElement("span");
      span.className = "audio-cue";
      span.setAttribute("data-audio-cue", String(r.cue));
      span.textContent = s.slice(r.start, r.end);
      frag.appendChild(span);
      spans[r.cue] = span;
      pos = r.end;
    });
    if (pos < s.length) frag.appendChild(document.createTextNode(s.slice(pos)));
    p.textContent = "";
    p.appendChild(frag);
  }

  // 開始時刻の並びから、その時刻に読んでいる文を二分探索で求める
  function cueAt(starts, time) {
    var lo = 0;
    var hi = starts.length - 1;
    var found = -1;
    while (lo <= hi) {
      var mid = (lo + hi) >> 1;
      if (starts[mid] <= time) {
        found = mid;
        lo = mid + 1;
      } else {
        hi = mid - 1;
      }
    }
    return found;
  }

  // 上部に貼り付いたプレイヤーの下端。ハイライトはこれより下に置く
  function contentTop() {
    var style = getComputedStyle(document.documentElement);
    var top = parseFloat(style.getPropertyValue("--audio-sticky-top"));
    var height = parseFloat(style.getPropertyValue("--audio-sticky-height"));
    if (isNaN(top)) {
      var header = document.querySelector(".md-header");
      top = header ? header.offsetHeight : 0;
    }
    return top + (isNaN(height) ? 0 : height);
  }

  function scrollToSpan(span) {
    var top = contentTop();
    var rect = span.getBoundingClientRect();
    var visible =
      rect.top >= top + VISIBLE_MARGIN_PX && rect.bottom <= window.innerHeight - VISIBLE_MARGIN_PX;
    if (visible) return;
    var y = window.pageYOffset + rect.top - top - (window.innerHeight - top) * SCROLL_ANCHOR_RATIO;
    window.scrollTo({ top: Math.max(0, y), behavior: "smooth" });
  }

  function setup(audio, cues) {
    var article = document.querySelector(".md-typeset");
    if (!article) return;
    var paragraphs = scriptParagraphs(article);
    if (!paragraphs.length) return;
    var plans = alignCues(paragraphs, cues);
    if (!plans) return;

    var spans = [];
    paragraphs.forEach(function (p, i) {
      wrapParagraph(p, plans[i], spans);
    });
    var starts = cues.map(function (cue) {
      return cue.t;
    });

    var follow = loadFollow();
    var current = -1;
    // 再生を始める（または文をクリックする）まではスクロールしない。読み込み直後は
    // 前回の再生位置が復元されるだけなので、ページを開いた瞬間に飛ばされると驚く
    var engaged = false;

    // 追従のオン・オフ。プレイヤーと同じ行に置き、貼り付けたまま操作できるようにする
    var label = document.createElement("label");
    label.className = "audio-follow";
    label.title = "再生に合わせて本文を自動でスクロールする";
    var box = document.createElement("input");
    box.type = "checkbox";
    box.checked = follow;
    label.appendChild(box);
    label.appendChild(document.createTextNode("追従"));
    audio.parentNode.insertBefore(label, audio.nextSibling);

    function setFollow(on) {
      if (follow === on) return;
      follow = on;
      box.checked = on;
      saveFollow(on);
      if (on && current >= 0 && spans[current]) scrollToSpan(spans[current]);
    }

    box.addEventListener("change", function () {
      setFollow(box.checked);
    });

    function update() {
      var index = cueAt(starts, audio.currentTime);
      if (index === current) return;
      if (current >= 0 && spans[current]) spans[current].classList.remove("audio-cue-active");
      current = index;
      if (current < 0 || !spans[current]) return;
      spans[current].classList.add("audio-cue-active");
      if (follow && engaged) scrollToSpan(spans[current]);
    }

    audio.addEventListener("timeupdate", update);
    audio.addEventListener("seeked", update);
    audio.addEventListener("play", function () {
      engaged = true;
    });
    update();

    // 読者が自分でスクロールしたら追従を止める。スクロールイベントで判定すると
    // 自動スクロール自身と区別できないため、読者の操作そのものを見る
    function stopFollow(event) {
      if (!follow) return;
      if (event.type === "keydown") {
        var keys = ["ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End"];
        if (keys.indexOf(event.key) < 0) return;
        var tag = event.target && event.target.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA" || tag === "AUDIO") return;
      }
      setFollow(false);
    }
    window.addEventListener("wheel", stopFollow, { passive: true });
    window.addEventListener("touchmove", stopFollow, { passive: true });
    window.addEventListener("keydown", stopFollow);

    // 文をクリックしたら、その文の先頭から再生位置を移す。
    // 文字を選択しただけのときは動かさない
    article.addEventListener("click", function (event) {
      var span = event.target;
      if (!span || !span.classList || !span.classList.contains("audio-cue")) return;
      var selection = window.getSelection();
      if (selection && !selection.isCollapsed) return;
      var index = Number(span.getAttribute("data-audio-cue"));
      if (isNaN(index) || !cues[index]) return;
      engaged = true;
      audio.currentTime = cues[index].t;
      update();
    });
  }

  function init() {
    if (!/\/audio-scripts\//.test(window.location.pathname)) return;
    var audio = document.querySelector(".md-typeset audio");
    if (!audio || !window.fetch) return;
    var url = timingUrl(audio);
    if (!url) return;
    fetch(url)
      .then(function (res) {
        if (!res.ok) throw new Error("timing not found");
        return res.json();
      })
      .then(function (data) {
        if (data && data.cues && data.cues.length) setup(audio, data.cues);
      })
      .catch(function () {
        // タイミングデータがない章は、ハイライトなしの表示のまま残す
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
