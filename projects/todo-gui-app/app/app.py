"""
app.py — 主應用程式控制器
整合 TodoStorage（資料層）與所有 UI 元件，管理資料流與事件。
"""

import tkinter as tk
from tkinter import ttk
from app.storage import TodoStorage
from app.theme import Colors, Spacing, Sizes
from app.components.header import Header
from app.components.input_bar import InputBar
from app.components.todo_list import TodoList


class TodoApp(ttk.Frame):
    """
    主應用程式元件。
    負責：
      - 持有 TodoStorage 實例（唯一資料來源）
      - 組裝所有 UI 子元件
      - 協調「資料變動 → 重新渲染」的單向資料流
      - 管理全域鍵盤快捷鍵
    """

    def __init__(self, master: tk.Tk, **kwargs):
        super().__init__(master, style="TFrame", **kwargs)
        self._root   = master
        self._storage = TodoStorage()
        self._build_ui()
        self._bind_shortcuts()
        self._refresh()   # 初始渲染

    # ── UI 建構 ──────────────────────────────────────────────────

    def _build_ui(self):
        self.pack(fill="both", expand=True)

        # ── Header ───────────────────────────────────────────
        self._header = Header(self)
        self._header.pack(fill="x")

        # Header 底部細線
        tk.Frame(self, bg=Colors.BORDER, height=2).pack(fill="x")

        # ── InputBar ─────────────────────────────────────────
        self._input_bar = InputBar(self, on_add=self._handle_add)
        self._input_bar.pack(fill="x")

        # InputBar 底部細線
        tk.Frame(self, bg=Colors.BORDER, height=1).pack(fill="x")

        # ── TodoList ─────────────────────────────────────────
        self._todo_list = TodoList(
            self,
            on_toggle=self._handle_toggle,
            on_delete=self._handle_delete,
        )
        self._todo_list.pack(fill="both", expand=True)

        # ── 底部狀態列 ────────────────────────────────────────
        self._build_statusbar()

    def _build_statusbar(self):
        """底部狀態列：顯示快捷鍵提示。"""
        tk.Frame(self, bg=Colors.BORDER, height=1).pack(fill="x")

        bar = tk.Frame(self, bg=Colors.BG_SURFACE)
        bar.pack(fill="x")

        hints = [
            ("Enter", "新增"),
            ("Ctrl+N", "聚焦輸入框"),
            ("Esc", "取消對話框"),
        ]
        for key, desc in hints:
            tk.Label(
                bar,
                text=f"  {key}",
                font=(("Consolas", 8)),
                bg=Colors.BG_SURFACE,
                fg=Colors.ACCENT,
            ).pack(side="left")
            tk.Label(
                bar,
                text=f" {desc}",
                font=(("Segoe UI", 8)),
                bg=Colors.BG_SURFACE,
                fg=Colors.TEXT_MUTED,
            ).pack(side="left")
            tk.Label(
                bar,
                text="  │",
                font=(("Segoe UI", 8)),
                bg=Colors.BG_SURFACE,
                fg=Colors.BORDER,
            ).pack(side="left")

        # 右側版本號
        tk.Label(
            bar,
            text="v1.0  ",
            font=(("Segoe UI", 8)),
            bg=Colors.BG_SURFACE,
            fg=Colors.TEXT_MUTED,
        ).pack(side="right")

    # ── 快捷鍵 ───────────────────────────────────────────────────

    def _bind_shortcuts(self):
        """綁定全域鍵盤快捷鍵（在根視窗層級）。"""
        self._root.bind("<Control-n>", self._shortcut_focus_input)
        self._root.bind("<Control-N>", self._shortcut_focus_input)

    def _shortcut_focus_input(self, event=None):
        self._input_bar.focus_entry()

    # ── 資料事件處理 ─────────────────────────────────────────────

    def _handle_add(self, text: str) -> bool:
        """
        處理新增 Todo。
        InputBar 呼叫此方法，回傳 True（成功）或 False（失敗）。
        """
        todo = self._storage.add(text)
        if todo is None:
            return False
        self._refresh()
        return True

    def _handle_toggle(self, todo_id: str) -> None:
        """處理切換完成狀態。"""
        self._storage.toggle_done(todo_id)
        self._refresh()

    def _handle_delete(self, todo_id: str) -> None:
        """處理刪除（確認對話框已在 TodoItem 層顯示，此處直接刪除）。"""
        self._storage.delete(todo_id)
        self._refresh()

    # ── 重新渲染 ─────────────────────────────────────────────────

    def _refresh(self) -> None:
        """
        資料變動後的統一重新渲染入口。
        1. 更新 Header 統計
        2. 重新渲染 TodoList
        """
        todos  = self._storage.get_all()
        done   = self._storage.count_done()
        total  = self._storage.count_total()

        self._header.update_stats(done, total)
        self._todo_list.render(todos)
