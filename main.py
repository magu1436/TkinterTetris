import tkinter as tk
import random
from enum import StrEnum

# 定数定義
CELL_SIZE = 30                # セル1マスのピクセルサイズ
COLUMNS = 10                  # フィールドの横マス数
ROWS = 20                     # フィールドの縦マス数
WIDTH = CELL_SIZE * COLUMNS   # キャンバス幅
HEIGHT = CELL_SIZE * ROWS     # キャンバス高さ
GRID_COLOR = "#000000"       # グリッド線の色
BACKGROUND_COLOR = "#CCCCCC" # 背景色
FALL_INTERVAL = 500           # ミノが1行落下するのに要する時間（ミリ秒）
FAST_FALL_INTERVAL = 50       # 下キー押下時のミノ落下間隔（ミリ秒）
MOVE_INTERVAL = 100           # 押し続けたときのミノ移動間隔（ミリ秒）
# キー定義（変更可能）
KEY_LEFT = 'Left'
KEY_RIGHT = 'Right'
KEY_DOWN = 'Down'
KEY_UP = 'Up'
KEY_ROTATE_RIGHT = 'e'
KEY_ROTATE_LEFT = 'q'

# Mino 種別を表す列挙型
class Mino(StrEnum):
    I = 'I'
    O = 'O'
    S = 'S'
    Z = 'Z'
    J = 'J'
    L = 'L'
    T = 'T'

# 基本ミノ定義
BASE_MINOS = {
    Mino.I: [(0, 0), (0, 1), (0, 2), (0, 3)],
    Mino.O: [(0, 0), (0, 1), (1, 0), (1, 1)],
    Mino.S: [(0, 1), (0, 2), (1, 0), (1, 1)],
    Mino.Z: [(0, 0), (0, 1), (1, 1), (1, 2)],
    Mino.J: [(0, 0), (1, 0), (1, 1), (1, 2)],
    Mino.L: [(0, 2), (1, 0), (1, 1), (1, 2)],
    Mino.T: [(0, 1), (1, 0), (1, 1), (1, 2)],
}
# ミノカラー定義
MINO_COLORS = {
    Mino.I: '#00FFFF',
    Mino.O: '#FFFF00',
    Mino.S: '#00FF00',
    Mino.Z: '#FF0000',
    Mino.J: '#0000FF',
    Mino.L: '#FFA500',
    Mino.T: '#800080',
}
# 回転軸定義 (SRSに準拠したおおよその中心)
PIVOTS = {
    Mino.I: (0.5, 1.5),
    Mino.O: (0.5, 0.5),
    Mino.S: (1, 1),
    Mino.Z: (1, 1),
    Mino.J: (1, 1),
    Mino.L: (1, 1),
    Mino.T: (1, 1),
}

# ユーティリティ関数
def rotate_shape(shape, mtype, direction):
    """
    SRS風の回転: direction=1で右回転、-1で左回転
    回転軸PIVOTS[mtype]を中心にブロックを回転させる
    """
    pivot_r, pivot_c = PIVOTS[mtype]
    new_shape = []
    for r, c in shape:
        dr = r - pivot_r
        dc = c - pivot_c
        if direction == 1:  # 右回転: (dr,dc)->( -dc, dr )? or (dc, -dr)? For Tetris clockwise uses (dr,dc)->(dc, -dr)
            nr = pivot_r + dc
            nc = pivot_c - dr
        else:  # 左回転: (dr,dc)->(-dc, dr)
            nr = pivot_r - dc
            nc = pivot_c + dr
        new_shape.append((int(round(nr)), int(round(nc))))
    return new_shape


def valid_position(field, shape, row, col):
    for r, c in shape:
        nr = row + r
        nc = col + c
        if nc < 0 or nc >= COLUMNS or nr < 0 or nr >= ROWS or field[nr][nc]:
            return False
    return True

# 描画関数
def draw_field(canvas):
    canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BACKGROUND_COLOR, outline="")
    for col in range(COLUMNS + 1):
        x = col * CELL_SIZE
        canvas.create_line(x, 0, x, HEIGHT, fill=GRID_COLOR)
    for row in range(ROWS + 1):
        y = row * CELL_SIZE
        canvas.create_line(0, y, WIDTH, y, fill=GRID_COLOR)

def draw_mino(canvas, shape, row, col, color):
    ids = []
    for r, c in shape:
        x1 = (col + c) * CELL_SIZE
        y1 = (row + r) * CELL_SIZE
        ids.append(canvas.create_rectangle(x1, y1, x1 + CELL_SIZE, y1 + CELL_SIZE,
                                          fill=color, outline=GRID_COLOR))
    return ids

# 固定ミノリスト保持: Trueならブロックあり
field_grid = [[False] * COLUMNS for _ in range(ROWS)]

# ハードドロップ実装
def hard_drop(canvas, field, state, start_col, root):
    mtype = state['type']
    row = state['row']
    col = state['col']
    shape = state['shape']
    ids = state['ids']
    # 落下可能距離計算
    dist = ROWS
    for r, c in shape:
        d = 0
        while True:
            if row + r + d + 1 >= ROWS or field[row + r + d + 1][col + c]:
                break
            d += 1
        dist = min(dist, d)
    # 削除 & 移動
    for oid in ids:
        canvas.delete(oid)
    new_row = row + dist
    new_ids = draw_mino(canvas, shape, new_row, col, MINO_COLORS[mtype])
    # 固定
    for r, c in shape:
        field[new_row + r][col + c] = True
    # 次ミノ生成
    spawn_new_mino(canvas, field, state, start_col, root)

# ミノ生成
def spawn_new_mino(canvas, field, state, start_col, root):
    if state.get('drop_job'):
        root.after_cancel(state['drop_job'])
    mtype = random.choice(list(Mino))
    shape = BASE_MINOS[mtype]
    row, col = 0, start_col
    ids = draw_mino(canvas, shape, row, col, MINO_COLORS[mtype])
    state.update({'type': mtype, 'shape': shape, 'row': row, 'col': col, 'ids': ids, 'down': False})
    job = root.after(FALL_INTERVAL, lambda: drop(canvas, field, state, start_col, root))
    state['drop_job'] = job

# 自動落下
def drop(canvas, field, state, start_col, root):
    mtype = state['type']
    shape = state['shape']
    row = state['row']
    col = state['col']
    ids = state['ids']
    down = state['down']
    collision = False
    for r, c in shape:
        if row + r + 1 >= ROWS or field[row + r + 1][col + c]:
            collision = True
            break
    if collision:
        for r, c in shape:
            field[row + r][col + c] = True
        return spawn_new_mino(canvas, field, state, start_col, root)
    for oid in ids:
        canvas.delete(oid)
    new_row = row + 1
    new_ids = draw_mino(canvas, shape, new_row, col, MINO_COLORS[mtype])
    state.update({'row': new_row, 'ids': new_ids})
    interval = FAST_FALL_INTERVAL if down else FALL_INTERVAL
    job = root.after(interval, lambda: drop(canvas, field, state, start_col, root))
    state['drop_job'] = job

# 左右移動
def try_move(canvas, field, state, direction):
    shape = state['shape']
    row = state['row']
    col = state['col']
    ids = state['ids']
    new_col = col + direction
    if not valid_position(field, shape, row, new_col):
        return
    for oid in ids:
        canvas.delete(oid)
    new_ids = draw_mino(canvas, shape, row, new_col, MINO_COLORS[state['type']])
    state.update({'col': new_col, 'ids': new_ids})

# 回転処理
def rotate_mino(canvas, field, state, direction):
    mtype = state['type']
    shape = state['shape']
    row = state['row']
    col = state['col']
    ids = state['ids']
    new_shape = rotate_shape(shape, mtype, direction)
    if not valid_position(field, new_shape, row, col):
        return
    for oid in ids:
        canvas.delete(oid)
    new_ids = draw_mino(canvas, new_shape, row, col, MINO_COLORS[mtype])
    state.update({'shape': new_shape, 'ids': new_ids})

# 移動ハンドラ
def handle_move(canvas, field, state, root):
    if state.get('left'):
        try_move(canvas, field, state, -1)
    if state.get('right'):
        try_move(canvas, field, state, 1)
    root.after(MOVE_INTERVAL, lambda: handle_move(canvas, field, state, root))

# メイン関数
def main():
    root = tk.Tk()
    root.title("Tetris Field")
    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
    canvas.pack()
    draw_field(canvas)
    state = {'left': False, 'right': False, 'down': False, 'drop_job': None}
    # キーバインド設定
    root.bind(f"<KeyPress-{KEY_LEFT}>", lambda e: state.update(left=True))
    root.bind(f"<KeyRelease-{KEY_LEFT}>", lambda e: state.update(left=False))
    root.bind(f"<KeyPress-{KEY_RIGHT}>", lambda e: state.update(right=True))
    root.bind(f"<KeyRelease-{KEY_RIGHT}>", lambda e: state.update(right=False))
    root.bind(f"<KeyPress-{KEY_DOWN}>", lambda e: state.update(down=True))
    root.bind(f"<KeyRelease-{KEY_DOWN}>", lambda e: state.update(down=False))
    root.bind(f"<KeyPress-{KEY_UP}>", lambda e: hard_drop(canvas, field_grid, state, (COLUMNS // 2) - 2, root))
    root.bind(f"<KeyPress-{KEY_ROTATE_RIGHT}>", lambda e: rotate_mino(canvas, field_grid, state, 1))
    root.bind(f"<KeyPress-{KEY_ROTATE_LEFT}>", lambda e: rotate_mino(canvas, field_grid, state, -1))
    # 継続処理開始
    handle_move(canvas, field_grid, state, root)
    spawn_new_mino(canvas, field_grid, state, (COLUMNS // 2) - 2, root)
    root.mainloop()

if __name__ == "__main__":
    main()
