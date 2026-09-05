#!/usr/bin/env python3
"""イラストの生成モジュールから SVG を書き出す。

使い方:
  scripts/render-figures.py <教材>                      # diagrams/<教材>/figures/*.py のすべての図を描く
  scripts/render-figures.py <教材> fig-04-monoblock     # 名前を指定して描く

diagrams/<教材>/figures/ にある Python モジュールを順に読み込み、各モジュールの
FIGURES（{ファイル名（拡張子なし）: 関数} の辞書。関数は figlib.Figure を返す）を
docs/<教材>/img/<ファイル名>.svg に書き出す。
モジュールは scripts/figlib.py を `import figlib` で使う。
"""

import importlib.util
import os
import sys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    material = sys.argv[1]
    names = set(sys.argv[2:])
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(scripts_dir, "..")
    src_dir = os.path.join(root, "diagrams", material, "figures")
    out_dir = os.path.join(root, "docs", material, "img")
    if not os.path.isdir(src_dir):
        print(f"{os.path.relpath(src_dir, root)} がない", file=sys.stderr)
        sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    for fname in sorted(os.listdir(src_dir)):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(f"figures_{material}_{fname[:-3]}", os.path.join(src_dir, fname))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        figures = getattr(module, "FIGURES", {})
        for name, fn in figures.items():
            if names and name not in names:
                continue
            fig = fn()
            out = os.path.join(out_dir, name + ".svg")
            fig.save(out)
            print("render:", os.path.relpath(out, root))


if __name__ == "__main__":
    main()
