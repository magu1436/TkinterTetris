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
FALL_INTERVAL = 500           # ミノが1行落下するミリ秒
FAST_FALL_INTERVAL = 50       # 下キー押下時のミリ秒
MOVE_INTERVAL = 100           # ミノ移動間隔（ミリ秒）

# キー定義（変更可能）
KEY_LEFT = 'Left'
KEY_RIGHT = 'Right'
KEY_DOWN = 'Down'
KEY_UP = 'Up'
KEY_ROTATE_RIGHT = 'e'
KEY_ROTATE_LEFT = 'q'

# Mino 種別を表す列挙型
class Mino(StrEnum):
    I = 'I'; O = 'O'; S = 'S'; Z = 'Z'; J = 'J'; L = 'L'; T = 'T'

# 基本ミノ定義
BASE_MINOS = {
    Mino.I: [(0,0),(0,1),(0,2),(0,3)],
    Mino.O: [(0,0),(0,1),(1,0),(1,1)],
    Mino.S: [(0,1),(0,2),(1,0),(1,1)],
    Mino.Z: [(0,0),(0,1),(1,1),(1,2)],
    Mino.J: [(0,0),(1,0),(1,1),(1,2)],
    Mino.L: [(0,2),(1,0),(1,1),(1,2)],
    Mino.T: [(0,1),(1,0),(1,1),(1,2)],
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
    Mino.I: (0.5,1.5), Mino.O: (0.5,0.5),
    Mino.S: (1,1), Mino.Z: (1,1),
    Mino.J: (1,1), Mino.L: (1,1), Mino.T: (1,1),
}

# グリッド状態とブロックID保持
field_grid = [[False]*COLUMNS for _ in range(ROWS)]
block_ids = [[None]*COLUMNS for _ in range(ROWS)]

# ユーティリティ関数
def valid_position(field, shape, row, col):
    for r,c in shape:
        nr, nc = row+r, col+c
        if nc<0 or nc>=COLUMNS or nr<0 or nr>=ROWS or field[nr][nc]:
            return False
    return True

def rotate_shape(shape, mtype, direction):
    pr,pc = PIVOTS[mtype]
    out = []
    for r,c in shape:
        dr,dc = r-pr, c-pc
        if direction==1:
            nr, nc = pr+dc, pc-dr
        else:
            nr, nc = pr-dc, pc+dr
        out.append((int(round(nr)), int(round(nc))))
    return out

# 描画関数
def draw_field(canvas):
    canvas.create_rectangle(0,0,WIDTH,HEIGHT,fill=BACKGROUND_COLOR,outline="")
    for i in range(COLUMNS+1): canvas.create_line(i*CELL_SIZE,0,i*CELL_SIZE,HEIGHT,fill=GRID_COLOR)
    for i in range(ROWS+1):    canvas.create_line(0,i*CELL_SIZE,WIDTH,i*CELL_SIZE,fill=GRID_COLOR)

def draw_cell(canvas,row,col,color):
    x,y = col*CELL_SIZE, row*CELL_SIZE
    return canvas.create_rectangle(x,y,x+CELL_SIZE,y+CELL_SIZE,fill=color,outline=GRID_COLOR)

def clear_lines(canvas):
    r = ROWS-1
    while r>=0:
        if all(field_grid[r][c] for c in range(COLUMNS)):
            # 削除
            for c in range(COLUMNS):
                oid = block_ids[r][c]; canvas.delete(oid)
            # 下げる
            for rr in range(r-1,-1,-1):
                for c in range(COLUMNS):
                    oid = block_ids[rr][c]
                    if oid: canvas.move(oid,0,CELL_SIZE)
                    block_ids[rr+1][c] = block_ids[rr][c]
                    field_grid[rr+1][c] = field_grid[rr][c]
            # クリア最上行
            for c in range(COLUMNS): block_ids[0][c]=None; field_grid[0][c]=False
        else:
            r-=1

# ハードドロップ

def hard_drop(canvas, field, state, start_col, root):
    mtype = state['type']; row = state['row']; col = state['col'];
    shape = state['shape']; ids = state['ids']
    # 最大落下距離計算
    min_dist = ROWS
    for sr,sc in shape:
        dist=0
        while True:
            nr = row+sr+dist+1
            if nr>=ROWS or field[nr][col+sc]: break
            dist+=1
        min_dist = min(min_dist, dist)
    # 削除
    for oid in ids: canvas.delete(oid)
    # 固定配置
    for sr,sc in shape:
        r1 = row+sr+min_dist; c1 = col+sc
        oid = draw_cell(canvas,r1,c1,MINO_COLORS[mtype])
        block_ids[r1][c1] = oid
        field[r1][c1] = True
    clear_lines(canvas)
    spawn_new_mino(canvas,field,state,start_col,root)

# 新ミノ生成

def spawn_new_mino(canvas, field, state, start_col, root):
    if state.get('job'): root.after_cancel(state['job'])
    mtype = random.choice(list(Mino)); shape = BASE_MINOS[mtype]
    row,col = 0,start_col
    ids = [draw_cell(canvas,row+sr,col+sc,MINO_COLORS[mtype]) for sr,sc in shape]
    state.update(type=mtype,shape=shape,row=row,col=col,ids=ids,down=False)
    job = root.after(FALL_INTERVAL, lambda: drop(canvas,field,state,start_col,root))
    state['job']=job

# 自動落下

def drop(canvas, field, state, start_col, root):
    mtype,shape,row,col,ids,down = (
        state['type'],state['shape'],state['row'],state['col'],state['ids'],state['down']
    )
    # 衝突?
    for sr,sc in shape:
        nr=row+sr+1
        if nr>=ROWS or field[nr][col+sc]:
            # 固定
            for i,(sr2,sc2) in enumerate(shape):
                r1=row+sr2; c1=col+sc2
                block_ids[r1][c1]=ids[i]; field[r1][c1]=True
            clear_lines(canvas)
            return spawn_new_mino(canvas,field,state,start_col,root)
    # 移動
    for oid in ids: canvas.delete(oid)
    row+=1; state['row']=row
    new_ids=[draw_cell(canvas,row+sr,col+sc,MINO_COLORS[mtype]) for sr,sc in shape]
    state['ids']=new_ids
    interval = FAST_FALL_INTERVAL if down else FALL_INTERVAL
    job = root.after(interval, lambda: drop(canvas,field,state,start_col,root))
    state['job']=job

# 左右移動

def try_move(canvas, field, state, direction):
    row,col=state['row'],state['col']; shape=state['shape']; ids=state['ids']
    newc=col+direction
    if not valid_position(field,shape,row,newc): return
    for oid in ids: canvas.delete(oid)
    state['col']=newc
    state['ids']=[draw_cell(canvas,row+sr,newc+sc,MINO_COLORS[state['type']]) for sr,sc in shape]

# 回転

def rotate_mino(canvas, field, state, direction):
    mt,shape,row,col,ids = (
        state['type'],state['shape'],state['row'],state['col'],state['ids']
    )
    new_shape=rotate_shape(shape,mt,direction)
    if not valid_position(field,new_shape,row,col): return
    for oid in ids: canvas.delete(oid)
    state['shape']=new_shape
    state['ids']=[draw_cell(canvas,row+sr,col+sc,MINO_COLORS[mt]) for sr,sc in new_shape]

# 移動ハンドラ

def handle_move(canvas, field, state, root):
    if state.get('left'): try_move(canvas,field,state,-1)
    if state.get('right'): try_move(canvas,field,state,1)
    root.after(MOVE_INTERVAL, lambda: handle_move(canvas,field,state,root))

# メイン

def main():
    root=tk.Tk(); root.title("Tetris Field")
    canvas=tk.Canvas(root,width=WIDTH,height=HEIGHT); canvas.pack()
    draw_field(canvas)
    state={'left':False,'right':False,'down':False,'job':None}
    root.bind(f"<KeyPress-{KEY_LEFT}>",lambda e: state.update(left=True))
    root.bind(f"<KeyRelease-{KEY_LEFT}>",lambda e: state.update(left=False))
    root.bind(f"<KeyPress-{KEY_RIGHT}>",lambda e: state.update(right=True))
    root.bind(f"<KeyRelease-{KEY_RIGHT}>",lambda e: state.update(right=False))
    root.bind(f"<KeyPress-{KEY_DOWN}>",lambda e: state.update(down=True))
    root.bind(f"<KeyRelease-{KEY_DOWN}>",lambda e: state.update(down=False))
    root.bind(f"<KeyPress-{KEY_UP}>",lambda e: hard_drop(canvas,field_grid,state,(COLUMNS//2)-2,root))
    root.bind(f"<KeyPress-{KEY_ROTATE_RIGHT}>",lambda e: rotate_mino(canvas,field_grid,state,1))
    root.bind(f"<KeyPress-{KEY_ROTATE_LEFT}>",lambda e: rotate_mino(canvas,field_grid,state,-1))
    handle_move(canvas,field_grid,state,root)
    spawn_new_mino(canvas,field_grid,state,(COLUMNS//2)-2,root)
    root.mainloop()

if __name__=="__main__": main()
