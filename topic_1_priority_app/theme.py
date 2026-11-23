"""Colors and fonts for the standalone Topic 1 screen."""

import sys
from tkinter import font, ttk
from types import SimpleNamespace

import customtkinter as ctk

# Each pair contains the light and dark value.
COLORS = {
    "bg": ("#eef2f7", "#16181c"),
    "card": ("#ffffff", "#202329"),
    "field": ("#f8fafc", "#2a2e35"),
    "border": ("#d9dee8", "#33373f"),
    "border_strong": ("#c3cbd8", "#474c56"),
    "soft": ("#f1f4f9", "#2a2e35"),
    "text": ("#1f2937", "#e5e7eb"),
    "muted": ("#6b7280", "#9ca3af"),
    "accent": ("#2563eb", "#3b82f6"),
    "accent_hover": ("#1d4ed8", "#2563eb"),
    "accent_text": ("#1e40af", "#93c5fd"),
    "accent_soft": ("#e8efff", "#1e2b44"),
    "segment": ("#94a3b8", "#3b414b"),
    "scroll": ("#c5ccd8", "#454a54"),
    "scroll_hover": ("#a9b3c3", "#5a606b"),
    "error": ("#b91c1c", "#fca5a5"),
}
FONT = SimpleNamespace()
CFONT = SimpleNamespace()
SCALE = 1.0

def C(name):
    return COLORS[name]


def P():
    mode = 1 if ctk.get_appearance_mode() == "Dark" else 0
    return {name: pair[mode] for name, pair in COLORS.items()}


def px(size):
    """Scale measurements used by the plain Tk canvas and table."""
    return round(size * SCALE)


def setup_fonts(root):
    global SCALE
    SCALE = ctk.ScalingTracker.get_widget_scaling(root)

    mono = "Consolas" if sys.platform.startswith("win") else "TkFixedFont"
    if mono == "TkFixedFont":
        mono = font.nametofont(mono, root=root).actual("family")
    FONT.title = ctk.CTkFont(size=20, weight="bold")
    FONT.bold = ctk.CTkFont(size=14, weight="bold")
    FONT.ui = ctk.CTkFont(size=14)
    FONT.small = ctk.CTkFont(size=12)
    FONT.mono = ctk.CTkFont(family=mono, size=13)

    family = FONT.ui.cget("family")
    CFONT.ui = font.Font(root=root, family=family, size=-px(13))
    CFONT.bold = font.Font(root=root, family=family, size=-px(13), weight="bold")


def style_tables(root):
    p = P()
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "Result.Treeview", background=p["card"], fieldbackground=p["card"],
        foreground=p["text"], font=CFONT.ui, bordercolor=p["border"],
        rowheight=CFONT.ui.metrics("linespace") + px(14),
    )
    style.configure(
        "Result.Treeview.Heading", background=p["soft"], foreground=p["text"],
        font=CFONT.bold, padding=(px(4), px(6)),
    )
    style.map("Result.Treeview", background=[("selected", p["accent_soft"])],
              foreground=[("selected", p["text"])])
    style.map("Result.Treeview.Heading", background=[("active", p["accent_soft"])])
