import threading
import time
from time_utils import get_now


class ClockService:
    """
    Alt barda (status_bar.lbl_clock) saati her saniye güncelleyen servis.
    """

    def __init__(self, status_bar):
        self.status_bar = status_bar
        self._running = True

        # Arkaplanda thread çalıştır
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while self._running:
            now = get_now()
            text = now.strftime("%d.%m.%Y %H:%M:%S")
            self.status_bar.set_clock(text)
            time.sleep(1)

    def stop(self):
        self._running = False
