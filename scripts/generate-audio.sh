#!/usr/bin/env bash
# docs/audio-scripts/*.md から章ごとの mp3 を docs/audio/ に生成する。
#
# 使い方:
#   scripts/generate-audio.sh            # 全章を生成
#   scripts/generate-audio.sh 03 11      # 第3章と第11章だけ再生成
#
# 依存: edge-tts (pip install edge-tts)。音声合成にネットワーク接続が必要。
# 音声や話速は環境変数 VOICE / RATE で変更できる。
set -euo pipefail

cd "$(dirname "$0")/.."

VOICE="${VOICE:-ja-JP-NanamiNeural}"
RATE="${RATE:-+0%}"

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
  tmp="$(mktemp)"
  # 見出し行（行頭が #）は読み上げ対象から除く
  grep -v '^#' "$src" > "$tmp"
  echo "generate: $out"
  edge-tts --voice "$VOICE" --rate "$RATE" --file "$tmp" --write-media "$out"
  rm -f "$tmp"
done
