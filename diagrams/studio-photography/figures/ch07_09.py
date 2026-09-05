"""第 7〜9 章のイラスト。scripts/render-figures.py studio-photography で docs/studio-photography/img/ に書き出す。"""
import math

import figlib as fl
from figlib import INK, MUTED, LIGHT, ACCENT, DIM, SKIN, CLOTH, HAIR, WALL, BLACK, FLOOR, BODY, CAMERA_BODY


# ---------------------------------------------------------------- 共通の小さな補助
def portrait(f, cx, cy, s=1.0, shade=0.5, mode="key", rim=False):
    """旧スクリプトの face(mode, shade, rim) を figlib.face に対応づける。"""
    shadow = {"key": "gradient", "flat": "even", "dark": "dark"}[mode]
    fl.face(f, cx, cy, s=s, shadow=shadow, dark=shade, rim="right" if rim else None,
            catch=None if mode == "dark" else "ul")


# ================================================================ fig-07-build-order
def fig_07_build_order():
    W, H = 800, 400
    f = fl.Figure(W, H, "一灯ずつ点けて足す手順", "上段は上から見た配置（点いている灯だけに色）、下段は顔の見え方")
    panels = [
        ("段階 1", "キーだけ", dict(key=True, fill=False, rim=False), dict(mode="key", shade=0.62, rim=False)),
        ("段階 2", "フィルだけ", dict(key=False, fill=True, rim=False), dict(mode="flat", shade=0.42, rim=False)),
        ("段階 3", "キー＋フィル", dict(key=True, fill=True, rim=False), dict(mode="key", shade=0.36, rim=False)),
        ("段階 4", "リムだけ", dict(key=False, fill=False, rim=True), dict(mode="dark", shade=0.78, rim=True)),
        ("段階 5", "全部を点ける", dict(key=True, fill=True, rim=True), dict(mode="key", shade=0.36, rim=True)),
    ]
    notes = ["影の形と露出を決める", "影の方向が付かないか", "影側に階調が残るか", "縁だけに光、レンズに直射なし", "ヒストグラムで仕上がり確認"]
    pw, gap, left = 146, 8, 26
    for i, (step, name, scene, fc) in enumerate(panels):
        x = left + i * (pw + gap)
        f.text(x + pw / 2, 76, f"{step}　{name}", size=12.5, anchor="middle", weight="bold")
        fl.mini_scene(f, x, 86, pw, 112, **scene)
        portrait(f, x + pw / 2, 258, s=0.72, **fc)
        f.text(x + pw / 2, 358, notes[i], size=11, anchor="middle", color=MUTED)
        if i < 4:
            f.arrow(x + pw + 1, 150, x + pw + gap - 1, 150, MUTED, 1.2)
    f.text(W - 24, H - 14, "後の段階で気になっても、前の段階の灯は動かさない", size=11, anchor="end", color=MUTED)
    return f


# ================================================================ fig-07-ratio
def fig_07_ratio():
    W, H = 760, 360
    f = fl.Figure(W, H, "ライティング比を段差で表す", "キーは画面左上から。フィルの強さで影側（右）の明るさが変わる")
    cols = [
        ("段差 1", "2:1", 0.22, "f/8", "f/5.6", "影がごく薄く、顔が平ら"),
        ("段差 2", "4:1", 0.42, "f/8", "f/4", "階調が残り、立体感がある"),
        ("段差 3", "8:1", 0.62, "f/8", "f/2.8", "影が濃く、半分が沈む"),
        ("フィルなし", "", 0.88, "f/8", "ほぼ黒", "ローキー（第 9 章）"),
    ]
    cw, left = 176, 28
    for i, (name, ratio, shade, hi, lo, impression) in enumerate(cols):
        x = left + i * cw + cw / 2
        f.text(x, 78, name + (f"（{ratio}）" if ratio else ""), size=13, anchor="middle", weight="bold")
        portrait(f, x, 156, s=0.82, shade=shade, mode="key")
        # 明部と暗部の帯
        bx = x - 66
        f.rect(bx, 252, 60, 18, SKIN, INK, 1)
        f.rect(bx + 72, 252, 60, 18, SKIN, INK, 1)
        f.rect(bx + 72, 252, 60, 18, "#1e1a17", "none", 0, opacity=round(shade, 2))
        f.text(bx + 30, 285, f"明部 {hi}", size=11, anchor="middle", color=MUTED)
        f.text(bx + 102, 285, f"暗部 {lo}", size=11, anchor="middle", color=MUTED)
        f.text(x, 310, impression, size=11.5, anchor="middle")
    # キーの向き
    f.arrow(40, 100, 70, 118, LIGHT, 2)
    f.text(36, 96, "キー", size=11, color=DIM)
    f.text(W - 24, H - 14, "フィルの出力を 1 段下げるごとに段差が 1 増える。絞りとキーは動かさない", size=11, anchor="end", color=MUTED)
    return f


# ================================================================ fig-07-rim-flare
def fig_07_rim_flare():
    W, H = 780, 356
    f = fl.Figure(W, H, "リムライトの直射光とフレアの対策", "上から見た図。橙の線はリムの発光面からレンズへ向かう光")
    pw, gap, left = 230, 14, 26
    panels = [
        ("発光面がカメラから見える", "レンズに直射光が入り、\n黒が浮いてコントラストが落ちる",
         dict(key=True, fill=False, rim=True, show_fill=False, rim_pos=(0.62, 0.16), ray_to_camera="hit")),
        ("斜め後ろ 45 度に回し、グリッドで絞る", "発光面が身体の陰に入り、\n光は縁だけに当たる",
         dict(key=True, fill=False, rim=True, show_fill=False, rim_pos=(0.86, 0.22), rim_grid=True, ray_to_camera="blocked", ray_block=(0.56, 0.44))),
        ("フラッグで遮る", "灯とレンズの間に黒い板を立てる。\n被写体へ向かう光は遮らない",
         dict(key=True, fill=False, rim=True, show_fill=False, rim_pos=(0.80, 0.18), flag=(0.70, 0.50, 35), ray_to_camera="blocked", ray_block=(0.70, 0.50))),
    ]
    for i, (title, note, scene) in enumerate(panels):
        x = left + i * (pw + gap)
        f.text(x + pw / 2, 78, title, size=12.5, anchor="middle", weight="bold")
        fl.mini_scene(f, x, 90, pw, 180, **scene)
        f.text(x + pw / 2, 292, note, size=11, anchor="middle", color=MUTED)
    f.text(26, H - 14, "判定は「カメラの位置から灯の発光面が見えるか」で行う", size=11, color=MUTED)
    return f


# ================================================================ fig-08-cyc-section
def fig_08_cyc_section():
    W, H = 800, 440
    f = fl.Figure(W, H, "白ホリの断面と全身撮影の配置", "横から見た図。壁と床は R 面でつながり、境界線が写らない")
    M = 78  # px / m
    x_wall, y_floor, R = 70, 360, 70

    def X(m):
        return x_wall + m * M

    def Y(h):
        return y_floor - h * M

    fl.room_side(f, x_wall, y_floor, Y(3.5), W - 24, radius=R)
    # 壁面の明るさ（背景ライトで飛ぶ）と床の反射の範囲
    f.rect(x_wall, Y(3.2), 10, y_floor - R - Y(3.2), LIGHT, "none", 0, opacity=0.35)
    gid = f.uid("floorglow")
    f.add_def(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{LIGHT}" stop-opacity="0.4"/><stop offset="1" stop-color="{LIGHT}" stop-opacity="0"/></linearGradient>')
    f.rect(x_wall + R, y_floor - 8, X(2.6) - x_wall - R, 8, f"url(#{gid})", "none", 0)
    # 背景ライト（壁から 1.5m、高さ 1.2m、壁に向ける）
    bx, by = X(1.5), Y(1.2)
    fl.stand(f, bx, by, y_floor)
    ang = math.degrees(math.atan2(Y(2.0) - by, x_wall - bx))
    f.path(f"M{bx},{by} L{x_wall},{Y(3.3)} L{x_wall},{Y(0.3)} Z", LIGHT, "none", 0, opacity=0.16)
    fl.reflector_side(f, bx, by, ang)
    f.badge(bx + 22, by - 20, 2)
    # 被写体（壁から 2.5m、身長 1.7m）。足元の影はキーの反対側（壁側）へ落ちる
    px_ = X(2.5)
    fl.person_side(f, px_, y_floor, M=M)
    f.badge(px_ - 34, Y(1.75), 3)
    # キーライト（被写体の斜め前。横から見ると 1.5m 手前、中心は胸の高さ、少し見下ろす）
    kx, ky = X(4.0), Y(1.35)
    fl.stand(f, kx, ky, y_floor)
    ka = math.degrees(math.atan2(Y(1.2) - ky, px_ - kx))
    f.path(f"M{kx},{ky} L{px_ - 30},{Y(1.9)} L{px_ - 30},{Y(0.0)} Z", LIGHT, "none", 0, opacity=0.14)
    fl.softbox_side(f, kx - 14, ky, ka, face=76, depth=26)
    f.badge(kx + 26, ky - 44, 4)
    # 白レフ（被写体の反対側。横から見ると被写体の脇）
    fl.board_side(f, px_ + 43, Y(1.5) + 0.45 * M, 0.9 * M, "white")
    f.badge(px_ + 60, Y(1.55), 5)
    # カメラ（被写体から 3.3m、胸の高さ 1.2m、水平）
    cx, cy = X(5.8), Y(1.2)
    fl.camera_side(f, cx, cy, s=0.6, tripod_to=y_floor, facing=-1)
    f.line(cx - 26, cy, px_ + 20, cy, ACCENT, 1, "4 3")
    f.badge(cx + 4, cy - 26, 6)
    # R 面と床の番号
    f.badge(x_wall + 30, y_floor - 30, 1)
    f.badge(X(1.9), y_floor + 34, 7)
    # 寸法
    f.measure(x_wall, y_floor + 40, bx, y_floor + 40, "1.5m")
    f.measure(x_wall, y_floor + 62, px_, y_floor + 62, "2.5m")
    f.measure(px_, y_floor + 40, cx, y_floor + 40, "3.3m")
    # 凡例（番号の説明）
    items = ["R 面。踏まない", "背景ライト（壁から 1.5m、壁へ向けて 1/16）", "被写体（壁から 2.5m）",
             "キーライト（2.1m、中心は胸の高さ、1/2）", "白レフ（1m）", "カメラ（3.3m、胸の高さで水平）", "床の反射。壁に近いほど白く、離れると灰色"]
    f.callout_list(470, 80, items)
    f.text(x_wall + 6, Y(3.5) - 14, "壁", size=11, color=MUTED)
    return f


# ================================================================ fig-08-background-stops
def fig_08_background_stops():
    W, H = 800, 380
    f = fl.Figure(W, H, "背景ライトの明るさと背景の写り方", "被写体を f/8 で適正にしたまま、壁面の明るさだけを変えたとき")
    cols = [
        ("段差 0", "壁面 f/8", "#b9b9b9", "灰色に写る", False, False),
        ("＋1 段", "壁面 f/11", "#ffffff", "白く飛ぶ", False, False),
        ("＋1.5 段", "壁面 f/13", "#ffffff", "白く飛ぶ", False, False),
        ("＋2 段以上", "壁面 f/16〜", "#ffffff", "輪郭が溶け、黒が浮く", True, True),
    ]
    cw, left, fw, fh = 186, 30, 150, 150
    for i, (name, wall, bg, result, halo, flare) in enumerate(cols):
        x = left + i * cw
        f.text(x + fw / 2, 80, name, size=13, anchor="middle", weight="bold")
        f.text(x + fw / 2, 98, wall, size=11, anchor="middle", color=MUTED)
        y = 108
        f.rect(x, y, fw, fh, bg, INK, 1)
        cx, cy = x + fw / 2, y + 74
        if halo:
            f.add(f'<g filter="url(#blur)"><ellipse cx="{cx}" cy="{cy - 6}" rx="36" ry="44" fill="#fff" opacity="0.9"/>'
                  f'<path d="M{cx - 54},{y + fh} C{cx - 54},{cy + 50} {cx - 14},{cy + 38} {cx},{cy + 38} C{cx + 14},{cy + 38} {cx + 54},{cy + 50} {cx + 54},{y + fh} Z" fill="#fff" opacity="0.9"/></g>')
        # 顔は枠で切り抜き、肩が枠の外へ出ないようにする
        cid = f.uid("frame")
        f.add_def(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{fw}" height="{fh}"/></clipPath>')
        f.add(f'<g clip-path="url(#{cid})">')
        portrait(f, cx, cy, s=0.66, shade=0.36, mode="key")
        f.add('</g>')
        if halo:
            # 輪郭が溶ける表現：髪と肩の縁を白でにじませる
            f.add(f'<g filter="url(#blur)"><ellipse cx="{cx}" cy="{cy - 6}" rx="28" ry="32" fill="none" stroke="#fff" stroke-width="10" opacity="0.8"/></g>')
        if flare:
            f.rect(x, y, fw, fh, "#fff", "none", 0, opacity=0.28)
        f.text(x + fw / 2, y + fh + 22, result, size=12, anchor="middle")
    # 推奨範囲の括弧
    x1 = left + 1 * cw
    x2 = left + 2 * cw + fw
    f.path(f"M{x1},308 L{x1},316 L{x2},316 L{x2},308", "none", ACCENT, 1.5)
    f.text((x1 + x2) / 2, 334, "白飛びする最小限で止める（ハイライト警告が背景だけで点滅）", size=12, anchor="middle", color=ACCENT)
    f.text(left + 3 * cw + fw / 2, 334, "壁からの回り込みとフレア", size=11, anchor="middle", color=DIM)
    f.text(left + fw / 2, 334, "背景ライトなし", size=11, anchor="middle", color=MUTED)
    return f


# ================================================================ fig-09-paper-booth
def fig_09_paper_booth():
    W, H = 780, 420
    f = fl.Figure(W, H, "背景紙のブース", "横から見た図。紙は壁に沿って垂らし、床へ緩やかに延ばす")
    M = 80
    x_wall, y_floor = 90, 350

    def X(m):
        return x_wall + m * M

    def Y(h):
        return y_floor - h * M

    fl.room_side(f, x_wall, y_floor, Y(3.0), W - 24)
    # ブラケットとロール
    f.rect(x_wall, Y(2.75), 30, 6, BODY, "none", 0)
    f.circle(x_wall + 30, Y(2.6), 16, "#d9d4cc", INK, 1.2)
    f.circle(x_wall + 30, Y(2.6), 4, BODY, "none", 0)
    f.badge(x_wall + 30, Y(2.6) - 30, 1)
    # 紙：ロールの下から壁沿いに下り、床へ曲線で延びる
    px0 = x_wall + 44
    curve_r = 60
    f.path(f"M{px0},{Y(2.6)} L{px0},{y_floor - curve_r} Q{px0},{y_floor - 3} {px0 + curve_r},{y_floor - 3} L{X(1.5) + 44},{y_floor - 3}", "none", "#8c8c8c", 5)
    f.badge(px0 + 26, Y(1.7), 2)
    f.badge(X(0.9), y_floor - 24, 3)
    # 養生テープ
    tx = X(1.5) + 40
    f.rect(tx - 8, y_floor - 8, 16, 7, "#8ec5a0", INK, 0.8)
    f.badge(tx, y_floor - 26, 4)
    # 汚れと切る位置
    f.circle(X(1.2), y_floor - 3, 5, "#6b5a3e", "none", 0, opacity=0.7)
    f.line(X(0.55), y_floor - 20, X(0.55), y_floor + 10, DIM, 1.2, "4 3")
    f.badge(X(0.55), y_floor + 30, 5)
    # 被写体（紙の上、壁から 2m）
    sx = X(2.0)
    fl.person_side(f, sx, y_floor, M=M, height=1.6, shadow=False)
    f.badge(sx + 34, Y(1.7), 6)
    # カメラ
    fl.camera_side(f, X(4.4), Y(1.2), s=0.6, tripod_to=y_floor, facing=-1)
    # 寸法
    f.measure(px0, y_floor + 44, tx, y_floor + 44, "床に 1.5m ほど伸ばす", label_offset=14)
    f.line(px0 - 20, Y(2.6), px0 - 20, y_floor - 3, DIM, 1, "5 3")
    f.text(px0 - 26, Y(1.3), "幅 2.72m の紙", size=11, anchor="end", color=DIM)
    # 凡例
    items = ["ロール。上から引き出す", "壁に沿って床まで垂らす", "床へは緩い曲線でつなぐ（境目が写らない）",
             "先端は養生テープで床に留める", "汚れた部分は最小限を切り落とす", "被写体は紙の上に立つ。靴の裏を拭く"]
    f.callout_list(470, 80, items)
    f.text(470, 216, "撤収時は床の部分を持ち上げてから巻き上げる。", size=11, color=MUTED)
    f.text(470, 232, "伸ばしたまま巻くと、床との角で紙が折れる。", size=11, color=MUTED)
    return f


# ================================================================ fig-09-gray-range
def fig_09_gray_range():
    W, H = 800, 360
    f = fl.Figure(W, H, "グレーの背景紙一本で白から黒まで", "顔を f/8 に固定したまま、紙の上の明るさ（キーとの段差）だけを変える")
    cols = [
        ("白", "＋2〜3 段", "#f6f6f6", "背景ライトで紙を照らす", "紙の上 f/16 以上"),
        ("中間のグレー", "0 段", "#8e8e8e", "背景ライトを弱く当てる", "紙の上 f/8"),
        ("暗いグレー", "−2 段", "#4a4a4a", "キーだけ。被写体は紙から 2m", "紙の上 f/4 前後"),
        ("黒", "−4 段以下", "#141414", "紙から 3m 以上離し、黒レフで漏れを遮る", "紙の上 f/2 以下"),
    ]
    cw, left, fw, fh = 186, 30, 150, 130
    for i, (name, stops, bg, how, value) in enumerate(cols):
        x = left + i * cw
        f.text(x + fw / 2, 80, name, size=13, anchor="middle", weight="bold")
        f.text(x + fw / 2, 98, f"キーとの段差 {stops}", size=11, anchor="middle", color=MUTED)
        y = 108
        f.rect(x, y, fw, fh, bg, INK, 1)
        cid = f.uid("frame")
        f.add_def(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{fw}" height="{fh}"/></clipPath>')
        f.add(f'<g clip-path="url(#{cid})">')
        portrait(f, x + fw / 2, y + 66, s=0.6, shade=0.4, mode="key")
        f.add('</g>')
        f.text(x + fw / 2, y + fh + 22, how, size=11, anchor="middle")
        f.text(x + fw / 2, y + fh + 40, value, size=11, anchor="middle", color=MUTED)
    # 下の階調バー
    gid = f.uid("gray")
    f.add_def(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#111"/><stop offset="1" stop-color="#fafafa"/></linearGradient>')
    bx0, bx1, by = 60, 740, 316
    f.rect(bx0, by, bx1 - bx0, 14, f"url(#{gid})", INK, 0.8)
    for label, pos in (("−4", 0.08), ("−2", 0.36), ("0", 0.62), ("＋2", 0.9)):
        xx = bx0 + (bx1 - bx0) * pos
        f.line(xx, by - 4, xx, by + 18, ACCENT, 1.2)
        f.text(xx, by + 32, f"段差 {label}", size=10.5, anchor="middle", color=ACCENT)
    f.text(bx0, by - 8, "紙の上の明るさが低い", size=10.5, color=MUTED)
    f.text(bx1, by - 8, "高い", size=10.5, anchor="end", color=MUTED)
    return f


# ================================================================ fig-09-ambient-mix
def fig_09_ambient_mix():
    W, H = 780, 400
    f = fl.Figure(W, H, "シャッター速度は定常光の分だけを変える", "ストロボ光を 100 としたときの、センサーに届く光の量")
    AMBIENT = "#9dc183"
    OPEN = "#d7e3c9"
    # 凡例（副題の下）
    f.rect(24, 62, 12, 12, LIGHT, INK, 0.8)
    f.text(40, 72, "ストロボ光（閃光）", size=11)
    f.rect(150, 62, 12, 12, AMBIENT, INK, 0.8)
    f.text(166, 72, "定常光（蛍光灯や窓）", size=11)
    f.rect(300, 62, 24, 10, OPEN, INK, 0.8)
    f.rect(304, 59, 3, 16, LIGHT, "none", 0)
    f.text(330, 72, "シャッターが開いている時間と閃光の位置", size=11)
    cols = [("1/200 秒", 100, 12, "3 段下。影の側にわずかな色かぶり"),
            ("1/60 秒", 100, 40, "1.7 段増えて混ざりが見える"),
            ("1/15 秒", 100, 160, "定常光が主役になり、ブレも出る")]
    base_y = 312
    scale = 0.6
    cw, left, bw = 190, 110, 54
    f.line(left - 40, base_y, left + 3 * cw, base_y, INK, 1)
    f.line(left - 40, base_y, left - 40, base_y - 270 * scale, INK, 1)
    for v in (100, 200):
        yy = base_y - v * scale
        f.line(left - 44, yy, left - 40, yy, INK, 1)
        f.text(left - 48, yy + 4, str(v), size=10.5, anchor="end", color=MUTED)
    f.text(left - 40, base_y - 270 * scale - 8, "光の量", size=10.5, anchor="middle", color=MUTED)
    for i, (name, strobe, ambient, note) in enumerate(cols):
        x = left + i * cw
        sw = 24 + i * 48
        f.text(x, 100, name, size=13, weight="bold")
        f.rect(x, 108, sw, 10, OPEN, INK, 0.8)
        f.rect(x + 4, 104, 3, 18, LIGHT, "none", 0)
        hs = strobe * scale
        ha = ambient * scale
        f.rect(x, base_y - hs, bw, hs, LIGHT, INK, 0.8)
        f.rect(x, base_y - hs - ha, bw, ha, AMBIENT, INK, 0.8)
        f.text(x + bw + 8, base_y - hs / 2 + 4, "ストロボ光 100", size=11)
        f.text(x + bw + 8, base_y - hs - ha / 2 + 4, f"定常光 {ambient}", size=11, color="#3f6b2a")
        f.text(x, base_y + 22, note, size=10.5, color=MUTED)
    f.text(left - 40, base_y + 52, "ストロボの閃光は 1/1000 秒前後で終わるので、シャッターを長く開けても増えるのは定常光だけである。", size=11)
    f.text(left - 40, base_y + 70, "確認は「ストロボを切って同じ設定で撮る」。真っ黒なら定常光は写っていない。", size=11)
    return f


FIGURES = {
    "fig-07-build-order": fig_07_build_order,
    "fig-07-ratio": fig_07_ratio,
    "fig-07-rim-flare": fig_07_rim_flare,
    "fig-08-cyc-section": fig_08_cyc_section,
    "fig-08-background-stops": fig_08_background_stops,
    "fig-09-paper-booth": fig_09_paper_booth,
    "fig-09-gray-range": fig_09_gray_range,
    "fig-09-ambient-mix": fig_09_ambient_mix,
}
