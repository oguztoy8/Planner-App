import tkinter as tk
from tkinter import ttk

from .week_view import WeekView
from .task_view import TaskView
from .status_bar import StatusBar
from .clock_service import ClockService
from .timer_service import TimerService


class PlannerApp(tk.Tk):
    def __init__(self, db):
        super().__init__()

        self.db = db

        # Window
        self.title("Planner App")
        self.geometry("1100x650")
        self.minsize(900, 550)

        dark_bg = "#1e1e1e"
        panel_bg = "#252526"
        text = "#f0f0f0"
        accent = "#007acc"

        self.configure(bg=dark_bg)
        self.option_add("*Font", "SegoeUI 10")

        # ----- Styles / Theme -----
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Frames
        self.style.configure("TFrame", background=dark_bg)
        self.style.configure("Main.TFrame", background=dark_bg)
        self.style.configure("Top.TFrame", background=panel_bg)
        self.style.configure("Side.TFrame", background=panel_bg)

        # Labels
        self.style.configure("TLabel", background=dark_bg, foreground=text)
        self.style.configure("Top.TLabel", background=panel_bg, foreground=text)

        # Default button
        self.style.configure(
            "TButton",
            background="#333333",
            foreground=text,
            padding=6,
            borderwidth=0,
        )
        self.style.map(
            "TButton",
            background=[("active", "#444444"), ("pressed", "#222222")],
        )

        # Accent button
        self.style.configure(
            "Accent.TButton",
            background=accent,
            foreground="white",
            padding=6,
            borderwidth=0,
        )
        self.style.map(
            "Accent.TButton",
            background=[("active", "#108ee9"), ("pressed", "#0b64a0")],
        )

        # Selected day button
        self.style.configure(
            "Selected.TButton",
            background=accent,
            foreground="white",
        )
        self.style.map(
            "Selected.TButton",
            background=[("active", "#108ee9")]
        )

        # Treeview dark + bigger font
        self.style.configure(
            "Treeview",
            background=dark_bg,
            foreground=text,
            fieldbackground=dark_bg,
            bordercolor="#3c3c3c",
            borderwidth=1,
            rowheight=26,
            font=("SegoeUI", 11),
        )
        self.style.configure(
            "Treeview.Heading",
            background=panel_bg,
            foreground=text,
            font=("SegoeUI", 10, "bold"),
        )
        self.style.map(
            "Treeview.Heading",
            background=[("active", panel_bg)],
            foreground=[("active", text)],
        )
        self.style.map(
            "Treeview",
            background=[("selected", "#094771")],
            foreground=[("selected", "#ffffff")],
        )

        # Dark entry
        self.style.configure(
            "Dark.TEntry",
            fieldbackground="#2d2d30",
            foreground="white",
            bordercolor="#3c3c3c",
            lightcolor="#3c3c3c",
            darkcolor="#3c3c3c",
        )

        # ----- Layout -----
        self._create_layout()

        self.clock_service = ClockService(self.status_bar)
        self.timer_service = TimerService(self.task_view)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_layout(self):
        self.week_view = WeekView(self, self.db)
        self.week_view.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        middle = ttk.Frame(self, style="Main.TFrame")
        middle.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.task_view = TaskView(middle, self.db, self.week_view)
        self.task_view.pack(fill=tk.BOTH, expand=True)

        self.status_bar = StatusBar(self)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _on_close(self):
        try:
            self.timer_service.stop()
            self.clock_service.stop()
        except Exception:
            pass

        try:
            self.db.close()
        except Exception:
            pass

        self.destroy()
