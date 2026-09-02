#!/usr/bin/env bash
# 教材のディレクトリと雛形を作り、mkdocs.yml の nav と docs/index.md の教材一覧に登録する。
#
# 使い方:
#   scripts/new-material.sh <ディレクトリ名> "<教材のタイトル>" ["<タブのラベル>"]
#   例: scripts/new-material.sh data-pipeline "データパイプラインの学習ドキュメント" "データパイプライン"
#
# ディレクトリ名は docs/ 直下に作る名前で、公開 URL のパスにもなる（英小文字とハイフン）。
# タブのラベルを省略すると教材のタイトルをそのまま使う。
# 作成後は scripts/new-chapter.sh で章を追加する。
set -euo pipefail

cd "$(dirname "$0")/.."

if [ "$#" -lt 2 ]; then
  echo "使い方: $0 <ディレクトリ名> \"<教材のタイトル>\" [\"<タブのラベル>\"]" >&2
  exit 1
fi
dir="$1"
title="$2"
label="${3:-$2}"

case "$dir" in
  *[!a-z0-9-]*|"") echo "ディレクトリ名は英小文字、数字、ハイフンだけにする: $dir" >&2; exit 1 ;;
esac
if [ -e "docs/$dir" ]; then
  echo "docs/$dir はすでにある" >&2
  exit 1
fi

mkdir -p "docs/$dir/exercises" "docs/$dir/audio-scripts" "docs/$dir/audio"
python3 - "$dir" "$title" "$label" <<'PY'
import re, sys
dir_, title, label = sys.argv[1:4]

index = open("templates/material-index.md", encoding="utf-8").read().replace("{{TITLE}}", title)
open(f"docs/{dir_}/index.md", "w", encoding="utf-8").write(index)

# mkdocs.yml の nav: 「ラベル: ディレクトリ/」の最後の行の直後に追加する
path = "mkdocs.yml"
lines = open(path, encoding="utf-8").read().split("\n")
last = max(i for i, l in enumerate(lines) if re.match(r"^  - .+: [a-z0-9-]+/$", l))
lines.insert(last + 1, f"  - {label}: {dir_}/")
open(path, "w", encoding="utf-8").write("\n".join(lines))

# docs/index.md の教材一覧の表: 最後の行の直後に追加する
path = "docs/index.md"
lines = open(path, encoding="utf-8").read().split("\n")
last = max(i for i, l in enumerate(lines) if l.startswith("| [") )
lines.insert(last + 1, f"| [{label}]({dir_}/index.md) | （教材の内容を一文で書く） | 全 N 章 |")
open(path, "w", encoding="utf-8").write("\n".join(lines))
PY

cat <<MSG
作成した:
  docs/$dir/index.md            教材のトップページ（説明と目次の表を埋める）
  docs/$dir/exercises/          演習問題
  docs/$dir/audio-scripts/      読み上げ原稿
  docs/$dir/audio/              読み上げ音声（scripts/generate-audio.sh $dir で生成）
登録した:
  mkdocs.yml の nav に「$label: $dir/」
  docs/index.md の教材一覧に 1 行（内容と章数を書き換える）
次の手順:
  scripts/new-chapter.sh $dir 01 <slug> "<章のタイトル>"
MSG
