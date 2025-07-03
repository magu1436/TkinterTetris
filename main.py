import tkinter as tk

# 定数定義
CELL_SIZE = 30             # セル1マスのピクセルサイズ
COLUMNS = 10               # フィールドの横マス数
ROWS = 20                  # フィールドの縦マス数
WIDTH = CELL_SIZE * COLUMNS  # キャンバス幅
HEIGHT = CELL_SIZE * ROWS    # キャンバス高さ
GRID_COLOR = "#000000"   # グリッド線の色
BACKGROUND_COLOR = "#CCCCCC" # 背景色


def draw_field(canvas: tk.Canvas) -> None:
    """
    フィールドの背景とグリッド線を描画する関数
    """
    # 背景を塗りつぶし
    canvas.create_rectangle(
        0, 0, WIDTH, HEIGHT,
        fill=BACKGROUND_COLOR,
        outline=""
    )
    # 縦線を描画
    for col in range(COLUMNS + 1):
        x = col * CELL_SIZE
        canvas.create_line(x, 0, x, HEIGHT, fill=GRID_COLOR)
    # 横線を描画
    for row in range(ROWS + 1):
        y = row * CELL_SIZE
        canvas.create_line(0, y, WIDTH, y, fill=GRID_COLOR)


def main() -> None:
    root = tk.Tk()
    root.title("Tetris Field")

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
    canvas.pack()

    draw_field(canvas)
    root.mainloop()


if __name__ == "__main__":
    main()
