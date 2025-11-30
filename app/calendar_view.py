import tkinter as tk
from tkinter import ttk
import calendar
from datetime import date

from time_utils import get_now


class CalendarPopup(tk.Toplevel):
    """
    Monthly calendar popup.
    Clicking a day calls WeekView.set_date().
    """

    def __init__(self, master, week_view):
        super().__init__(master)

        self.week_view = week_view

        self.title("Calendar")
        self.resizable(False, False)
        self.configure(bg="#1e1e1e")

        self.curr_date = week_view.get_selected_date()
        self.year = self.curr_date.year
        self.month = self.curr_date.month

        self._build_ui()
        self._render_month()

        self.transient(master)
        self.grab_set()

    def _build_ui(self):
        header = ttk.Frame(self, style="Top.TFrame")
        header.pack(fill=tk.X, padx=8, pady=5)

        self.btn_prev = ttk.Button(
            header, text="⟨", width=3, command=self._prev_month, style="Accent.TButton"
        )
        self.btn_prev.pack(side=tk.LEFT)

        self.lbl_month = ttk.Label(
            header, text="", style="Top.TLabel"
        )
        self.lbl_month.pack(side=tk.LEFT, expand=True)

        self.btn_next = ttk.Button(
            header, text="⟩", width=3, command=self._next_month, style="Accent.TButton"
        )
        self.btn_next.pack(side=tk.RIGHT)

        self.days_frame = ttk.Frame(self, style="Main.TFrame")
        self.days_frame.pack(padx=8, pady=(0, 8))

    def _render_month(self):
        for w in self.days_frame.winfo_children():
            w.destroy()

        cal = calendar.Calendar(firstweekday=0)  # Monday start

        month_name = calendar.month_name[self.month]
        self.lbl_month.config(text=f"{month_name} {self.year}")

        headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, name in enumerate(headers):
            lbl = ttk.Label(self.days_frame, text=name)
            lbl.grid(row=0, column=col, padx=3, pady=3)

        row = 1
        for week in cal.monthdatescalendar(self.year, self.month):
            for col, d in enumerate(week):
                if d.month != self.month:
                    lbl = ttk.Label(
                        self.days_frame,
                        text=str(d.day),
                        foreground="#666666",
                    )
                    lbl.grid(row=row, column=col, padx=2, pady=2)
                else:
                    btn = ttk.Button(
                        self.days_frame,
                        text=str(d.day),
                        width=4,
                        command=lambda dd=d: self._on_day_click(dd),
                    )
                    if d == self.curr_date:
                        btn.configure(style="Selected.TButton")
                    btn.grid(row=row, column=col, padx=2, pady=2)
            row += 1

    def _on_day_click(self, day: date):
        self.week_view.set_date(day)
        self.destroy()

    def _prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self._render_month()

    def _next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self._render_month()
