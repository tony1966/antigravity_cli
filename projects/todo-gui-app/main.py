"""
main.py — 程式進入點
負責：
  - 建立根視窗（Tk）
  - 設定視窗標題、圖示、尺寸、置中
  - 套用 ttk 主題
  - 啟動 TodoApp
"""

import tkinter as tk
from app.theme import apply_theme, Sizes, Colors
from app.app import TodoApp


def center_window(root: tk.Tk, width: int, height: int) -> None:
    """將視窗置中於螢幕。"""
    root.update_idletasks()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")


def main():
    # ── 建立根視窗 ────────────────────────────────────────────
    root = tk.Tk()
    root.title("✅ Todo List")
    root.minsize(Sizes.WINDOW_MIN_W, Sizes.WINDOW_MIN_H)

    # ── 套用自訂主題（必須在任何 Widget 建立前）────────────────
    apply_theme(root)

    # ── 視窗置中 ──────────────────────────────────────────────
    center_window(root, Sizes.WINDOW_W, Sizes.WINDOW_H)

    # ── 啟動主應用程式 ────────────────────────────────────────
    app = TodoApp(root)

    # ── 關閉視窗前確保資料已存檔 ──────────────────────────────
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    # ── 進入事件迴圈 ──────────────────────────────────────────
    root.mainloop()


if __name__ == "__main__":
    main()
