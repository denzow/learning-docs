#!/usr/bin/env python3
"""ライティングの配置図（上から見た図）を JSON の仕様から SVG に描く。

使い方:
  scripts/render-diagrams.py <教材>            # diagrams/<教材>/*.json をすべて描く
  scripts/render-diagrams.py <教材> 06-one-light  # 名前を指定して描く

diagrams/<教材>/<name>.json を読み、docs/<教材>/img/<name>.svg に書く。
座標はメートルで、x は右向き、y は背景（上）からカメラ（下）へ向かう。原点は背景の壁の中央。

仕様の例:
  {
    "title": "一灯と白レフ板",
    "room": {"width": 5, "depth": 4.5},
    "background": {"type": "paper", "label": "グレー背景紙", "color": "#9a9a9a"},
    "subject": {"x": 0, "y": 1.5, "label": "被写体"},
    "camera": {"x": 0, "y": 3.5, "label": "カメラ（RF 50mm）"},
    "lights": [
      {"type": "softbox", "x": -1.06, "y": 2.56, "group": "A", "label": "キー 1/4"}
    ],
    "boards": [{"type": "white", "x": 1.0, "y": 1.5, "rot": 90, "label": "白レフ"}],
    "measures": [{"from": "light:0", "to": "subject", "label": "1.5m"}],
    "angles": [{"at": "subject", "from": "camera", "to": "light:0", "label": "45°"}],
    "notes": [{"x": -2.3, "y": 0.5, "text": "壁は照らさない"}]
  }

要素の種類:
  background.type: cyc | paper | sweep | none。paper と sweep は width（既定 2.72）と color を持てる。
                   lit: true で照らされた壁として描く。
  subject.kind:    person（既定）| mug | glass | plate。facing は向き（度。180 がカメラ側）。
  lights[].type:   softbox | umbrella | umbrella-reflective | reflector | reflector-grid | bare
  lights[].aim:    "subject"（既定）| "camera" | [x, y] | "background"（真上の壁）
  lights[].gel:    色（例 "#3b6fd6"）。光の色に使う
  lights[].height: "floor" で床置きの短いスタンドとして描く（記号を小さくする）
  boards[].type:   white | black | flag
  measures[].from/to: "subject" | "camera" | "light:N" | "board:N" | "background" | [x, y]
  angles[].at/from/to: 同上
  参照先から見た向きの記号は、aim の方向に合わせて自動で回転する。
"""

import json
import math
import os
import sys

SCALE = 110  # px / m
MARGIN_X = 40
TOP = 100
BOTTOM = 100
FONT = "'Noto Sans JP','Noto Sans CJK JP','Hiragino Sans','Yu Gothic','Meiryo',sans-serif"
INK = "#333333"
MUTED = "#7a7a7a"
LIGHT = "#f2a900"
CONE_OPACITY = 0.16
WALL = "#e6e1d8"
PAPER_DEFAULT = "#9a9a9a"
SKIN = "#f1d9c2"
CLOTH = "#a9b8cf"
CAMERA = "#3c3c3c"

CONE_HALF_ANGLE = {
    "softbox": 38,
    "umbrella": 48,
    "umbrella-reflective": 44,
    "reflector": 26,
    "reflector-grid": 12,
    "bare": 60,
}
LEGEND_NAMES = {
    "softbox": "ソフトボックス",
    "umbrella": "透過アンブレラ",
    "umbrella-reflective": "反射アンブレラ",
    "reflector": "標準リフレクター",
    "reflector-grid": "リフレクター＋グリッド",
    "bare": "ストロボ（用具なし）",
    "white": "白レフ",
    "black": "黒レフ",
    "flag": "フラッグ（黒）",
    "person": "被写体",
    "mug": "被写体（マグカップ）",
    "glass": "被写体（グラス）",
    "plate": "被写体（皿）",
    "camera": "カメラ",
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Canvas:
    def __init__(self, spec):
        self.spec = spec
        room = spec.get("room", {})
        self.w_m = room.get("width", 5.0)
        self.d_m = room.get("depth", 5.0)
        self.width = int(self.w_m * SCALE + 2 * MARGIN_X)
        self.height = int(self.d_m * SCALE + TOP + BOTTOM)
        self.parts = []
        self.legend = []

    def px(self, x, y):
        return (MARGIN_X + (x + self.w_m / 2) * SCALE, TOP + y * SCALE)

    def add(self, s):
        self.parts.append(s)

    def use(self, key):
        if key not in self.legend:
            self.legend.append(key)

    # 参照（"subject" など）を座標に解決する
    def resolve(self, ref):
        spec = self.spec
        if isinstance(ref, (list, tuple)):
            return float(ref[0]), float(ref[1])
        if ref == "subject":
            s = spec["subject"]
            return s["x"], s["y"]
        if ref == "camera":
            c = spec["camera"]
            return c["x"], c["y"]
        if ref == "background":
            s = spec.get("subject", {"x": 0})
            return s.get("x", 0), 0.0
        if ref.startswith("light:"):
            l = spec["lights"][int(ref.split(":")[1])]
            return l["x"], l["y"]
        if ref.startswith("board:"):
            b = spec["boards"][int(ref.split(":")[1])]
            return b["x"], b["y"]
        raise ValueError(f"unknown ref: {ref}")

    def text(self, x, y, s, size=13, anchor="middle", color=INK, weight="normal", dy=0):
        lines = str(s).split("\n")
        out = [f'<text x="{x:.1f}" y="{y + dy:.1f}" font-family="{FONT}" font-size="{size}" '
               f'text-anchor="{anchor}" fill="{color}" font-weight="{weight}">']
        for i, line in enumerate(lines):
            dy_attr = "0" if i == 0 else f"{size * 1.35:.1f}"
            out.append(f'<tspan x="{x:.1f}" dy="{dy_attr}">{esc(line)}</tspan>')
        out.append("</text>")
        self.add("".join(out))

    # ---- 背景 ----
    def draw_background(self):
        bg = self.spec.get("background", {"type": "none"})
        kind = bg.get("type", "none")
        x0, y0 = self.px(-self.w_m / 2, 0)
        x1, _ = self.px(self.w_m / 2, 0)
        if kind == "cyc":
            fill = "#fff4cf" if bg.get("lit") else WALL
            self.add(f'<rect x="{x0:.1f}" y="{y0 - 26:.1f}" width="{x1 - x0:.1f}" height="26" fill="{fill}" stroke="{INK}" stroke-width="1"/>')
            # R 面（壁と床のつなぎ）を薄い帯で示す
            self.add(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="22" fill="{fill}" opacity="0.55"/>')
            if bg.get("lit"):
                self.add(f'<rect x="{x0:.1f}" y="{y0 - 26:.1f}" width="{x1 - x0:.1f}" height="48" fill="url(#glow)"/>')
            self.text((x0 + x1) / 2, y0 - 9, bg.get("label", "白ホリの壁"), size=12, color=INK)
        elif kind in ("paper", "sweep"):
            width = bg.get("width", 2.72)
            cx = bg.get("x", 0)
            color = bg.get("color", PAPER_DEFAULT)
            stroke = INK
            px0, _ = self.px(cx - width / 2, 0)
            px1, _ = self.px(cx + width / 2, 0)
            self.add(f'<rect x="{px0:.1f}" y="{y0 - 18:.1f}" width="{px1 - px0:.1f}" height="18" fill="{color}" stroke="{stroke}" stroke-width="1"/>')
            # ロールの端
            for px in (px0, px1):
                self.add(f'<circle cx="{px:.1f}" cy="{y0 - 9:.1f}" r="7" fill="#d9d4cc" stroke="{stroke}" stroke-width="1"/>')
            if kind == "sweep":
                # 床（テーブル）に延ばした紙
                length = bg.get("length", 1.2)
                _, py1 = self.px(0, length)
                self.add(f'<path d="M{px0:.1f},{y0:.1f} L{px0:.1f},{py1:.1f} L{px1:.1f},{py1:.1f} L{px1:.1f},{y0:.1f} Z" fill="{color}" opacity="0.35" stroke="{stroke}" stroke-width="0.8" stroke-dasharray="4 3"/>')
            label_color = INK
            self.text((px0 + px1) / 2, y0 - 26, bg.get("label", "背景紙"), size=12, color=label_color)

    # ---- 光の扇 ----
    def draw_cone(self, light):
        lx, ly = self.px(light["x"], light["y"])
        ax, ay = self.aim_of(light)
        apx, apy = self.px(ax, ay)
        ang = math.atan2(apy - ly, apx - lx)
        half = math.radians(CONE_HALF_ANGLE.get(light.get("type", "bare"), 30))
        dist = math.hypot(apx - lx, apy - ly)
        length = light.get("cone_length")
        length = length * SCALE if length else dist * 1.25
        color = light.get("gel", LIGHT)
        p1 = (lx + length * math.cos(ang - half), ly + length * math.sin(ang - half))
        p2 = (lx + length * math.cos(ang + half), ly + length * math.sin(ang + half))
        self.add(f'<path clip-path="url(#floor)" d="M{lx:.1f},{ly:.1f} L{p1[0]:.1f},{p1[1]:.1f} A{length:.1f},{length:.1f} 0 0,1 {p2[0]:.1f},{p2[1]:.1f} Z" '
                 f'fill="{color}" opacity="{CONE_OPACITY}"/>')
        # 中心線
        self.add(f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{apx:.1f}" y2="{apy:.1f}" stroke="{color}" stroke-width="1" stroke-dasharray="3 4" opacity="0.7"/>')

    def aim_of(self, light):
        aim = light.get("aim", "subject")
        return self.resolve(aim)

    # ---- ライトの記号 ----
    def draw_light(self, i, light):
        kind = light.get("type", "bare")
        self.use(kind)
        lx, ly = self.px(light["x"], light["y"])
        ax, ay = self.px(*self.aim_of(light))
        deg = math.degrees(math.atan2(ay - ly, ax - lx))
        scale = 0.7 if light.get("height") == "floor" else 1.0
        color = light.get("gel", LIGHT)
        g = [f'<g transform="translate({lx:.1f},{ly:.1f}) rotate({deg:.1f}) scale({scale})">']
        # 本体（モノブロック）は原点、照射方向は +x
        if kind == "softbox":
            g.append(f'<rect x="-6" y="-33" width="30" height="66" fill="#f7f7f7" stroke="{INK}" stroke-width="1.4"/>')
            g.append(f'<line x1="-6" y1="-33" x2="24" y2="0" stroke="{MUTED}" stroke-width="0.8"/>')
            g.append(f'<line x1="-6" y1="33" x2="24" y2="0" stroke="{MUTED}" stroke-width="0.8"/>')
            g.append(f'<rect x="22" y="-33" width="5" height="66" fill="{color}" stroke="{INK}" stroke-width="1"/>')
            g.append(f'<circle cx="-12" cy="0" r="8" fill="#555" stroke="{INK}" stroke-width="1"/>')
        elif kind in ("umbrella", "umbrella-reflective"):
            if kind == "umbrella":
                g.append(f'<path d="M-10,-40 Q28,0 -10,40" fill="#fdfdfd" stroke="{INK}" stroke-width="1.4"/>')
                g.append(f'<line x1="-10" y1="0" x2="-30" y2="0" stroke="{INK}" stroke-width="1.4"/>')
                g.append(f'<circle cx="-30" cy="0" r="8" fill="#555" stroke="{INK}" stroke-width="1"/>')
                g.append(f'<path d="M-6,-30 Q20,0 -6,30" fill="none" stroke="{color}" stroke-width="2"/>')
            else:
                g.append(f'<path d="M10,-40 Q-28,0 10,40" fill="#fdfdfd" stroke="{INK}" stroke-width="1.4"/>')
                g.append(f'<line x1="-10" y1="0" x2="10" y2="0" stroke="{INK}" stroke-width="1.4"/>')
                g.append(f'<circle cx="12" cy="0" r="8" fill="#555" stroke="{INK}" stroke-width="1"/>')
                g.append(f'<path d="M6,-30 Q-18,0 6,30" fill="none" stroke="{color}" stroke-width="2"/>')
        elif kind in ("reflector", "reflector-grid"):
            g.append(f'<circle cx="-10" cy="0" r="9" fill="#555" stroke="{INK}" stroke-width="1"/>')
            g.append(f'<path d="M-2,-8 L14,-16 L14,16 L-2,8 Z" fill="#e0e0e0" stroke="{INK}" stroke-width="1.4"/>')
            g.append(f'<line x1="14" y1="-16" x2="14" y2="16" stroke="{color}" stroke-width="3"/>')
            if kind == "reflector-grid":
                for yy in (-12, -6, 0, 6, 12):
                    g.append(f'<line x1="8" y1="{yy}" x2="14" y2="{yy}" stroke="{INK}" stroke-width="1"/>')
        else:  # bare
            g.append(f'<circle cx="0" cy="0" r="9" fill="#555" stroke="{INK}" stroke-width="1"/>')
            g.append(f'<circle cx="8" cy="0" r="4" fill="{color}"/>')
        g.append("</g>")
        self.add("".join(g))
        # グループのバッジ（照射方向の反対側）
        if light.get("group"):
            rad = math.radians(deg + 180)
            off = 42 * scale
            bx, by = lx + off * math.cos(rad), ly + off * math.sin(rad)
            self.add(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="10" fill="{INK}"/>')
            self.text(bx, by + 4.5, light["group"], size=12, color="#fff", weight="bold")
        # ラベル
        if light.get("label"):
            dx = light.get("label_dx", 0)
            dy = light.get("label_dy", 0)
            if dx == 0 and dy == 0:
                rad = math.radians(deg + 180)
                dx = (64 if light.get("group") else 48) * math.cos(rad)
                dy = (64 if light.get("group") else 48) * math.sin(rad) + 4
            anchor = light.get("label_anchor") or ("end" if dx < -10 else "start" if dx > 10 else "middle")
            x = lx + dx
            if x < MARGIN_X + 8:
                x, anchor = MARGIN_X + 4, "start"
            elif x > self.width - MARGIN_X - 8:
                x, anchor = self.width - MARGIN_X - 4, "end"
            self.text(x, ly + dy, light["label"], size=12, anchor=anchor)

    # ---- レフ板 ----
    def draw_board(self, i, board):
        kind = board.get("type", "white")
        self.use(kind)
        bx, by = self.px(board["x"], board["y"])
        rot = board.get("rot", 0)
        length = board.get("length", 0.9) * SCALE
        thick = 7
        if kind == "white":
            fill, stroke = "#ffffff", INK
        else:
            fill, stroke = "#222222", "#222222"
        if kind == "flag":
            length = board.get("length", 0.6) * SCALE
        self.add(f'<g transform="translate({bx:.1f},{by:.1f}) rotate({rot})">'
                 f'<rect x="{-length / 2:.1f}" y="{-thick / 2}" width="{length:.1f}" height="{thick}" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>'
                 f'</g>')
        if board.get("label"):
            dx = board.get("label_dx", 0)
            dy = board.get("label_dy", -14)
            anchor = board.get("label_anchor", "middle")
            self.text(bx + dx, by + dy, board["label"], size=12, anchor=anchor)

    # ---- 被写体 ----
    def draw_subject(self):
        s = self.spec["subject"]
        kind = s.get("kind", "person")
        self.use(kind)
        sx, sy = self.px(s["x"], s["y"])
        facing = s.get("facing", 180)
        if kind == "person":
            g = [f'<g transform="translate({sx:.1f},{sy:.1f}) rotate({facing - 90})">']
            g.append(f'<ellipse cx="0" cy="0" rx="14" ry="27" fill="{CLOTH}" stroke="{INK}" stroke-width="1.2"/>')
            g.append(f'<circle cx="3" cy="0" r="11" fill="{SKIN}" stroke="{INK}" stroke-width="1.2"/>')
            g.append(f'<path d="M14,-4 L19,0 L14,4 Z" fill="{SKIN}" stroke="{INK}" stroke-width="1"/>')
            g.append("</g>")
            self.add("".join(g))
        elif kind == "mug":
            self.add(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="11" fill="#fafafa" stroke="{INK}" stroke-width="1.4"/>')
            self.add(f'<path d="M{sx + 11:.1f},{sy - 5:.1f} a7,7 0 1,1 0,10" fill="none" stroke="{INK}" stroke-width="1.6"/>')
        elif kind == "glass":
            self.add(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="10" fill="#eef6fb" stroke="{INK}" stroke-width="1.4"/>')
            self.add(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="7" fill="none" stroke="{INK}" stroke-width="0.8"/>')
        elif kind == "plate":
            self.add(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="18" fill="#fafafa" stroke="{INK}" stroke-width="1.4"/>')
            self.add(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="11" fill="#f3e2c8" stroke="{INK}" stroke-width="0.8"/>')
        if s.get("label"):
            dx = s.get("label_dx", 0)
            dy = s.get("label_dy", 46)
            anchor = s.get("label_anchor", "middle" if dx == 0 else "start" if dx > 0 else "end")
            self.text(sx + dx, sy + dy, s["label"], size=12, anchor=anchor)

    # ---- カメラ ----
    def draw_camera(self):
        c = self.spec.get("camera")
        if not c:
            return
        self.use("camera")
        cx, cy = self.px(c["x"], c["y"])
        ax, ay = self.px(*self.resolve(c.get("aim", "subject")))
        deg = math.degrees(math.atan2(ay - cy, ax - cx))
        g = [f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({deg:.1f})">']
        g.append(f'<rect x="-14" y="-11" width="20" height="22" rx="3" fill="{CAMERA}"/>')
        g.append(f'<rect x="6" y="-7" width="14" height="14" fill="#666" stroke="{INK}" stroke-width="1"/>')
        g.append(f'<circle cx="20" cy="0" r="5" fill="#9ec5e8" stroke="{INK}" stroke-width="1"/>')
        g.append("</g>")
        self.add("".join(g))
        if c.get("tripod"):
            self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="22" fill="none" stroke="{MUTED}" stroke-width="1" stroke-dasharray="2 3"/>')
        if c.get("label"):
            dx = c.get("label_dx", 0)
            dy = c.get("label_dy", 30)
            anchor = c.get("label_anchor", "middle")
            self.text(cx + dx, cy + dy, c["label"], size=12, anchor=anchor)

    # ---- 寸法 ----
    def draw_measure(self, m):
        x0, y0 = self.px(*self.resolve(m["from"]))
        x1, y1 = self.px(*self.resolve(m["to"]))
        offset = m.get("offset", 0.22) * SCALE
        ang = math.atan2(y1 - y0, x1 - x0)
        nx, ny = -math.sin(ang), math.cos(ang)
        ox0, oy0 = x0 + nx * offset, y0 + ny * offset
        ox1, oy1 = x1 + nx * offset, y1 + ny * offset
        color = m.get("color", "#b3541e")
        self.add(f'<line x1="{ox0:.1f}" y1="{oy0:.1f}" x2="{ox1:.1f}" y2="{oy1:.1f}" stroke="{color}" stroke-width="1" stroke-dasharray="5 3"/>')
        for (px, py) in ((ox0, oy0), (ox1, oy1)):
            self.add(f'<line x1="{px - nx * 5:.1f}" y1="{py - ny * 5:.1f}" x2="{px + nx * 5:.1f}" y2="{py + ny * 5:.1f}" stroke="{color}" stroke-width="1.2"/>')
        mx, my = (ox0 + ox1) / 2 + nx * 12, (oy0 + oy1) / 2 + ny * 12
        self.text(mx, my + 4, m.get("label", ""), size=12, color=color)

    # ---- 角度 ----
    def draw_angle(self, a):
        cx, cy = self.px(*self.resolve(a["at"]))
        fx, fy = self.px(*self.resolve(a["from"]))
        tx, ty = self.px(*self.resolve(a["to"]))
        r = a.get("radius", 0.55) * SCALE
        a0 = math.atan2(fy - cy, fx - cx)
        a1 = math.atan2(ty - cy, tx - cx)
        d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi  # -pi..pi
        sweep = 1 if d > 0 else 0
        large = 1 if abs(d) > math.pi else 0
        p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
        color = a.get("color", "#2f6db5")
        self.add(f'<path d="M{p0[0]:.1f},{p0[1]:.1f} A{r:.1f},{r:.1f} 0 {large},{sweep} {p1[0]:.1f},{p1[1]:.1f}" fill="none" stroke="{color}" stroke-width="1.2"/>')
        # 基準線（at → from）を薄く
        self.add(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{fx:.1f}" y2="{fy:.1f}" stroke="{color}" stroke-width="0.8" stroke-dasharray="2 3" opacity="0.6"/>')
        mid = a0 + d / 2
        lx, ly = cx + (r + 16) * math.cos(mid), cy + (r + 16) * math.sin(mid)
        self.text(lx, ly + 4, a.get("label", ""), size=12, color=color)

    # ---- 注記と矢印 ----
    def draw_note(self, n):
        x, y = self.px(n["x"], n["y"])
        self.text(x, y, n["text"], size=n.get("size", 12), anchor=n.get("anchor", "start"), color=n.get("color", MUTED))

    def draw_arrow(self, a):
        x0, y0 = self.px(*self.resolve(a["from"]))
        x1, y1 = self.px(*self.resolve(a["to"]))
        color = a.get("color", MUTED)
        self.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{color}" stroke-width="1.2" marker-end="url(#arrow)"/>')
        if a.get("label"):
            self.text((x0 + x1) / 2, (y0 + y1) / 2 - 6, a["label"], size=12, color=color)

    # ---- 凡例とスケール ----
    def draw_legend(self):
        y = self.height - BOTTOM + 36
        x = MARGIN_X
        limit = self.width - MARGIN_X - SCALE - 40
        items = [k for k in self.legend if k in LEGEND_NAMES]
        for key in items:
            name = LEGEND_NAMES[key]
            item_w = 30 + len(name) * 11 + 26
            if x + item_w > limit and x > MARGIN_X:
                x = MARGIN_X
                y += 24
            self.add(f'<g transform="translate({x:.1f},{y:.1f})">{self.legend_icon(key)}</g>')
            self.text(x + 30, y + 4, name, size=11, anchor="start", color=MUTED)
            x += item_w
        # スケール
        sx = self.width - MARGIN_X - SCALE
        sy = self.height - BOTTOM + 36
        self.add(f'<line x1="{sx}" y1="{sy}" x2="{sx + SCALE}" y2="{sy}" stroke="{INK}" stroke-width="1.5"/>')
        for px in (sx, sx + SCALE):
            self.add(f'<line x1="{px}" y1="{sy - 4}" x2="{px}" y2="{sy + 4}" stroke="{INK}" stroke-width="1.5"/>')
        self.text(sx + SCALE / 2, sy + 16, "1m", size=11, color=MUTED)

    def legend_icon(self, key):
        s = 0.42
        if key == "softbox":
            return f'<g transform="rotate(-90) scale({s})"><rect x="-6" y="-33" width="30" height="66" fill="#f7f7f7" stroke="{INK}" stroke-width="2"/><rect x="22" y="-33" width="5" height="66" fill="{LIGHT}"/></g>'
        if key == "umbrella":
            return f'<g transform="rotate(-90) scale({s})"><path d="M-10,-40 Q28,0 -10,40" fill="#fdfdfd" stroke="{INK}" stroke-width="2.5"/><line x1="-10" y1="0" x2="-30" y2="0" stroke="{INK}" stroke-width="2.5"/></g>'
        if key == "umbrella-reflective":
            return f'<g transform="rotate(-90) scale({s})"><path d="M10,-40 Q-28,0 10,40" fill="#fdfdfd" stroke="{INK}" stroke-width="2.5"/><circle cx="12" cy="0" r="8" fill="#555"/></g>'
        if key in ("reflector", "reflector-grid"):
            grid = "".join(f'<line x1="8" y1="{yy}" x2="14" y2="{yy}" stroke="{INK}" stroke-width="2"/>' for yy in (-12, -6, 0, 6, 12)) if key == "reflector-grid" else ""
            return f'<g transform="rotate(-90) scale({s * 1.4})"><circle cx="-10" cy="0" r="9" fill="#555"/><path d="M-2,-8 L14,-16 L14,16 L-2,8 Z" fill="#e0e0e0" stroke="{INK}" stroke-width="1.6"/>{grid}</g>'
        if key == "bare":
            return f'<circle cx="0" cy="0" r="6" fill="#555"/>'
        if key == "white":
            return f'<rect x="-12" y="-3" width="24" height="6" fill="#fff" stroke="{INK}" stroke-width="1.4"/>'
        if key in ("black", "flag"):
            return f'<rect x="-12" y="-3" width="24" height="6" fill="#222"/>'
        if key == "person":
            return f'<g transform="rotate(90) scale(0.5)"><ellipse cx="0" cy="0" rx="14" ry="27" fill="{CLOTH}" stroke="{INK}" stroke-width="2"/><circle cx="3" cy="0" r="11" fill="{SKIN}" stroke="{INK}" stroke-width="2"/></g>'
        if key in ("mug", "glass", "plate"):
            return f'<circle cx="0" cy="0" r="7" fill="#fafafa" stroke="{INK}" stroke-width="1.4"/>'
        if key == "camera":
            return f'<g transform="rotate(-90) scale(0.55)"><rect x="-14" y="-11" width="20" height="22" rx="3" fill="{CAMERA}"/><rect x="6" y="-7" width="14" height="14" fill="#666"/></g>'
        return ""

    def render(self):
        spec = self.spec
        self.add(f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
                 f'<path d="M0,0 L10,5 L0,10 Z" fill="{MUTED}"/></marker>'
                 f'<linearGradient id="glow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{LIGHT}" stop-opacity="0.35"/><stop offset="1" stop-color="{LIGHT}" stop-opacity="0"/></linearGradient>'
                 f'<clipPath id="floor"><rect x="{MARGIN_X}" y="{TOP - 26}" width="{self.w_m * SCALE:.1f}" height="{self.d_m * SCALE + 26:.1f}"/></clipPath></defs>')
        self.add(f'<rect x="0.5" y="0.5" width="{self.width - 1}" height="{self.height - 1}" rx="8" fill="#ffffff" stroke="#d9d9d9"/>')
        # 床（撮影エリア）
        fx, fy = self.px(-self.w_m / 2, 0)
        self.add(f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{self.w_m * SCALE:.1f}" height="{self.d_m * SCALE:.1f}" fill="#fbfaf7"/>')
        if spec.get("title"):
            self.text(MARGIN_X, 30, spec["title"], size=16, anchor="start", weight="bold")
        if spec.get("subtitle"):
            self.text(MARGIN_X, 52, spec["subtitle"], size=12, anchor="start", color=MUTED)
        self.draw_background()
        for light in spec.get("lights", []):
            if light.get("cone", True):
                self.draw_cone(light)
        for i, board in enumerate(spec.get("boards", [])):
            self.draw_board(i, board)
        for m in spec.get("measures", []):
            self.draw_measure(m)
        for a in spec.get("angles", []):
            self.draw_angle(a)
        self.draw_subject()
        for i, light in enumerate(spec.get("lights", [])):
            self.draw_light(i, light)
        self.draw_camera()
        for a in spec.get("arrows", []):
            self.draw_arrow(a)
        for n in spec.get("notes", []):
            self.draw_note(n)
        self.draw_legend()
        body = "\n".join(self.parts)
        title = esc(spec.get("title", ""))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" '
                f'width="{self.width}" height="{self.height}" role="img" aria-label="{title}">\n{body}\n</svg>\n')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    material = sys.argv[1]
    names = sys.argv[2:]
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    src_dir = os.path.join(root, "diagrams", material)
    out_dir = os.path.join(root, "docs", material, "img")
    os.makedirs(out_dir, exist_ok=True)
    files = sorted(f for f in os.listdir(src_dir) if f.endswith(".json"))
    if names:
        files = [f for f in files if f[:-5] in names]
    for f in files:
        spec = json.load(open(os.path.join(src_dir, f), encoding="utf-8"))
        svg = Canvas(spec).render()
        out = os.path.join(out_dir, f[:-5] + ".svg")
        open(out, "w", encoding="utf-8").write(svg)
        print("render:", os.path.relpath(out, root))


if __name__ == "__main__":
    main()
