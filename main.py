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
# 方向キー（変更可能）
KEY_LEFT = 'Left'
KEY_RIGHT = 'Right'
KEY_DOWN = 'Down'
KEY_UP = 'Up'

# Mino 種別を表す列挙型
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


def draw_mino(canvas: tk.Canvas, mtype: Mino, row: int, col: int) -> list[int]:
    """
    ミノを指定位置に描画し、オブジェクトIDリストを返す
    """
    ids: list[int] = []
    for r, c in MINOS[mtype]:
        x1, y1 = (col + c) * CELL_SIZE, (row + r) * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        ids.append(canvas.create_rectangle(x1, y1, x2, y2, fill=MINO_COLORS[mtype], outline=GRID_COLOR))
    return ids


def hard_drop(canvas: tk.Canvas, field: list[list[bool]], state: dict, start_col: int, root: tk.Tk) -> None:
    """
    ハードドロップ: 現在位置から一気に落下させ固定し次ミノを生成
    """
    mtype, row, col, ids = state['type'], state['row'], state['col'], state['ids']
    # 最大落下距離を計算
    drop_distance = ROWS
    for r, c in MINOS[mtype]:
        dist = 0
        while True:
            nr = row + r + dist + 1
            nc = col + c
            if nr >= ROWS or field[nr][nc]:
                break
            dist += 1
        drop_distance = min(drop_distance, dist)
    # 現ミノ削除
    for oid in ids:
        canvas.delete(oid)
    # 座標更新
    row += drop_distance
    state['row'] = row
    # 再描画
    state['ids'] = draw_mino(canvas, mtype, row, col)
    # 固定
    for r, c in MINOS[mtype]:
        field[row + r][col + c] = True
    # 新ミノ生成
    spawn_new_mino(canvas, field, state, start_col, root)


def spawn_new_mino(canvas: tk.Canvas, field: list[list[bool]], state: dict, start_col: int, root: tk.Tk) -> None:
    """
    新しいミノを生成し、落下処理をスケジュールする関数
    """
    # 既存の落下スケジュールをキャンセル
    if state.get('drop_job'):
        root.after_cancel(state['drop_job'])
    # ミノ選択・初期化
    mtype = random.choice(list(Mino))
    row = 0
    col = start_col
    max_r = max(r for r, _ in MINOS[mtype])
    # 描画
    ids = draw_mino(canvas, mtype, row, col)
    # 状態更新
    state.update({
        'type': mtype,
        'row': row,
        'col': col,
        'max_r': max_r,
        'ids': ids,
        'down': False
    })
    # 落下開始
    job = root.after(FALL_INTERVAL, lambda: drop(canvas, field, state, start_col, root))
    state['drop_job'] = job


def drop(canvas: tk.Canvas, field: list[list[bool]], state: dict, start_col: int, root: tk.Tk) -> None:
    """
    ミノを1行落下させ、衝突判定・固定・次ミノ生成を行う関数
    """
    mtype = state['type']
    row = state['row']
    col = state['col']
    max_r = state['max_r']
    ids = state['ids']
    down = state['down']
    # 衝突判定
    collision = False
    for r, c in MINOS[mtype]:
        nr, nc = row + r + 1, col + c
        if nr >= ROWS or field[nr][nc]:
            collision = True
            break
    if collision:
        # 固定
        for r, c in MINOS[mtype]:
            field[row + r][col + c] = True
        # 次ミノ生成
        spawn_new_mino(canvas, field, state, start_col, root)
        return
    # 削除
    for oid in ids:
        canvas.delete(oid)
    # 位置更新・再描画
    row += 1
    state['row'] = row
    state['ids'] = draw_mino(canvas, mtype, row, col)
    # 次回スケジュール
    interval = FAST_FALL_INTERVAL if down else FALL_INTERVAL
    job = root.after(interval, lambda: drop(canvas, field, state, start_col, root))
    state['drop_job'] = job


def try_move(canvas: tk.Canvas, field: list[list[bool]], state: dict, direction: int) -> None:
    """
    左右移動の衝突判定と移動処理
    """
    mtype = state['type']
    row = state['row']
    col = state['col']
    ids = state['ids']
    newc = col + direction
    # 範囲外・衝突チェック
    for r, c in MINOS[mtype]:
        if newc + c < 0 or newc + c >= COLUMNS or field[row + r][newc + c]:
            return
    # 移動
    for oid in ids:
        canvas.delete(oid)
    state['col'] = newc
    state['ids'] = draw_mino(canvas, mtype, row, newc)


def handle_move(canvas: tk.Canvas, field: list[list[bool]], state: dict, root: tk.Tk) -> None:
    """
    方向キー入力に応じた連続移動・高速落下を処理する
    """
    if state.get('left'):
        try_move(canvas, field, state, -1)
    if state.get('right'):
        try_move(canvas, field, state, 1)
    # 継続スケジュール
    root.after(MOVE_INTERVAL, lambda: handle_move(canvas, field, state, root))


def main() -> None:
    root = tk.Tk()
    root.title("Tetris Field")
    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
    canvas.pack()

    # フィールド状態: True=ブロックあり
    field = [[False] * COLUMNS for _ in range(ROWS)]
    draw_field(canvas)

    # 状態管理辞書
    state: dict = {'left': False, 'right': False, 'down': False, 'drop_job': None}

    # キーバインド設定
    root.bind(f"<KeyPress-{KEY_LEFT}>", lambda e: state.update(left=True))
    root.bind(f"<KeyRelease-{KEY_LEFT}>", lambda e: state.update(left=False))
    root.bind(f"<KeyPress-{KEY_RIGHT}>", lambda e: state.update(right=True))
    root.bind(f"<KeyRelease-{KEY_RIGHT}>", lambda e: state.update(right=False))
    root.bind(f"<KeyPress-{KEY_DOWN}>", lambda e: state.update(down=True))
    root.bind(f"<KeyRelease-{KEY_DOWN}>", lambda e: state.update(down=False))
    root.bind(f"<KeyPress-{KEY_UP}>", lambda e: hard_drop(canvas, field, state, (COLUMNS // 2) - 2, root))

    # 継続処理開始
    handle_move(canvas, field, state, root)
    spawn_new_mino(canvas, field, state, (COLUMNS // 2) - 2, root)

    root.mainloop()


if __name__ == "__main__":
    main()