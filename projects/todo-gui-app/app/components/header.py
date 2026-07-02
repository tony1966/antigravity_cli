"""
header.py — 頂部標題列元件
顯示 App 名稱與即時統計（待完成 / 總計）。
"""

import tkinter as tk
from tkinter import ttk
from app.theme import Colors, Fonts, Spacing


class Header(ttk.Frame):
    """
    頂部 Header 元件。
    - 左側：App 標題 icon + 名稱
    - 右側：統計標籤（已完成 / 總計）
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, style="Header.TFrame", **kwargs)
        self._build_ui()

    def _build_ui(self):
        # 左側：標題區
        left_frame = ttk.Frame(self, style="Header.TFrame")
        left_frame.pack(side="left", padx=Spacing.LG, pady=Spacing.MD)

        # App icon + 標題
        title_row = ttk.Frame(left_frame, style="Header.TFrame")
        title_row.pack(anchor="w")

        self._icon_label = tk.Label(
            title_row,
            text="✅",
            font=(Fonts.FAMILY, 20),
            bg=Colors.BG_HEADER,
            fg=Colors.TEXT_PRIMARY,
        )
        self._icon_label.pack(side="left", padx=(0, Spacing.XS))

        self._title_label = ttk.Label(
            title_row,
            text="Todo List",
            style="Title.TLabel",
        )
        self._title_label.pack(side="left")

        # 副標題
        self._subtitle_label = ttk.Label(
            left_frame,
            text="保持專注，一次完成一件事",
            style="Subtitle.TLabel",
        )
        self._subtitle_label.pack(anchor="w", pady=(2, 0))

        # 右側：統計區
        right_frame = ttk.Frame(self, style="Header.TFrame")
        right_frame.pack(side="right", padx=Spacing.LG, pady=Spacing.MD)

        # 統計卡片容器（利用 tk.Frame 模擬圓角卡片邊框）
        stats_card = tk.Frame(
            right_frame,
            bg=Colors.BG_SURFACE,
            padx=Spacing.MD,
            pady=Spacing.SM,
        )
        stats_card.pack()

        # 上方：已完成數
        done_row = tk.Frame(stats_card, bg=Colors.BG_SURFACE)
        done_row.pack(fill="x")

        tk.Label(
            done_row,
            text="已完成",
            font=Fonts.SMALL,
            bg=Colors.BG_SURFACE,
            fg=Colors.TEXT_SECONDARY,
        ).pack(side="left")

        self._done_label = tk.Label(
            done_row,
            text="0",
            font=Fonts.BODY_BOLD,
            bg=Colors.BG_SURFACE,
            fg=Colors.ACCENT,
        )
        self._done_label.pack(side="right", padx=(Spacing.SM, 0))

        # 分隔線
        tk.Frame(stats_card, bg=Colors.BORDER, height=1).pack(
            fill="x", pady=(Spacing.XS, Spacing.XS)
        )

        # 下方：總計數
        total_row = tk.Frame(stats_card, bg=Colors.BG_SURFACE)
        total_row.pack(fill="x")

        tk.Label(
            total_row,
            text="總計",
            font=Fonts.SMALL,
            bg=Colors.BG_SURFACE,
            fg=Colors.TEXT_SECONDARY,
        ).pack(side="left")

        self._total_label = tk.Label(
            total_row,
            text="0",
            font=Fonts.BODY_BOLD,
            bg=Colors.BG_SURFACE,
            fg=Colors.TEXT_PRIMARY,
        )
        self._total_label.pack(side="right", padx=(Spacing.SM, 0))

    def update_stats(self, done: int, total: int) -> None:
        """更新統計數字。由 TodoApp 在資料變動後呼叫。"""
        self._done_label.config(text=str(done))
        self._total_label.config(text=str(total))

        # 全部完成時 icon 改為慶祝樣式
        if total > 0 and done == total:
            self._icon_label.config(text="🎉")
        else:
            self._icon_label.config(text="✅")
