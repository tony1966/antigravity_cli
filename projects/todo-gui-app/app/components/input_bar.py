"""
input_bar.py — 新增 Todo 輸入列元件
包含文字輸入框與 Add 按鈕，支援 Enter 鍵送出與空輸入驗證。
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from app.theme import Colors, Fonts, Spacing, Sizes


class InputBar(ttk.Frame):
    """
    新增 Todo 的輸入列。
    - ttk.Entry：輸入新 Todo 文字
    - Add 按鈕 / Enter 鍵：觸發新增
    - 空輸入驗證：顯示紅色邊框與錯誤提示
    - on_add callback：新增成功後通知 App 層
    """

    PLACEHOLDER = "新增待辦事項..."

    def __init__(self, master, on_add: Callable[[str], bool], **kwargs):
        """
        on_add: 接收文字字串，若新增成功回傳 True，失敗（空值）回傳 False。
        """
        super().__init__(master, style="Input.TFrame", **kwargs)
        self._on_add = on_add
        self._error_after_id: Optional[str] = None
        self._build_ui()

    def _build_ui(self):
        # 外層 padding 容器
        inner = ttk.Frame(self, style="Input.TFrame")
        inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)

        # ── 輸入框區域 ────────────────────────────────────────
        entry_container = tk.Frame(
            inner,
            bg=Colors.BG_INPUT,
            highlightbackground=Colors.BORDER,
            highlightthickness=2,
            bd=0,
        )
        entry_container.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))

        self._entry = tk.Entry(
            entry_container,
            font=Fonts.INPUT,
            bg=Colors.BG_INPUT,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
        )
        self._entry.pack(
            fill="x", padx=Spacing.MD, pady=Spacing.SM + 2
        )

        # Placeholder 邏輯
        self._show_placeholder()
        self._entry.bind("<FocusIn>",  self._on_focus_in)
        self._entry.bind("<FocusOut>", self._on_focus_out)
        self._entry.bind("<Return>",   self._on_submit)
        self._entry.bind("<Key>",      self._clear_error)

        # ── Add 按鈕 ──────────────────────────────────────────
        self._add_btn = tk.Button(
            inner,
            text="＋ 新增",
            font=Fonts.BUTTON,
            bg=Colors.ACCENT,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.ACCENT_HOVER,
            activeforeground=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=Sizes.BUTTON_PAD_X,
            pady=Sizes.BUTTON_PAD_Y,
            cursor="hand2",
            command=self._on_submit,
        )
        self._add_btn.pack(side="left")

        # ── 錯誤提示標籤（初始隱藏）─────────────────────────
        self._error_label = ttk.Label(
            self,
            text="⚠ 請輸入待辦事項內容",
            style="Error.TLabel",
        )
        # 不 pack，僅在需要時 place

        # Hover 效果
        self._add_btn.bind("<Enter>", lambda e: self._add_btn.config(bg=Colors.ACCENT_HOVER))
        self._add_btn.bind("<Leave>", lambda e: self._add_btn.config(bg=Colors.ACCENT))

        # 儲存 entry_container 供邊框變色使用
        self._entry_container = entry_container

    # ── Placeholder ─────────────────────────────────────────────

    def _show_placeholder(self):
        if not self._entry.get():
            self._entry.insert(0, self.PLACEHOLDER)
            self._entry.config(fg=Colors.TEXT_MUTED)
            self._is_placeholder = True
        else:
            self._is_placeholder = False

    def _on_focus_in(self, event=None):
        if getattr(self, "_is_placeholder", False):
            self._entry.delete(0, "end")
            self._entry.config(fg=Colors.TEXT_PRIMARY)
            self._is_placeholder = False
        # 聚焦時邊框變成 Accent 色
        self._entry_container.config(highlightbackground=Colors.BORDER_FOCUS)

    def _on_focus_out(self, event=None):
        if not self._entry.get().strip():
            self._show_placeholder()
        # 失焦時還原邊框
        self._entry_container.config(highlightbackground=Colors.BORDER)

    # ── 提交 ────────────────────────────────────────────────────

    def _on_submit(self, event=None):
        text = self._get_real_text()
        if not text:
            self._show_error()
            return
        success = self._on_add(text)
        if success:
            self._entry.delete(0, "end")
            self._show_placeholder()
            self._clear_error()
        else:
            self._show_error()

    def _get_real_text(self) -> str:
        """取得真實文字（排除 placeholder）。"""
        if getattr(self, "_is_placeholder", False):
            return ""
        return self._entry.get().strip()

    # ── 驗證回饋 ────────────────────────────────────────────────

    def _show_error(self):
        """顯示紅色邊框與錯誤訊息，3 秒後自動清除。"""
        self._entry_container.config(highlightbackground=Colors.DANGER)
        self._error_label.place(relx=0, rely=1.0, anchor="nw",
                                x=Spacing.LG, y=-2)
        # 取消舊的 after（避免重複）
        if self._error_after_id:
            self.after_cancel(self._error_after_id)
        self._error_after_id = self.after(3000, self._clear_error)
        # 讓輸入框 shake 動畫（簡單的左右移動）
        self._shake(self._entry_container)

    def _clear_error(self, event=None):
        """清除錯誤狀態。"""
        focused = self.focus_get() == self._entry
        self._entry_container.config(
            highlightbackground=Colors.BORDER_FOCUS if focused else Colors.BORDER
        )
        self._error_label.place_forget()
        if self._error_after_id:
            self.after_cancel(self._error_after_id)
            self._error_after_id = None

    def _shake(self, widget, times: int = 6, distance: int = 4):
        """簡單的水平 shake 動畫（利用 place offset 模擬）。"""
        original_x = 0
        offsets = []
        for i in range(times):
            offsets.append(distance if i % 2 == 0 else -distance)
        offsets.append(0)

        def _step(idx):
            if idx >= len(offsets):
                return
            # 使用 pack_configure 偏移 padx 模擬晃動
            dx = offsets[idx]
            widget.config(highlightbackground=Colors.DANGER)
            self.after(40, lambda: _step(idx + 1))

        _step(0)

    # ── 公開方法 ─────────────────────────────────────────────────

    def focus_entry(self):
        """聚焦到輸入框（供快捷鍵呼叫）。"""
        self._entry.focus_set()
        self._on_focus_in()
