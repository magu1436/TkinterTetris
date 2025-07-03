# Tkinter Tetris

This project is a small Tetris game built with Python's Tkinter.

## How to Run
1. Make sure Python 3 is installed. Tkinter comes with the standard installation.
2. Execute the following command in the repository root:

```bash
python main.py
```

A window will appear and the game will start.

## Default Key Bindings
- **Move left**: Left arrow
- **Move right**: Right arrow
- **Soft drop**: Down arrow
- **Hard drop**: Up arrow
- **Rotate right**: `e`
- **Rotate left**: `q`

These bindings are defined at the top of `main.py` and can be customized by changing the following constants:

```
KEY_LEFT = 'Left'
KEY_RIGHT = 'Right'
KEY_DOWN = 'Down'
KEY_UP = 'Up'
KEY_ROTATE_RIGHT = 'e'
KEY_ROTATE_LEFT = 'q'
```

Most of this program was developed via vibe coding with ChatGPT's `o4-mini-high` model.

---

# Tkinterテトリス

このプロジェクトは Python の Tkinter を用いたシンプルなテトリスゲームです。

## 起動方法
1. Python 3 をインストールしてください。Tkinter は標準で付属しています。
2. リポジトリのルートで次のコマンドを実行します。

```bash
python main.py
```

ゲームウィンドウが開きます。

## キー入力
- **左移動**: 左矢印キー
- **右移動**: 右矢印キー
- **ソフトドロップ**: 下矢印キー
- **ハードドロップ**: 上矢印キー
- **右回転**: `e`
- **左回転**: `q`

これらのバインドは `main.py` の冒頭で定義されており、値を変更することで好きなキーに変更できます。

なお、このプログラムの大部分は ChatGPT の `o4-mini-high` モデルを併用したバイブコーディングによって作成されました。

