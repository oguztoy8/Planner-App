from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Task:
    id: int
    title: str
    description: Optional[str]
    task_date: date
    status: str
    total_seconds: Optional[int]
    active_timer_start: Optional[str]
    sort_order: int
