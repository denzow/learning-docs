// 音声の再生位置を localStorage に保存し、聴きかけの章を続きから再開できるようにする。
// 読み上げ原稿ページ（docs/<教材>/audio-scripts/*.md）では <audio> の再生位置を保存・復元し、
// プレイヤーの下に「前回の続き」の案内を出す。トップページの章一覧表では
// mp3 リンクの隣に進捗バッジ（「68%」または「聴了」）を注入する。
// localStorage が使えない環境では何もせず、従来どおりの表示のまま残す。
(function () {
  "use strict";

  var SAVE_INTERVAL_MS = 5000;
  // 残りがこの秒数を切ったら聴了扱いにする
  var DONE_REMAINING_SEC = 5;

  function storageKey(slug) {
    return "audioProgress:" + slug;
  }

  // mp3 の URL（相対パスでもよい）から保存キーに使う「教材/章」を取り出す。
  // 教材ごとに docs/<教材>/audio/ へ分かれているので、ファイル名だけを使うと
  // 別の教材の同名の章（01-overview など）と進捗が混ざる。教材ディレクトリ名まで含める
  function slugFromUrl(url) {
    var path;
    try {
      path = new URL(url || "", window.location.href).pathname;
    } catch (e) {
      return null;
    }
    var m = path.match(/([^\/]+)\/audio\/([^\/]+)\.mp3$/);
    if (m) return m[1] + "/" + m[2];
    var base = path.match(/([^\/]+)\.mp3$/);
    return base ? base[1] : null;
  }

  function loadProgress(slug) {
    try {
      var raw = localStorage.getItem(storageKey(slug));
      if (!raw) return null;
      var data = JSON.parse(raw);
      if (typeof data.time !== "number" || typeof data.duration !== "number") return null;
      return data;
    } catch (e) {
      return null;
    }
  }

  function saveProgress(slug, audio, done) {
    try {
      localStorage.setItem(
        storageKey(slug),
        JSON.stringify({
          time: audio.currentTime,
          duration: audio.duration,
          done: !!done,
          updatedAt: Date.now(),
        })
      );
    } catch (e) {
      // プライベートブラウジング等で保存できなくても再生自体は妨げない
    }
  }

  function formatTime(sec) {
    var total = Math.floor(sec);
    var m = Math.floor(total / 60);
    var s = total % 60;
    return m + ":" + (s < 10 ? "0" : "") + s;
  }

  function percent(data) {
    if (!data.duration) return 0;
    return Math.min(100, Math.round((data.time / data.duration) * 100));
  }

  function isDone(data) {
    return !!data.done || (data.duration > 0 && data.duration - data.time < DONE_REMAINING_SEC);
  }

  // 原稿ページ：プレイヤーを画面上部に貼り付け、スクロールしても操作できるようにする。
  // 貼り付ける位置はヘッダの高さで決まるが、Material はヘッダ高の CSS 変数を公開して
  // いないため、実測して CSS 変数に渡す
  function setupSticky(audio) {
    // ビルド後の HTML では <audio> は <p> に包まれる。案内テキストも同じ <p> に入るので、
    // <p> ごと貼り付ければ両方が一緒に動く
    var target = audio.parentNode && audio.parentNode.tagName === "P" ? audio.parentNode : audio;
    target.classList.add("audio-sticky");
    // 「ページトップへ戻る」ボタン（.md-top, top: 3.2rem 固定）が貼り付けたプレイヤーと
    // 重なるので、このページだけボタンをプレイヤーの下へ逃がす
    document.body.classList.add("audio-sticky-page");

    var header = document.querySelector(".md-header");
    var root = document.documentElement.style;
    var applyMetrics = function () {
      if (header) root.setProperty("--audio-sticky-top", header.offsetHeight + "px");
      root.setProperty("--audio-sticky-height", target.offsetHeight + "px");
    };
    applyMetrics();
    window.addEventListener("resize", applyMetrics);
    // 案内テキストの削除やコントロールの折り返しで高さが変わるため、追随させる
    if (window.ResizeObserver) new ResizeObserver(applyMetrics).observe(target);
  }

  // 原稿ページ：再生位置の保存と復元、案内表示
  function setupPlayer(audio) {
    var slug = slugFromUrl(audio.getAttribute("src") || audio.currentSrc);
    if (!slug) return;

    var saved = loadProgress(slug);
    var noticeText = null;
    if (saved && isDone(saved)) {
      noticeText = "この章は聴了しています";
    } else if (saved && saved.time > 0) {
      noticeText =
        "前回の続き " + formatTime(saved.time) + " から再生できます（" + percent(saved) + "% 聴取済み）";
    }
    var notice = null;
    if (noticeText) {
      notice = document.createElement("span");
      notice.className = "audio-progress-notice";
      notice.textContent = noticeText;
      audio.parentNode.insertBefore(notice, audio.nextSibling);
    }
    // 案内が意味を持つのは再生を始めるまでなので、始まったら消す。
    // プレイヤーは画面上部に貼り付いたままなので、その分だけ本文の見える範囲が広がる
    audio.addEventListener("play", function () {
      if (notice && notice.parentNode) {
        notice.parentNode.removeChild(notice);
        notice = null;
      }
    });

    // 聴了した章は先頭から。聴きかけの章だけ保存位置に復元する（自動再生はしない）
    if (saved && !isDone(saved) && saved.time > 0) {
      var restore = function () {
        if (saved.time < audio.duration) audio.currentTime = saved.time;
      };
      if (audio.readyState >= 1) {
        restore();
      } else {
        audio.addEventListener("loadedmetadata", restore);
      }
    }

    var lastSave = 0;
    audio.addEventListener("timeupdate", function () {
      // 停止中のシーク（復元時の位置合わせを含む）でも timeupdate が飛ぶので、再生中だけ保存する
      if (audio.paused) return;
      var now = Date.now();
      if (now - lastSave < SAVE_INTERVAL_MS) return;
      if (!audio.duration) return;
      lastSave = now;
      saveProgress(slug, audio, false);
    });
    audio.addEventListener("pause", function () {
      // 再生終了時も pause が先に飛ぶが、直後の ended で done: true に上書きされる
      if (!audio.duration || audio.ended) return;
      saveProgress(slug, audio, false);
    });
    audio.addEventListener("ended", function () {
      saveProgress(slug, audio, true);
    });
  }

  // トップページ：章一覧表の mp3 リンクの隣に進捗バッジを注入する。
  // 表の中に限定することで、各章末尾の「演習と音声」リンクには注入しない
  function injectBadges() {
    var links = document.querySelectorAll(".md-typeset table a[href$='.mp3']");
    Array.prototype.forEach.call(links, function (link) {
      var slug = slugFromUrl(link.getAttribute("href"));
      if (!slug) return;
      var data = loadProgress(slug);
      if (!data) return;
      var done = isDone(data);
      var pct = percent(data);
      if (!done && pct <= 0) return;
      var badge = document.createElement("span");
      badge.className = "audio-progress-badge" + (done ? " audio-progress-done" : "");
      badge.textContent = done ? "聴了" : pct + "%";
      link.parentNode.insertBefore(badge, link.nextSibling);
    });
  }

  function init() {
    if (/\/audio-scripts\//.test(window.location.pathname)) {
      var audio = document.querySelector(".md-typeset audio");
      if (audio) {
        setupSticky(audio);
        setupPlayer(audio);
      }
      return;
    }
    injectBadges();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
