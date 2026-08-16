#!/usr/bin/env python3
"""edge-tts が出力した SRT を、読み上げ原稿ページ用のタイミング JSON に変換する。

使い方: scripts/srt-to-timing.py <入力.srt> <出力.json> [<読み上げテキスト>]

出力は {"cues": [{"t": 開始秒, "text": "文"}, ...]} の形で、docs/js/audio-highlight.js が
本文の文字列と突き合わせて段落を文単位に分割するのに使う。edge-tts の字幕は文単位で
区切られるため、ハイライトの対応づけは順に突き合わせるだけでよい。

ただし字幕のテキストは原稿と一字一句同じとは限らない。中黒（・）が読点に置き換わる例が
あるため、読み上げテキストを渡した場合は、各文のテキストを原稿側の同じ位置の文字列で
置き換える。こうしておけば、JSON の文はページ本文と必ず一致する。
"""
import json
import re
import sys

TIME = re.compile(r"(\d+):(\d\d):(\d\d)[,.](\d+)")


def to_seconds(stamp):
    m = TIME.match(stamp.strip())
    if not m:
        raise ValueError(f"時刻として読めない: {stamp!r}")
    h, mi, s, frac = m.groups()
    return int(h) * 3600 + int(mi) * 60 + int(s) + int(frac) / 10 ** len(frac)


def parse_srt(text):
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [line for line in block.split("\n") if line.strip()]
        if len(lines) < 3:
            continue
        start = lines[1].split("-->")[0]
        body = " ".join(line.strip() for line in lines[2:])
        cues.append({"t": round(to_seconds(start), 3), "text": body})
    return cues


def align_to_source(cues, source):
    """各文のテキストを、原稿の同じ位置の文字列で置き換える。

    空白を除いた文字数だけを頼りに位置を進めるので、字幕側で文字が置き換わっていても
    原稿の表記に揃う。文字数が合わなければ、対応づけが崩れているので中断する。
    """
    positions = [i for i, ch in enumerate(source) if not ch.isspace()]
    total = sum(len(re.sub(r"\s+", "", cue["text"])) for cue in cues)
    if total != len(positions):
        sys.exit(f"字幕と原稿で文字数が合わない: 字幕 {total} 文字, 原稿 {len(positions)} 文字")

    replaced = 0
    at = 0
    for cue in cues:
        n = len(re.sub(r"\s+", "", cue["text"]))
        span = source[positions[at] : positions[at + n - 1] + 1]
        if re.sub(r"\s+", "", span) != re.sub(r"\s+", "", cue["text"]):
            replaced += 1
        cue["text"] = span.strip()
        at += n
    return replaced


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit("使い方: srt-to-timing.py <入力.srt> <出力.json> [<読み上げテキスト>]")
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        cues = parse_srt(f.read())
    if not cues:
        sys.exit(f"字幕が空である: {src}")

    note = ""
    if len(sys.argv) == 4:
        with open(sys.argv[3], encoding="utf-8") as f:
            replaced = align_to_source(cues, f.read())
        if replaced:
            note = f", 原稿の表記に揃えた文 {replaced}"

    with open(dst, "w", encoding="utf-8") as f:
        json.dump({"cues": cues}, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"timing: {dst} ({len(cues)} 文{note})")


if __name__ == "__main__":
    main()
