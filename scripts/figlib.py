"""教材のイラスト（SVG）を Python で組み立てるための作図ライブラリ。

使い方:
    import figlib as fl

    def fig_example():
        f = fl.Figure(800, 400, "タイトル", "副題（任意）")
        f.panel(30, 70, 360, 300, "左の見出し")
        fl.face(f, 210, 190, s=0.9, shadow="loop", catch="ul")
        f.callout(1, 60, 100, to=(120, 140))
        f.callout_list(430, 90, ["発光管", "モデリングランプ"])
        return f

    FIGURES = {"fig-00-example": fig_example}   # scripts/render-figures.py がこの辞書を見る

座標はすべて左上原点の px。角度は度で、回転は時計回りが正（SVG の慣習）。
部品は Figure のメソッドか、Figure を第一引数に取るモジュール関数として提供する。
描画結果は文字列として fig.add() で積み、fig.save(path) か fig.to_svg() で SVG にする。

スタイル定数
    FONT, INK, MUTED, LIGHT, ACCENT, DIM, SKIN, CLOTH, HAIR, SHADOW, WALL, BLACK, FLOOR, BODY,
    CAMERA_BODY, LENS, PAPER。scripts/render-diagrams.py も同じ定数を使う。

Figure（枠と基本図形）
    Figure(width, height, title=None, subtitle=None)   白地の角丸の枠、タイトル 16px 太字、副題 12px
    .add(svg)                 SVG 断片を積む
    .add_def(svg)             <defs> に入れる断片を積む（gradient、clipPath など）
    .uid(prefix)              図の中で重複しない id
    .text(x, y, s, size=12, anchor="start", color=INK, weight="normal", lh=1.35)   複数行は \\n
    .line / .rect / .circle / .path                     基本図形
    .marker(color)            色に応じた矢印マーカーの id（arrow-ink など）を返し、必要なら登録する
    .to_svg() / .save(path)

汎用部品
    .panel(x, y, w, h, title=None, fill=FLOOR, stroke="#e8e5df", rx=6, title_size=13)   比較用のカード枠
    .badge(x, y, label, r=10, fill=INK)                 番号や記号の入った丸
    .leader(x1, y1, x2, y2, color=INK)                  引き出し線（先端に点）
    .callout(n, x, y, to=None, r=10)                    番号付きの丸と、to への引き出し線
    .callout_list(x, y, items, r=8, step=20, size=11)   番号と説明の一覧
    .legend(x, y, items, size=10.5)                     色見本と名前の並び。items は (色, 名前) か (色, 名前, dash)
    .arrow(x1, y1, x2, y2, color=INK, width=1.3, dash=None)
    .measure(x0, y0, x1, y1, label, color=DIM, offset=0, label_offset=-8)   寸法線（両端に目盛り）
    .note(x, y, s, size=11, color=MUTED, anchor="start")
    .fan(x, y, half_deg, length, direction_deg=0, color=LIGHT, opacity=0.18)   光の扇（向きで指定）
    .light_cone(x, y, tx, ty, half_deg, length=None, color=LIGHT, opacity=0.18)   光の扇（目標点で指定）
    .light_glyph(x, y, r=9, color=LIGHT)                放射線付きの小さな光源

領域固有の部品（撮影の教材向け。関数は Figure を第一引数に取る）
    face(f, cx, cy, s=1.0, shadow=None, dark=0.34, catch=None, rim=None, turn=0, ear=None, label=None)
        正面の顔（高さ約 100px × s）。shadow は影の型:
        loop | rembrandt | butterfly | split | front | top | back | broad | short（ライトは左）
        gradient（右側が徐々に暗い。dark が濃さ）| even（全体を均一に暗く）| dark（全体を暗く。リム用）
        catch はキャッチライトの位置 "ul" | "uc" | "ur" | "l-only" | "r-only"。rim は "left" | "right"。
    person_side(f, x, y_floor, M=78, height=1.7, facing=1)   横から見た立ち姿（M は px/m）
    person_top(f, x, y, facing_deg=180, s=1.0)                上から見た人（肩と頭）
    camera_side(f, x, y, deg=0, s=1.0, tripod_to=None)        横から見たカメラ（レンズは +x）。tripod_to は床の y
    camera_top(f, x, y, deg=-90, s=1.0)                       上から見たカメラ（レンズは deg の向き）
    monoblock_side(f, x, y, deg=0, s=1.0, reflector=True, cable=True)   横から見たモノブロック（照射は +x）
    softbox_side(f, x, y, deg=0, face=170, depth=56, color=LIGHT)      横から見たソフトボックス（発光面は +x 側）
    softbox_top(f, x, y, deg=0, s=1.0, color=LIGHT)                    上から見たソフトボックス
    umbrella_side(f, x, y, deg=0, reflective=False, r=44)              アンブレラ（透過 / 反射）
    reflector_side(f, x, y, deg=0, grid=False, s=1.0, color=LIGHT)     標準リフレクター（グリッド付き可）
    stand(f, x, y_top, y_floor, color=BODY, feet=16)                   ライトスタンドの支柱と脚
    board_side(f, x, y, h, kind="white", rot=0, w=6)                   白レフ / 黒レフ / フラッグ
    mini_topview(f, cx, cy, angle_deg, r=46, label=None, height_note=None, cone=True, head_turn=0)
        被写体を中心にした小さな上面図。ライト 1 灯をカメラから見た角度（左が正）に置く
    mini_scene(f, x0, y0, w, h, key=True, fill=True, rim=True, ...)
        背景紙、被写体、カメラ、キー A / フィル B / リム C の小さな上面図。点いている灯だけに色
    timeline(f, x0, x1, bar_y, start_h, end_h, slots, markers=(), notes_rows=4)
        帯の時間割。slots は (開始 "HH:MM", 終了, ラベル, 種類 set|shoot|move|slack|pack|data, 確認点)
        戻り値は描画の下端 y。timeline_figure() は枠ごと作る
    flow_box(f, x, y, w, h, text, fill="#fff", head=None, head_w=112, size=12)   流れ図の箱
    flow_arrow(f, x1, y1, x2, y2, label=None, color=INK, curve=None)              流れ図の矢印

clipPath や gradient は f.add_def() で登録し、id は f.uid() で作る。
clipPath の中身は、参照する要素と同じ座標系（ローカル座標）で書く。
絶対座標の transform を付けると二重に変換されて描画が消える。
"""

import math

# ---------------------------------------------------------------- スタイル定数
FONT = "'Noto Sans JP','Noto Sans CJK JP','Hiragino Sans','Yu Gothic','Meiryo',sans-serif"
INK = "#333333"        # 線と文字
MUTED = "#7a7a7a"      # 補足の文字
LIGHT = "#f2a900"      # 光と発光面
ACCENT = "#2f6db5"     # 注記、角度
DIM = "#b3541e"        # 距離、寸法
SKIN = "#f1d9c2"
CLOTH = "#a9b8cf"
HAIR = "#6b4f3a"
SHADOW = "#3a2c22"
WALL = "#e6e1d8"
BLACK = "#222222"
FLOOR = "#fbfaf7"
BODY = "#555555"       # 機材の本体
CAMERA_BODY = "#3c3c3c"
LENS = "#9ec5e8"
PAPER = "#9a9a9a"
# 旧スクリプトとの互換の別名
BLUE = ACCENT
BROWN = DIM


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_text(x, y, s, size=12, anchor="start", color=INK, weight="normal", lh=1.35):
    """<text> の文字列を返す（グループの中に組み込むとき用）。複数行は \\n で区切る。"""
    lines = str(s).split("\n")
    out = [f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
           f'text-anchor="{anchor}" fill="{color}" font-weight="{weight}">']
    for i, line in enumerate(lines):
        dy = "0" if i == 0 else f"{size * lh:.1f}"
        out.append(f'<tspan x="{x:.1f}" dy="{dy}">{esc(line)}</tspan>')
    out.append("</text>")
    return "".join(out)


# ---------------------------------------------------------------- Figure
class Figure:
    def __init__(self, width, height, title=None, subtitle=None):
        self.w, self.h = width, height
        self.title = title or ""
        self.parts = []
        self.defs = []
        self._uid = 0
        self._markers = {}
        self.add_def('<filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>')
        self.add(f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" fill="#ffffff" stroke="#d9d9d9"/>')
        if title:
            self.text(24, 30, title, size=16, weight="bold")
        if subtitle:
            self.text(24, 52, subtitle, size=12, color=MUTED)

    # ---- 基本 ----
    def add(self, s):
        self.parts.append(s)

    def add_def(self, s):
        self.defs.append(s)

    def uid(self, prefix="u"):
        self._uid += 1
        return f"{prefix}{self._uid}"

    def marker(self, color=INK, size=8):
        """色に対応する矢印マーカーの id を返す。未登録なら登録する。"""
        key = (color, size)
        if key not in self._markers:
            mid = self.uid("arrow")
            self._markers[key] = mid
            self.add_def(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{size}" markerHeight="{size}" '
                         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 Z" fill="{color}"/></marker>')
        return self._markers[key]

    def text(self, x, y, s, size=12, anchor="start", color=INK, weight="normal", lh=1.35):
        self.add(svg_text(x, y, s, size, anchor, color, weight, lh))

    def line(self, x0, y0, x1, y1, color=INK, width=1.4, dash=None, arrow=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = f' marker-end="url(#{self.marker(color)})"' if arrow else ""
        self.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{color}" stroke-width="{width}"{d}{m}/>')

    def rect(self, x, y, w, h, fill="#fff", stroke=INK, width=1.4, rx=0, opacity=None, dash=None):
        op = f' opacity="{opacity}"' if opacity is not None else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{op}{d}/>')

    def circle(self, cx, cy, r, fill="#fff", stroke=INK, width=1.4, opacity=None):
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{op}/>')

    def path(self, d, fill="none", stroke=INK, width=1.4, opacity=None, dash=None, extra=""):
        op = f' opacity="{opacity}"' if opacity is not None else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{op}{da} {extra}/>')

    # ---- 汎用部品 ----
    def panel(self, x, y, w, h, title=None, fill=FLOOR, stroke="#e8e5df", rx=6, title_size=13):
        """比較用のカード枠。title は枠の上部に中央揃えで置く。"""
        self.rect(x, y, w, h, fill, stroke, 1, rx)
        if title:
            self.text(x + w / 2, y + 22, title, size=title_size, anchor="middle", weight="bold")

    def badge(self, x, y, label, r=10, fill=INK, color="#fff"):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>')
        self.text(x, y + r * 0.43, label, size=r * 1.2, anchor="middle", color=color, weight="bold")

    def leader(self, x1, y1, x2, y2, color=INK):
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1"/>')
        self.add(f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="2.2" fill="{color}"/>')

    def callout(self, n, x, y, to=None, r=10):
        """番号付きの丸を (x, y) に置き、to=(px, py) があれば丸の縁から引き出し線を引く。"""
        if to:
            ang = math.atan2(to[1] - y, to[0] - x)
            self.leader(x + r * math.cos(ang), y + r * math.sin(ang), to[0], to[1])
        self.badge(x, y, n, r)

    def callout_list(self, x, y, items, r=8, step=20, size=11, start=1, color=INK):
        """番号と説明の一覧。items は文字列のリスト。戻り値は次の行の y。"""
        for k, s in enumerate(items):
            yy = y + k * step
            self.badge(x, yy, start + k, r)
            self.text(x + r + 6, yy + 4, s, size=size, color=color)
        return y + len(items) * step

    def legend(self, x, y, items, size=10.5, swatch=(22, 12), gap=24):
        """色見本と名前を横に並べる。items は (fill, name) か (fill, name, dash)。戻り値は末尾の x。"""
        for it in items:
            fill, name = it[0], it[1]
            dash = it[2] if len(it) > 2 else None
            self.rect(x, y - swatch[1] / 2, swatch[0], swatch[1], fill, INK, 0.8, dash=dash)
            self.text(x + swatch[0] + 6, y + 4, name, size=size, color=MUTED)
            x += swatch[0] + 6 + len(name) * size * 0.95 + gap
        return x

    def arrow(self, x1, y1, x2, y2, color=INK, width=1.3, dash=None):
        self.line(x1, y1, x2, y2, color, width, dash, arrow=True)

    def measure(self, x0, y0, x1, y1, label, color=DIM, offset=0, label_offset=-8, size=11, dash="5 3"):
        """(x0,y0)-(x1,y1) の寸法線。offset は線を法線方向へずらす px、label_offset はラベルの法線方向のずれ。"""
        ang = math.atan2(y1 - y0, x1 - x0)
        nx, ny = -math.sin(ang), math.cos(ang)
        ax, ay = x0 + nx * offset, y0 + ny * offset
        bx, by = x1 + nx * offset, y1 + ny * offset
        self.line(ax, ay, bx, by, color, 1, dash)
        for px, py in ((ax, ay), (bx, by)):
            self.line(px - nx * 5, py - ny * 5, px + nx * 5, py + ny * 5, color, 1.2)
        mx, my = (ax + bx) / 2 + nx * label_offset, (ay + by) / 2 + ny * label_offset
        self.text(mx, my + size * 0.35, label, size=size, anchor="middle", color=color)

    def note(self, x, y, s, size=11, color=MUTED, anchor="start"):
        self.text(x, y, s, size=size, anchor=anchor, color=color)

    def fan(self, x, y, half_deg, length, direction_deg=0, color=LIGHT, opacity=0.18):
        a = math.radians(direction_deg)
        h = math.radians(half_deg)
        p1 = (x + length * math.cos(a - h), y + length * math.sin(a - h))
        p2 = (x + length * math.cos(a + h), y + length * math.sin(a + h))
        self.add(f'<path d="M{x:.1f},{y:.1f} L{p1[0]:.1f},{p1[1]:.1f} A{length:.1f},{length:.1f} 0 0,1 {p2[0]:.1f},{p2[1]:.1f} Z" fill="{color}" opacity="{opacity}"/>')

    def light_cone(self, x, y, tx, ty, half_deg, length=None, color=LIGHT, opacity=0.18):
        d = math.degrees(math.atan2(ty - y, tx - x))
        L = length or math.hypot(tx - x, ty - y) * 1.3
        self.fan(x, y, half_deg, L, d, color, opacity)

    def light_glyph(self, x, y, r=9, color=LIGHT):
        self.circle(x, y, r, color, INK, 1)
        for k in range(8):
            a = math.radians(k * 45)
            self.line(x + (r + 3) * math.cos(a), y + (r + 3) * math.sin(a), x + (r + 8) * math.cos(a), y + (r + 8) * math.sin(a), color, 1.6)

    # ---- 出力 ----
    def to_svg(self):
        defs = f'<defs>{"".join(self.defs)}</defs>\n' if self.defs else ""
        body = "\n".join(self.parts)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                f'role="img" aria-label="{esc(self.title)}">\n{defs}{body}\n</svg>\n')

    def save(self, path):
        open(path, "w", encoding="utf-8").write(self.to_svg())


# ---------------------------------------------------------------- 顔
FACE_PATH = "M0,-48 C24,-48 38,-30 38,-4 C38,22 22,46 0,46 C-22,46 -38,22 -38,-4 C-38,-30 -24,-48 0,-48 Z"
BODY_PATH = "M-62,92 Q-40,66 -16,60 L-16,44 L16,44 L16,60 Q40,66 62,92 Z"


def face(f, cx, cy, s=1.0, shadow=None, dark=0.34, catch=None, rim=None, turn=0, ear=None, label=None):
    """正面から見た模式的な顔。高さは約 100px × s。ライトは画面左から当たる前提で影を描く。

    shadow: loop | rembrandt | butterfly | split | front | top | back | broad | short |
            gradient | even | dark | None
    dark:   影の濃さ（0〜1）
    catch:  キャッチライト "ul" | "uc" | "ur" | "l-only" | "r-only" | None
    rim:    "left" | "right" | True（right）| None。髪と肩の縁の光
    turn:   顔の特徴を右へ寄せる px（顔を右へ振った表現）
    ear:    "left" | "right"。見える側の耳
    """
    cid = f.uid("face")
    bid = f.uid("body")
    f.add_def(f'<clipPath id="{cid}"><path d="{FACE_PATH}"/></clipPath>')
    f.add_def(f'<clipPath id="{bid}"><path d="{BODY_PATH}"/></clipPath>')
    t = turn
    g = [f'<g transform="translate({cx:.1f},{cy:.1f}) scale({s})">']
    g.append(f'<path d="{BODY_PATH}" fill="{CLOTH}" stroke="{INK}" stroke-width="1.2"/>')
    g.append(f'<rect x="-14" y="30" width="28" height="30" fill="{SKIN}" stroke="{INK}" stroke-width="1.2"/>')
    if ear == "left":
        g.append(f'<ellipse cx="-38" cy="6" rx="6" ry="10" fill="{SKIN}" stroke="{INK}" stroke-width="1.2"/>')
    if ear == "right":
        g.append(f'<ellipse cx="38" cy="6" rx="6" ry="10" fill="{SKIN}" stroke="{INK}" stroke-width="1.2"/>')
    g.append(f'<path d="{FACE_PATH}" fill="{SKIN}" stroke="{INK}" stroke-width="1.3"/>')
    g.append(f'<path d="M-38,-6 C-40,-40 -20,-52 0,-52 C20,-52 40,-40 38,-6 C34,-22 22,-30 0,-32 C-22,-30 -34,-22 -38,-6 Z" fill="{HAIR}" stroke="{INK}" stroke-width="1.2"/>')
    g.append(f'<path d="M{-24 + t},-16 Q{-16 + t},-21 {-8 + t},-17" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    g.append(f'<path d="M{8 + t},-17 Q{16 + t},-21 {24 + t},-16" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    for ex in (-15 + t, 15 + t):
        g.append(f'<ellipse cx="{ex}" cy="-8" rx="6.5" ry="3.6" fill="#fff" stroke="{INK}" stroke-width="1.1"/>')
        g.append(f'<circle cx="{ex}" cy="-8" r="2.9" fill="#3b2f2a"/>')
    g.append(f'<path d="M{-1 + t},-6 L{-5 + t},13 Q{0 + t},17 {5 + t},13" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    g.append(f'<path d="M{-10 + t},27 Q{0 + t},32 {10 + t},27" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    g.append("</g>")
    f.add("".join(g))

    # 影（顔の形で切り抜く。座標は顔のローカル座標）
    sh, body_sh = [], []
    op = dark
    if shadow == "loop":
        sh.append(f'<path d="M{3 + t},2 Q{16 + t},8 {12 + t},18 Q{6 + t},20 {4 + t},14 Z" fill="{SHADOW}" opacity="{op}"/>')
        sh.append(f'<path d="M{26 + t},-40 C{44 + t},-20 {44 + t},20 {24 + t},48 L50,48 L50,-50 Z" fill="{SHADOW}" opacity="{op * 0.8:.2f}"/>')
    elif shadow == "rembrandt":
        sh.append(f'<path fill-rule="evenodd" d="M{2 + t},-50 L{2 + t},-20 L{-2 + t},-6 L{-5 + t},13 Q{4 + t},19 {8 + t},13 L{10 + t},22 Q{4 + t},34 {2 + t},50 L60,50 L60,-50 Z '
                  f'M{11 + t},-1 L{31 + t},-3 L{18 + t},17 Z" fill="{SHADOW}" opacity="{op}"/>')
    elif shadow == "butterfly":
        sh.append(f'<path d="M{-9 + t},15 Q{-3 + t},13 {0 + t},16 Q{3 + t},13 {9 + t},15 Q{6 + t},24 {0 + t},21 Q{-6 + t},24 {-9 + t},15 Z" fill="{SHADOW}" opacity="{op}"/>')
        sh.append(f'<path d="M-38,4 Q-24,16 -14,22 Q-26,20 -38,12 Z" fill="{SHADOW}" opacity="{op * 0.7:.2f}"/>')
        sh.append(f'<path d="M38,4 Q24,16 14,22 Q26,20 38,12 Z" fill="{SHADOW}" opacity="{op * 0.7:.2f}"/>')
        sh.append(f'<path d="M-20,40 Q0,50 20,40 L20,60 L-20,60 Z" fill="{SHADOW}" opacity="{op * 0.8:.2f}"/>')
    elif shadow == "split":
        sh.append(f'<rect x="{0 + t}" y="-60" width="70" height="120" fill="{SHADOW}" opacity="{op}"/>')
    elif shadow == "front":
        sh.append(f'<path d="M{-5 + t},14 Q{0 + t},19 {5 + t},14 Q{0 + t},18 {-5 + t},14 Z" fill="{SHADOW}" opacity="{op * 0.6:.2f}"/>')
        sh.append(f'<path d="M-14,44 L14,44 L14,52 L-14,52 Z" fill="{SHADOW}" opacity="{op * 0.6:.2f}"/>')
    elif shadow == "top":
        sh.append(f'<ellipse cx="{-15 + t}" cy="-12" rx="12" ry="7" fill="{SHADOW}" opacity="{op}"/>')
        sh.append(f'<ellipse cx="{15 + t}" cy="-12" rx="12" ry="7" fill="{SHADOW}" opacity="{op}"/>')
        sh.append(f'<path d="M{-7 + t},14 Q{0 + t},18 {7 + t},14 L{6 + t},22 L{-6 + t},22 Z" fill="{SHADOW}" opacity="{op}"/>')
        sh.append(f'<path d="M-24,36 Q0,46 24,36 L24,60 L-24,60 Z" fill="{SHADOW}" opacity="{op}"/>')
    elif shadow == "back":
        sh.append(f'<rect x="-60" y="-60" width="120" height="120" fill="{SHADOW}" opacity="{min(op * 1.3, 0.9):.2f}"/>')
    elif shadow == "broad":
        sh.append(f'<path d="M{18 + t},-50 C{40 + t},-30 {40 + t},20 {20 + t},50 L60,50 L60,-50 Z" fill="{SHADOW}" opacity="{op}"/>')
        sh.append(f'<path d="M{3 + t},2 Q{14 + t},8 {11 + t},17 Q{6 + t},19 {4 + t},14 Z" fill="{SHADOW}" opacity="{op}"/>')
    elif shadow == "short":
        sh.append(f'<path d="M{-3 + t},-50 C{-14 + t},-30 {-14 + t},20 {-5 + t},50 L-60,50 L-60,-50 Z" fill="{SHADOW}" opacity="{op}"/>')
        sh.append(f'<path d="M{-3 + t},2 Q{-14 + t},8 {-11 + t},17 Q{-6 + t},19 {-4 + t},14 Z" fill="{SHADOW}" opacity="{op}"/>')
    elif shadow == "gradient":
        gid = f.uid("grad")
        f.add_def(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
                  f'<stop offset="0.4" stop-color="{SHADOW}" stop-opacity="0"/>'
                  f'<stop offset="0.6" stop-color="{SHADOW}" stop-opacity="{op}"/>'
                  f'<stop offset="1" stop-color="{SHADOW}" stop-opacity="{op}"/></linearGradient>')
        sh.append(f'<rect x="-40" y="-60" width="80" height="120" fill="url(#{gid})"/>')
        if op > 0.15:
            sh.append(f'<ellipse cx="{8 + t}" cy="14" rx="7" ry="4.5" fill="{SHADOW}" opacity="{min(op * 0.9, 0.7):.2f}"/>')
        body_sh.append(f'<rect x="2" y="40" width="70" height="60" fill="{SHADOW}" opacity="{op * 0.8:.2f}"/>')
    elif shadow == "even":
        sh.append(f'<rect x="-60" y="-60" width="120" height="120" fill="{SHADOW}" opacity="{op}"/>')
        body_sh.append(f'<rect x="-70" y="40" width="140" height="60" fill="{SHADOW}" opacity="{op * 0.8:.2f}"/>')
    elif shadow == "dark":
        sh.append(f'<rect x="-60" y="-60" width="120" height="120" fill="{SHADOW}" opacity="{op}"/>')
        body_sh.append(f'<rect x="-70" y="40" width="140" height="60" fill="{SHADOW}" opacity="{op}"/>')
    if sh:
        f.add(f'<g clip-path="url(#{cid})" transform="translate({cx:.1f},{cy:.1f}) scale({s})">{"".join(sh)}</g>')
    if body_sh:
        f.add(f'<g clip-path="url(#{bid})" transform="translate({cx:.1f},{cy:.1f}) scale({s})">{"".join(body_sh)}</g>')
    # 縁の光
    if rim is True:
        rim = "right"
    if rim == "left":
        f.add(f'<g transform="translate({cx:.1f},{cy:.1f}) scale({s})">'
              f'<path d="M-38,-6 C-40,-40 -20,-52 0,-52 C10,-52 20,-49 28,-44" fill="none" stroke="{LIGHT}" stroke-width="3" stroke-linecap="round"/>'
              f'<path d="M-62,92 Q-40,66 -16,60" fill="none" stroke="{LIGHT}" stroke-width="3" stroke-linecap="round"/></g>')
    elif rim == "right":
        f.add(f'<g transform="translate({cx:.1f},{cy:.1f}) scale({s})">'
              f'<path d="M-28,-44 C-20,-49 -10,-52 0,-52 C20,-52 40,-40 38,-6" fill="none" stroke="{LIGHT}" stroke-width="6" stroke-linecap="round" opacity="0.45"/>'
              f'<path d="M-28,-44 C-20,-49 -10,-52 0,-52 C20,-52 40,-40 38,-6" fill="none" stroke="#fff7d6" stroke-width="2.5" stroke-linecap="round"/>'
              f'<path d="M16,60 Q40,66 62,92" fill="none" stroke="{LIGHT}" stroke-width="6" stroke-linecap="round" opacity="0.45"/>'
              f'<path d="M16,60 Q40,66 62,92" fill="none" stroke="#fff7d6" stroke-width="2.5" stroke-linecap="round"/></g>')
    # キャッチライト
    if catch:
        pos = {"ul": (-2.2, -1.8), "uc": (0, -2.2), "ur": (2.2, -1.8)}
        eyes = [-15 + turn, 15 + turn]
        if catch == "l-only":
            eyes, (dx, dy) = [-15 + turn], pos["ul"]
        elif catch == "r-only":
            eyes, (dx, dy) = [15 + turn], pos["ur"]
        else:
            dx, dy = pos[catch]
        for ex in eyes:
            f.add(f'<circle cx="{cx + (ex + dx) * s:.1f}" cy="{cy + (-8 + dy) * s:.1f}" r="{1.3 * s:.1f}" fill="#fff"/>')
    if label:
        f.text(cx, cy + 112 * s, label, size=13, anchor="middle", weight="bold")


# ---------------------------------------------------------------- 人物と機材
def person_side(f, x, y_floor, M=78, height=1.7, facing=1, shadow=True):
    """横から見た立ち姿。x は身体の中心、y_floor は足元。M は px/m。facing は顔の向き（+1 で右）。"""
    def Y(h):
        return y_floor - h * M
    k = height / 1.7
    if shadow:
        f.add(f'<ellipse cx="{x - 18 * facing:.1f}" cy="{y_floor - 3}" rx="26" ry="6" fill="{SHADOW}" opacity="0.25"/>')
    f.rect(x - 16, Y(0.9 * k), 32, 0.9 * k * M, "#5c6b80", INK, 1)
    f.path(f"M{x - 24},{Y(1.45 * k)} C{x - 24},{Y(1.5 * k)} {x - 6},{Y(1.5 * k)} {x},{Y(1.5 * k)} C{x + 6},{Y(1.5 * k)} {x + 24},{Y(1.5 * k)} {x + 24},{Y(1.45 * k)} L{x + 22},{Y(0.9 * k)} L{x - 22},{Y(0.9 * k)} Z", CLOTH, INK, 1)
    r = 0.12 * M * k
    f.circle(x, Y(1.58 * k), r, SKIN, INK, 1)
    f.path(f"M{x - r},{Y(1.6 * k)} A{r},{r} 0 0,1 {x + r},{Y(1.6 * k)} Z", HAIR, "none", 0)


def person_top(f, x, y, facing_deg=180, s=1.0):
    """上から見た人。facing_deg は顔の向き（180 で画面下）。"""
    f.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate({facing_deg - 90}) scale({s})">'
          f'<ellipse cx="0" cy="0" rx="14" ry="27" fill="{CLOTH}" stroke="{INK}" stroke-width="1.2"/>'
          f'<circle cx="3" cy="0" r="11" fill="{SKIN}" stroke="{INK}" stroke-width="1.2"/>'
          f'<path d="M14,-4 L19,0 L14,4 Z" fill="{SKIN}" stroke="{INK}" stroke-width="1"/></g>')


def camera_side(f, x, y, deg=0, s=1.0, tripod_to=None):
    """横から見たカメラ。レンズは +x を deg 回転した向き。tripod_to に床の y を渡すと三脚を描く。"""
    if tripod_to is not None:
        f.path(f"M{x - 14 * s},{tripod_to} L{x},{y + 10 * s} L{x + 14 * s},{tripod_to} M{x},{y + 10 * s} L{x},{tripod_to}", "none", BODY, 1.5)
    f.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate({deg}) scale({s})">'
          f'<rect x="-30" y="-16" width="34" height="30" rx="4" fill="{CAMERA_BODY}"/>'
          f'<rect x="-22" y="-24" width="14" height="8" fill="{CAMERA_BODY}"/>'
          f'<rect x="4" y="-10" width="26" height="20" fill="#666" stroke="{INK}" stroke-width="1"/>'
          f'<rect x="30" y="-9" width="3" height="18" fill="{LENS}" stroke="{INK}" stroke-width="1"/></g>')


def camera_top(f, x, y, deg=-90, s=1.0):
    """上から見たカメラ。レンズは deg の向き（-90 で画面上）。"""
    f.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate({deg}) scale({s})">'
          f'<rect x="-14" y="-11" width="20" height="22" rx="3" fill="{CAMERA_BODY}"/>'
          f'<rect x="6" y="-7" width="14" height="14" fill="#666" stroke="{INK}" stroke-width="1"/>'
          f'<circle cx="20" cy="0" r="5" fill="{LENS}" stroke="{INK}" stroke-width="1"/></g>')


def monoblock_side(f, x, y, deg=0, s=1.0, reflector=True, cable=True, mount=True):
    """横から見たモノブロック。(x, y) は本体の中心、照射方向は +x を deg 回転した向き。
    本体は 150×80、リフレクターは前面に 68 伸びる。戻り値はローカル座標での主要点の辞書。"""
    g = [f'<g transform="translate({x:.1f},{y:.1f}) rotate({deg}) scale({s})">']
    if cable:
        g.append(f'<path d="M-75,0 C-115,0 -125,70 -105,100" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    g.append(f'<rect x="-75" y="-40" width="150" height="80" rx="10" fill="{BODY}" stroke="{INK}" stroke-width="1.4"/>')
    for k in range(5):
        g.append(f'<line x1="{-55 + k * 8}" y1="-20" x2="{-55 + k * 8}" y2="20" stroke="#9a9a9a" stroke-width="2"/>')
    g.append(f'<rect x="43" y="-54" width="26" height="14" rx="3" fill="#777" stroke="{INK}" stroke-width="1"/>')
    g.append(f'<circle cx="56" cy="-47" r="4" fill="#fff" stroke="{INK}" stroke-width="1"/>')
    g.append(f'<rect x="75" y="-44" width="12" height="88" fill="#777" stroke="{INK}" stroke-width="1.2"/>')
    if reflector:
        g.append(f'<path d="M87,-32 L155,-62 L155,62 L87,32 Z" fill="#e0e0e0" stroke="{INK}" stroke-width="1.4"/>')
        g.append(f'<line x1="155" y1="-62" x2="155" y2="62" stroke="{LIGHT}" stroke-width="4"/>')
    if mount:
        g.append(f'<rect x="-15" y="40" width="30" height="16" fill="#777" stroke="{INK}" stroke-width="1.2"/>')
        g.append(f'<circle cx="30" cy="50" r="7" fill="#999" stroke="{INK}" stroke-width="1.2"/>')
        g.append(f'<line x1="30" y1="50" x2="47" y2="50" stroke="{INK}" stroke-width="3"/>')
    g.append("</g>")
    f.add("".join(g))
    return {"front": (155 if reflector else 87, 0), "top": (0, -40), "mount": (0, 56), "umbrella_hole": (56, -47)}


def softbox_side(f, x, y, deg=0, face=170, depth=56, color=LIGHT):
    """横から見たソフトボックス。発光面の中心が (x, y)、照射方向は +x を deg 回転した向き。"""
    f.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate({deg})">'
          f'<path d="M{-depth},-{face * 0.28:.0f} L0,-{face / 2:.0f} L0,{face / 2:.0f} L{-depth},{face * 0.28:.0f} Z" fill="#f7f7f7" stroke="{INK}" stroke-width="1.4"/>'
          f'<rect x="-3" y="-{face / 2:.0f}" width="6" height="{face}" fill="{color}" stroke="{INK}" stroke-width="1"/>'
          f'<circle cx="{-depth - 10}" cy="0" r="10" fill="{BODY}" stroke="{INK}" stroke-width="1"/></g>')


def softbox_top(f, x, y, deg=0, s=1.0, color=LIGHT):
    """上から見たソフトボックス。本体が (x, y)、発光面は +x を deg 回転した向き。"""
    f.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate({deg}) scale({s})">'
          f'<rect x="-6" y="-33" width="30" height="66" fill="#f7f7f7" stroke="{INK}" stroke-width="1.4"/>'
          f'<line x1="-6" y1="-33" x2="24" y2="0" stroke="{MUTED}" stroke-width="0.8"/>'
          f'<line x1="-6" y1="33" x2="24" y2="0" stroke="{MUTED}" stroke-width="0.8"/>'
          f'<rect x="22" y="-33" width="5" height="66" fill="{color}" stroke="{INK}" stroke-width="1"/>'
          f'<circle cx="-12" cy="0" r="8" fill="{BODY}" stroke="{INK}" stroke-width="1"/></g>')


def umbrella_side(f, x, y, deg=0, reflective=False, r=44):
    """アンブレラ。(x, y) は傘の軸の中心、照射方向は +x を deg 回転した向き。
    透過は頭が傘の後ろで前へ光らせ、反射は頭が傘の前で傘に向けて光らせる。"""
    g = [f'<g transform="translate({x:.1f},{y:.1f}) rotate({deg})">']
    if reflective:
        g.append(f'<path d="M10,-{r} Q-{r * 0.64:.0f},0 10,{r}" fill="#fdfdfd" stroke="{INK}" stroke-width="1.3"/>')
        g.append(f'<line x1="-6" y1="0" x2="34" y2="0" stroke="{INK}" stroke-width="1.4"/>')
        g.append(f'<rect x="26" y="-12" width="30" height="24" rx="4" fill="{BODY}" stroke="{INK}" stroke-width="1.1"/>')
        g.append(f'<rect x="22" y="-6" width="4" height="12" fill="{LIGHT}"/>')
    else:
        g.append(f'<path d="M-10,-{r} Q{r * 0.64:.0f},0 -10,{r}" fill="#fdfdfd" stroke="{INK}" stroke-width="1.3"/>')
        g.append(f'<line x1="-10" y1="0" x2="-42" y2="0" stroke="{INK}" stroke-width="1.4"/>')
        g.append(f'<rect x="-72" y="-12" width="30" height="24" rx="4" fill="{BODY}" stroke="{INK}" stroke-width="1.1"/>')
        g.append(f'<rect x="-42" y="-6" width="4" height="12" fill="{LIGHT}"/>')
    g.append("</g>")
    f.add("".join(g))


def reflector_side(f, x, y, deg=0, grid=False, s=1.0, color=LIGHT):
    """標準リフレクター付きのストロボ（横または上から見た小さな記号）。(x, y) は本体の中心。"""
    gl = "".join(f'<line x1="8" y1="{yy}" x2="14" y2="{yy}" stroke="{INK}" stroke-width="1"/>' for yy in (-12, -6, 0, 6, 12)) if grid else ""
    f.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate({deg}) scale({s})">'
          f'<circle cx="-10" cy="0" r="9" fill="{BODY}" stroke="{INK}" stroke-width="1"/>'
          f'<path d="M-2,-8 L14,-16 L14,16 L-2,8 Z" fill="#e0e0e0" stroke="{INK}" stroke-width="1.3"/>'
          f'<line x1="14" y1="-16" x2="14" y2="16" stroke="{color}" stroke-width="3"/>{gl}</g>')


def stand(f, x, y_top, y_floor, color=BODY, feet=16):
    """ライトスタンドの支柱と脚（横から見た図）。"""
    f.line(x, y_top, x, y_floor, color, 2)
    f.line(x - feet, y_floor, x + feet, y_floor, color, 2)


def board_side(f, x, y, h, kind="white", rot=0, w=6):
    """白レフ / 黒レフ / フラッグ。(x, y) は板の中心。"""
    fill = "#fff" if kind == "white" else BLACK
    stroke = INK if kind == "white" else BLACK
    f.add(f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot})"><rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/></g>')


# ---------------------------------------------------------------- 小さな上面図
def mini_topview(f, cx, cy, angle_deg, r=46, label=None, height_note=None, cone=True, head_turn=0):
    """被写体を中心にした小さな上面図。カメラは下、ライトはカメラから見た角度（左が正）に置く。"""
    f.circle(cx, cy, r + 14, FLOOR, "#e5e2dc", 1)
    ht = math.radians(90 + head_turn)
    f.circle(cx, cy, 7, SKIN, INK, 1)
    f.add(f'<path d="M{cx + 7 * math.cos(ht) - 3 * math.sin(ht):.1f},{cy + 7 * math.sin(ht) + 3 * math.cos(ht):.1f} '
          f'L{cx + 11 * math.cos(ht):.1f},{cy + 11 * math.sin(ht):.1f} '
          f'L{cx + 7 * math.cos(ht) + 3 * math.sin(ht):.1f},{cy + 7 * math.sin(ht) - 3 * math.cos(ht):.1f} Z" fill="{SKIN}" stroke="{INK}" stroke-width="0.8"/>')
    f.add(f'<rect x="{cx - 6:.1f}" y="{cy + r - 4:.1f}" width="12" height="9" rx="2" fill="{CAMERA_BODY}"/>')
    f.add(f'<rect x="{cx - 3:.1f}" y="{cy + r - 9:.1f}" width="6" height="6" fill="#666"/>')
    a = math.radians(90 + angle_deg)
    rl = r - 16 if angle_deg == 0 else r
    lx, ly = cx + rl * math.cos(a), cy + rl * math.sin(a)
    if cone:
        f.light_cone(lx, ly, cx, cy, 30, r * 1.3)
    rot = math.degrees(math.atan2(cy - ly, cx - lx))
    f.add(f'<g transform="translate({lx:.1f},{ly:.1f}) rotate({rot:.1f})"><rect x="-4" y="-9" width="9" height="18" fill="#f7f7f7" stroke="{INK}" stroke-width="1"/><rect x="4" y="-9" width="2.5" height="18" fill="{LIGHT}"/></g>')
    if angle_deg:
        ra = r * 0.55
        sweep = 1 if angle_deg > 0 else 0
        f.add(f'<path d="M{cx:.1f},{cy + ra:.1f} A{ra:.1f},{ra:.1f} 0 0,{sweep} {cx + ra * math.cos(a):.1f},{cy + ra * math.sin(a):.1f}" fill="none" stroke="{ACCENT}" stroke-width="1.1"/>')
    f.line(cx, cy, cx, cy + r - 8, MUTED, 0.7, "2 2")
    if label:
        f.text(cx, cy + r + 30, label, size=11, anchor="middle", color=ACCENT)
    if height_note:
        f.text(cx, cy + r + 45, height_note, size=11, anchor="middle", color=MUTED)


def mini_scene(f, x0, y0, w, h, key=True, fill=True, rim=True, show_fill=True, show_rim=True,
               rim_pos=(0.86, 0.22), rim_grid=False, flag=None, ray_to_camera=None, ray_block=None, backdrop=True):
    """x0, y0 を左上とする w×h の枠に、背景紙、被写体、カメラ、キー A、フィル B、リム C を描く。
    key / fill / rim は点いているか、show_* は描くか。flag=(fx, fy, rot) は枠内の比率でフラッグを置く。
    ray_to_camera は "hit"（リムの直射がレンズに入る）か "blocked"（ray_block=(bx, by) で遮られる）。"""
    f.rect(x0, y0, w, h, FLOOR, "#e5e5e5", 1)
    if backdrop:
        f.rect(x0 + w * 0.15, y0 + 6, w * 0.7, 6, PAPER, "none", 0)
    sx, sy = x0 + w * 0.5, y0 + h * 0.5
    camx, camy = x0 + w * 0.5, y0 + h * 0.92
    kx, ky = x0 + w * 0.18, y0 + h * 0.74
    fx, fy = x0 + w * 0.72, y0 + h * 0.88
    rx_, ry_ = x0 + w * rim_pos[0], y0 + h * rim_pos[1]

    def icon(px, py, kind, on):
        ang = math.degrees(math.atan2(sy - py, sx - px))
        col = LIGHT if on else "#c9c9c9"
        stroke = INK if on else "#b0b0b0"
        body = BODY if on else "#c9c9c9"
        if kind == "softbox":
            inner = (f'<rect x="-4" y="-14" width="12" height="28" fill="#f7f7f7" stroke="{stroke}" stroke-width="1"/>'
                     f'<rect x="7" y="-14" width="3" height="28" fill="{col}"/><circle cx="-8" cy="0" r="4" fill="{body}"/>')
        elif kind == "umbrella":
            inner = (f'<path d="M-4,-16 Q12,0 -4,16" fill="#fdfdfd" stroke="{stroke}" stroke-width="1"/>'
                     f'<path d="M-2,-11 Q8,0 -2,11" fill="none" stroke="{col}" stroke-width="1.5"/>'
                     f'<line x1="-4" y1="0" x2="-12" y2="0" stroke="{stroke}" stroke-width="1"/><circle cx="-12" cy="0" r="4" fill="{body}"/>')
        else:
            grid = "".join(f'<line x1="4" y1="{yy}" x2="7" y2="{yy}" stroke="{stroke}" stroke-width="0.8"/>' for yy in (-5, -2.5, 0, 2.5, 5)) if rim_grid else ""
            inner = (f'<circle cx="-5" cy="0" r="4.5" fill="{body}"/>'
                     f'<path d="M-1,-4 L7,-8 L7,8 L-1,4 Z" fill="#e0e0e0" stroke="{stroke}" stroke-width="1"/>'
                     f'<line x1="7" y1="-8" x2="7" y2="8" stroke="{col}" stroke-width="2"/>{grid}')
        f.add(f'<g transform="translate({px:.1f},{py:.1f}) rotate({ang:.1f})">{inner}</g>')

    if key:
        f.light_cone(kx, ky, sx, sy, 34)
    if fill and show_fill:
        f.light_cone(fx, fy, sx, sy, 44)
    if rim and show_rim:
        f.light_cone(rx_, ry_, sx, sy, 10 if rim_grid else 22)
    f.add(f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="13" ry="7" fill="{CLOTH}" stroke="{INK}" stroke-width="1"/>')
    f.circle(sx, sy + 1, 5.5, SKIN, INK, 1)
    f.add(f'<rect x="{camx - 6:.1f}" y="{camy - 5:.1f}" width="12" height="9" rx="2" fill="{CAMERA_BODY}"/>')
    f.add(f'<rect x="{camx - 3:.1f}" y="{camy - 10:.1f}" width="6" height="5" fill="#666"/>')
    icon(kx, ky, "softbox", key)
    f.text(kx - 14, ky + 4, "A", size=9, anchor="middle", color=INK if key else "#b0b0b0", weight="bold")
    if show_fill:
        icon(fx, fy, "umbrella", fill)
        f.text(fx + 16, fy + 4, "B", size=9, anchor="middle", color=INK if fill else "#b0b0b0", weight="bold")
    if show_rim:
        icon(rx_, ry_, "reflector", rim)
        f.text(rx_ + 12, ry_ - 8, "C", size=9, anchor="middle", color=INK if rim else "#b0b0b0", weight="bold")
    if flag:
        fxx, fyy, rot = flag
        f.add(f'<g transform="translate({x0 + w * fxx:.1f},{y0 + h * fyy:.1f}) rotate({rot})"><rect x="-12" y="-2.5" width="24" height="5" fill="{BLACK}"/></g>')
    if ray_to_camera == "hit":
        f.arrow(rx_, ry_, camx, camy - 10, DIM, 1.6)
        f.add(f'<circle cx="{camx:.1f}" cy="{camy - 8:.1f}" r="14" fill="{LIGHT}" opacity="0.35" filter="url(#blur)"/>')
    elif ray_to_camera == "blocked" and ray_block:
        bx, by = x0 + w * ray_block[0], y0 + h * ray_block[1]
        f.line(rx_, ry_, bx, by, DIM, 1.6)
        f.line(bx, by, camx, camy - 10, DIM, 1, "2 3")
        f.line(bx - 5, by - 5, bx + 5, by + 5, DIM, 2)
        f.line(bx - 5, by + 5, bx + 5, by - 5, DIM, 2)


# ---------------------------------------------------------------- 時間割
TIMELINE_FILLS = {"set": WALL, "shoot": "#fbe3a3", "move": WALL, "slack": "#ffffff", "pack": CLOTH, "data": CLOTH}


def timeline(f, x0, x1, bar_y, start_h, end_h, slots, markers=(), notes_rows=4, bar_h=40, legend=True):
    """帯の時間割を描く。slots は (開始, 終了, ラベル, 種類, 確認点) の並び。戻り値は描いた範囲の下端 y。"""
    span = end_h - start_h

    def tx(t):
        h, m = map(int, t.split(":"))
        return x0 + (h + m / 60 - start_h) / span * (x1 - x0)

    for h in range(start_h, end_h + 1):
        x = tx(f"{h:02d}:00")
        f.line(x, bar_y - 4, x, bar_y + bar_h + 4, MUTED, 0.8, "2 3")
    for (s_, e, label, kind, note) in slots:
        xs, xe = tx(s_), tx(e)
        f.rect(xs, bar_y, xe - xs, bar_h, TIMELINE_FILLS.get(kind, "#fff"), INK, 1, dash="4 3" if kind == "slack" else None)
    up_row, last_up_x = 0, -999
    for (s_, e, label, kind, note) in slots:
        xs, xe = tx(s_), tx(e)
        cx = (xs + xe) / 2
        if xe - xs >= len(label) * 11 + 8:
            f.text(cx, bar_y + bar_h / 2 + 4, label, size=11, anchor="middle")
        else:
            up_row = (up_row + 1) % 2 if cx - last_up_x < len(label) * 11 + 10 else 0
            ly = bar_y - 10 - up_row * 16
            f.line(cx, bar_y, cx, ly + 3, MUTED, 0.8)
            f.text(cx, ly, label, size=11, anchor="middle")
            last_up_x = cx
    times = [s_ for (s_, e, label, kind, note) in slots] + [slots[-1][1]]
    last_x = -999
    for t in times:
        x = tx(t)
        row = 1 if x - last_x < 34 else 0
        f.text(x, bar_y + bar_h + 16 + row * 12, t, size=10, anchor="middle", color=MUTED)
        last_x = x if row == 0 else last_x
    notes_y0 = bar_y + bar_h + 48
    row = 0
    for (s_, e, label, kind, note) in slots:
        if not note:
            continue
        xs, xe = tx(s_), tx(e)
        y = notes_y0 + row * 34
        anchor, nx = "start", xs + 6
        if nx + 150 > x1 + 16:
            anchor, nx = "end", xe - 2
        f.line(xs + 2, bar_y + bar_h + 30, xs + 2, y - 6, MUTED, 0.8, "2 2")
        f.text(nx, y + 4, note, size=10, anchor=anchor, lh=1.3)
        row = (row + 1) % notes_rows
    markers_y = notes_y0 + notes_rows * 34
    for t, label in markers:
        x = tx(t)
        f.add(f'<path d="M{x - 6:.1f},{markers_y} L{x + 6:.1f},{markers_y} L{x:.1f},{markers_y + 9} Z" fill="{ACCENT}"/>')
        f.text(x, markers_y + 24, f"{t} {label}", size=10, anchor="middle", color=ACCENT)
    bottom = markers_y + (44 if markers else 6)
    if legend:
        f.legend(x0, bottom + 18, [(TIMELINE_FILLS["set"], "セットを組む、変える"), (TIMELINE_FILLS["shoot"], "撮影"),
                                    (TIMELINE_FILLS["slack"], "余白", "4 3"), (TIMELINE_FILLS["pack"], "撤収とデータ")], size=10)
        bottom += 36
    return bottom


def timeline_figure(title, subtitle, start_h, end_h, slots, markers=(), notes_rows=4, width=780):
    """枠ごと時間割の図を作って返す。"""
    bar_y, bar_h = 104, 40
    height = bar_y + bar_h + 48 + notes_rows * 34 + (44 if markers else 6) + 44
    f = Figure(width, height, title, subtitle)
    timeline(f, 60, width - 40, bar_y, start_h, end_h, slots, markers, notes_rows, bar_h)
    return f


# ---------------------------------------------------------------- 流れ図
def flow_box(f, x, y, w, h, text, fill="#ffffff", head=None, head_w=112, size=12, rx=6, lh=1.3, anchor=None):
    """流れ図の箱。head を渡すと左に見出しの区画を付け、text はその右に左寄せで置く。"""
    f.rect(x, y, w, h, fill, INK, 1.4, rx)
    if head:
        f.rect(x, y, head_w, h, "#f4f4f4", INK, 1.4, rx)
        f.text(x + head_w / 2, y + h / 2 + 4, head, size=size, anchor="middle", weight="bold")
        n = text.count("\n") + 1
        f.text(x + head_w + 10, y + h / 2 + 4 - (n - 1) * size * lh / 2, text, size=size - 1.5, lh=lh)
    else:
        n = text.count("\n") + 1
        f.text(x + w / 2, y + h / 2 + 4 - (n - 1) * size * lh / 2, text, size=size, anchor=anchor or "middle", lh=lh)


def flow_arrow(f, x1, y1, x2, y2, label=None, color=INK, curve=None, label_anchor="middle", label_dy=-6):
    """流れ図の矢印。curve に px を渡すと、その分だけ左（負なら右）へ膨らむ曲線にする。"""
    if curve:
        f.add(f'<path d="M{x1:.1f},{y1:.1f} C{x1 - curve:.1f},{y1:.1f} {x2 - curve:.1f},{y2:.1f} {x2:.1f},{y2:.1f}" fill="none" stroke="{color}" stroke-width="1.2" marker-end="url(#{f.marker(color)})"/>')
        if label:
            f.text(min(x1, x2) - abs(curve) - 6, (y1 + y2) / 2, label, size=10.5, anchor="end", color=color, lh=1.3)
    else:
        f.arrow(x1, y1, x2, y2, color, 1.2)
        if label:
            f.text((x1 + x2) / 2, (y1 + y2) / 2 + label_dy, label, size=10, anchor=label_anchor, color=color)
