"""第 1〜3 章のイラスト。scripts/render-figures.py studio-photography で docs/studio-photography/img/ に書き出す。"""
import math

import figlib as fl
from figlib import INK, MUTED, LIGHT, ACCENT, DIM, SKIN, CLOTH, BLACK, FLOOR, BODY, CAMERA_BODY, LENS


# ================================================================ 図 1-1 機材の一覧
def fig_01_equipment():
    f = fl.Figure(760, 440, "教材で使う機材", "光を出すもの、光の形を変えるもの、支えるもの、撮るもの")

    def camera(cx, cy):
        fl.trigger_on_camera(f, cx + 8, cy + 8, 1.15)

    def monoblock(cx, cy):
        fl.monoblock_side(f, cx - 18, cy - 4, 0, 0.45, cable=False)
        fl.rays(f, cx + 54, cy - 4, 0, 26, (-24, 0, 24))
        f.line(cx - 18, cy + 21, cx - 18, cy + 44, INK, 2)

    def stand_and_bag(cx, cy):
        fl.stand(f, cx, cy - 52, cy + 34, detail=True, spread=36)
        fl.sandbag(f, cx - 28, cy + 32, 16)

    def softbox(cx, cy):
        fl.softbox_side(f, cx + 12, cy - 4, 0, 92, 60)
        fl.rays(f, cx + 18, cy - 4, 0, 26, (-30, 0, 30))

    def umbrella(cx, cy):
        fl.umbrella_side(f, cx + 8, cy - 4, 0, reflective=False, r=44)
        fl.rays(f, cx + 34, cy - 4, 0, 26, (-30, 0, 30))

    def reflector(cx, cy):
        fl.reflector_side(f, cx - 8, cy - 4, 0, grid=True, s=2.1)
        fl.rays(f, cx + 26, cy - 4, 0, 30, (-8, 0, 8))

    def white_board(cx, cy):
        fl.board_side(f, cx + 14, cy - 8, 96, "white", -4, 8)
        for k, off in enumerate((-26, -2, 22)):
            f.line(cx - 46, cy - 8 + off - 8, cx + 6, cy - 8 + off, LIGHT, 1.4)
            f.line(cx + 6, cy - 8 + off, cx - 40, cy - 8 + off + 18, LIGHT, 1.2, "3 2")
        f.line(cx + 14, cy + 40, cx + 24, cy + 50, INK, 1.2)

    def black_board(cx, cy):
        fl.board_side(f, cx + 14, cy - 8, 96, "black", -4, 8)
        for off in (-26, -2, 22):
            f.line(cx - 50, cy - 8 + off - 8, cx + 6, cy - 8 + off, LIGHT, 1.4)
        f.line(cx + 14, cy + 40, cx + 24, cy + 50, INK, 1.2)

    cards = [
        ("カメラとトリガー", ["EOS R10 のホットシューに", "XPro II-C を付けて発光させる"], camera),
        ("モノブロックストロボ", ["閃光を出す。出力は 1/1〜1/16", "モデリングランプで向きを確かめる"], monoblock),
        ("スタンドとサンドバッグ", ["ストロボを持ち上げて固定する", "サンドバッグは転倒を防ぐ重り"], stand_and_bag),
        ("ソフトボックス", ["光源を大きくして柔らかくする", "教材では 60×90cm を使う"], softbox),
        ("アンブレラ", ["透過か反射で光を広げて柔らかくする", "ソフトボックスより広く回る"], umbrella),
        ("標準リフレクターとグリッド", ["光を狭い範囲に集める", "硬い光や背景専用の光を作る"], reflector),
        ("白レフ板", ["光を反射して影を薄める", "被写体から 1m でキーの 2 段下"], white_board),
        ("黒レフ板（フラッグ）", ["光を吸って影を締める", "余計な光を遮る板としても使う"], black_board),
    ]
    for k, (title, lines, draw) in enumerate(cards):
        x = 20 + (k % 4) * 180
        y = 70 + (k // 4) * 180
        f.card(x, y, title, lines, draw)
    return f


# ================================================================ 図 1-2 スタンドの立て方と安全
def fig_01_stand_safety():
    f = fl.Figure(760, 500, "ライトスタンドの立て方と安全（横から見た図）")
    floor = 420
    f.rect(24, floor, 470, 30, FLOOR, "none", 0)
    f.line(24, floor, 494, floor, INK, 1.4)
    f.text(30, 440, "床", size=11, color=MUTED)

    sx = 300
    fl.stand(f, sx, 140, floor, detail=True, spread=110)
    # ソフトボックス付きのヘッド（左下へ 20 度向ける）。発光面の中心から見て頭がスタンドの上に来る位置に置く
    deg = 160
    depth = 56
    hx, hy = sx, 128
    ang = math.radians(deg)
    fx = hx - (-(depth + 10)) * math.cos(ang)
    fy = hy - (-(depth + 10)) * math.sin(ang)
    fl.softbox_side(f, fx, fy, deg, 110, depth)
    # 本体（頭の後ろの箱）とモデリングランプの熱
    f.add(f'<g transform="translate({hx},{hy}) rotate({deg - 180})">'
          f'<rect x="-8" y="-16" width="60" height="32" rx="6" fill="{BODY}" stroke="{INK}" stroke-width="1.2"/>'
          f'<rect x="20" y="-10" width="22" height="8" fill="#cfe7cf" stroke="{INK}" stroke-width="0.8"/></g>')
    for dx in (-10, -2, 6):
        f.path(f"M{hx - 40 + dx},{hy - 28} q4,-8 0,-14 q-4,-6 0,-12", "none", DIM, 1.4)
    # 電源ケーブル：ヘッドから支柱に一巻きして床へ、床はテープで留める
    f.path(f"M{sx + 40},{hy + 8} q20,10 14,40 q-10,20 -30,40 L{sx + 4},200 L{sx + 4},{floor} L{sx + 120},{floor} L{sx + 170},{floor}", "none", INK, 1.6)
    f.path(f"M{sx + 4},200 q-12,10 0,20 q12,10 0,20", "none", INK, 1.6)
    for tx in (sx + 40, sx + 120):
        f.rect(tx, floor - 6, 22, 12, LIGHT, "none", 0, opacity=0.8)
    fl.sandbag(f, sx - 72, floor - 2, 24)

    # 番号と引き出し線
    f.callout(1, 230, 470, to=(sx, floor + 16))
    f.callout(2, 190, 392, to=(sx - 78, 404))
    f.callout(3, 380, 300, to=(sx + 6, 300))
    f.callout(4, 400, 64, to=(hx - 42, hy - 44))
    f.callout(5, 360, 176, to=(sx + 20, 146))

    f.callout_notes(520, 90, [
        ("脚を最大まで広げ、支柱を垂直に立てる", ["脚をすぼめたままだと重心が高く倒れやすい"]),
        ("サンドバッグはソフトボックス側の脚に", ["重い用具が張り出す側を押さえる", "配置を変えるたびに載せ直す"]),
        ("ケーブルは支柱に沿わせて床へ下ろす", ["支柱に一巻きして遊びを作り、", "人が通る床は養生テープで留める"]),
        ("モデリングランプ（150W）は熱くなる", ["撤収の前に切って冷ます。", "用具を外すときは布を使う"]),
        ("角度を決めたら締めネジを確実に締める", ["緩いとヘッドが下を向き、", "重心が動いて倒れる原因になる"]),
    ])
    return f


# ================================================================ 図 2-1 段の物差し
def fig_02_stops():
    f = fl.Figure(760, 400, "段（stop）の物差し", "隣り合う目盛りの差は、どの行でも光の量が 2 倍または半分（1 段）")
    x0, step = 180, 90
    f.rect(315, 104, 90, 236, LIGHT, "none", 0, 4, opacity=0.12)
    f.text(360, 355, "教材の基準（f/8、1/200 秒、ISO 100、出力 1/4）", size=11, anchor="middle", color=DIM)
    mid = f.marker(MUTED, 7)
    f.add(f'<line x1="180" y1="78" x2="720" y2="78" stroke="{MUTED}" stroke-width="1.2" marker-start="url(#{mid})" marker-end="url(#{mid})"/>')
    f.text(180, 98, "← 明るい（光が多い）", size=11, color=MUTED)
    f.text(720, 98, "暗い（光が少ない）→", size=11, anchor="end", color=MUTED)
    for k, s in enumerate(["2 段明るい", "1 段明るい", "基準", "1 段暗い", "2 段暗い", "3 段暗い"]):
        f.text(x0 + k * step, 120, s, size=11, anchor="middle", color=MUTED)

    rows = [
        ("絞り", "1.4 倍ずつ", ["f/4", "f/5.6", "f/8", "f/11", "f/16", "f/22"]),
        ("シャッター速度", "2 倍ずつ", ["1/50", "1/100", "1/200", "1/400", "1/800", "1/1600"]),
        ("ISO", "2 倍ずつ", ["400", "200", "100", None, None, None]),
        ("ストロボ出力", "2 倍ずつ", ["1/1", "1/2", "1/4", "1/8", "1/16", None]),
    ]
    for r, (name, ratio, values) in enumerate(rows):
        y = 148 + r * 55
        f.text(140, y + 2, name, size=13, anchor="end", weight="bold")
        f.text(140, y + 19, ratio, size=11, anchor="end", color=MUTED)
        f.scale_row(x0, y, step, values, bold_index=2, line_to=700)
    f.text(450, 258, "（R10 にはない）", size=10, anchor="middle", color=MUTED)
    f.text(630, 313, "1/32（SK400II にはない）", size=10, anchor="middle", color=MUTED)
    f.text(24, 382, "例：絞りを f/8 から f/4 に 2 段開けたら、出力を 1/4 から 1/16 に 2 段落とせば同じ明るさになる。", size=11, color=MUTED)
    return f


# ================================================================ 図 2-2 閃光とシャッター
def fig_02_flash_and_shutter():
    f = fl.Figure(760, 430, "シャッター速度はストロボ光に効かず、定常光にだけ効く", "横軸は時間。色の付いた面積がセンサーに届く光の量")
    f.rect(520, 40, 14, 10, LIGHT, "none", 0)
    f.text(540, 49, "ストロボ光（閃光 1/1000 秒前後）", size=11)
    f.rect(520, 56, 14, 10, CLOTH, "none", 0)
    f.text(540, 65, "定常光（モデリングランプや部屋の照明）", size=11)

    def panel(oy, heading, open_w, open_label, notes):
        f.text(24, oy + 20, heading, size=13, weight="bold")
        base = oy + 130
        f.axes(100, base, 620, 90, [(100, "0"), (220, "5ms"), (340, "10ms")], x_label="時間", y_label="光の強さ")
        f.rect(100, base - 70, open_w, 70, "none", INK, 1, dash="4 3")
        f.text(100 + open_w / 2, base - 74, open_label, size=11, anchor="middle")
        f.rect(100, base - 12, open_w, 12, CLOTH, "none", 0)
        f.path(f"M112,{base} L116,{base - 60} L120,{base - 66} L124,{base - 60} L136,{base} Z", LIGHT, "none", 0)
        for (nx, ny, s, color) in notes:
            f.text(nx, oy + ny, s, size=11, color=color)

    panel(80, "シャッター速度 1/200 秒（5ms）", 120, "シャッターが開いている", [
        (250, 90, "閃光は 1ms ほどで出きる。", INK),
        (250, 106, "帯の残りの時間には、ストロボの光はない", INK),
    ])
    panel(250, "シャッター速度 1/100 秒（10ms）に遅くすると", 240, "シャッターが開いている（2 倍の時間）", [
        (370, 84, "ストロボ光の面積は同じ → 肌の明るさは変わらない", INK),
        (370, 102, "定常光の面積は 2 倍 → 部屋の光だけが 1 段明るく写る", INK),
        (370, 120, "ISO 100、f/8 では定常光の帯はほぼゼロで、真っ黒に写る", MUTED),
    ])
    return f


# ================================================================ 図 2-3 ヒストグラム
def fig_02_histogram():
    f = fl.Figure(760, 300, "ヒストグラムで見るもの", "左が黒、右が白。見るのは肌の山の位置と、左右の端に張り付いていないか")
    w, h, y = 220, 130, 94
    # 適正
    x = 30
    f.histogram(x, y, w, h, [(0.09, 0.03), (0.23, 0.12), (0.36, 0.2), (0.5, 0.34), (0.59, 0.54), (0.66, 0.65), (0.73, 0.57), (0.8, 0.34), (0.89, 0.11), (1, 0.02)],
              title="適正", caption="右端にも左端にも山がない")
    f.line(x + 152, y + 38, x + 152, y + 16, DIM, 1)
    f.text(x + 152, y + 12, "肌の山（中央から右寄り）", size=11, anchor="middle", color=DIM)
    # 白飛び
    x = 270
    f.histogram(x, y, w, h, [(0.18, 0.02), (0.41, 0.11), (0.59, 0.29), (0.75, 0.54), (0.86, 0.65), (0.93, 0.57), (0.96, 0.42), (0.97, 0.72), (1, 0.95)],
              title="明るすぎる（白飛び）", caption="肌が右端に届き、情報が失われている")
    f.rect(x + 213, y + 6, 7, h - 6, DIM, "none", 0, opacity=0.8)
    f.line(x + 216, y + 4, x + 200, y + 16, DIM, 1)
    f.text(x + 196, y + 16, "右端に張り付く", size=11, anchor="end", color=DIM)
    # 背景を飛ばしたとき
    x = 510
    f.histogram(x, y, w, h, [(0.09, 0.03), (0.23, 0.14), (0.36, 0.25), (0.48, 0.42), (0.57, 0.51), (0.64, 0.45), (0.73, 0.25), (0.84, 0.08), (0.93, 0.03), (0.96, 0.03), (0.96, 0.88), (1, 0.95)],
              title="背景を白く飛ばしたとき", caption="右端の山は背景。人物の山だけを見る")
    f.rect(x + 211, y + 6, 9, h - 6, LIGHT, "none", 0, opacity=0.9)
    f.line(x + 128, y + 56, x + 128, y + 16, DIM, 1)
    f.text(x + 128, y + 12, "人物の山", size=11, anchor="middle", color=DIM)
    f.line(x + 214, y + 10, x + 196, y + 32, DIM, 1)
    f.text(x + 194, y + 42, "背景（意図した白）", size=11, anchor="end", color=DIM)
    return f


# ================================================================ 図 3-1 シャッター方式と同調速度
def fig_03_sync_and_shutter_modes():
    f = fl.Figure(760, 560, "シャッター方式と同調速度",
                  "四角はセンサー。ストロボは一瞬しか光らないので、その瞬間にセンサー全体が開いている必要がある")
    hatch = f.hatch()
    open_fill = "#fff4cf"

    # ---- 上段: 三つの方式 ----
    ox, oy = 40, 70
    f.text(ox, oy + 14, "三つのシャッター方式（露光の始まりと終わりを何が担うか）", size=13, weight="bold")

    def mode(x, y, name, ok, note, top_fill, top_label, top_color, bottom):
        fl.sensor_frame(f, x, y, 150, 100, 26, 20, open_fill, top_fill=top_fill)
        if not bottom:
            f.rect(x, y + 80, 150, 20, open_fill, "none", 0)
        f.text(x + 75, y + 18, top_label, size=10, anchor="middle", color=top_color)
        if bottom:
            f.text(x + 75, y + 94, "後幕（メカ）", size=10, anchor="middle", color="#fff")
        f.arrow(x + 75, y + 30, x + 75, y + 74, ACCENT, 1.2)
        f.text(x + 75, y + 120, name, size=12, anchor="middle", weight="bold")
        f.text(x + 75, y + 136, "ストロボ可" if ok else "ストロボ不可", size=11, anchor="middle",
               color=INK if ok else DIM, weight="normal" if ok else "bold")
        f.text(x + 75, y + 151, note, size=11, anchor="middle", color=MUTED)

    mode(ox, oy + 30, "メカシャッター", True, "同調速度 1/250 秒", BODY, "先幕（メカ）", "#fff", True)
    mode(ox + 200, oy + 30, "電子先幕", True, "同調速度 1/250 秒", hatch, "先幕（電子的なリセット）", INK, True)
    # 電子シャッター
    x, y = ox + 400, oy + 30
    f.rect(x, y, 150, 100, "#f3f3f3", INK, 1.2)
    f.rect(x, y, 150, 14, hatch, MUTED, 0.8)
    f.rect(x, y + 34, 150, 14, open_fill, MUTED, 0.8)
    f.text(x + 75, y + 28, "読み出しが上から下へ順に進む", size=10, anchor="middle")
    f.text(x + 75, y + 70, "全体が同時に開く瞬間がない", size=10, anchor="middle", color=MUTED)
    f.arrow(x + 75, y + 78, x + 75, y + 94, ACCENT, 1.2)
    f.text(x + 75, y + 120, "電子シャッター", size=12, anchor="middle", weight="bold")
    f.text(x + 75, y + 136, "ストロボ不可", size=11, anchor="middle", color=DIM, weight="bold")
    f.text(x + 75, y + 151, "発光しない", size=11, anchor="middle", color=MUTED)
    f.text(ox + 580, oy + 60, "薄い黄色：\n露光している面", size=11, color=MUTED)
    f.text(ox + 580, oy + 100, "濃い灰色：\n幕が覆っている面", size=11, color=MUTED)

    # ---- 下段: 同調速度 ----
    ox, oy = 40, 270
    f.text(ox, oy + 14, "同調速度より速いと黒い帯が出る（メカシャッターの例）", size=13, weight="bold")
    x, y = ox, oy + 30
    f.text(x + 75, y + 14, "1/200 秒", size=12, anchor="middle")
    fl.sensor_frame(f, x, y + 24, 150, 100, 6, 6, open_fill)
    f.text(x + 75, y + 78, "先幕が開ききり、\n後幕はまだ閉じ始めない", size=11, anchor="middle")
    f.text(x + 75, y + 146, "この瞬間にストロボが光る", size=11, anchor="middle")
    f.text(x + 75, y + 162, "→ 全面が写る", size=11, anchor="middle", color=ACCENT)

    x = ox + 200
    f.text(x + 75, y + 14, "1/500 秒", size=12, anchor="middle", weight="bold")
    fl.sensor_frame(f, x, y + 24, 150, 100, 40, 30, open_fill)
    f.text(x + 75, y + 48, "後幕がもう閉じ始めている", size=10, anchor="middle", color="#fff")
    f.text(x + 75, y + 83, "スリットの部分だけ露光", size=10, anchor="middle")
    f.text(x + 75, y + 113, "先幕がまだ開ききらない", size=10, anchor="middle", color="#fff")
    f.text(x + 75, y + 146, "この瞬間にストロボが光る", size=11, anchor="middle")
    f.text(x + 75, y + 162, "→ スリットだけ写る", size=11, anchor="middle", color=DIM)

    x = ox + 420
    f.text(x + 75, y + 14, "写真（1/500 秒）", size=12, anchor="middle")
    f.rect(x, y + 24, 150, 100, BLACK, INK, 1.2)
    f.rect(x, y + 64, 150, 30, SKIN, "none", 0)
    f.text(x + 75, y + 46, "黒い帯", size=10, anchor="middle", color="#fff")
    f.text(x + 75, y + 112, "黒い帯", size=10, anchor="middle", color="#fff")
    f.text(x + 75, y + 83, "被写体が写る部分", size=10, anchor="middle")
    f.text(x + 75, y + 146, "同調速度 1/250 秒でも、\n無線の遅れで端に細い帯が出うる", size=11, anchor="middle")
    f.text(ox + 600, oy + 90, "教材の基準は", size=11)
    f.text(ox + 600, oy + 106, "1/200 秒", size=13, color=ACCENT, weight="bold")
    f.text(ox + 600, oy + 124, "同調速度に対する余裕", size=11, color=MUTED)
    return f


# ================================================================ 図 3-2 カメラの操作部
def fig_03_camera_top():
    f = fl.Figure(760, 500, "この教材で触るカメラの操作部（模式図）", "位置関係だけを示す。実機の配置は取扱説明書で確かめる")

    # ---- 上から見た図 ----
    ox, oy = 60, 80
    f.text(ox + 130, oy, "上から見た図", size=13, anchor="middle", weight="bold")
    f.rect(ox + 90, oy + 20, 80, 60, "#444", INK, 1.2)
    f.rect(ox + 86, oy + 14, 88, 8, LENS, INK, 1)
    f.text(ox + 130, oy + 56, "レンズ", size=10, anchor="middle", color="#fff")
    f.rect(ox + 20, oy + 80, 220, 70, BODY, INK, 1.2, 6)
    # ホットシューとトリガー
    f.rect(ox + 112, oy + 86, 36, 10, INK, "none", 0)
    f.rect(ox + 106, oy + 98, 48, 40, "#e8e8e8", INK, 1.2, 3)
    f.rect(ox + 112, oy + 104, 36, 16, "#cfe7cf", INK, 0.8)
    f.text(ox + 130, oy + 116, "CH1 A 1/4", size=8, anchor="middle")
    for k, col in enumerate(("#ddd", "#ddd", "#e8a0a0")):
        f.circle(ox + 118 + k * 12, oy + 130, 3, col, INK, 0.6)
    # モードダイヤル
    f.circle(ox + 205, oy + 112, 20, "#777", INK, 1.2)
    f.text(ox + 205, oy + 117, "M", size=13, anchor="middle", color="#fff", weight="bold")
    f.circle(ox + 205, oy + 94, 2, LIGHT, "none", 0)
    # シャッターボタンと電子ダイヤル
    f.circle(ox + 44, oy + 100, 8, "#ddd", INK, 1)
    f.rect(ox + 62, oy + 96, 30, 9, "#ddd", INK, 0.8, 4)
    for k in range(4):
        f.line(ox + 68 + k * 6, oy + 97, ox + 68 + k * 6, oy + 104, INK, 0.8)
    f.callout(1, ox + 250, oy + 70, to=(ox + 222, oy + 100))
    f.callout(2, ox + 130, oy + 170, to=(ox + 130, oy + 140))
    f.callout(3, ox + 10, oy + 130, to=(ox + 40, oy + 108))
    f.text(ox + 130, oy + 200, "↑ 被写体側", size=11, anchor="middle", color=MUTED)

    # ---- 背面 ----
    ox, oy = 340, 80
    f.text(ox + 120, oy, "背面", size=13, anchor="middle", weight="bold")
    f.rect(ox + 88, oy + 12, 64, 24, "#444", INK, 1.2, 4)
    f.rect(ox + 104, oy + 18, 32, 12, BLACK, "none", 0, 2)
    f.rect(ox, oy + 36, 240, 150, BODY, INK, 1.2, 6)
    f.rect(ox + 12, oy + 52, 140, 110, BLACK, INK, 1, 3)
    f.rect(ox + 20, oy + 60, 124, 80, "#3a3a3a", "none", 0)
    f.path(f"M{ox + 28},{oy + 132} L{ox + 40},{oy + 128} L{ox + 56},{oy + 118} L{ox + 72},{oy + 104} L{ox + 86},{oy + 98} "
           f"L{ox + 98},{oy + 106} L{ox + 112},{oy + 122} L{ox + 128},{oy + 130} L{ox + 136},{oy + 132} Z", CLOTH, "none", 0)
    f.text(ox + 82, oy + 152, "ヒストグラム表示", size=8, anchor="middle", color="#ddd")
    f.circle(ox + 200, oy + 100, 20, "#777", INK, 1.2)
    f.circle(ox + 200, oy + 100, 7, "#ddd", INK, 0.8)
    for (bx, by, label) in ((164, 52, "MENU"), (200, 52, "INFO"), (164, 140, "再生"), (200, 140, "拡大")):
        f.rect(ox + bx, oy + by, 26, 12, "#ddd", "none", 0, 2)
        f.text(ox + bx + 13, oy + by + 9, label, size=7, anchor="middle")
    f.callout(4, ox + 256, oy + 30, to=(ox + 222, oy + 54))
    f.callout(5, ox + 256, oy + 176, to=(ox + 226, oy + 152))
    f.callout(6, ox + 82, oy + 200, to=(ox + 82, oy + 164))

    f.callout_list(40, 316, [
        "モードダイヤルを M にする",
        "ホットシューにトリガー（XPro II-C）を付けて電源を入れる",
        "シャッターボタンと電子ダイヤルで、絞り、シャッター速度、ISO を基準値に合わせる",
        "MENU から露出Simulation、シャッター方式、ホワイトバランス、記録画質、AF を設定する",
        "再生と拡大で、ヒストグラムとピントを確かめる",
        "背面モニター。明るさの判断は見た目ではなくヒストグラムで行う",
    ], r=9, step=26, size=12)
    return f


FIGURES = {
    "fig-01-equipment": fig_01_equipment,
    "fig-01-stand-safety": fig_01_stand_safety,
    "fig-02-stops": fig_02_stops,
    "fig-02-flash-and-shutter": fig_02_flash_and_shutter,
    "fig-02-histogram": fig_02_histogram,
    "fig-03-sync-and-shutter-modes": fig_03_sync_and_shutter_modes,
    "fig-03-camera-top": fig_03_camera_top,
}
