import tkinter as tk
from tkinter import messagebox
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
FALL_INTERVAL = 500           # ミノが1行落下するまでの時間（ミリ秒）
FAST_FALL_INTERVAL = 50       # 下キー押下時の落下間隔（ミリ秒）
MOVE_INTERVAL = 100           # 押し続け時の移動間隔（ミリ秒）

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

# 回転軸定義 (簡易SRS)
PIVOTS = {
    Mino.I: (0.5, 1.5),
    Mino.O: (0.5, 0.5),
    Mino.S: (1, 1),
    Mino.Z: (1, 1),
    Mino.J: (1, 1),
    Mino.L: (1, 1),
    Mino.T: (1, 1),
}

# フィールド状態とブロックID保持
field_grid = [[False] * COLUMNS for _ in range(ROWS)]
block_ids = [[None] * COLUMNS for _ in range(ROWS)]

# ユーティリティ関数
def valid_position(field, shape, row, col):
    for r, c in shape:
        nr, nc = row + r, col + c
        if nc < 0 or nc >= COLUMNS or nr < 0 or nr >= ROWS or field[nr][nc]:
            return False
    return True

# 回転ロジック
def rotate_shape(shape, mtype, direction):
    pivot_r, pivot_c = PIVOTS[mtype]
    new_shape = []
    for r, c in shape:
        dr, dc = r - pivot_r, c - pivot_c
        if direction == 1:
            nr = pivot_r + dc
            nc = pivot_c - dr
        else:
            nr = pivot_r - dc
            nc = pivot_c + dr
        new_shape.append((int(round(nr)), int(round(nc))))
    return new_shape

# 描画関数
def draw_field(canvas):
    canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BACKGROUND_COLOR, outline="")
    for i in range(COLUMNS + 1):
        x = i * CELL_SIZE
        canvas.create_line(x, 0, x, HEIGHT, fill=GRID_COLOR)
    for i in range(ROWS + 1):
        y = i * CELL_SIZE
        canvas.create_line(0, y, WIDTH, y, fill=GRID_COLOR)

def draw_cell(canvas, row, col, color):
    x = col * CELL_SIZE
    y = row * CELL_SIZE
    return canvas.create_rectangle(x, y, x + CELL_SIZE, y + CELL_SIZE, fill=color, outline=GRID_COLOR)

def clear_lines(canvas):
    r = ROWS - 1
    while r >= 0:
        if all(field_grid[r][c] for c in range(COLUMNS)):
            # 指定行のブロック削除
            for c in range(COLUMNS):
                oid = block_ids[r][c]
                if oid:
                    canvas.delete(oid)
                    block_ids[r][c] = None
                    field_grid[r][c] = False
            # 上行を一段下に移動
            for rr in range(r - 1, -1, -1):
                for c in range(COLUMNS):
                    oid = block_ids[rr][c]
                    if oid:
                        canvas.move(oid, 0, CELL_SIZE)
                    block_ids[rr + 1][c] = block_ids[rr][c]
                    field_grid[rr + 1][c] = field_grid[rr][c]
            # 最上行を空に
            for c in range(COLUMNS):
                block_ids[0][c] = None
                field_grid[0][c] = False
        else:
            r -= 1

# ゲームオーバー処理
def game_over(root):
    messagebox.showinfo("Game Over", "ゲームオーバーです！")
    root.destroy()

# ミノ生成と落下制御
def spawn_new_mino(canvas, field, state, start_col, root):
    if state.get('job'):
        root.after_cancel(state['job'])
    mtype = random.choice(list(Mino))
    shape = BASE_MINOS[mtype]
    row, col = 0, start_col
    # ゲームオーバー判定
    if not valid_position(field, shape, row, col):
        return game_over(root)
    # 描画
    ids = [draw_cell(canvas, row + sr, col + sc, MINO_COLORS[mtype]) for sr, sc in shape]
    state.update(type=mtype, shape=shape, row=row, col=col, ids=ids, down=False)
    state['job'] = root.after(FALL_INTERVAL, lambda: drop(canvas, field, state, start_col, root))

# ハードドロップ
def hard_drop(canvas, field, state, start_col, root):
    mtype = state['type']
    shape = state['shape']
    row = state['row']
    col = state['col']
    ids = state['ids']
    # 最大落下距離計算
    min_dist = ROWS
    for sr, sc in shape:
        dist = 0
        while True:
            nr = row + sr + dist + 1
            if nr >= ROWS or field[nr][col + sc]:
                break
            dist += 1
        min_dist = min(min_dist, dist)
    # 現ミノ削除
    for oid in ids:
        canvas.delete(oid)
    # 固定描画
    for sr, sc in shape:
        r1 = row + sr + min_dist
        c1 = col + sc
        oid = draw_cell(canvas, r1, c1, MINO_COLORS[mtype])
        block_ids[r1][c1] = oid
        field_grid[r1][c1] = True
    clear_lines(canvas)
    spawn_new_mino(canvas, field, state, start_col, root)

# 自動落下
def drop(canvas, field, state, start_col, root):
    mtype = state['type']
    shape = state['shape']
    row = state['row']
    col = state['col']
    ids = state['ids']
    down = state['down']
    # 衝突判定
    for sr, sc in shape:
        nr = row + sr + 1
        if nr >= ROWS or field[nr][col + sc]:
            # 固定
            for idx, (sr2, sc2) in enumerate(shape):
                r1 = row + sr2
                c1 = col + sc2
                block_ids[r1][c1] = ids[idx]
                field_grid[r1][c1] = True
            clear_lines(canvas)
            return spawn_new_mino(canvas, field, state, start_col, root)
    # 移動
    for oid in ids:
        canvas.delete(oid)
    new_row = row + 1
    state['row'] = new_row
    state['ids'] = [draw_cell(canvas, new_row + sr, col + sc, MINO_COLORS[mtype]) for sr, sc in shape]
    interval = FAST_FALL_INTERVAL if down else FALL_INTERVAL
    state['job'] = root.after(interval, lambda: drop(canvas, field, state, start_col, root))

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
    state['col'] = new_col
    state['ids'] = [draw_cell(canvas, row + sr, new_col + sc, MINO_COLORS[state['type']]) for sr, sc in shape]

# 回転
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
    state['shape'] = new_shape
    state['ids'] = [draw_cell(canvas, row + sr, col + sc, MINO_COLORS[mtype]) for sr, sc in new_shape]

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
    state = {'left': False, 'right': False, 'down': False, 'job': None}
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