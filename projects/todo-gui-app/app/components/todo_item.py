"""
todo_item.py — 單筆 Todo 列元件
包含：勾選框（toggle done）、Todo 文字、刪除按鈕、Hover 效果。
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any
from app.theme import Colors, Fonts, Spacing
from app.dialogs.confirm_dialog import ConfirmDialog


class TodoItem(tk.Frame):
    """
    代表一筆 Todo 的 Row Widget。

    回呼函式：
      on_toggle(todo_id)  — 切換完成狀態
      on_delete(todo_id)  — 刪除（已在此元件內彈出確認視窗）
    """

    def __init__(
        self,
        master,
        todo: Dict[str, Any],
        on_toggle: Callable[[str], None],
        on_delete: Callable[[str], None],
        **kwargs,
    ):
        # 依完成狀態選擇背景色
        bg = Colors.BG_ITEM_DONE if todo["done"] else Colors.BG_ITEM
        super().__init__(master, bg=bg, **kwargs)

        self._todo    = todo
        self._on_toggle = on_toggle
        self._on_delete = on_delete
        self._bg_normal = bg
        self._bg_hover  = Colors.BG_ITEM_HOVER

        self._var = tk.BooleanVar(value=todo["done"])
        self._build_ui()
        self._bind_hover()

    # ── UI 建構 ──────────────────────────────────────────────────

    def _build_ui(self):
        done = self._todo["done"]
        bg   = self._bg_normal

        # 左側：完成狀態勾選框
        self._check = tk.Checkbutton(
            self,
            variable=self._var,
            command=self._on_check,
            bg=bg,
            activebackground=self._bg_hover,
            selectcolor=Colors.ACCENT if done else Colors.BG_INPUT,
            fg=Colors.ACCENT,
            activeforeground=Colors.ACCENT,
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        self._check.pack(side="left", padx=(Spacing.MD, Spacing.XS), pady=Spacing.MD)

        # 中間：Todo 文字
        text_fg   = Colors.TEXT_MUTED    if done else Colors.TEXT_PRIMARY
        text_font = Fonts.STRIKE         if done else Fonts.BODY

        self._text_label = tk.Label(
            self,
            text=self._todo["text"],
            font=text_font,
            bg=bg,
            fg=text_fg,
            anchor="w",
            wraplength=420,
            justify="left",
        )
        self._text_label.pack(
            side="left", fill="x", expand=True,
            padx=(0, Spacing.SM), pady=Spacing.MD,
        )

        # 右側：時間戳記（小字）
        created = self._todo.get("created_at", "")
        if created:
            # 只顯示 HH:MM
            time_str = created[11:16] if len(created) > 15 else created
            self._time_label = tk.Label(
                self,
                text=time_str,
                font=Fonts.SMALL,
                bg=bg,
                fg=Colors.TEXT_MUTED,
            )
            self._time_label.pack(side="right", padx=(0, Spacing.XS))

        # 右側：刪除按鈕（🗑 垃圾桶）
        self._del_btn = tk.Button(
            self,
            text="🗑",
            font=(Fonts.FAMILY, 13),
            bg=bg,
            fg=Colors.DANGER,
            activebackground=self._bg_hover,
            activeforeground=Colors.DANGER_HOVER,
            relief="flat",
            bd=0,
            padx=Spacing.SM,
            pady=Spacing.XS,
            cursor="hand2",
            command=self._on_delete_click,
        )
        self._del_btn.pack(side="right", padx=(0, Spacing.SM), pady=Spacing.SM)

        # 底部分隔線
        sep = tk.Frame(self, bg=Colors.BORDER, height=1)
        sep.pack(side="bottom", fill="x")

    # ── Hover 效果 ───────────────────────────────────────────────

    def _bind_hover(self):
        """為所有子 widget 綁定 hover enter/leave 事件。"""
        for widget in [self, self._check, self._text_label, self._del_btn]:
            widget.bind("<Enter>", self._on_enter, add="+")
            widget.bind("<Leave>", self._on_leave, add="+")
        if hasattr(self, "_time_label"):
            self._time_label.bind("<Enter>", self._on_enter, add="+")
            self._time_label.bind("<Leave>", self._on_leave, add="+")

    def _on_enter(self, event=None):
        self._set_bg(self._bg_hover)

    def _on_leave(self, event=None):
        self._set_bg(self._bg_normal)

    def _set_bg(self, color: str):
        """統一更新所有子 widget 的背景色。"""
        widgets = [self, self._check, self._text_label, self._del_btn]
        if hasattr(self, "_time_label"):
            widgets.append(self._time_label)
        for w in widgets:
            try:
                w.config(bg=color)
            except tk.TclError:
                pass

    # ── 事件處理 ─────────────────────────────────────────────────

    def _on_check(self):
        """勾選框被點擊，觸發 toggle 回呼。"""
        self._on_toggle(self._todo["id"])

    def _on_delete_click(self):
        """點擊刪除按鈕，彈出確認對話框。"""
        text_preview = self._todo["text"]
        if len(text_preview) > 30:
            text_preview = text_preview[:27] + "..."

        ConfirmDialog(
            parent=self.winfo_toplevel(),
            title="刪除確認",
            message="確定要刪除這筆待辦事項？",
            detail=f"「{text_preview}」",
            confirm_text="刪除",
            cancel_text="取消",
            on_confirm=lambda: self._on_delete(self._todo["id"]),
            danger=True,
        )
