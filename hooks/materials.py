"""mkdocs.yml の nav に書いた教材ディレクトリを、章ごとの入れ子に展開する MkDocs hook。

mkdocs.yml の nav には、教材ごとに「ラベル: ディレクトリ名/」の 1 行だけを書く。

    nav:
      - ホーム: index.md
      - データモデリング: data-modeling/

この hook は、値が / で終わる項目を教材ディレクトリと見なし、docs/<ディレクトリ>/ の
ファイル構成から次の入れ子を組み立てて置き換える。

    - データモデリング:
        - data-modeling/index.md
        - 第1章 データモデリングの全体像:
            - data-modeling/01-overview.md
            - 第1章 演習問題: data-modeling/exercises/01-overview.md
            - 第1章 読み上げ原稿: data-modeling/audio-scripts/01-overview.md
        - ...

教材ディレクトリの規約:

- index.md            教材のトップページ。navigation.indexes によりセクション見出しのリンク先になる
- NN-<slug>.md        章の本文。NN は 2 桁の章番号で、この順に並ぶ。ラベルは本文の H1
- exercises/NN-<slug>.md      章の演習問題（任意）。ラベルは「第N章 演習問題」
- audio-scripts/NN-<slug>.md  章の読み上げ原稿（任意）。ラベルは「第N章 読み上げ原稿」
- audio/NN-<slug>.mp3         読み上げ音声（任意）。nav には載せない

章の本文は、見出しをそのままラベルに使うため、パスだけを nav に置く（MkDocs が H1 を採用する）。
演習と原稿は同じ章番号のファイルがあるときだけ加える。

あわせて、章の本文の末尾に演習問題と音声への導線の節（「## 演習と音声」）を、
存在するファイルだけから組み立てて足す。本文の Markdown には書かない。
mp3 を生成する前の章でも、存在しないファイルへのリンクが生まれず strict ビルドが通る。
"""

import os
import re

CHAPTER_FILE = re.compile(r"^(\d{2})-[^/]+\.md$")

# 章ごとの付属ページ。ディレクトリ名と nav ラベルの組
COMPANIONS = (
    ("exercises", "演習問題"),
    ("audio-scripts", "読み上げ原稿"),
)


def on_config(config):
    if config.get("nav"):
        config["nav"] = [expand(item, config["docs_dir"]) for item in config["nav"]]
    return config


def expand(item, docs_dir):
    """「ラベル: ディレクトリ/」の項目だけを展開し、それ以外はそのまま返す。"""
    if not isinstance(item, dict) or len(item) != 1:
        return item
    (label, target), = item.items()
    if not isinstance(target, str) or not target.endswith("/"):
        return item
    material = target.rstrip("/")
    root = os.path.join(docs_dir, material)
    if not os.path.isdir(root):
        raise FileNotFoundError(f"nav の教材ディレクトリが見つからない: docs/{material}/")
    return {label: material_nav(root, material)}


def material_nav(root, material):
    entries = []
    if os.path.exists(os.path.join(root, "index.md")):
        entries.append(f"{material}/index.md")
    for name in sorted(os.listdir(root)):
        m = CHAPTER_FILE.match(name)
        if not m:
            continue
        number = int(m.group(1))
        section = [f"{material}/{name}"]
        for subdir, label in COMPANIONS:
            if os.path.exists(os.path.join(root, subdir, name)):
                section.append({f"第{number}章 {label}": f"{material}/{subdir}/{name}"})
        entries.append({heading(os.path.join(root, name), name): section})
    return entries


def heading(path, fallback):
    """ファイル先頭の H1 をセクションのラベルにする。H1 がなければファイル名で代用する。"""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("# "):
                return line[2:].strip()
    return fallback


# 章末の導線。本文にこれらの見出しがすでにあれば二重に足さない
TRAILER_HEADINGS = ("## 演習と音声", "## 演習", "## 音声")


def on_page_markdown(markdown, page, config, files):
    parts = page.file.src_uri.split("/")
    if len(parts) != 2:
        return markdown
    material, name = parts
    m = CHAPTER_FILE.match(name)
    if not m:
        return markdown
    if any(f"\n{h}\n" in markdown for h in TRAILER_HEADINGS):
        return markdown

    root = os.path.join(config["docs_dir"], material)
    number = int(m.group(1))
    base = name[:-3]
    exercise = os.path.exists(os.path.join(root, "exercises", name))
    script = os.path.exists(os.path.join(root, "audio-scripts", name))
    mp3 = os.path.exists(os.path.join(root, "audio", base + ".mp3"))

    items = []
    if exercise:
        items.append(f"- [第{number}章 演習問題](exercises/{name})：四択で章の理解を確認できる。")
    if mp3:
        note = f"（[原稿](audio-scripts/{name})）" if script else ""
        items.append(f"- [読み上げ音声（mp3）](audio/{base}.mp3)：聴いて復習できる{note}。")
    elif script:
        items.append(f"- [読み上げ原稿](audio-scripts/{name})：音声は未生成のため原稿のみ。")
    if not items:
        return markdown

    heading = "演習と音声" if exercise and (mp3 or script) else ("演習" if exercise else "音声")
    return markdown.rstrip("\n") + f"\n\n## {heading}\n\n" + "\n".join(items) + "\n"
