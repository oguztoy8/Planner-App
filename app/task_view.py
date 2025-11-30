import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from typing import Optional

from models import Task
from time_utils import format_duration, get_now, format_date_pretty


class TaskView(ttk.Frame):
   

    def __init__(self, master, db, week_view):
        super().__init__(master, style="Main.TFrame")

        self.db = db
        self.week_view = week_view

        self.tasks_by_item = {}
        self.context_item: Optional[str] = None

        self._drag_item: Optional[str] = None

        self._build_ui()

    # ----------------------------------------------------------------------
    def _build_ui(self):
        container = ttk.Frame(self, style="Main.TFrame")
        container.pack(fill=tk.BOTH, expand=True)

        # Left panel – add task
        left = ttk.Frame(container, style="Side.TFrame")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        lbl_day = ttk.Label(left, text="Selected day:", style="Top.TLabel")
        lbl_day.pack(anchor="w", pady=(8, 0))

        self.lbl_day_value = ttk.Label(left, text="", style="Top.TLabel")
        self.lbl_day_value.pack(anchor="w", pady=(0, 10))

        ttk.Label(left, text="New task title:", style="Top.TLabel").pack(anchor="w")
        self.entry_title = ttk.Entry(left, width=25, style="Dark.TEntry")
        self.entry_title.pack(anchor="w", pady=3)

        ttk.Label(left, text="Description (optional):", style="Top.TLabel").pack(anchor="w")
        self.txt_desc = tk.Text(
            left,
            width=25,
            height=6,
            bg="#2d2d30",
            fg="#ffffff",
            insertbackground="white",
            relief=tk.FLAT,
            bd=1,
            highlightbackground="#3c3c3c",
            highlightcolor="#3c3c3c",
        )
        self.txt_desc.pack(anchor="w", pady=3)

        self.btn_add = ttk.Button(
            left, text="Add task", command=self.add_task, style="Accent.TButton"
        )
        self.btn_add.pack(anchor="w", pady=5)

        # Right panel – main list + summary tabs
        right = ttk.Frame(container, style="Main.TFrame")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        lbl_main = ttk.Label(right, text="Tasks for selected day", style="Top.TLabel")
        lbl_main.pack(anchor="w", pady=(4, 0))

        # Main list: Task, Description, Status, Duration
        cols = ("title", "description", "status", "duration")

        self.tree = ttk.Treeview(
            right,
            columns=cols,
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("title", text="Task")
        self.tree.heading("description", text="Description")
        self.tree.heading("status", text="Status")
        self.tree.heading("duration", text="Duration")

        self.tree.column("title", width=260)
        self.tree.column("description", width=260, anchor="w")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("duration", width=120, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        scrollbar = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Summary tabs
        lbl_lists = ttk.Label(
            right, text="Global task lists", style="Top.TLabel"
        )
        lbl_lists.pack(anchor="w", pady=(8, 0))

        self.nb = ttk.Notebook(right)
        self.nb.pack(fill=tk.BOTH, expand=False, pady=(2, 0))

        # To-do
        frame_todo = ttk.Frame(self.nb, style="Main.TFrame")
        self.nb.add(frame_todo, text="To-do")

        self.tree_todo = ttk.Treeview(
            frame_todo,
            columns=("title", "date", "duration"),
            show="headings",
            selectmode="browse",
        )
        self.tree_todo.heading("title", text="Task")
        self.tree_todo.heading("date", text="Date")
        self.tree_todo.heading("duration", text="Duration")
        self.tree_todo.column("title", width=350)
        self.tree_todo.column("date", width=110, anchor="center")
        self.tree_todo.column("duration", width=110, anchor="center")
        self.tree_todo.pack(fill=tk.BOTH, expand=True)

        # Done
        frame_done = ttk.Frame(self.nb, style="Main.TFrame")
        self.nb.add(frame_done, text="Completed")

        self.tree_done = ttk.Treeview(
            frame_done,
            columns=("title", "date", "duration"),
            show="headings",
            selectmode="browse",
        )
        self.tree_done.heading("title", text="Task")
        self.tree_done.heading("date", text="Date")
        self.tree_done.heading("duration", text="Duration")
        self.tree_done.column("title", width=350)
        self.tree_done.column("date", width=110, anchor="center")
        self.tree_done.column("duration", width=110, anchor="center")
        self.tree_done.pack(fill=tk.BOTH, expand=True)

        # Overdue
        frame_over = ttk.Frame(self.nb, style="Main.TFrame")
        self.nb.add(frame_over, text="Overdue")

        self.tree_over = ttk.Treeview(
            frame_over,
            columns=("title", "date", "duration"),
            show="headings",
            selectmode="browse",
        )
        self.tree_over.heading("title", text="Task")
        self.tree_over.heading("date", text="Date")
        self.tree_over.heading("duration", text="Duration")
        self.tree_over.column("title", width=350)
        self.tree_over.column("date", width=110, anchor="center")
        self.tree_over.column("duration", width=110, anchor="center")
        self.tree_over.pack(fill=tk.BOTH, expand=True)

        # Context menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Mark as done", command=self.mark_done)
        self.menu.add_command(label="Mark as not done", command=self.mark_not_done)
        self.menu.add_separator()
        self.menu.add_command(label="▶ Start timer", command=self.start_timer)
        self.menu.add_command(label="⏸ Stop timer", command=self.stop_timer)
        self.menu.add_separator()
        self.menu.add_command(label="Edit task", command=self.edit_task)
        self.menu.add_command(label="Delete task", command=self.delete_task)
        self.menu.add_separator()
        self.menu.add_command(label="Open notes", command=self.open_notes)

        self.tree.bind("<Button-3>", self._on_right_click)

        self.tree.bind("<ButtonPress-1>", self._on_left_press)
        self.tree.bind("<B1-Motion>", self._on_left_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_left_release)

    
    def update_day(self, day):
        self.lbl_day_value.config(text=day.strftime("%d.%m.%Y"))
        self._load_tasks()

    
    def add_task(self):
        title = self.entry_title.get().strip()
        desc = self.txt_desc.get("1.0", tk.END).strip()

        if not title:
            messagebox.showwarning("Warning", "Task title cannot be empty.")
            return

        day = self.week_view.get_selected_date()
        self.db.add_task(title, desc, day)

        self.entry_title.delete(0, tk.END)
        self.txt_desc.delete("1.0", tk.END)

        self._load_tasks()

    def _load_tasks(self):
        day = self.week_view.get_selected_date()
        tasks = self.db.get_tasks_by_date(day)

        self.tree.delete(*self.tree.get_children())
        self.tasks_by_item.clear()

        for task in tasks:
            sec = self._compute_display_seconds(task)
            item = self.tree.insert(
                "",
                tk.END,
                values=(
                    task.title,
                    (task.description or "").strip(),
                    task.status,
                    format_duration(sec),
                ),
            )
            self.tasks_by_item[item] = task

        self._refresh_summary_lists()

    
    def _fill_summary_tree(self, tree, tasks):
        tree.delete(*tree.get_children())
        for task in tasks:
            sec = self._compute_display_seconds(task)
            tree.insert(
                "",
                tk.END,
                values=(
                    task.title,
                    format_date_pretty(task.task_date),
                    format_duration(sec),
                ),
            )

    def _refresh_summary_lists(self):
        today = get_now().date()
        todos = self.db.get_upcoming_todos(today)
        done = self.db.get_completed_tasks()
        overdue = self.db.get_overdue_tasks(today)

        self._fill_summary_tree(self.tree_todo, todos)
        self._fill_summary_tree(self.tree_done, done)
        self._fill_summary_tree(self.tree_over, overdue)

    
    def _compute_display_seconds(self, task: Task) -> int:
        base = int(task.total_seconds or 0)

        if task.active_timer_start:
            try:
                start = datetime.fromisoformat(task.active_timer_start)
                now = get_now()
                extra = max(0, int((now - start).total_seconds()))
                return base + extra
            except Exception:
                return base

        return base

    
    def _on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        self.context_item = item
        self.menu.tk_popup(event.x_root, event.y_root)

    def _get_task(self) -> Optional[Task]:
        if not self.context_item:
            return None
        return self.tasks_by_item.get(self.context_item)

    
    def mark_done(self):
        task = self._get_task()
        if not task:
            return
        self.db.set_task_status(task.id, "Done")
        self._load_tasks()

    def mark_not_done(self):
        task = self._get_task()
        if not task:
            return
        self.db.set_task_status(task.id, "Not done")
        self._load_tasks()


    def start_timer(self):
        task = self._get_task()
        if not task:
            return

        if task.active_timer_start:
            messagebox.showinfo("Info", "Timer is already running for this task.")
            return

        now = get_now().isoformat()
        self.db.set_task_timer_start(task.id, now)
        self._load_tasks()

    def stop_timer(self):
        task = self._get_task()
        if not task:
            return

        if not task.active_timer_start:
            messagebox.showinfo("Info", "No running timer for this task.")
            return

        try:
            start = datetime.fromisoformat(task.active_timer_start)
            now = get_now()
            elapsed = max(0, int((now - start).total_seconds()))
        except Exception:
            elapsed = 0

        total = int(task.total_seconds or 0) + elapsed

        self.db.update_task_total_seconds(task.id, total)
        self.db.set_task_timer_start(task.id, None)

        self._load_tasks()

    def edit_task(self):
        task = self._get_task()
        if not task:
            return

        new_title = simpledialog.askstring(
            "Edit task", "New title:", initialvalue=task.title
        )
        if not new_title:
            return

        new_desc = simpledialog.askstring(
            "Edit task",
            "New description:",
            initialvalue=task.description or "",
        )
        if new_desc is None:
            new_desc = ""

        self.db.update_task_title_desc(task.id, new_title, new_desc)
        self._load_tasks()

    def delete_task(self):
        task = self._get_task()
        if not task:
            return

        if not messagebox.askyesno("Delete", f"Delete '{task.title}'?"):
            return

        self.db.delete_task(task.id)
        self._load_tasks()

    # ----------------------------------------------------------------------
    # Notes (TXT files) – save on close, Ctrl+S, etc.
    # ----------------------------------------------------------------------

    def _get_note_path(self, task: Task) -> str:
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))

        notes_dir = os.path.join(base_dir, "notes")
        os.makedirs(notes_dir, exist_ok=True)
        return os.path.join(notes_dir, f"task_{task.id}.txt")

    def open_notes(self):
        task = self._get_task()
        if not task:
            return

        path = self._get_note_path(task)
        content = ""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

        win = tk.Toplevel(self)
        win.title(f"Task notes - {task.title}")
        win.geometry("600x400")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        txt = tk.Text(win, wrap="word")
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", content)

        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill=tk.X)

        def do_save():
            data = txt.get("1.0", tk.END).rstrip()
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)

        def save_and_close():
            do_save()
            win.destroy()

        ttk.Button(
            btn_frame, text="Save and close", command=save_and_close
        ).pack(side=tk.RIGHT, padx=8, pady=4)

        win.bind("<Control-s>", lambda e: do_save())
        win.protocol("WM_DELETE_WINDOW", save_and_close)

    # ----------------------------------------------------------------------
    # Drag & drop ordering
    # ----------------------------------------------------------------------

    def _on_left_press(self, event):
        item = self.tree.identify_row(event.y)
        self._drag_item = item

    def _on_left_motion(self, event):
        if not self._drag_item:
            return
        target = self.tree.identify_row(event.y)
        if not target or target == self._drag_item:
            return
        index = self.tree.index(target)
        self.tree.move(self._drag_item, "", index)

    def _on_left_release(self, event):
        if not self._drag_item:
            return
        self._save_order_to_db()
        self._drag_item = None

    def _save_order_to_db(self):
        for order, item_id in enumerate(self.tree.get_children()):
            task = self.tasks_by_item.get(item_id)
            if task:
                self.db.set_task_order(task.id, order)
