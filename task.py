from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pet import Pet

@dataclass
class Task:
    pet: Pet
    description: str
    time: datetime
    frequency: str
    priority: str = "medium"
    completed: bool = False
    is_recurring: bool = False
    recurrence_interval: Optional[timedelta] = None

    def update_time(self, new_time: datetime) -> None:
        """Update the scheduled time for the task."""
        self.time = new_time

    def update_frequency(self, new_frequency: str) -> None:
        """Update the execution frequency for the task."""
        self.frequency = new_frequency

    def mark_completed(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def get_next_occurrences(self, start_date: datetime, count: int = 5) -> List[datetime]:
        """Generate next N occurrence dates for recurring tasks."""
        if not self.is_recurring or not self.recurrence_interval:
            return [self.time] if self.time >= start_date else []
        
        occurrences = []
        current = self.time
        while len(occurrences) < count and current >= start_date:
            if current >= start_date:
                occurrences.append(current)
            current += self.recurrence_interval
        
        return occurrences
