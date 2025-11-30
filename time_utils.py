from datetime import datetime, date


def get_now() -> datetime:
    
    return datetime.now()


def format_date_pretty(d: date) -> str:
    
    weekday_names = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]
    name = weekday_names[d.weekday()]
    return f"{d.day:02d}.{d.month:02d}.{d.year} {name}"


def format_duration(total_seconds: int) -> str:
    """
    seconds -> hh:mm:ss
    """
    if total_seconds is None:
        total_seconds = 0
    total_seconds = int(total_seconds)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"
