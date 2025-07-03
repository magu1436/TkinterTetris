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

# Mino種別を表す列挙型
class Mino(StrEnum):
    I = 'I'
    O = 'O'
    S = 'S'
    Z = 'Z'
    J = 'J'
    L = 'L'
    T = 'T'

# ミノ定義（各座標は (row, col)）
MINOS: dict[Mino, list[tuple[int, int]]] = {
    Mino.I: [(0, 0), (0, 1), (0, 2), (0, 3)],
    Mino.O: [(0, 0), (0, 1), (1, 0), (1, 1)],
    Mino.S: [(0, 1), (0, 2), (1, 0), (1, 1)],
    Mino.Z: [(0, 0), (0, 1), (1, 1), (1, 2)],
    Mino.J: [(0, 0), (1, 0), (1, 1), (1, 2)],
    Mino.L: [(0, 2), (1, 0), (1, 1), (1, 2)],
    Mino.T: [(0, 1), (1, 0), (1, 1), (1, 2)],
}

# ミノ色定義
MINO_COLORS: dict[Mino, str] = {
    Mino.I: '#00FFFF',  # 水色
    Mino.O: '#FFFF00',  # 黄色
    Mino.S: '#00FF00',  # 緑色
    Mino.Z: '#FF0000',  # 赤色
    Mino.J: '#0000FF',  # 青色
    Mino.L: '#FFA500',  # オレンジ色
    Mino.T: '#800080',  # 紫色
}


def draw_field(canvas: tk.Canvas) -> None:
    """
    フィールドの背景とグリッド線を描画する関数
    """
    canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BACKGROUND_COLOR, outline="")
    for col in range(COLUMNS + 1):
        x = col * CELL_SIZE
        canvas.create_line(x, 0, x, HEIGHT, fill=GRID_COLOR)
    for row in range(ROWS + 1):
        y = row * CELL_SIZE
        canvas.create_line(0, y, WIDTH, y, fill=GRID_COLOR)


def draw_mino(canvas: tk.Canvas, mino_type: Mino, offset_row: int, offset_col: int) -> list[int]:
    """
    指定のMino種別を指定位置に描画する関数
    offset_row, offset_col はフィールド上のグリッド位置
    描画した矩形オブジェクトIDのリストを返す
    """
    shape = MINOS[mino_type]
    color = MINO_COLORS[mino_type]
    ids: list[int] = []
    for r, c in shape:
        x1 = (offset_col + c) * CELL_SIZE
        y1 = (offset_row + r) * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        rect_id = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=GRID_COLOR)
        ids.append(rect_id)
    return ids


def spawn_new_mino(canvas: tk.Canvas, field_grid: list[list[bool]], state: dict, start_col: int, root: tk.Tk) -> None:
    """
    新しいミノを生成し、フィールド上部に描画、落下処理を開始する関数
    state: 辞書でミノの状態（mino_type, current_row, max_r, current_ids）を管理
    """
    # ランダムにミノ種を選択
    mino_type = random.choice(list(Mino))
    current_row = 0
    max_r = max(r for r, _ in MINOS[mino_type])
    # 既存オブジェクトがあれば削除せずにそのまま残す（固定ブロック）
    # 新ミノを描画
    current_ids = draw_mino(canvas, mino_type, current_row, start_col)
    # state を更新
    state.clear()
    state['mino_type'] = mino_type
    state['current_row'] = current_row
    state['max_r'] = max_r
    state['current_ids'] = current_ids
    # 落下処理をスケジュール
    root.after(FALL_INTERVAL, lambda: drop(canvas, field_grid, state, start_col, root))


def drop(canvas: tk.Canvas, field_grid: list[list[bool]], state: dict, start_col: int, root: tk.Tk) -> None:
    """
    現在のミノを1行落下させ、衝突判定を行う関数
    衝突した場合はミノをフィールドに固定し、新しいミノを生成する
    """
    mino_type = state['mino_type']
    current_row = state['current_row']
    max_r = state['max_r']
    current_ids = state['current_ids']
    # 次位置の衝突判定
    can_move = True
    for r, c in MINOS[mino_type]:
        nr = current_row + r + 1
        nc = start_col + c
        if nr >= ROWS or field_grid[nr][nc]:
            can_move = False
            break
    if can_move:
        # 旧ミノを削除
        for obj_id in current_ids:
            canvas.delete(obj_id)
        # 行を下げる
        current_row += 1
        # 再描画
        current_ids = draw_mino(canvas, mino_type, current_row, start_col)
        # state 更新
        state['current_row'] = current_row
        state['current_ids'] = current_ids
        # 次の落下をスケジュール
        root.after(FALL_INTERVAL, lambda: drop(canvas, field_grid, state, start_col, root))
    else:
        # フィールドに固定
        for r, c in MINOS[mino_type]:
            fr = current_row + r
            fc = start_col + c
            field_grid[fr][fc] = True
        # 次ミノ生成
        spawn_new_mino(canvas, field_grid, state, start_col, root)


def main() -> None:
    root = tk.Tk()
    root.title("Tetris Field")

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
    canvas.pack()

    # フィールドグリッド状態: True=ブロックがある
    field_grid: list[list[bool]] = [[False] * COLUMNS for _ in range(ROWS)]

    draw_field(canvas)
    # ミノ状態用辞書
    state: dict = {}
    start_col = (COLUMNS // 2) - 2

    # ゲーム開始: 最初のミノを生成
    spawn_new_mino(canvas, field_grid, state, start_col, root)

    root.mainloop()


if __name__ == "__main__":
    main()
