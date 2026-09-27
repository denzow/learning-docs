// 読み上げ原稿ページに RSVP（Rapid Serial Visual Presentation）モードを足す。
// オンにすると原稿を隠し、その場所に置いたパネルへ、読み上げに合わせて文節を
// 一つずつ大きく表示する。目を動かさずに読めるので、聴きながら文字を追う負荷が減る。
//
// 表示の進み方は音声の再生位置だけで決める。文の開始時刻は timing.json にあり、
// 文の中は文節の文字数に比例して時刻を割り振る。速く読みたいときはプレイヤーの
// 再生速度を上げればよく、この JS は独自の時計を持たない。
// 文節の区切りには Intl.Segmenter を使い、使えないブラウザでは句読点と固定長で区切る。
// timing.json を置いていない章では何もせず、素の表示のまま残す。
(function () {
  "use strict";

  var RSVP_KEY = "audioRsvp";
  // 一度に見せる文字数の上限。読み上げの速さ（1 秒に 6〜7 字）で 1.5 秒ほどになる長さ。
  // 文節の途中では切らないので、長い文節はこれを越えて一つで出す
  var CHUNK_MAX_CHARS = 10;
  // 最後の文の長さが音声の長さから取れないときに使う、1 秒あたりの文字数
  var FALLBACK_CHARS_PER_SEC = 6.5;

  function loadEnabled() {
    try {
      return localStorage.getItem(RSVP_KEY) === "on";
    } catch (e) {
      return false;
    }
  }

  function saveEnabled(on) {
    try {
      localStorage.setItem(RSVP_KEY, on ? "on" : "off");
    } catch (e) {
      // 保存できなくてもそのページの間は動く
    }
  }

  function timingUrl(audio) {
    var src = audio.currentSrc || audio.src || "";
    if (!/\.mp3(\?|#|$)/.test(src)) return null;
    return src.replace(/\.mp3(\?[^#]*)?(#.*)?$/, ".timing.json");
  }

  function isPunctuation(text) {
    return /^[、。，．,.!?！？]+$/.test(text);
  }

  function startsWithHiragana(text) {
    return /^[ぁ-ゖ]/.test(text);
  }

  function endsWithDigit(text) {
    return /[0-9０-９]$/.test(text);
  }

  // 文を語に分ける。Intl.Segmenter があれば辞書に基づく語、なければ句読点と 1 文字ずつ
  function segments(text) {
    if (window.Intl && Intl.Segmenter) {
      var segmenter = new Intl.Segmenter("ja", { granularity: "word" });
      var out = [];
      var iter = segmenter.segment(text);
      var it = iter[Symbol.iterator]();
      for (var r = it.next(); !r.done; r = it.next()) {
        if (r.value.segment.trim()) out.push(r.value.segment);
      }
      return out;
    }
    return text.replace(/\s+/g, "").split(/([、。，．,.!?！？])/).filter(Boolean);
  }

  // 語を文節にまとめる。Intl.Segmenter の語は「光」「が」「分」「かって」のように細かいので、
  // 一つずつ出すと読みにくい。ひらがなで始まる語（助詞、助動詞、送り仮名）は直前の語に
  // つなぐ。一文字の語（「第」「各」）や数字で終わる語（「第2」に続く「章」）も次につなぐ。
  // 句読点は直前につなぎ、そこで区切る
  function bunsetsu(text) {
    var out = [];
    var current = "";
    segments(text).forEach(function (seg) {
      if (isPunctuation(seg)) {
        current += seg;
        out.push(current);
        current = "";
        return;
      }
      var joins = startsWithHiragana(seg) || current.length === 1 || endsWithDigit(current);
      if (current && !joins) {
        out.push(current);
        current = "";
      }
      current += seg;
    });
    if (current) out.push(current);
    return out;
  }

  // 文節を、上限の文字数までつないで一度に見せる単位にする。文節の途中では切らず、
  // 句読点で終わる文節の後では必ず区切る
  function chunkSentence(text) {
    var chunks = [];
    var current = "";
    bunsetsu(text).forEach(function (b) {
      if (current && current.length + b.length > CHUNK_MAX_CHARS) {
        chunks.push(current);
        current = "";
      }
      current += b;
      if (isPunctuation(b.charAt(b.length - 1))) {
        chunks.push(current);
        current = "";
      }
    });
    if (current) chunks.push(current);
    return chunks;
  }

  // 全文を文節に展開し、それぞれの開始時刻を付ける。文の長さは次の文の開始時刻までとし、
  // 文の中は文字数に比例して配る。最後の文だけは音声の長さで閉じる
  function buildChunks(cues, duration) {
    var chunks = [];
    cues.forEach(function (cue, i) {
      var text = cue.text.replace(/\s+/g, "");
      var end;
      if (i + 1 < cues.length) {
        end = cues[i + 1].t;
      } else if (isFinite(duration) && duration > cue.t) {
        end = duration;
      } else {
        end = cue.t + text.length / FALLBACK_CHARS_PER_SEC;
      }
      var parts = chunkSentence(text);
      var total = 0;
      parts.forEach(function (p) {
        total += p.length;
      });
      var offset = 0;
      parts.forEach(function (p) {
        chunks.push({ t: cue.t + ((end - cue.t) * offset) / total, text: p, sentence: i });
        offset += p.length;
      });
    });
    return chunks;
  }

  function indexAt(chunks, time) {
    var lo = 0;
    var hi = chunks.length - 1;
    var found = -1;
    while (lo <= hi) {
      var mid = (lo + hi) >> 1;
      if (chunks[mid].t <= time) {
        found = mid;
        lo = mid + 1;
      } else {
        hi = mid - 1;
      }
    }
    return found;
  }

  function setup(audio, cues) {
    var sticky = audio.parentNode;
    if (!sticky) return;
    var article = sticky.parentNode;
    if (!article) return;

    var panel = document.createElement("div");
    panel.className = "audio-rsvp";
    panel.setAttribute("aria-live", "off");
    var word = document.createElement("div");
    word.className = "audio-rsvp-word";
    var hint = document.createElement("p");
    hint.className = "audio-rsvp-hint";
    hint.textContent = "再生すると、読み上げに合わせて文節を一つずつ表示します。速さはプレイヤーの再生速度で変えられます。";
    var context = document.createElement("p");
    context.className = "audio-rsvp-context";
    var meter = document.createElement("p");
    meter.className = "audio-rsvp-meter";
    panel.appendChild(word);
    panel.appendChild(hint);
    panel.appendChild(context);
    panel.appendChild(meter);
    // パネルを押すと再生と一時停止を切り替える。文字を選択しただけのときは何もしない
    panel.addEventListener("click", function () {
      var selection = window.getSelection();
      if (selection && !selection.isCollapsed) return;
      if (audio.paused) {
        audio.play();
      } else {
        audio.pause();
      }
    });

    // RSVP のオン・オフ。追従のチェックと同じ行に置き、貼り付けたまま切り替えられるようにする
    var label = document.createElement("label");
    label.className = "audio-rsvp-toggle";
    label.title = "原稿の代わりに、読み上げに合わせて文節を一つずつ大きく表示する";
    var box = document.createElement("input");
    box.type = "checkbox";
    label.appendChild(box);
    label.appendChild(document.createTextNode("RSVP"));
    var notice = sticky.querySelector(".audio-progress-notice");
    sticky.insertBefore(label, notice);

    var chunks = null;
    var current = -1;

    function rebuild() {
      chunks = buildChunks(cues, audio.duration);
      current = -1;
    }

    function render() {
      if (!chunks) rebuild();
      var index = indexAt(chunks, audio.currentTime);
      if (index === current) return;
      current = index;
      if (index < 0) {
        word.textContent = "";
        context.textContent = "";
        meter.textContent = "";
        hint.style.display = "";
        return;
      }
      hint.style.display = "none";
      var chunk = chunks[index];
      word.textContent = chunk.text;
      // 文脈が分かるよう、いま読んでいる文を小さく添え、表示中の文節を強調する
      context.textContent = "";
      var start = index;
      while (start > 0 && chunks[start - 1].sentence === chunk.sentence) start--;
      for (var i = start; i < chunks.length && chunks[i].sentence === chunk.sentence; i++) {
        var span = document.createElement("span");
        if (i === index) span.className = "audio-rsvp-current";
        span.textContent = chunks[i].text;
        context.appendChild(span);
      }
      meter.textContent = chunk.sentence + 1 + " / " + cues.length + " 文";
    }

    var raf = 0;
    function tick() {
      render();
      raf = audio.paused ? 0 : requestAnimationFrame(tick);
    }

    function setEnabled(on) {
      box.checked = on;
      saveEnabled(on);
      if (on) {
        document.body.classList.add("audio-rsvp-on");
        if (!panel.parentNode) article.insertBefore(panel, sticky.nextSibling);
        current = -1;
        tick();
      } else {
        document.body.classList.remove("audio-rsvp-on");
        if (panel.parentNode) panel.parentNode.removeChild(panel);
        if (raf) cancelAnimationFrame(raf);
        raf = 0;
      }
    }

    box.addEventListener("change", function () {
      setEnabled(box.checked);
    });

    // 再生中は毎フレーム、停止中はシークのたびに表示を合わせる。
    // timeupdate は 4 分の 1 秒おきにしか飛ばず、文節の切り替わりが遅れて見えるため rAF を使う
    audio.addEventListener("play", function () {
      if (box.checked && !raf) tick();
    });
    audio.addEventListener("seeked", function () {
      if (box.checked) render();
    });
    audio.addEventListener("timeupdate", function () {
      if (box.checked && audio.paused) render();
    });
    // 最後の文の長さは音声の長さで決まる。長さが分かった時点で割り直す
    audio.addEventListener("loadedmetadata", function () {
      rebuild();
      if (box.checked) render();
    });
    audio.addEventListener("durationchange", function () {
      rebuild();
      if (box.checked) render();
    });

    if (loadEnabled()) setEnabled(true);
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
        // タイミングデータがない章は、RSVP の切り替えを出さない
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
