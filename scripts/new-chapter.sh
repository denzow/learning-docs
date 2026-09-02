#!/usr/bin/env bash
# 教材に章を追加する。本文、演習問題、読み上げ原稿の雛形を templates/ から作る。
#
# 使い方:
#   scripts/new-chapter.sh <教材> <NN> <slug> "<章のタイトル>" [chapter|exercise|audio-script ...]
#   例: scripts/new-chapter.sh data-pipeline 01 overview "データパイプラインの全体像"
#       scripts/new-chapter.sh data-pipeline 01 overview "データパイプラインの全体像" exercise
#
# <NN> は 2 桁の章番号、<slug> は英小文字のファイル名（ファイルは NN-slug.md になる）。
# 末尾に種類を並べると、その種類だけ作る。省略すると三つとも作る。
# すでにあるファイルは上書きしない。
set -euo pipefail

cd "$(dirname "$0")/.."

if [ "$#" -lt 4 ]; then
  echo "使い方: $0 <教材> <NN> <slug> \"<章のタイトル>\" [chapter|exercise|audio-script ...]" >&2
  exit 1
fi
material="$1"
number="$2"
slug="$3"
title="$4"
shift 4
kinds=("$@")
if [ "${#kinds[@]}" -eq 0 ]; then
  kinds=(chapter exercise audio-script)
fi

if [ ! -d "docs/$material" ]; then
  echo "docs/$material がない。先に scripts/new-material.sh で教材を作る" >&2
  exit 1
fi
case "$number" in
  [0-9][0-9]) ;;
  *) echo "章番号は 2 桁で指定する: $number" >&2; exit 1 ;;
esac
case "$slug" in
  *[!a-z0-9-]*|"") echo "slug は英小文字、数字、ハイフンだけにする: $slug" >&2; exit 1 ;;
esac

file="$number-$slug"
for kind in "${kinds[@]}"; do
  case "$kind" in
    chapter) dst="docs/$material/$file.md" ;;
    exercise) dst="docs/$material/exercises/$file.md" ;;
    audio-script) dst="docs/$material/audio-scripts/$file.md" ;;
    *) echo "種類は chapter, exercise, audio-script のいずれか: $kind" >&2; exit 1 ;;
  esac
  if [ -e "$dst" ]; then
    echo "skip (exists): $dst"
    continue
  fi
  mkdir -p "$(dirname "$dst")"
  python3 - "templates/$kind.md" "$dst" "$number" "$file" "$title" <<'PY'
import sys
src, dst, number, file, title = sys.argv[1:6]
text = open(src, encoding="utf-8").read()
text = text.replace("{{N}}", str(int(number))).replace("{{FILE}}", file).replace("{{TITLE}}", title)
open(dst, "w", encoding="utf-8").write(text)
PY
  echo "create: $dst"
done

cat <<MSG
次の手順:
  docs/$material/index.md の目次の表に第$((10#$number))章の行を足す
  本文と演習問題を執筆したら、読み上げ原稿を書いて scripts/generate-audio.sh $material $number で音声を作る
MSG
