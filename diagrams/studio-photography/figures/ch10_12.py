"""第 10〜12 章のイラスト。scripts/render-figures.py studio-photography で docs/studio-photography/img/ に書き出す。"""
import math

import figlib as fl
from figlib import INK, MUTED, LIGHT, ACCENT, DIM, WALL, BLACK, FLOOR, BODY


# ---------------------------------------------------------------- 図 10-4 物撮りの側面図
def fig_10_product_side():
    W, H = 780, 560
    f = fl.Figure(W, H, "物撮りのセッティング（側面から見た図）",
                  "テーブル上のスイープ、上後方 45 度のソフトボックス、20 度見下ろすカメラ")
    M = 200  # px / m
    floor_y = 520
    table_y = floor_y - 0.75 * M
    mug_x = 430
    wall_x = 660
    # 床と壁
    f.line(40, floor_y, W - 40, floor_y, INK, 1.2)
    f.text(60, floor_y - 6, "床", size=11, color=MUTED)
    f.line(wall_x, 80, wall_x, floor_y, INK, 1.2)
    f.text(wall_x + 6, 96, "壁", size=11, color=MUTED)
    # テーブル
    f.rect(170, table_y, wall_x - 170, 10, WALL, INK, 1.2)
    for lx in (200, wall_x - 30):
        f.line(lx, table_y + 10, lx, floor_y, INK, 1.2)
    f.line(120, table_y, 120, floor_y, DIM, 1, "5 3")
    f.line(114, table_y, 126, table_y, DIM, 1.2)
    f.line(114, floor_y, 126, floor_y, DIM, 1.2)
    f.text(112, (table_y + floor_y) / 2 + 4, "テーブルの高さ\n70〜75cm", size=11, anchor="end", color=DIM)
    # スイープ
    curve_x = mug_x + 0.4 * M
    f.path(f"M{wall_x - 4},120 L{wall_x - 4},{table_y - 80} Q{wall_x - 4},{table_y - 2} {curve_x},{table_y - 2} "
           f"L210,{table_y - 2} L210,{table_y - 8} L{curve_x},{table_y - 8} Q{wall_x - 10},{table_y - 8} {wall_x - 10},{table_y - 80} "
           f"L{wall_x - 10},120 Z", "#f4f2ee", INK, 1.2)
    f.text(wall_x - 16, 136, "白い背景紙の\nスイープ", size=11, anchor="end", color=MUTED)
    f.line(curve_x, table_y - 2, curve_x, table_y + 22, MUTED, 0.8, "2 2")
    # マグカップ
    mh, mw = 0.09 * M, 0.08 * M
    f.rect(mug_x - mw / 2, table_y - 2 - mh, mw, mh, "#fafafa", INK, 1.4, 2)
    f.path(f"M{mug_x + mw / 2},{table_y - 2 - mh * 0.72:.1f} a5,5 0 1,1 0,{mh * 0.45:.1f}", "none", INK, 1.4)
    mug_cx, mug_cy = mug_x, table_y - 2 - mh / 2
    f.line(mug_x, table_y + 16, curve_x, table_y + 16, DIM, 1, "5 3")
    for xx in (mug_x, curve_x):
        f.line(xx, table_y + 12, xx, table_y + 20, DIM, 1.2)
    f.text((mug_x + curve_x) / 2, table_y + 32, "40cm", size=11, anchor="middle", color=DIM)
    f.text(curve_x + 6, table_y + 32, "曲がり始め", size=10, color=MUTED)
    # ソフトボックス：上後方 45 度、1m
    d = 1.0 * M
    sb_x = mug_cx + d * math.cos(math.radians(45))
    sb_y = mug_cy - d * math.sin(math.radians(45))
    f.path(f"M{sb_x:.1f},{sb_y:.1f} L{mug_cx - 110:.1f},{table_y - 2} L{mug_cx + 70:.1f},{table_y - 2} Z", LIGHT, "none", 0, opacity=0.16)
    # ブームスタンド（テーブルの脇に立てる）
    f.line(sb_x + 36, sb_y - 26, sb_x + 36, floor_y, MUTED, 1.2, "6 3")
    f.line(sb_x + 16, sb_y - 40, sb_x + 36, sb_y - 26, MUTED, 1.2)
    f.rect(sb_x + 18, floor_y - 14, 36, 14, "#8a7a62", INK, 1, 3)
    f.text(sb_x + 42, table_y + 40, "ブーム\nスタンド", size=10, color=MUTED)
    f.text(sb_x + 36, floor_y + 16, "サンドバッグ", size=10, anchor="middle", color=MUTED)
    fl.softbox_side(f, sb_x, sb_y, 135)
    f.line(sb_x, sb_y, mug_cx, mug_cy, LIGHT, 1, "3 4")
    # 角度と距離
    f.line(mug_cx, mug_cy, mug_cx, mug_cy - 110, ACCENT, 0.8, "2 3")
    r = 64
    f.path(f"M{mug_cx},{mug_cy - r} A{r},{r} 0 0,1 {mug_cx + r * math.cos(math.radians(45)):.1f},{mug_cy - r * math.sin(math.radians(45)):.1f}",
           "none", ACCENT, 1.2)
    f.text(mug_cx + 18, mug_cy - r - 10, "45°", size=12, anchor="middle", color=ACCENT)
    midx, midy = (sb_x + mug_cx) / 2, (sb_y + mug_cy) / 2
    f.text(midx + 12, midy + 12, "1m", size=12, color=DIM)
    f.text(360, 104, "キー：60×90cm ソフトボックス\n上後方 45 度、被写体から 1m\n出力 1/4、上面が f/11", size=12)
    f.line(548, 118, sb_x - 40, sb_y - 30, MUTED, 0.8)
    # カメラ：60cm、20 度見下ろし
    cd = 0.6 * M
    cam_x = mug_cx - cd * math.cos(math.radians(20))
    cam_y = mug_cy - cd * math.sin(math.radians(20))
    f.line(cam_x, cam_y, mug_cx, mug_cy, MUTED, 1, "3 3")
    f.line(cam_x, cam_y, cam_x + 90, cam_y, ACCENT, 0.8, "2 3")
    ra = 54
    f.path(f"M{cam_x + ra},{cam_y} A{ra},{ra} 0 0,1 {cam_x + ra * math.cos(math.radians(20)):.1f},{cam_y + ra * math.sin(math.radians(20)):.1f}",
           "none", ACCENT, 1.2)
    f.text(cam_x + ra + 6, cam_y - 6, "20°", size=12, color=ACCENT)
    fl.camera_side(f, cam_x, cam_y, 20)
    # 三脚（旧図と同じ形。カメラの左下から床へ）
    f.line(cam_x - 10, cam_y + 16, cam_x - 10, floor_y, INK, 1.4)
    f.line(cam_x - 10, cam_y + 90, cam_x - 44, floor_y, INK, 1.2)
    f.line(cam_x - 10, cam_y + 90, cam_x + 24, floor_y, INK, 1.2)
    f.text(cam_x - 20, cam_y - 60, "カメラ：RF 50mm、三脚\n60cm、20 度見下ろし\nMF、f/11", size=12, anchor="middle")
    # 白レフと黒レフ
    wb_x = mug_cx - 0.4 * M
    fl.board_side(f, wb_x, table_y - 2 - 20, 40, "white")
    f.rect(mug_cx - 60, table_y - 2 - 46, 6, 46, BLACK, BLACK, 1, opacity=0.55)
    # 引き出し線で下の余白に説明を置く
    lab_x = 330
    f.line(mug_cx - 2, table_y + 10, lab_x + 8, 424, MUTED, 0.8)
    f.text(lab_x + 12, 428, "マグカップ（曲がり始めから 40cm 手前）", size=11)
    f.line(wb_x, table_y + 10, lab_x + 8, 454, MUTED, 0.8)
    f.text(lab_x + 12, 458, "白レフ（レンズの下、被写体から 40cm）", size=11)
    f.line(mug_cx - 57, table_y + 10, lab_x + 8, 484, MUTED, 0.8)
    f.text(lab_x + 12, 488, "黒レフ（左の縁の映り込み用。紙面の手前側に立てる）", size=11)
    return f


# ---------------------------------------------------------------- 図 10-1 反射の角度の族
def fig_10_reflection_family():
    W, H = 780, 440
    f = fl.Figure(W, H, "反射の角度の族",
                  "カメラから面を見たとき、面が鏡だとして映る方向の範囲。そこに置いたものが面に映る")
    C = (150, 120)
    S1, S2 = (300, 330), (520, 330)

    def reflect(S):
        dx, dy = S[0] - C[0], S[1] - C[1]
        return (dx, -dy)

    r1, r2 = reflect(S1), reflect(S2)
    top = 70
    t1 = (S1[1] - top) / (-r1[1])
    p1 = (S1[0] + r1[0] * t1, top)
    xr = 740
    t2 = (xr - S2[0]) / r2[0]
    p2 = (xr, S2[1] + r2[1] * t2)
    # 扇
    f.path(f"M{S1[0]},{S1[1]} L{p1[0]:.1f},{p1[1]} L{xr},{top} L{p2[0]:.1f},{p2[1]:.1f} L{S2[0]},{S2[1]} Z",
           ACCENT, "none", 0, opacity=0.12)
    f.text(600, 96, "反射の角度の族", size=13, anchor="middle", color=ACCENT, weight="bold")
    f.text(600, 114, "この範囲にある光源は\n面にハイライトとして映る", size=11, anchor="middle", color=ACCENT)
    # 面
    f.rect(S1[0], S1[1], S2[0] - S1[0], 12, "#f4f4f4", INK, 1.4)
    f.text((S1[0] + S2[0]) / 2, 366, "光沢のある面（釉薬の陶器の表面）", size=12, anchor="middle")
    # カメラ
    fl.camera_top(f, C[0], C[1], deg=55, s=1.1)
    f.text(C[0] - 30, C[1] - 6, "カメラ", size=12, anchor="end")
    # 入射（カメラ→面）と反射線
    for S, r, p in ((S1, r1, p1), (S2, r2, p2)):
        f.line(C[0], C[1], S[0], S[1], MUTED, 1, "4 3")
        f.line(S[0], S[1], p[0], p[1], ACCENT, 1.2, "4 3")
    # 法線と等角の印
    f.line(S1[0] + 60, S1[1], S1[0] + 60, S1[1] - 60, MUTED, 0.8, "2 3")
    f.text(S1[0] + 66, S1[1] - 50, "法線", size=10, color=MUTED)
    f.text(S1[0] - 8, S1[1] - 46, "入射角 = 反射角", size=11, anchor="end", color=MUTED)
    # ソフトボックス A（族の中）
    ax, ay = 590, 175
    fl.softbox_top(f, ax, ay, deg=125, s=1.15)
    f.badge(ax + 46, ay - 30, "A")
    f.text(ax + 62, ay - 26, "族の中：面に長方形の\nハイライトとして映る", size=11)
    # ソフトボックス B（族の外）
    bx, by = 690, 290
    fl.softbox_top(f, bx, by, deg=200, s=1.0)
    f.badge(bx + 10, by + 50, "B")
    f.text(bx - 6, by + 74, "族の外：面を明るくするが\n像としては映らない", size=11, anchor="end")
    f.text(410, 400, "白い板を族の中に置けば白い縁、黒い板を置けば暗い縁が面に映る（ライトを動かさずに見え方を変えられる）",
           size=11, anchor="middle", color=MUTED)
    return f


# ---------------------------------------------------------------- 図 10-2 透過光のグラス
def fig_10_glass():
    W, H = 780, 400
    f = fl.Figure(W, H, "透明なグラスを透過光で撮る", "左：上から見た配置。右：カメラから見た仕上がり")
    # 左：上から見た図
    ox = 60
    f.rect(ox, 70, 320, 300, FLOOR, "none", 0)
    f.rect(ox + 60, 82, 200, 10, "#f4f2ee", INK, 1)
    f.text(ox + 160, 78, "白の背景紙（写らない）", size=10, anchor="middle", color=MUTED)
    # ソフトボックス（真後ろ、下向き）
    sx, sy = ox + 160, 130
    f.path(f"M{sx - 30},{sy + 14} L{sx - 110},{sy + 200} L{sx + 110},{sy + 200} L{sx + 30},{sy + 14} Z", LIGHT, "none", 0, opacity=0.16)
    fl.softbox_top(f, sx, sy, deg=90)
    f.badge(sx, sy - 24, "A")
    f.text(sx + 44, sy + 4, "透過光\nグラスの真後ろ、1m", size=11)
    # グラス
    gx, gy = sx, 250
    f.circle(gx, gy, 12, "#eef6fb", INK, 1.4)
    f.circle(gx, gy, 8, "none", INK, 0.8)
    f.text(gx, gy + 30, "グラス", size=11, anchor="middle")
    # 黒レフ
    for bx in (gx - 44, gx + 44):
        fl.board_side(f, bx, gy, 60, "black")
    f.text(gx - 54, gy - 36, "黒レフ", size=11, anchor="end")
    f.text(gx + 54, gy - 36, "黒レフ", size=11)
    # 縁への映り込み（黒が映る）
    for sgn in (-1, 1):
        f.line(gx + sgn * 44, gy - 6, gx + sgn * 12, gy + 2, MUTED, 0.9, "2 2", arrow=True)
    # カメラ
    cx, cy = gx, 340
    fl.camera_top(f, cx, cy, deg=-90)
    f.text(cx + 30, cy + 4, "カメラ（三脚）", size=11)
    # 右：仕上がり
    rx0, ry0, rw, rh = 440, 80, 300, 290
    glow = f.uid("glow")
    coffee = f.uid("coffee")
    f.add_def(f'<radialGradient id="{glow}" cx="0.5" cy="0.5" r="0.7"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#f6e7b8"/></radialGradient>')
    f.add_def(f'<linearGradient id="{coffee}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a3a22"/><stop offset="0.55" stop-color="#8b5a3a"/>'
              f'<stop offset="0.62" stop-color="#d9c1a3"/><stop offset="1" stop-color="#f3ecdf"/></linearGradient>')
    f.rect(rx0, ry0, rw, rh, "#fff8e1", INK, 1.2)
    f.rect(rx0 + 1, ry0 + 1, rw - 2, rh - 2, f"url(#{glow})", "none", 0)
    gcx = rx0 + rw / 2
    gtop, gbot = ry0 + 60, ry0 + rh - 40
    gw = 90
    # 中身（層）
    f.path(f"M{gcx - gw / 2 + 6},{gtop + 30} L{gcx - gw / 2 + 10},{gbot - 6} Q{gcx},{gbot + 4} {gcx + gw / 2 - 10},{gbot - 6} L{gcx + gw / 2 - 6},{gtop + 30} Z",
           f"url(#{coffee})", "none", 0)
    # 氷
    for (ix, iy, r) in ((gcx - 18, gtop + 44, 12), (gcx + 14, gtop + 62, 11), (gcx - 4, gtop + 88, 10)):
        f.rect(ix - r, iy - r, 2 * r, 2 * r, "#ffffff", "#c9d8e6", 1, 3, opacity=0.55)
    # グラスの輪郭（暗い縁）
    f.path(f"M{gcx - gw / 2},{gtop} L{gcx - gw / 2 + 8},{gbot} Q{gcx},{gbot + 16} {gcx + gw / 2 - 8},{gbot} L{gcx + gw / 2},{gtop}",
           "none", BLACK, 4, opacity=0.85, extra='stroke-linejoin="round"')
    f.add(f'<ellipse cx="{gcx}" cy="{gtop}" rx="{gw / 2}" ry="8" fill="none" stroke="{BLACK}" stroke-width="2.5" opacity="0.7"/>')
    # 注記
    f.arrow(gcx - gw / 2 - 4, gtop + 120, rx0 + 30, gtop + 150, MUTED, 0.9)
    f.text(rx0 + 8, gtop + 166, "黒レフが映って\n縁が暗い線になる", size=10)
    f.arrow(gcx + gw / 2 - 20, gtop + 120, rx0 + rw - 20, gtop + 100, MUTED, 0.9)
    f.text(rx0 + rw - 8, gtop + 84, "後ろからの光で\n層が透けて見える", size=10, anchor="end")
    f.text(gcx, ry0 + 24, "ソフトボックスの面が白い背景になる", size=11, anchor="middle", color=MUTED)
    f.text(gcx, ry0 + rh - 12, "カメラから見た仕上がり", size=11, anchor="middle", color=MUTED)
    return f


# ---------------------------------------------------------------- 図 11-2 撮影日のタイムテーブル
def fig_11_timeline():
    slots = [
        ("10:00", "10:05", "入室", "set", "備品の数、暗幕\n3 灯が点くか"),
        ("10:05", "10:20", "白ホリのセット", "set", "テストボタンで 3 灯\nCH1、A 1/4、C 1/16"),
        ("10:20", "10:30", "試し撮り", "set", "ストロボなしで真っ黒\n顔 f/8、背景だけ警告"),
        ("10:30", "11:10", "上半身の撮影", "shoot", "20〜30 枚ごとに\nヒストグラムと瞳のピント"),
        ("11:10", "11:25", "全身に変更", "set", "キー 2.1m、1/2\n立ち位置にテープ"),
        ("11:25", "12:00", "全身の撮影", "shoot", "足元の影、床の反射\nテザーを外す"),
        ("12:00", "12:20", "物撮りのセット", "set", "三脚、MF と拡大表示\nf/11"),
        ("12:20", "13:00", "物撮り", "shoot", "白レフと黒レフの\n映り込み、埃"),
        ("13:00", "13:20", "余白", "slack", "押した枠の追加\n試したかった一枚"),
        ("13:20", "13:40", "撤収", "pack", "ランプを消して冷ます\nサンドバッグを先に外す"),
        ("13:40", "14:00", "データのコピー", "data", "コピー完了を確かめて\nカードを抜く"),
    ]
    return fl.timeline_figure("撮影日のタイムテーブル（10:00 入室、14:00 退室）",
                              "撤収とデータのコピーを先に固定し、残りを撮影の枠に割り振る。帯の下は各枠で確認すること",
                              10, 14, slots, (), 4)


# ---------------------------------------------------------------- 図 12-5 総合演習のタイムテーブル
def fig_12_timeline():
    slots = [
        ("13:00", "13:20", "搬入と点検", "set", "暗幕、ストロボを切って\n1 枚（環境光の確認）"),
        ("13:20", "13:50", "白ホリのセット", "set", "一灯ずつ点けて確認\n試し撮りは同行者で"),
        ("13:50", "14:35", "スタッフ 3 人", "shoot", "壁だけに警告、瞳のピント\n3 人の山の位置を揃える"),
        ("14:35", "15:05", "ブースへ移動", "set", "テーブルとスイープ\n三脚とテザー"),
        ("15:05", "16:05", "ケーキ 3 品とコーヒー", "shoot", "最初にグレーカード\n皿の手前と奥のピント"),
        ("16:05", "16:35", "透過光に組み替え", "set", "水のグラスで試し撮り\n層と縁を確かめる"),
        ("16:35", "17:00", "撤収", "pack", "ランプを冷ます間に\n2 か所へバックアップ"),
    ]
    return fl.timeline_figure("総合演習のタイムテーブル（13:00〜17:00）",
                              "組み替えは 2 回。スタッフとオーナーの来る時刻を帯に合わせる",
                              13, 17, slots,
                              (("13:50", "スタッフ到着"), ("15:00", "ケーキ搬入"), ("16:20", "ラテを作る")), 3)


# ---------------------------------------------------------------- 図 11-1 トラブルの切り分け
def fig_11_troubleshooting():
    W, H = 780, 700
    f = fl.Figure(W, H, "トラブルは光の経路の順に切り分ける",
                  "症状から原因を当てにいくより、トリガー、ストロボ、カメラの順に確かめるほうが早い")
    sx0, sy = 60, 84
    f.stage_strip(sx0, sy, ["シャッター", "トリガー", "電波", "ストロボ", "被写体の光", "センサー"])
    f.text(sx0, sy + 44, "光が写るまでの経路（上）。下の流れは、この経路を確かめやすい順にたどる", size=10, color=MUTED)
    qx, qw, qh = 60, 300, 52
    ax_, aw = 430, 310
    rows = [
        ("トリガーのテストボタンで\n3 灯すべてが光るか", "光らない", "トリガーとストロボの設定\n電源、シューの固定、CH と ID、\nグループの OFF、S1/S2、チャージ", "症状：発光しない"),
        ("写真の一部が黒い帯になるか", "なる", "シャッター速度が 1/250 秒を超えている\n1/200 秒に戻す。HSS を切る", "症状：黒い帯"),
        ("暗いコマが規則的に混ざるか", "混ざる", "チャージが追いついていない\nレディ音を待つ。出力を下げて ISO を上げる", "症状：暗いコマ"),
        ("色が想定と違うか", "違う", "WB を 5500K に戻す\nストロボを切って撮り、真っ黒でなければ\n環境光かモデリングランプの混入", "症状：色が合わない"),
        ("ファインダーや背面モニターが\n暗いか", "暗い", "露出Simulation を「しない」に戻す", "症状：ファインダーが暗い"),
        ("ピントが甘いか", "甘い", "拡大表示で確認。瞳検出が働いているか\nモデリングランプを最大に。f/8 まで絞る", "症状：ピント"),
    ]
    y, gap = 162, 84
    for i, (q, yes, act, sym) in enumerate(rows):
        cy = y + i * gap
        fl.flow_box(f, qx, cy, qw, qh, q, size=12)
        f.text(qx, cy - 6, sym, size=10, color=ACCENT, weight="bold")
        fl.flow_arrow(f, qx + qw, cy + qh / 2, ax_, cy + qh / 2, yes)
        lines = act.count("\n") + 1
        ah = 14 + lines * 15
        f.rect(ax_, cy + qh / 2 - ah / 2, aw, ah, "#fff8e1", INK, 1, 6)
        f.text(ax_ + 10, cy + qh / 2 - ah / 2 + 18, act, size=11, lh=1.3)
        if i < len(rows) - 1:
            f.arrow(qx + qw - 40, cy + qh, qx + qw - 40, cy + gap - 2, INK, 1.2)
            f.text(qx + qw - 34, cy + qh + 13, "問題なし", size=10, color=MUTED)
    f.text(qx, y + len(rows) * gap - 8, "ここまでで見つからなければ、被写体の位置と用具の向きを最初の配置図と見比べる", size=10, color=MUTED)
    return f


# ---------------------------------------------------------------- 図 12-1 撮影計画の依存の向き
def fig_12_plan_dependencies():
    W, H = 780, 560
    f = fl.Figure(W, H, "撮影計画の依存の向き", "後の段階の判断は、前の段階の成果物の上に載る。矢印は依存の向き")
    stages = [
        ("要件の整理", "何を、どの用途で、何カット、\nどの形式で納めるか", "第 1 章"),
        ("露出の基準", "用途と被写界深度から絞りを決め、\nISO とシャッター速度を固定する", "第 2 章"),
        ("カメラの設定", "シャッター方式、AF か MF か、\nレンズと焦点距離、テザーの有無", "第 3 章"),
        ("灯数と用具", "3 灯に何を付け、\nどのグループに割り当てるか", "第 4 章、第 5 章"),
        ("配置と出力", "キー、フィル、背景の位置と\n出力を段差で組む", "第 6〜10 章"),
        ("確認", "ヒストグラム、ハイライト警告、\n拡大表示で一灯ずつ確かめる", "第 2、7、11 章"),
        ("撤収と納品", "熱を冷ましてから片付け、\nバックアップし、現像して納める", "第 11 章"),
    ]
    bx, bw, bh = 270, 370, 50
    y0, gap = 84, 66
    for i, (name, what, ch) in enumerate(stages):
        cy = y0 + i * gap
        fl.flow_box(f, bx, cy, bw, bh, what, head=name, head_w=112, size=12)
        f.text(bx + bw + 14, cy + bh / 2 + 4, ch, size=11, color=MUTED)
        if i < len(stages) - 1:
            f.arrow(bx + 56, cy + bh, bx + 56, cy + gap - 2, INK, 1.2)

    def dep(i_from, i_to, label, dx):
        ya = y0 + i_from * gap + bh / 2
        yb = y0 + i_to * gap + bh / 2
        fl.flow_arrow(f, bx, ya, bx - 4, yb, label, ACCENT, curve=dx)

    dep(0, 1, "用途が絞りを決める\n（顔だけか皿の奥までか）", 60)
    dep(1, 4, "絞りが出力を決める\n（f/8 で 1/4、f/16 で 1/2）", 110)
    dep(3, 4, "段差が配置を決める\n（2 段下なら白レフ 1m）", 60)
    f.text(24, H - 20, "実際の作業は段階を行き来するが、依存の向きは変わらない", size=10, color=MUTED)
    return f


FIGURES = {
    "fig-10-product-side": fig_10_product_side,
    "fig-10-reflection-family": fig_10_reflection_family,
    "fig-10-glass": fig_10_glass,
    "fig-11-timeline": fig_11_timeline,
    "fig-11-troubleshooting": fig_11_troubleshooting,
    "fig-12-plan-dependencies": fig_12_plan_dependencies,
    "fig-12-timeline": fig_12_timeline,
}
