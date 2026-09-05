"""第 4〜6 章のイラスト。scripts/render-figures.py studio-photography で docs/studio-photography/img/ に書き出す。"""
import math

import figlib as fl
from figlib import INK, MUTED, LIGHT, ACCENT, DIM, SKIN, WALL, BLACK, FLOOR, BODY, SHADOW


# ---------------------------------------------------------------- 図 4-1 モノブロック
def fig_04_monoblock():
    f = fl.Figure(800, 600, "モノブロックストロボの各部（模式図）",
                  "左上は前面（用具を外した状態）、中央は側面（標準リフレクターを付けた状態）、下は背面の操作部")
    # ---- 前面 ----
    fx, fy = 120, 170
    f.text(fx - 60, fy - 96, "前面", size=12, anchor="middle", color=MUTED)
    f.circle(fx, fy, 72, "#444", INK, 1.4)
    f.circle(fx, fy, 60, "#e9e9e9", INK, 1.2)
    for k in range(3):
        f.add(f'<rect x="-9" y="-72" width="18" height="12" rx="2" fill="#777" stroke="{INK}" stroke-width="1" transform="translate({fx},{fy}) rotate({180 + k * 120})"/>')
    f.circle(fx, fy, 38, "none", LIGHT, 7, opacity=0.9)
    f.circle(fx, fy, 38, "none", "#c98a00", 1)
    f.circle(fx, fy, 16, "#fff1c2", INK, 1.2)
    f.circle(fx, fy, 7, "#f7d774", INK, 0.8)
    f.callout(1, fx + 52, fy - 52, to=(fx + 27, fy - 27))
    f.callout(2, fx - 58, fy + 62, to=(fx - 10, fy + 12))
    f.callout(3, fx + 8, fy - 100, to=(fx + 4, fy - 76))

    # ---- 側面 ----
    bx, by = 300, 160  # 本体の左上（旧図の基準点）
    f.text(400, 78, "側面", size=12, anchor="middle", color=MUTED)
    fl.monoblock_side(f, bx + 75, by + 40)
    for k in (-1, 0, 1):
        f.arrow(bx + 236, by + 40 + k * 30, bx + 275, by + 40 + k * 46, LIGHT, 1.6)
    # ライトスタンドの先端
    f.rect(bx + 68, by + 96, 14, 40, "#8a8a8a", INK, 1.2)
    f.circle(bx + 60, by + 112, 5, "#999", INK, 1)
    f.text(bx + 75, by + 152, "ライトスタンド", size=11, anchor="middle", color=MUTED)
    f.callout(4, bx + 250, by - 40, to=(bx + 215, by - 8))
    f.callout(5, bx + 131, by - 40, to=(bx + 131, by - 16))
    f.callout(6, bx + 150, by + 130, to=(bx + 112, by + 92))
    f.callout(7, bx + 40, by - 20, to=(bx + 40, by + 14))
    f.callout(8, bx - 60, by + 100, to=(bx - 36, by + 90))

    # ---- 背面パネル ----
    px, py = 80, 340
    f.text(px + 165, py - 12, "背面（操作部）", size=12, anchor="middle", color=MUTED)
    f.rect(px, py, 330, 200, BODY, INK, 1.4, 10)
    f.rect(px + 22, py + 22, 150, 64, "#dfe9d9", INK, 1.2, 4)
    f.text(px + 34, py + 48, "1/4", size=22, weight="bold")
    f.text(px + 92, py + 44, "CH 1  GR A", size=11)
    f.text(px + 92, py + 62, "M", size=11)
    f.text(px + 34, py + 76, "モデリング  ブザー ON", size=9, color=MUTED)
    f.circle(px + 250, py + 58, 34, "#8a8a8a", INK, 1.4)
    f.circle(px + 250, py + 58, 26, "#a8a8a8", INK, 1)
    f.line(px + 250, py + 58, px + 262, py + 36, INK, 2.5)
    for k, (name, col) in enumerate([("TEST", "#e8b64a"), ("MODEL", "#e0e0e0"), ("BUZZ", "#e0e0e0"), ("CH/GR", "#e0e0e0"), ("SLAVE", "#e0e0e0")]):
        x = px + 22 + k * 62
        f.rect(x, py + 104, 50, 26, col, INK, 1, 5)
        f.text(x + 25, py + 121, name, size=9.5, anchor="middle")
    f.rect(px + 22, py + 150, 40, 28, "#c33", INK, 1, 4)
    f.text(px + 42, py + 168, "ON", size=10, anchor="middle", color="#fff", weight="bold")
    f.rect(px + 80, py + 150, 34, 28, "#222", INK, 1, 3)
    f.text(px + 97, py + 168, "AC", size=9, anchor="middle", color="#ddd")
    f.rect(px + 200, py + 150, 108, 28, "#3a3a3a", INK, 1, 3)
    for k in range(9):
        f.line(px + 208 + k * 12, py + 154, px + 208 + k * 12, py + 174, "#777", 2)
    f.text(px + 254, py + 192, "放熱ファンの吸気口", size=9.5, anchor="middle", color="#ccc")
    f.callout(9, px + 97, py + 8, to=(px + 97, py + 24))
    f.callout(10, px + 300, py + 22, to=(px + 276, py + 40))
    f.callout(11, px + 47, py + 96, to=(px + 47, py + 108))
    f.callout(12, px + 109, py + 96, to=(px + 109, py + 108))
    f.callout(13, px + 233, py + 96, to=(px + 233, py + 108))
    f.callout(14, px + 42, py + 196, to=(px + 42, py + 180))
    f.callout_list(470, 330, [
        "発光管（リング状。本番の光を出す）",
        "モデリングランプ（配置の確認用の連続光）",
        "Bowens マウントの爪（用具を差して回す）",
        "標準リフレクター（付属の金属の皿）",
        "傘穴（アンブレラの軸を通す）",
        "スタンド取り付け部と角度の締めネジ",
        "放熱ファンの排気口",
        "AC ケーブル",
        "表示部（出力、チャンネル、グループ）",
        "出力ダイヤル（0.1 段刻み）",
        "テスト発光ボタン",
        "モデリングランプのボタン",
        "無線のチャンネルとグループ、光スレーブの切り替え",
        "電源スイッチ（入り切りは本体で行う）",
    ])
    return f


# ---------------------------------------------------------------- 図 4-2 トリガー
def fig_04_trigger():
    f = fl.Figure(800, 470, "トリガーの設定と受信側の対応",
                  "送信機はカメラのホットシューに付け、チャンネルと ID をストロボと揃え、グループごとに出力を送る")
    cx, cy = 60, 290
    f.text(60, 100, "カメラとトリガー", size=12, color=MUTED)
    f.rect(cx, cy - 60, 150, 100, fl.CAMERA_BODY, INK, 1.4, 10)
    f.path(f"M{cx + 40},{cy - 60} L{cx + 50},{cy - 82} L{cx + 110},{cy - 82} L{cx + 120},{cy - 60} Z", fl.CAMERA_BODY, INK, 1.2)
    f.rect(cx + 150, cy - 40, 70, 60, "#4a4a4a", INK, 1.2, 6)
    f.circle(cx + 232, cy - 10, 22, fl.LENS, INK, 1.2)
    f.rect(cx + 62, cy - 92, 36, 10, "#888", INK, 1)
    f.rect(cx + 52, cy - 150, 56, 58, "#2a2a2a", INK, 1.2, 5)
    f.rect(cx + 58, cy - 144, 44, 30, "#dfe9d9", "none", 0, 2)
    f.rect(cx + 62, cy - 108, 12, 8, "#e8b64a", "none", 0, 2)
    f.rect(cx + 78, cy - 108, 12, 8, "#bbb", "none", 0, 2)
    f.line(cx + 108, cy - 140, cx + 130, cy - 170, INK, 1.6)
    f.callout(1, cx + 30, cy - 130, to=(cx + 52, cy - 126))
    f.callout(2, cx + 30, cy - 88, to=(cx + 62, cy - 87))
    f.text(cx + 36, cy + 70, "1 トリガー（送信機）  2 ホットシュー", size=11, color=MUTED)
    for r in (16, 27, 38):
        f.path(f"M{cx + 130 + r * 0.3:.1f},{cy - 170 - r * 0.95:.1f} A{r},{r} 0 0,1 {cx + 130 + r * 0.95:.1f},{cy - 170 - r * 0.3:.1f}", "none", ACCENT, 1.4)
    f.text(cx + 176, cy - 176, "2.4GHz", size=11, color=ACCENT)

    px, py = 340, 110
    f.text(px + 105, py - 12, "送信機の表示（拡大）", size=12, anchor="middle", color=MUTED)
    f.rect(px, py, 210, 230, "#2a2a2a", INK, 1.4, 8)
    f.rect(px + 12, py + 12, 186, 160, "#dfe9d9", INK, 1, 3)
    f.text(px + 22, py + 34, "CH 1", size=15, weight="bold")
    f.text(px + 90, py + 34, "ID OFF", size=13)
    f.text(px + 160, py + 34, "M", size=13, weight="bold")
    f.line(px + 18, py + 44, px + 192, py + 44, INK, 0.8)
    rows = [("A", "M", "1/4", "キー"), ("B", "M", "1/8", "フィル"), ("C", "M", "1/16", "リム / 背景"), ("D", "OFF", "--", ""), ("E", "OFF", "--", "")]
    for k, (g, mode, pw, role) in enumerate(rows):
        y = py + 66 + k * 22
        col = INK if mode == "M" else MUTED
        f.text(px + 22, y, g, size=14, weight="bold", color=col)
        f.text(px + 50, y, mode, size=12, color=col)
        f.text(px + 96, y, pw, size=14, weight="bold", color=col)
        f.text(px + 140, y, role, size=10, color=MUTED)
    for k, (name, col) in enumerate([("TEST", "#e8b64a"), ("MODEL", "#bbb"), ("電源", "#bbb")]):
        x = px + 16 + k * 62
        f.rect(x, py + 184, 52, 24, col, INK, 1, 5)
        f.text(x + 26, py + 200, name, size=10, anchor="middle")
    f.text(px, py + 258, "3 テスト発光ボタン  4 モデリングランプのボタン", size=11, color=MUTED)
    f.badge(px + 42, py + 222, 3)
    f.badge(px + 104, py + 222, 4)

    sx = 630
    f.text(sx + 60, 98, "受信側（ストロボ本体）", size=12, anchor="middle", color=MUTED)
    for k, (g, pw, role) in enumerate([("A", "1/4", "キー"), ("B", "1/8", "フィル"), ("C", "1/16", "リム / 背景")]):
        y = 130 + k * 90
        f.rect(sx, y, 120, 56, BODY, INK, 1.2, 8)
        f.rect(sx + 10, y + 10, 70, 36, "#dfe9d9", "none", 0, 3)
        f.text(sx + 16, y + 26, f"CH 1  GR {g}", size=11)
        f.text(sx + 16, y + 42, pw, size=13, weight="bold")
        f.badge(sx + 100, y + 28, g)
        f.text(sx + 60, y + 72, role, size=11, anchor="middle", color=MUTED)
        f.arrow(px + 212, py + 62 + k * 22, sx - 6, y + 28, ACCENT)
    f.text(sx - 20, 420, "同じチャンネル（と ID）に合わせ、\n灯ごとにグループを割り当てる", size=11, color=ACCENT)
    f.note(24, 445, "SK400II が受け付ける出力は 1/16 まで。それより下を送っても 1/16 で光る")
    return f


# ---------------------------------------------------------------- 図 4-3 逆二乗則
def fig_04_inverse_square():
    f = fl.Figure(800, 400, "逆二乗則：距離が伸びるほど同じ光が広い面に薄まる",
                  "光源からの距離が √2 倍になるごとに、光が広がる面積は 2 倍になり、明るさは 1 段ずつ下がる")
    ox, oy = 90, 220
    f.rect(ox - 24, oy - 30, 24, 60, "#f7f7f7", INK, 1.3)
    f.rect(ox - 4, oy - 30, 4, 60, LIGHT, "none", 0)
    f.text(ox - 12, oy + 52, "光源", size=12, anchor="middle")
    px_per_m = 100
    base = 44
    for d, side, stop, fv, op in [(1.5, 1.0, 0, "f/8", 0.55), (2.1, 1.41, -1, "f/5.6", 0.32), (3.0, 2.0, -2, "f/4", 0.18)]:
        x = ox + d * px_per_m
        h = base * side
        w = h * 0.5
        f.path(f"M{x},{oy - h / 2} L{x + w * 0.35},{oy - h / 2 - w * 0.25} L{x + w * 0.35},{oy + h / 2 - w * 0.25} L{x},{oy + h / 2} Z", LIGHT, INK, 1, opacity=op)
        f.line(x, oy - h / 2, x, oy + h / 2, INK, 1.2)
        f.text(x + 6, oy + h / 2 + 22, f"{d}m", size=13, anchor="middle", weight="bold")
        f.text(x + 6, oy + h / 2 + 40, f"面積 {'1' if side == 1 else '2' if side < 2 else '4'} 倍", size=11, anchor="middle", color=MUTED)
        f.text(x + 6, oy + h / 2 + 56, f"{'±0' if stop == 0 else stop} 段　{fv}", size=11, anchor="middle", color=DIM)
    far_x = ox + 3.0 * px_per_m
    far_h = base * 2
    for k in (-1, 1):
        f.line(ox, oy, far_x, oy + k * far_h / 2, LIGHT, 1.4)
    f.path(f"M{ox},{oy} L{far_x},{oy - far_h / 2} L{far_x},{oy + far_h / 2} Z", LIGHT, "none", 0, opacity=0.10)
    y = oy - 90
    f.line(ox, y, far_x, y, DIM, 1, "5 3")
    for d in (0, 1.5, 2.1, 3.0):
        x = ox + d * px_per_m
        f.line(x, y - 5, x, y + 5, DIM, 1.2)
    f.text((ox + far_x) / 2, y - 10, "光源からの距離（√2 倍ごとに 1 段）", size=11, anchor="middle", color=DIM)
    f.note(24, 372, "出力 1/4 のソフトボックスなら、1.5m で f/8、2.1m で f/5.6、3m で f/4。位置を決めたら明るさは出力で合わせる")
    return f


# ---------------------------------------------------------------- 図 5-1 硬い光と柔らかい光
def fig_05_hard_soft():
    f = fl.Figure(800, 560, "影の縁を決めるのは、被写体から見た光源の見かけの大きさ")

    def panel(x0, y0, big, title):
        f.text(x0, y0, title, size=13, weight="bold")
        lx, ly = x0 + 30, y0 + 110
        bx, by = x0 + 190, y0 + 110
        wx = x0 + 330
        f.rect(wx, y0 + 20, 14, 180, WALL, INK, 1)
        f.text(wx + 7, y0 + 216, "壁", size=11, anchor="middle", color=MUTED)
        r = 26
        if big:
            top, bot = ly - 60, ly + 60
            f.rect(lx - 10, top, 14, 120, LIGHT, INK, 1.2)
            f.text(lx - 3, y0 + 216, "大きな光源", size=11, anchor="middle", color=MUTED)
        else:
            top, bot = ly - 3, ly + 3
            f.light_glyph(lx, ly, r=6)
            f.text(lx, y0 + 216, "小さな光源", size=11, anchor="middle", color=MUTED)

        def hit(sy, tangent_y):
            t = (wx - lx) / (bx - lx)
            return sy + (tangent_y - sy) * t

        u1, u2 = hit(top, by + r), hit(bot, by - r)
        p1, p2 = hit(top, by - r), hit(bot, by + r)
        if big:
            ga, gb = f.uid("pen"), f.uid("pen")
            f.add_def(f'<linearGradient id="{ga}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SHADOW}" stop-opacity="0"/><stop offset="1" stop-color="{SHADOW}" stop-opacity="0.55"/></linearGradient>')
            f.add_def(f'<linearGradient id="{gb}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SHADOW}" stop-opacity="0.55"/><stop offset="1" stop-color="{SHADOW}" stop-opacity="0"/></linearGradient>')
            f.add(f'<rect x="{wx}" y="{p1:.1f}" width="14" height="{u2 - p1:.1f}" fill="url(#{ga})"/>')
            f.add(f'<rect x="{wx}" y="{u2:.1f}" width="14" height="{u1 - u2:.1f}" fill="{SHADOW}" opacity="0.55"/>')
            f.add(f'<rect x="{wx}" y="{u1:.1f}" width="14" height="{p2 - u1:.1f}" fill="url(#{gb})"/>')
            for sy, ty in ((top, by - r), (top, by + r), (bot, by - r), (bot, by + r)):
                f.add(f'<line x1="{lx}" y1="{sy}" x2="{wx}" y2="{hit(sy, ty):.1f}" stroke="{LIGHT}" stroke-width="1" opacity="0.9"/>')
            f.text(wx + 20, (p1 + u2) / 2 + 4, "半影", size=11, color=ACCENT)
            f.text(wx + 20, (u1 + u2) / 2 + 4, "本影", size=11)
            f.text(wx + 20, (u1 + p2) / 2 + 4, "半影", size=11, color=ACCENT)
        else:
            f.add(f'<rect x="{wx}" y="{u2:.1f}" width="14" height="{u1 - u2:.1f}" fill="{SHADOW}" opacity="0.55"/>')
            for ty in (by - r, by + r):
                f.line(lx, ly, wx, hit(ly, ty), LIGHT, 1)
            f.text(wx + 20, (u1 + u2) / 2 + 4, "本影だけ", size=11)
        gid = f.uid("ball")
        f.add_def(f'<radialGradient id="{gid}" cx="0.3" cy="0.35" r="0.8"><stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#cfcfcf"/><stop offset="1" stop-color="#6f6f6f"/></radialGradient>')
        f.circle(bx, by, r, f"url(#{gid})", INK, 1.2)
        f.text(bx, y0 + 216, "被写体", size=11, anchor="middle", color=MUTED)

    panel(24, 80, False, "硬い光：点に近い光源。影の縁は鋭い")
    panel(410, 80, True, "柔らかい光：面積を持つ光源。半影の幅が広い")

    y0 = 340
    f.text(30, y0, "同じソフトボックスでも、距離で見かけの大きさが変わる", size=13, weight="bold")
    fx, fy = 80, y0 + 100
    f.circle(fx, fy, 14, SKIN, INK, 1.2)
    f.text(fx, fy + 40, "被写体", size=11, anchor="middle", color=MUTED)
    m = 66
    for d, col, lab in ((1.5, LIGHT, "1.5m：約 33 度"), (5.0, "#c9a24a", "5m：約 10 度")):
        x = fx + d * m
        half = 0.45 * m
        f.rect(x - 5, fy - half, 10, 2 * half, "#f7f7f7", INK, 1.2)
        f.rect(x - 5, fy - half, 3, 2 * half, col, "none", 0)
        f.line(fx, fy, x - 5, fy - half, col, 1, "4 3")
        f.line(fx, fy, x - 5, fy + half, col, 1, "4 3")
        f.text(x, fy - half - 10, lab, size=11, anchor="middle")
    for d, col, ra in ((1.5, ACCENT, 60), (5.0, "#7a5a1a", 120)):
        x = fx + d * m
        a = math.atan2(0.45 * m, x - 5 - fx)
        f.path(f"M{fx + ra * math.cos(-a):.1f},{fy + ra * math.sin(-a):.1f} A{ra},{ra} 0 0,1 {fx + ra * math.cos(a):.1f},{fy + ra * math.sin(a):.1f}", "none", col, 1.2)
    f.note(fx + 5.0 * m + 60, fy + 4, "光の質は用具だけでは決まらず、\n用具と距離の組み合わせで決まる")
    return f


# ---------------------------------------------------------------- 図 5-2 用具
def fig_05_modifiers():
    f = fl.Figure(800, 560, "ライティング用具の断面と光の広がり方",
                  "扇の広さは光の広がり、色の濃さは効率の目安。反射アンブレラだけは傘に向けて光らせ、跳ね返った光を使う")
    cw, ch = 190, 225

    def head(x, y, facing=1):
        f.rect(x - 22, y - 12, 30, 24, BODY, INK, 1.1, 4)
        f.rect(x + 8 if facing > 0 else x - 26, y - 6, 4, 12, LIGHT, "none", 0)

    def caption(x, y, name, q, spread, eff):
        f.text(x, y, name, size=12.5, anchor="middle", weight="bold")
        f.text(x, y + 17, f"{q}　{spread}", size=11, anchor="middle", color=MUTED)
        f.text(x, y + 32, eff, size=11, anchor="middle", color=DIM)

    positions = [(30 + k * cw, 70) for k in range(4)] + [(30 + 95 + k * cw, 70 + ch + 20) for k in range(3)]
    for (x0, y0) in positions:
        f.panel(x0, y0, cw - 10, ch)
    cxs = [x0 + (cw - 10) / 2 for (x0, y0) in positions]
    cys = [y0 + 90 for (x0, y0) in positions]

    # 1 ソフトボックス
    x, y = cxs[0] - 40, cys[0]
    f.fan(x + 46, y, 38, 95, 0, opacity=0.22)
    head(x, y)
    f.path(f"M{x + 12},{y - 12} L{x + 46},{y - 40} L{x + 46},{y + 40} L{x + 12},{y + 12} Z", "#2d2d2d", INK, 1.1)
    f.line(x + 46, y - 40, x + 46, y + 40, "#fff", 4)
    f.line(x + 46, y - 40, x + 46, y + 40, INK, 1)
    f.text(x + 46, y + 56, "拡散布", size=10, anchor="middle", color=MUTED)
    caption(cxs[0], cys[0] + 85, "ソフトボックス", "柔らかい", "前方だけ", "効率 −2〜−3 段")

    # 2 透過アンブレラ
    x, y = cxs[1] - 40, cys[1]
    f.fan(x + 40, y, 80, 80, 0, opacity=0.16)
    f.fan(x + 40, y, 40, 40, 180, opacity=0.16)
    fl.umbrella_side(f, x + 40, y)
    f.text(x + 44, y + 58, "白い布を透過", size=10, anchor="middle", color=MUTED)
    caption(cxs[1], cys[1] + 85, "透過アンブレラ", "柔らかい", "四方に回る", "効率 −2〜−3 段")

    # 3 反射アンブレラ
    x, y = cxs[2] + 10, cys[2]
    f.fan(x + 44, y, 50, 110, 180, opacity=0.18)
    fl.umbrella_side(f, x + 40, y, deg=180, reflective=True)
    f.text(x + 40, y + 58, "内側で跳ね返す", size=10, anchor="middle", color=MUTED)
    caption(cxs[2], cys[2] + 85, "反射アンブレラ", "柔らかい", "透過より狭い", "効率 −2 段前後")

    # 4 標準リフレクター
    x, y = cxs[3] - 40, cys[3]
    f.fan(x + 30, y, 30, 100, 0, opacity=0.34)
    head(x, y)
    f.path(f"M{x + 8},{y - 10} L{x + 30},{y - 22} L{x + 30},{y + 22} L{x + 8},{y + 10} Z", "#e0e0e0", INK, 1.2)
    f.text(x + 30, y + 44, "金属の皿", size=10, anchor="middle", color=MUTED)
    caption(cxs[3], cys[3] + 85, "標準リフレクター", "硬い", "前方 60 度ほど", "効率 基準（0 段）")

    # 5 グリッド
    x, y = cxs[4] - 40, cys[4]
    f.fan(x + 36, y, 15, 105, 0, opacity=0.30)
    head(x, y)
    f.path(f"M{x + 8},{y - 10} L{x + 30},{y - 22} L{x + 30},{y + 22} L{x + 8},{y + 10} Z", "#e0e0e0", INK, 1.2)
    for yy in range(-20, 21, 5):
        f.line(x + 30, y + yy, x + 38, y + yy, INK, 1)
    f.rect(x + 30, y - 22, 8, 44, "none", INK, 1.2)
    f.text(x + 34, y + 44, "格子", size=10, anchor="middle", color=MUTED)
    caption(cxs[4], cys[4] + 85, "リフレクター＋グリッド", "硬い", "20〜40 度に絞る", "効率 −1 段前後")

    # 6 白レフ
    x, y = cxs[5], cys[5]
    f.arrow(x - 70, y - 60, x + 30, y + 10, LIGHT, 1.8)
    fl.board_side(f, x + 34, y + 5, 90, "white", w=8)
    f.fan(x + 30, y + 10, 45, 70, 200, opacity=0.14)
    f.line(x + 30, y + 10, x - 40, y + 40, LIGHT, 1.4, "4 3", arrow=True)
    f.text(x - 40, y - 62, "キーの光", size=10, color=MUTED)
    f.text(x - 45, y + 60, "弱く広い反射光", size=10, color=MUTED)
    caption(cxs[5], cys[5] + 85, "白レフ板", "柔らかい", "反射なので弱い", "フィルに使う")

    # 7 黒レフ
    x, y = cxs[6], cys[6]
    f.arrow(x - 70, y - 60, x + 30, y + 10, LIGHT, 1.8)
    fl.board_side(f, x + 34, y + 5, 90, "black", w=8)
    f.line(x + 30, y + 10, x - 30, y + 36, MUTED, 1.2, "3 3")
    f.line(x - 12, y + 14, x + 2, y + 34, "#c33", 1.6)
    f.line(x + 2, y + 14, x - 12, y + 34, "#c33", 1.6)
    f.text(x - 40, y - 62, "回り込む光", size=10, color=MUTED)
    f.text(x - 50, y + 60, "反射しない（光を引く）", size=10, color=MUTED)
    caption(cxs[6], cys[6] + 85, "黒レフ板", "（光を引く）", "回り込みを止める", "影を濃くする")
    return f


# ---------------------------------------------------------------- 図 5-3 方向と顔
def fig_05_direction_faces():
    f = fl.Figure(800, 400, "光の方向で変わる鼻の影とキャッチライト", "ライトはカメラから見て左側に置いた。矢印は光の向き")
    cells = [
        ("正面", "front", "uc", "影は後ろに落ちる。平坦"),
        ("斜め前 45 度", "loop", "ul", "鼻の影が反対の頬へ。立体感"),
        ("サイド 90 度", "split", "l-only", "顔の半分が影。質感が出る"),
        ("逆光 45 度", "back", None, "顔は影。輪郭に光の縁"),
        ("トップ", "top", None, "目の窪みと鼻の下、顎の下に影"),
    ]
    for k, (name, sh, catch, note) in enumerate(cells):
        cx, cy = 100 + k * 150, 190
        f.panel(cx - 70, cy - 110, 140, 270, name, title_size=13)
        if sh == "back":
            ax, ay = cx - 44, cy - 70
            f.arrow(ax - 8, ay - 8, ax + 22, ay + 22, LIGHT, 2.2)
            f.light_glyph(ax - 14, ay - 14, r=6)
        elif sh == "top":
            f.light_glyph(cx, cy - 74, r=6)
            f.arrow(cx, cy - 64, cx, cy - 46, LIGHT, 2.2)
        elif sh == "front":
            f.light_glyph(cx, cy - 74, r=6)
            f.text(cx + 16, cy - 70, "カメラの真上から", size=9, color=MUTED)
        elif sh == "split":
            f.light_glyph(cx - 58, cy - 10, r=6)
            f.arrow(cx - 50, cy - 10, cx - 34, cy - 10, LIGHT, 2.2)
        else:
            f.light_glyph(cx - 54, cy - 60, r=6)
            f.arrow(cx - 46, cy - 52, cx - 30, cy - 36, LIGHT, 2.2)
        fl.face(f, cx, cy + 10, s=0.72, shadow=sh, catch=catch, rim="left" if sh == "back" else None, dark=0.36)
        f.text(cx, cy + 122, note, size=10.5, anchor="middle", color=MUTED)
    return f


# ---------------------------------------------------------------- 図 6-1 四つの型
def fig_06_patterns():
    f = fl.Figure(800, 470, "鼻の影で見分ける四つの型",
                  "上は正面から見た顔、下はカメラから見たライトの角度と高さ。ライトはカメラから見て左側")
    cells = [
        ("ループ", "loop", "ul", 40, "30〜45 度", "顔より少し上", "鼻の影は小さな輪。頬の影とつながらない"),
        ("レンブラント", "rembrandt", "ul", 55, "45〜60 度", "顔よりかなり上", "影側の頬に逆三角形の光が残る"),
        ("バタフライ", "butterfly", "uc", 0, "0 度（正面）", "顔よりかなり上", "鼻の下に蝶の形の影"),
        ("スプリット", "split", "l-only", 90, "90 度（真横）", "顔と同じ", "顔の中心線で明暗が分かれる"),
    ]
    for k, (name, sh, catch, ang, ang_t, h_t, note) in enumerate(cells):
        cx = 115 + k * 190
        f.panel(cx - 88, 70, 176, 380, name, title_size=14)
        fl.face(f, cx, 175, s=0.78, shadow=sh, catch=catch, dark=0.36)
        f.text(cx, 268, note, size=10, anchor="middle", color=MUTED)
        fl.mini_topview(f, cx - 30, 340, ang, r=40, label=ang_t)
        hx = cx + 52
        f.line(hx - 16, 350, hx + 16, 350, MUTED, 1)
        f.circle(hx, 350, 5, SKIN, INK, 1)
        hy = {"顔より少し上": 332, "顔よりかなり上": 316, "顔と同じ": 350}[h_t]
        f.rect(hx + 14, hy - 6, 8, 12, "#f7f7f7", INK, 1)
        f.rect(hx + 12, hy - 6, 2.5, 12, LIGHT, "none", 0)
        f.line(hx + 12, hy, hx + 5, 350 - (350 - hy) * 0.15, LIGHT, 1, "2 2")
        f.text(hx + 2, 388, h_t, size=10.5, anchor="middle", color=MUTED)
        f.text(hx + 2, 402, "（横から見た高さ）", size=9, anchor="middle", color=MUTED)
    return f


# ---------------------------------------------------------------- 図 6-2 ブロードとショート
def fig_06_broad_short():
    f = fl.Figure(800, 400, "ブロードライティングとショートライティング",
                  "被写体はカメラから見て右へ顔を振っている。左（耳が見える側）が広く見える側、右が狭く見える側")
    panels = [
        ("ブロードライティング", "broad", 45, "ul", "広く見える側にキーが当たる。\n顔が大きく、平坦に見えやすい"),
        ("ショートライティング", "short", -45, "ur", "狭く見える側にキーが当たる。\n輪郭が引き締まり、立体感が出る"),
    ]
    for k, (name, sh, ang, catch, note) in enumerate(panels):
        x0 = 30 + k * 380
        f.panel(x0, 70, 360, 300, name, title_size=14)
        fl.face(f, x0 + 110, 190, s=0.9, shadow=sh, catch=catch, turn=8, ear="left", dark=0.36)
        fl.mini_topview(f, x0 + 270, 190, ang, r=48, head_turn=-30)
        f.text(x0 + 270, 262, "上から見た配置", size=10.5, anchor="middle", color=MUTED)
        f.text(x0 + 270, 276, "（顔は右へ 30 度）", size=10.5, anchor="middle", color=MUTED)
        f.text(x0 + 180, 320, note, size=11.5, anchor="middle")
    f.note(24, 388, "ライトを動かさなくても、顔を反対側へ振ってもらうだけで二つは入れ替わる")
    return f


FIGURES = {
    "fig-04-monoblock": fig_04_monoblock,
    "fig-04-trigger": fig_04_trigger,
    "fig-04-inverse-square": fig_04_inverse_square,
    "fig-05-hard-soft": fig_05_hard_soft,
    "fig-05-modifiers": fig_05_modifiers,
    "fig-05-direction-faces": fig_05_direction_faces,
    "fig-06-patterns": fig_06_patterns,
    "fig-06-broad-short": fig_06_broad_short,
}
