"""
confirm_dialog.py — 自訂刪除確認對話框
使用 tk.Toplevel 實作，完全套用 App 深色主題，
而非使用外觀無法客製的系統 messagebox。
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from app.theme import Colors, Fonts, Spacing, Sizes


class ConfirmDialog(tk.Toplevel):
    """
    自訂確認對話框（Modal）。

    用法：
        dialog = ConfirmDialog(
            parent,
            title="刪除確認",
            message="確定要刪除這筆待辦事項？",
            on_confirm=callback_fn,
        )
        # dialog 是 modal，會阻擋父視窗互動直到關閉。
    """

    def __init__(
        self,
        parent: tk.Widget,
        title: str = "確認",
        message: str = "確定要執行此操作？",
        detail: str = "",
        confirm_text: str = "確認刪除",
        cancel_text: str = "取消",
        on_confirm: Optional[Callable] = None,
        danger: bool = True,
    ):
        super().__init__(parent)
        self._on_confirm = on_confirm
        self._result = False

        self._setup_window(parent, title)
        self._build_ui(message, detail, confirm_text, cancel_text, danger)
        self._animate_in()

        # Modal：阻擋父視窗
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    # ── 視窗設定 ─────────────────────────────────────────────────

    def _setup_window(self, parent: tk.Widget, title: str):
        self.title(title)
        self.configure(bg=Colors.DIALOG_BG)
        self.resizable(False, False)

        # 去除標準標題列（自訂外觀）
        self.overrideredirect(False)

        # 置中於父視窗
        self.update_idletasks()
        w, h = 380, 200
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        x = parent_x + (parent_w - w) // 2
        y = parent_y + (parent_h - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # 關閉按鈕 = 取消
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # ESC 鍵取消
        self.bind("<Escape>", lambda e: self._on_cancel())
        # Enter 鍵確認
        self.bind("<Return>", lambda e: self._on_confirm_click())

    # ── UI 建構 ──────────────────────────────────────────────────

    def _build_ui(
        self,
        message: str,
        detail: str,
        confirm_text: str,
        cancel_text: str,
        danger: bool,
    ):
        # 主容器（統一 padding）
        main = tk.Frame(self, bg=Colors.DIALOG_BG)
        main.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.LG)

        # ── Icon + 訊息區 ─────────────────────────────────────
        top_frame = tk.Frame(main, bg=Colors.DIALOG_BG)
        top_frame.pack(fill="x", pady=(Spacing.SM, Spacing.MD))

        # Warning icon
        icon = "🗑️" if danger else "❓"
        tk.Label(
            top_frame,
            text=icon,
            font=(Fonts.FAMILY, 28),
            bg=Colors.DIALOG_BG,
        ).pack(side="left", padx=(0, Spacing.MD))

        # 文字區
        text_frame = tk.Frame(top_frame, bg=Colors.DIALOG_BG)
        text_frame.pack(side="left", fill="x", expand=True)

        tk.Label(
            text_frame,
            text=message,
            font=Fonts.BODY_BOLD,
            bg=Colors.DIALOG_BG,
            fg=Colors.TEXT_PRIMARY,
            wraplength=260,
            justify="left",
        ).pack(anchor="w")

        if detail:
            tk.Label(
                text_frame,
                text=detail,
                font=Fonts.SMALL,
                bg=Colors.DIALOG_BG,
                fg=Colors.TEXT_MUTED,
                wraplength=260,
                justify="left",
            ).pack(anchor="w", pady=(Spacing.XS, 0))

        # ── 分隔線 ────────────────────────────────────────────
        tk.Frame(main, bg=Colors.BORDER, height=1).pack(fill="x", pady=(0, Spacing.MD))

        # ── 按鈕列 ────────────────────────────────────────────
        btn_frame = tk.Frame(main, bg=Colors.DIALOG_BG)
        btn_frame.pack(fill="x")

        # Cancel（左側）
        cancel_btn = tk.Button(
            btn_frame,
            text=cancel_text,
            font=Fonts.BUTTON,
            bg=Colors.BG_SURFACE,
            fg=Colors.TEXT_SECONDARY,
            activebackground=Colors.BORDER,
            activeforeground=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=Sizes.BUTTON_PAD_X,
            pady=Sizes.BUTTON_PAD_Y,
            cursor="hand2",
            command=self._on_cancel,
        )
        cancel_btn.pack(side="left")

        # Confirm（右側，Danger 色）
        confirm_bg = Colors.DANGER if danger else Colors.ACCENT
        confirm_hover = Colors.DANGER_HOVER if danger else Colors.ACCENT_HOVER

        self._confirm_btn = tk.Button(
            btn_frame,
            text=confirm_text,
            font=Fonts.BUTTON,
            bg=confirm_bg,
            fg=Colors.TEXT_PRIMARY,
            activebackground=confirm_hover,
            activeforeground=Colors.TEXT_PRIMARY,
            relief="flat",
            bd=0,
            padx=Sizes.BUTTON_PAD_X,
            pady=Sizes.BUTTON_PAD_Y,
            cursor="hand2",
            command=self._on_confirm_click,
        )
        self._confirm_btn.pack(side="right")

        # Hover 效果
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg=Colors.BORDER))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg=Colors.BG_SURFACE))
        self._confirm_btn.bind("<Enter>", lambda e: self._confirm_btn.config(bg=confirm_hover))
        self._confirm_btn.bind("<Leave>", lambda e: self._confirm_btn.config(bg=confirm_bg))

        # 預設聚焦在 Cancel（安全設計：避免誤按 Enter 就刪除）
        cancel_btn.focus_set()

    # ── 動畫 ─────────────────────────────────────────────────────

    def _animate_in(self):
        """淡入動畫（透過調整視窗透明度）。"""
        self.attributes("-alpha", 0.0)
        self._fade(0.0)

    def _fade(self, alpha: float):
        alpha = min(alpha + 0.08, 1.0)
        self.attributes("-alpha", alpha)
        if alpha < 1.0:
            self.after(16, lambda: self._fade(alpha))

    # ── 事件處理 ─────────────────────────────────────────────────

    def _on_confirm_click(self):
        self._result = True
        self.destroy()
        if self._on_confirm:
            self._on_confirm()

    def _on_cancel(self):
        self._result = False
        self.destroy()

    @property
    def result(self) -> bool:
        """回傳使用者選擇：True = 確認，False = 取消。"""
        return self._result
