#!/usr/bin/env bash
# docs/<教材>/audio-scripts/*.md から、章ごとの mp3 と文単位のタイミングデータを
# docs/<教材>/audio/ に生成する。
#
# 使い方:
#   scripts/generate-audio.sh <教材>                  # 全章の mp3 とタイミングを生成
#   scripts/generate-audio.sh <教材> 03 11            # 第3章と第11章だけ再生成
#   scripts/generate-audio.sh --timings-only <教材>   # mp3 は据え置き、タイミングだけ生成
#
# <教材> は docs/ 直下のディレクトリ名（例: data-modeling）。
#
# 依存: edge-tts (pip install edge-tts)。音声合成にネットワーク接続が必要。
# 音声や話速は環境変数 VOICE / RATE で変更できる。
#
# --timings-only は、合成した音声を捨ててタイミングだけを作り直す。同じ原稿を
# 同じ VOICE / RATE で合成すれば再生時間は変わらないため、コミット済みの mp3
# を差し替えずにタイムスタンプだけを更新できる。
set -euo pipefail

cd "$(dirname "$0")/.."

VOICE="${VOICE:-ja-JP-NanamiNeural}"
RATE="${RATE:-+0%}"

timings_only=false
if [ "${1:-}" = "--timings-only" ]; then
  timings_only=true
  shift
fi

if [ "$#" -lt 1 ] || [ ! -d "docs/$1/audio-scripts" ]; then
  echo "使い方: $0 [--timings-only] <教材> [章番号...]" >&2
  echo "教材は docs/ 直下のディレクトリ名で、docs/<教材>/audio-scripts/ が必要" >&2
  exit 1
fi
material="$1"
shift

scripts_dir="docs/$material/audio-scripts"
audio_dir="docs/$material/audio"
mkdir -p "$audio_dir"

for src in "$scripts_dir"/*.md; do
  base="$(basename "$src" .md)"
  if [ "$#" -gt 0 ]; then
    match=false
    for prefix in "$@"; do
      case "$base" in "$prefix"*) match=true ;; esac
    done
    "$match" || continue
  fi

  out="$audio_dir/${base}.mp3"
  timing="$audio_dir/${base}.timing.json"
  text="$(mktemp)"
  srt="$(mktemp)"
  # 読み上げるのは地の文の段落だけにする。見出し行（行頭が #）、プレイヤーの audio 要素、
  # 「対象章：」の行のようなリンクを含む行は除く。これらを残すと、記法や代替テキストが
  # そのまま読み上げられ、コミット済みの mp3 と再生時間がずれてタイミングが使えなくなる。
  # 除外の条件は docs/js/audio-highlight.js が本文段落と見なす条件（リンクや強調を含まない
  # 段落）に対応させている
  grep -v -e '^#' -e '^<' -e '](' "$src" > "$text"

  if "$timings_only"; then
    media="$(mktemp)"
    echo "timings: $timing"
  else
    media="$out"
    echo "generate: $out"
  fi

  edge-tts --voice "$VOICE" --rate "$RATE" --file "$text" \
    --write-media "$media" --write-subtitles "$srt"
  python3 scripts/srt-to-timing.py "$srt" "$timing" "$text"

  if "$timings_only"; then
    rm -f "$media"
  fi
  rm -f "$text" "$srt"
done
