import os
import sys

from database import Database
from app.ui import PlannerApp


def get_base_dir() -> str:
    """
    When running from source: project folder
    When frozen with PyInstaller: folder of the .exe
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def main():
    base_dir = get_base_dir()

    # DB file will live next to the .exe (or in project root when dev)
    db_path = os.path.join(base_dir, "tasks.db")

    db = Database(db_path)
    app = PlannerApp(db)
    app.mainloop()


if __name__ == "__main__":
    main()






### Exe olarak çalıştırmak istemiyorsanız aşağıdaki kodu yukarıdaki kod ile değiştirin
# from database import Database
# from app.ui import PlannerApp


# def main():
#     db = Database("tasks.db")
#     app = PlannerApp(db)
#     app.mainloop()


# if __name__ == "__main__":
#     main()
