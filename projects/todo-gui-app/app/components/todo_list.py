"""
todo_list.py — 可捲動的 Todo 列表容器
使用 Canvas + Frame + Scrollbar 組合實現捲動（tkinter 標準方案）。
支援滑鼠滾輪與空狀態 placeholder。
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Any
from app.theme import Colors, Fonts, Spacing
from app.components.todo_item import TodoItem


class TodoList(ttk.Frame):
    """
    可捲動的 Todo 列表容器。

    回呼函式（透傳給每個 TodoItem）：
      on_toggle(todo_id) — 切換完成狀態
      on_delete(todo_id) — 刪除
    """

    def __init__(
        self,
        master,
        on_toggle: Callable[[str], None],
        on_delete: Callable[[str], None],
        **kwargs,
    ):
        super().__init__(master, style="Surface.TFrame", **kwargs)
        self._on_toggle = on_toggle
        self._on_delete = on_delete
        self._items: List[TodoItem] = []
        self._build_ui()

    # ── UI 建構 ──────────────────────────────────────────────────

    def _build_ui(self):
        # 使用 Canvas + inner_frame 模擬可捲動區域
        self._canvas = tk.Canvas(
            self,
            bg=Colors.BG_SURFACE,
            bd=0,
            highlightthickness=0,
        )

        self._scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self._canvas.yview,
        )
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        # 捲軸右側，Canvas 填滿其餘空間
        self._scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        # Canvas 內的真實 Frame（所有 TodoItem 放在此）
        self._inner = tk.Frame(self._canvas, bg=Colors.BG_SURFACE)
        self._inner_window = self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw"
        )

        # 當 inner frame 大小改變時，更新 Canvas scrollregion
        self._inner.bind("<Configure>", self._on_inner_configure)
        # 當 Canvas 大小改變時，讓 inner frame 撐滿寬度
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # 滑鼠滾輪（Windows / Mac / Linux 三平台）
        self._canvas.bind("<MouseWheel>",   self._on_mousewheel_win)
        self._canvas.bind("<Button-4>",     self._on_mousewheel_up)
        self._canvas.bind("<Button-5>",     self._on_mousewheel_down)
        self._inner.bind("<MouseWheel>",    self._on_mousewheel_win)

    # ── 捲動事件 ─────────────────────────────────────────────────

    def _on_inner_configure(self, event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        self._canvas.itemconfig(self._inner_window, width=event.width)

    def _on_mousewheel_win(self, event):
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_up(self, event):
        self._canvas.yview_scroll(-1, "units")

    def _on_mousewheel_down(self, event):
        self._canvas.yview_scroll(1, "units")

    def _bind_scroll_to_item(self, item: TodoItem):
        """將滾輪事件透傳給 Canvas（讓子 widget 也能觸發捲動）。"""
        item.bind("<MouseWheel>", self._on_mousewheel_win, add="+")
        for child in item.winfo_children():
            child.bind("<MouseWheel>", self._on_mousewheel_win, add="+")

    # ── 渲染 ─────────────────────────────────────────────────────

    def render(self, todos: List[Dict[str, Any]]) -> None:
        """
        重新渲染整個列表。
        由 TodoApp 在資料變動後呼叫，傳入最新的 todos list。
        """
        # 清除現有元件
        for item in self._items:
            item.destroy()
        self._items.clear()

        # 移除舊的空狀態 placeholder（若有）
        if hasattr(self, "_empty_label") and self._empty_label.winfo_exists():
            self._empty_label.destroy()

        if not todos:
            self._show_empty_state()
            return

        # 建立 TodoItem（反序顯示：最新在上）
        for todo in reversed(todos):
            item = TodoItem(
                master=self._inner,
                todo=todo,
                on_toggle=self._on_toggle,
                on_delete=self._on_delete,
            )
            item.pack(fill="x", pady=(0, 2))
            self._bind_scroll_to_item(item)
            self._items.append(item)

        # 捲動到頂端（最新項目）
        self._canvas.yview_moveto(0.0)

    def _show_empty_state(self):
        """列表為空時顯示友善的空狀態提示。"""
        self._empty_label = tk.Frame(self._inner, bg=Colors.BG_SURFACE)
        self._empty_label.pack(fill="both", expand=True, pady=60)

        tk.Label(
            self._empty_label,
            text="🎯",
            font=(Fonts.FAMILY, 40),
            bg=Colors.BG_SURFACE,
            fg=Colors.TEXT_MUTED,
        ).pack()

        tk.Label(
            self._empty_label,
            text="尚無待辦事項",
            font=Fonts.EMPTY,
            bg=Colors.BG_SURFACE,
            fg=Colors.TEXT_MUTED,
        ).pack(pady=(Spacing.SM, Spacing.XS))

        tk.Label(
            self._empty_label,
            text="在上方輸入框新增你的第一筆任務吧！",
            font=Fonts.SMALL,
            bg=Colors.BG_SURFACE,
            fg=Colors.TEXT_MUTED,
        ).pack()

    def scroll_to_bottom(self):
        """捲動到底部（新增後可用）。"""
        self._canvas.yview_moveto(1.0)

    def scroll_to_top(self):
        """捲動到頂部。"""
        self._canvas.yview_moveto(0.0)
