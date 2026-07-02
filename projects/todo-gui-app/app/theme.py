"""
theme.py — 全域設計 Token 與 ttk 樣式設定
所有顏色、字體、間距常數都集中在此，方便日後統一調整外觀。
"""

import tkinter as tk
from tkinter import ttk

# ─────────────────────────────────────────
# 色彩 Palette
# ─────────────────────────────────────────
class Colors:
    # 背景層次
    BG_ROOT        = "#1A1A2E"   # 根視窗最底層背景（深藍黑）
    BG_SURFACE     = "#16213E"   # 卡片 / 面板背景
    BG_ITEM        = "#0F3460"   # Todo 列預設背景
    BG_ITEM_HOVER  = "#1A4A80"   # Todo 列 Hover 背景
    BG_ITEM_DONE   = "#0D2A4A"   # 已完成 Todo 列背景
    BG_INPUT       = "#1E2A45"   # 輸入框背景
    BG_HEADER      = "#0F3460"   # Header 背景
    BG_SCROLLBAR   = "#1A2A45"   # 捲軸背景

    # Accent / 互動色
    ACCENT         = "#7C6AF7"   # 主要 Accent（柔和紫）
    ACCENT_HOVER   = "#9B8BFF"   # Accent Hover 亮色
    ACCENT_PRESS   = "#5B4BD6"   # Accent 按下深色

    # 危險色（刪除）
    DANGER         = "#E05C7A"   # 刪除按鈕紅
    DANGER_HOVER   = "#FF7090"   # 刪除 Hover 亮紅

    # 文字色
    TEXT_PRIMARY   = "#E8EAF6"   # 主要文字（近白）
    TEXT_SECONDARY = "#9FA8DA"   # 次要文字（藍灰）
    TEXT_MUTED     = "#4A5568"   # 已完成 / 提示文字（暗灰）
    TEXT_ACCENT    = "#7C6AF7"   # Accent 文字
    TEXT_ERROR     = "#E05C7A"   # 錯誤提示文字

    # 邊框 / 分隔線
    BORDER         = "#2D3561"   # 一般邊框
    BORDER_FOCUS   = "#7C6AF7"   # 聚焦邊框（Accent）

    # 勾選框
    CHECK_DONE     = "#7C6AF7"   # 已完成勾選框色

    # 對話框
    DIALOG_BG      = "#1A1A2E"   # 確認對話框背景
    DIALOG_OVERLAY = "#00000080" # 半透明遮罩


# ─────────────────────────────────────────
# 字體設定
# ─────────────────────────────────────────
class Fonts:
    FAMILY      = "Segoe UI"      # Windows 原生現代字體
    FAMILY_MONO = "Consolas"      # 等寬備用

    APP_TITLE   = (FAMILY, 18, "bold")    # App 標題
    SECTION     = (FAMILY, 13, "bold")    # 區塊標題
    BODY        = (FAMILY, 11)            # 一般內文
    BODY_BOLD   = (FAMILY, 11, "bold")    # 粗體內文
    SMALL       = (FAMILY, 9)             # 小字 / 提示
    BUTTON      = (FAMILY, 10, "bold")    # 按鈕文字
    INPUT       = (FAMILY, 11)            # 輸入框
    STATS       = (FAMILY, 10)            # 統計數字
    EMPTY       = (FAMILY, 13)            # 空狀態提示
    STRIKE      = (FAMILY, 11, "overstrike")  # 已完成刪除線文字


# ─────────────────────────────────────────
# 間距 / 尺寸常數
# ─────────────────────────────────────────
class Spacing:
    XS  = 4
    SM  = 8
    MD  = 12
    LG  = 16
    XL  = 24
    XXL = 32

class Sizes:
    WINDOW_W     = 680
    WINDOW_H     = 580
    WINDOW_MIN_W = 480
    WINDOW_MIN_H = 400
    ITEM_HEIGHT  = 52      # 每筆 Todo 列高度（px）
    HEADER_H     = 80
    INPUT_BAR_H  = 60
    BUTTON_PAD_X = 16
    BUTTON_PAD_Y = 6
    RADIUS       = 8       # 圓角（供參考，ttk 部分以 padding 模擬）


# ─────────────────────────────────────────
# ttk Style 套用函式
# ─────────────────────────────────────────
def apply_theme(root: tk.Tk) -> ttk.Style:
    """
    建立並套用自訂 ttk Style。
    呼叫時機：Tk() 根視窗建立後、任何 Widget 建立前。
    回傳 style 物件供需要動態修改的元件使用。
    """
    style = ttk.Style(root)

    # 使用 'clam' 主題作為基底（最支援自訂色彩）
    style.theme_use("clam")

    # ── 根視窗背景 ──────────────────────────
    root.configure(bg=Colors.BG_ROOT)

    # ── TFrame ──────────────────────────────
    style.configure("TFrame",
                    background=Colors.BG_ROOT)

    style.configure("Surface.TFrame",
                    background=Colors.BG_SURFACE)

    style.configure("Header.TFrame",
                    background=Colors.BG_HEADER)

    style.configure("Item.TFrame",
                    background=Colors.BG_ITEM)

    style.configure("Input.TFrame",
                    background=Colors.BG_SURFACE)

    # ── TLabel ──────────────────────────────
    style.configure("TLabel",
                    background=Colors.BG_ROOT,
                    foreground=Colors.TEXT_PRIMARY,
                    font=Fonts.BODY)

    style.configure("Title.TLabel",
                    background=Colors.BG_HEADER,
                    foreground=Colors.TEXT_PRIMARY,
                    font=Fonts.APP_TITLE)

    style.configure("Subtitle.TLabel",
                    background=Colors.BG_HEADER,
                    foreground=Colors.TEXT_SECONDARY,
                    font=Fonts.STATS)

    style.configure("Stats.TLabel",
                    background=Colors.BG_HEADER,
                    foreground=Colors.ACCENT,
                    font=Fonts.BODY_BOLD)

    style.configure("Item.TLabel",
                    background=Colors.BG_ITEM,
                    foreground=Colors.TEXT_PRIMARY,
                    font=Fonts.BODY)

    style.configure("ItemDone.TLabel",
                    background=Colors.BG_ITEM_DONE,
                    foreground=Colors.TEXT_MUTED,
                    font=Fonts.STRIKE)

    style.configure("Empty.TLabel",
                    background=Colors.BG_SURFACE,
                    foreground=Colors.TEXT_MUTED,
                    font=Fonts.EMPTY)

    style.configure("Error.TLabel",
                    background=Colors.BG_SURFACE,
                    foreground=Colors.TEXT_ERROR,
                    font=Fonts.SMALL)

    style.configure("Surface.TLabel",
                    background=Colors.BG_SURFACE,
                    foreground=Colors.TEXT_PRIMARY,
                    font=Fonts.BODY)

    style.configure("Dialog.TLabel",
                    background=Colors.DIALOG_BG,
                    foreground=Colors.TEXT_PRIMARY,
                    font=Fonts.BODY)

    style.configure("DialogTitle.TLabel",
                    background=Colors.DIALOG_BG,
                    foreground=Colors.TEXT_PRIMARY,
                    font=Fonts.SECTION)

    # ── TButton ─────────────────────────────
    style.configure("TButton",
                    background=Colors.ACCENT,
                    foreground=Colors.TEXT_PRIMARY,
                    font=Fonts.BUTTON,
                    padding=(Sizes.BUTTON_PAD_X, Sizes.BUTTON_PAD_Y),
                    relief="flat",
                    borderwidth=0)

    style.map("TButton",
              background=[("active", Colors.ACCENT_HOVER),
                          ("pressed", Colors.ACCENT_PRESS)],
              foreground=[("active", Colors.TEXT_PRIMARY)])

    # 危險（刪除）按鈕
    style.configure("Danger.TButton",
                    background=Colors.BG_ITEM,
                    foreground=Colors.DANGER,
                    font=(Fonts.FAMILY, 13),
                    padding=(6, 4),
                    relief="flat",
                    borderwidth=0)

    style.map("Danger.TButton",
              background=[("active", Colors.BG_ITEM_HOVER)],
              foreground=[("active", Colors.DANGER_HOVER)])

    # 次要按鈕（對話框 Cancel）
    style.configure("Secondary.TButton",
                    background=Colors.BG_SURFACE,
                    foreground=Colors.TEXT_SECONDARY,
                    font=Fonts.BUTTON,
                    padding=(Sizes.BUTTON_PAD_X, Sizes.BUTTON_PAD_Y),
                    relief="flat",
                    borderwidth=0)

    style.map("Secondary.TButton",
              background=[("active", Colors.BORDER)],
              foreground=[("active", Colors.TEXT_PRIMARY)])

    # ── TCheckbutton ────────────────────────
    style.configure("TCheckbutton",
                    background=Colors.BG_ITEM,
                    foreground=Colors.TEXT_PRIMARY,
                    font=Fonts.BODY,
                    focuscolor=Colors.ACCENT,
                    indicatorcolor=Colors.BG_INPUT,
                    indicatorrelief="flat")

    style.map("TCheckbutton",
              background=[("active", Colors.BG_ITEM_HOVER)],
              indicatorcolor=[("selected", Colors.ACCENT),
                               ("active",  Colors.ACCENT_HOVER)])

    # ── TEntry ──────────────────────────────
    style.configure("TEntry",
                    fieldbackground=Colors.BG_INPUT,
                    foreground=Colors.TEXT_PRIMARY,
                    insertcolor=Colors.TEXT_PRIMARY,
                    bordercolor=Colors.BORDER,
                    lightcolor=Colors.BORDER,
                    darkcolor=Colors.BORDER,
                    focuscolor=Colors.BORDER_FOCUS,
                    font=Fonts.INPUT,
                    padding=(Spacing.SM, Spacing.SM))

    style.map("TEntry",
              bordercolor=[("focus", Colors.BORDER_FOCUS),
                           ("!focus", Colors.BORDER)],
              fieldbackground=[("focus", Colors.BG_INPUT),
                               ("!focus", Colors.BG_INPUT)])

    # ── TScrollbar ──────────────────────────
    style.configure("Vertical.TScrollbar",
                    background=Colors.BG_SCROLLBAR,
                    troughcolor=Colors.BG_SURFACE,
                    arrowcolor=Colors.TEXT_MUTED,
                    bordercolor=Colors.BG_SURFACE,
                    lightcolor=Colors.BG_SCROLLBAR,
                    darkcolor=Colors.BG_SCROLLBAR,
                    relief="flat",
                    arrowsize=12)

    style.map("Vertical.TScrollbar",
              background=[("active", Colors.ACCENT),
                          ("disabled", Colors.BG_SCROLLBAR)])

    # ── TSeparator ──────────────────────────
    style.configure("TSeparator",
                    background=Colors.BORDER)

    return style
