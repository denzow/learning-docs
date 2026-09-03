#!/usr/bin/env python3
"""edge-tts が出力した SRT を、読み上げ原稿ページ用のタイミング JSON に変換する。

使い方: scripts/srt-to-timing.py <入力.srt> <出力.json> [<読み上げテキスト>]

出力は {"cues": [{"t": 開始秒, "text": "文"}, ...]} の形で、docs/js/audio-highlight.js が
本文の文字列と突き合わせて段落を文単位に分割するのに使う。edge-tts の字幕は文単位で
区切られるため、ハイライトの対応づけは順に突き合わせるだけでよい。

ただし字幕のテキストは原稿と一字一句同じとは限らない。中黒（・）が読点に置き換わる例が
あるため、読み上げテキストを渡した場合は、各文のテキストを原稿側の同じ位置の文字列で
置き換える。こうしておけば、JSON の文はページ本文と必ず一致する。

また、edge-tts は長い原稿を内部で数千バイトごとに分割して合成するが、分割点が文の途中に
落ちると、その文は読み上げられるのに字幕から抜けることがある。原稿の途中で字幕に
現れない文字列があれば、直前の字幕の終了時刻を開始時刻とする文を補って埋める。
読み上げ自体は行われているので、音声を作り直す必要はない。
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
        start, end = lines[1].split("-->")[:2]
        body = " ".join(line.strip() for line in lines[2:])
        cues.append({"t": round(to_seconds(start), 3), "end": round(to_seconds(end), 3), "text": body})
    return cues


def align_to_source(cues, source):
    """各文のテキストを、原稿の同じ位置の文字列で置き換える。

    空白を除いた文字列で原稿の位置を進めるので、字幕側で文字が置き換わっていても
    原稿の表記に揃う。字幕に現れない文字列が原稿にあれば、直前の文の終了時刻から
    始まる文として補う。抜けたのが括弧のような記号だけなら、直後の文に含める。字幕の文が原稿のどこにも見つからなければ、対応づけが
    崩れているので中断する。

    戻り値は (原稿の表記に揃えた文の数, 補った文の数)。
    """
    positions = [i for i, ch in enumerate(source) if not ch.isspace()]
    compact = "".join(source[i] for i in positions)
    # 字幕側で置き換わる文字を原稿側の表記に寄せてから比べる
    def normalize(text):
        return re.sub(r"\s+", "", text).replace("・", "、")

    aligned = []
    replaced = 0
    filled = 0
    at = 0
    last_end = 0.0

    def span(start, end):
        return source[positions[start] : positions[end - 1] + 1].strip()

    for cue in cues:
        text = normalize(cue["text"])
        n = len(text)
        if normalize(compact[at : at + n]) != text:
            found = normalize(compact[at:]).find(text)
            if found < 0:
                sys.exit(f"字幕の文が原稿に見つからない: {cue['text'][:30]!r}（原稿の位置 {at}）")
            if re.search(r"\w", compact[at : at + found]):
                aligned.append({"t": last_end, "text": span(at, at + found)})
                filled += 1
                at += found
            else:
                # 括弧のような記号だけが抜けたときは、直後の文に含めて揃える
                n += found
                text = normalize(compact[at : at + n])
        if re.sub(r"\s+", "", compact[at : at + n]) != re.sub(r"\s+", "", cue["text"]):
            replaced += 1
        aligned.append({"t": cue["t"], "text": span(at, at + n)})
        last_end = cue["end"]
        at += n
    if at < len(compact):
        aligned.append({"t": last_end, "text": span(at, len(compact))})
        filled += 1
    cues[:] = aligned
    return replaced, filled


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
            replaced, filled = align_to_source(cues, f.read())
        if replaced:
            note += f", 原稿の表記に揃えた文 {replaced}"
        if filled:
            note += f", 字幕にない文を補った {filled}"
    for cue in cues:
        cue.pop("end", None)

    with open(dst, "w", encoding="utf-8") as f:
        json.dump({"cues": cues}, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"timing: {dst} ({len(cues)} 文{note})")


if __name__ == "__main__":
    main()
