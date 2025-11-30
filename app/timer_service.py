import threading
import time
from datetime import datetime
from time_utils import get_now
from models import Task


class TimerService:
    """
    Görev sürelerini HER SANİYE canlı olarak TreeView üzerinde günceller.

    NOT:
    - Görevleri her saniye DB'den çekmek yanlış.
    - Bunun yerine TaskView içindeki tasks_by_item üzerinden hesap yapılır.
    """

    def __init__(self, task_view):
        self.task_view = task_view
        self._running = True

        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while self._running:
            try:
                self._update_durations()
            except Exception:
                pass

            time.sleep(1)

    def _update_durations(self):
        """TreeView içindeki her görevin süre kolonunu canlı günceller."""

        for item_id, task in list(self.task_view.tasks_by_item.items()):
            seconds = self._compute_display_seconds(task)
            try:
                self.task_view.tree.set(item_id, "duration", self._format_duration(seconds))
            except:
                pass

    def _compute_display_seconds(self, task: Task) -> int:
        """TaskView’deki ile aynı hesap — ancak DB güncellemesi olmadan canlı hesap."""
        base = int(task.total_seconds or 0)

        if task.active_timer_start:
            try:
                start_dt = datetime.fromisoformat(task.active_timer_start)
                now = get_now()
                extra = max(0, int((now - start_dt).total_seconds()))
                return base + extra
            except:
                return base

        return base

    def _format_duration(self, total):
        """hh:mm:ss formatında süre string'i döner."""
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def stop(self):
        self._running = False
