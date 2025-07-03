import tkinter as tk
import random
from enum import StrEnum

# 定数定義
CELL_SIZE = 30               # セル1マスのピクセルサイズ
COLUMNS = 10                 # フィールドの横マス数
ROWS = 20                    # フィールドの縦マス数
WIDTH = CELL_SIZE * COLUMNS  # キャンバス幅
HEIGHT = CELL_SIZE * ROWS    # キャンバス高さ
GRID_COLOR = "#000000"     # グリッド線の色
BACKGROUND_COLOR = "#CCCCCC" # 背景色

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
MINOS: dict[Mino, list[tuple[int,int]]] = {
    Mino.I: [(0,0), (0,1), (0,2), (0,3)],
    Mino.O: [(0,0), (0,1), (1,0), (1,1)],
    Mino.S: [(0,1), (0,2), (1,0), (1,1)],
    Mino.Z: [(0,0), (0,1), (1,1), (1,2)],
    Mino.J: [(0,0), (1,0), (1,1), (1,2)],
    Mino.L: [(0,2), (1,0), (1,1), (1,2)],
    Mino.T: [(0,1), (1,0), (1,1), (1,2)],
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


def draw_mino(canvas: tk.Canvas, mino_type: Mino, offset_row: int, offset_col: int) -> None:
    """
    指定のMino種別を指定位置に描画する関数
    offset_row, offset_col はフィールド上のグリッド位置
    """
    shape = MINOS[mino_type]
    color = MINO_COLORS[mino_type]
    for r, c in shape:
        x1 = (offset_col + c) * CELL_SIZE
        y1 = (offset_row + r) * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=GRID_COLOR)


def main() -> None:
    root = tk.Tk()
    root.title("Tetris Field")

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
    canvas.pack()

    draw_field(canvas)

    # ランダムに1種類のMinoを選択し、フィールド上部中央に描画
    mino_type = random.choice(list(Mino))
    # 初期表示位置：上端（row=0）、中央付近
    start_col = (COLUMNS // 2) - 2
    draw_mino(canvas, mino_type, offset_row=0, offset_col=start_col)

    root.mainloop()


if __name__ == "__main__":
    main()
