import sqlite3
from datetime import date
from typing import List, Optional

from models import Task


class Database:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._migrate_sort_order()
        self._migrate_status_language()

    # ------------------------------------------------------------
    def _create_tables(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                task_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Not done',
                total_seconds INTEGER DEFAULT 0,
                active_timer_start TEXT,
                sort_order INTEGER DEFAULT 0
            )
            """
        )
        self.conn.commit()

    def _migrate_sort_order(self):
        """Eski DB'de sort_order yoksa ekler ve gün içinde sıraları doldurur."""
        cur = self.conn.execute("PRAGMA table_info(tasks)")
        cols = [row["name"] for row in cur.fetchall()]
        if "sort_order" not in cols:
            self.conn.execute(
                "ALTER TABLE tasks ADD COLUMN sort_order INTEGER DEFAULT 0"
            )
            cur2 = self.conn.execute(
                "SELECT id, task_date FROM tasks ORDER BY task_date, id"
            )
            orders = {}
            for row in cur2:
                d = row["task_date"]
                o = orders.get(d, 0)
                self.conn.execute(
                    "UPDATE tasks SET sort_order=? WHERE id=?", (o, row["id"])
                )
                orders[d] = o + 1
            self.conn.commit()

    def _migrate_status_language(self):
        """
        Eski Türkçe statüleri İngilizce'ye çevir:
        Yapılmadı -> Not done
        Yapıldı   -> Done
        """
        self.conn.execute(
            "UPDATE tasks SET status='Not done' WHERE status='Yapılmadı'"
        )
        self.conn.execute(
            "UPDATE tasks SET status='Done' WHERE status='Yapıldı'"
        )
        self.conn.commit()

    # ------------------------------------------------------------
    def _row_to_task(self, row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            task_date=date.fromisoformat(row["task_date"]),
            status=row["status"],
            total_seconds=row["total_seconds"],
            active_timer_start=row["active_timer_start"],
            sort_order=row["sort_order"] or 0,
        )

    # ------------------------------------------------------------
    # Daily operations
    # ------------------------------------------------------------

    def add_task(self, title: str, desc: str, day: date) -> int:
        date_str = day.isoformat()
        cur = self.conn.execute(
            "SELECT COALESCE(MAX(sort_order), -1) + 1 AS next_order "
            "FROM tasks WHERE task_date=?",
            (date_str,),
        )
        next_order = cur.fetchone()[0] or 0

        cur2 = self.conn.execute(
            """
            INSERT INTO tasks (title, description, task_date, status,
                               total_seconds, active_timer_start, sort_order)
            VALUES (?, ?, ?, 'Not done', 0, NULL, ?)
            """,
            (title, desc, date_str, next_order),
        )
        self.conn.commit()
        return cur2.lastrowid

    def get_tasks_by_date(self, day: date) -> List[Task]:
        cur = self.conn.execute(
            """
            SELECT * FROM tasks
            WHERE task_date=?
            ORDER BY sort_order, id
            """,
            (day.isoformat(),),
        )
        rows = cur.fetchall()
        return [self._row_to_task(r) for r in rows]

    def set_task_status(self, task_id: int, status: str):
        self.conn.execute(
            "UPDATE tasks SET status=? WHERE id=?", (status, task_id)
        )
        self.conn.commit()

    def set_task_timer_start(self, task_id: int, start_iso: Optional[str]):
        self.conn.execute(
            "UPDATE tasks SET active_timer_start=? WHERE id=?",
            (start_iso, task_id),
        )
        self.conn.commit()

    def update_task_total_seconds(self, task_id: int, total: int):
        self.conn.execute(
            "UPDATE tasks SET total_seconds=? WHERE id=?",
            (total, task_id),
        )
        self.conn.commit()

    def update_task_title_desc(self, task_id: int, title: str, desc: str):
        self.conn.execute(
            "UPDATE tasks SET title=?, description=? WHERE id=?",
            (title, desc, task_id),
        )
        self.conn.commit()

    def delete_task(self, task_id: int):
        self.conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.conn.commit()

    def set_task_order(self, task_id: int, order: int):
        self.conn.execute(
            "UPDATE tasks SET sort_order=? WHERE id=?", (order, task_id)
        )
        self.conn.commit()

    # ------------------------------------------------------------
    # Global lists (To-do / Done / Overdue)
    # ------------------------------------------------------------

    def get_upcoming_todos(self, today: date) -> List[Task]:
        """status 'Not done' and date today or later."""
        cur = self.conn.execute(
            """
            SELECT * FROM tasks
            WHERE status='Not done' AND task_date >= ?
            ORDER BY task_date, sort_order, id
            """,
            (today.isoformat(),),
        )
        return [self._row_to_task(r) for r in cur.fetchall()]

    def get_overdue_tasks(self, today: date) -> List[Task]:
        """status 'Not done' and date in the past."""
        cur = self.conn.execute(
            """
            SELECT * FROM tasks
            WHERE status='Not done' AND task_date < ?
            ORDER BY task_date DESC, sort_order, id
            """,
            (today.isoformat(),),
        )
        return [self._row_to_task(r) for r in cur.fetchall()]

    def get_completed_tasks(self) -> List[Task]:
        cur = self.conn.execute(
            """
            SELECT * FROM tasks
            WHERE status='Done'
            ORDER BY task_date DESC, sort_order, id
            """
        )
        return [self._row_to_task(r) for r in cur.fetchall()]

    def close(self):
        self.conn.close()
