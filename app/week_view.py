import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta

from time_utils import format_date_pretty, get_now
from .calendar_view import CalendarPopup


class WeekView(ttk.Frame):
    """
    Weekly view with:
    - previous / next week
    - day buttons
    - today
    - calendar popup
    - exit button
    """

    def __init__(self, master, db):
        super().__init__(master, style="Top.TFrame")
        self.master = master
        self.db = db

        today = get_now().date()

        self.week_start: date = today - timedelta(days=today.weekday())
        self.selected_date: date = today

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        ctrl_frame = ttk.Frame(self, style="Top.TFrame")
        ctrl_frame.pack(fill=tk.X, pady=(0, 5))

        self.btn_prev = ttk.Button(
            ctrl_frame, text="⟨ Previous Week", command=self.prev_week
        )
        self.btn_prev.pack(side=tk.LEFT)

        self.lbl_range = ttk.Label(
            ctrl_frame,
            text="",
            style="Top.TLabel",
        )
        self.lbl_range.pack(side=tk.LEFT, expand=True, padx=20)

        self.btn_exit = ttk.Button(
            ctrl_frame, text="Exit", command=self._exit_app, style="TButton"
        )
        self.btn_exit.pack(side=tk.RIGHT, padx=5)

        self.btn_today = ttk.Button(
            ctrl_frame, text="Today", command=self.go_today, style="Accent.TButton"
        )
        self.btn_today.pack(side=tk.RIGHT, padx=5)

        self.btn_calendar = ttk.Button(
            ctrl_frame, text="Calendar", command=self.open_calendar, style="Accent.TButton"
        )
        self.btn_calendar.pack(side=tk.RIGHT, padx=5)

        self.btn_next = ttk.Button(
            ctrl_frame, text="Next Week ⟩", command=self.next_week
        )
        self.btn_next.pack(side=tk.RIGHT)

        days_frame = ttk.Frame(self, style="Top.TFrame")
        days_frame.pack(fill=tk.X, pady=5)

        self.day_buttons = []
        for i in range(7):
            btn = ttk.Button(
                days_frame,
                text=f"Day {i+1}",
                width=14,
                command=lambda idx=i: self._select_day(idx),
            )
            btn.grid(row=0, column=i, padx=3, pady=3)
            self.day_buttons.append(btn)

    def _refresh(self):
        start = self.week_start
        end = start + timedelta(days=6)

        self.lbl_range.config(
            text=f"{format_date_pretty(start)}  -  {format_date_pretty(end)}"
        )

        names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for i, btn in enumerate(self.day_buttons):
            d = start + timedelta(days=i)
            text = f"{names[i]}\n{d.strftime('%d.%m')}"

            if d == self.selected_date:
                btn.config(text=text, style="Selected.TButton")
            else:
                btn.config(text=text, style="TButton")

        if hasattr(self.master, "task_view"):
            self.master.task_view.update_day(self.selected_date)

    def get_selected_date(self) -> date:
        return self.selected_date

    def set_date(self, new_date: date):
        self.selected_date = new_date
        self.week_start = new_date - timedelta(days=new_date.weekday())
        self._refresh()

    def _select_day(self, idx: int):
        self.selected_date = self.week_start + timedelta(days=idx)
        self._refresh()

    def prev_week(self):
        self.week_start -= timedelta(days=7)
        self._refresh()

    def next_week(self):
        self.week_start += timedelta(days=7)
        self._refresh()

    def go_today(self):
        today = get_now().date()
        self.set_date(today)

    def open_calendar(self):
        CalendarPopup(self.master, self)

    def _exit_app(self):
        root = self.winfo_toplevel()
        if hasattr(root, "_on_close"):
            root._on_close()
        else:
            root.destroy()
