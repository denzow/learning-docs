#!/usr/bin/env bash
# docs/audio-scripts/*.md から、章ごとの mp3 と文単位のタイミングデータを
# docs/audio/ に生成する。
#
# 使い方:
#   scripts/generate-audio.sh                  # 全章の mp3 とタイミングを生成
#   scripts/generate-audio.sh 03 11            # 第3章と第11章だけ再生成
#   scripts/generate-audio.sh --timings-only   # mp3 は据え置き、タイミングだけ生成
#
# 依存: edge-tts (pip install edge-tts)。音声合成にネットワーク接続が必要。
# 音声や話速は環境変数 VOICE / RATE で変更できる。
#
# --timings-only は、合成した音声を捨ててタイミングだけを作り直す。同じ原稿を
# 同じ VOICE / RATE で合成すれば再生時間は変わらないため、コミット済みの mp3
# （計 68MB）を差し替えずにタイムスタンプだけを更新できる。
set -euo pipefail

cd "$(dirname "$0")/.."

VOICE="${VOICE:-ja-JP-NanamiNeural}"
RATE="${RATE:-+0%}"

timings_only=false
if [ "${1:-}" = "--timings-only" ]; then
  timings_only=true
  shift
fi

mkdir -p docs/audio

for src in docs/audio-scripts/*.md; do
  base="$(basename "$src" .md)"
  if [ "$#" -gt 0 ]; then
    match=false
    for prefix in "$@"; do
      case "$base" in "$prefix"*) match=true ;; esac
    done
    "$match" || continue
  fi

  out="docs/audio/${base}.mp3"
  timing="docs/audio/${base}.timing.json"
  text="$(mktemp)"
  srt="$(mktemp)"
  # 見出し行（行頭が #）とプレイヤーの audio 要素は読み上げ対象から除く。
  # audio 要素の行を残すと、代替テキストが冒頭に読み上げられてしまい、
  # コミット済みの mp3 と再生時間がずれてタイミングが使えなくなる
  grep -v -e '^#' -e '^<audio' "$src" > "$text"

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
