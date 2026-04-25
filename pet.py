from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from task import Task

@dataclass
class Pet:
    name: str
    breed: str
    age: int
    activity_level: str
    medications: List[str] = field(default_factory=list)
    feeding_schedule: List[str] = field(default_factory=list)
    walking_schedule: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def add_medication(self, med: str) -> None:
        """Add a medication to the pet."""
        self.medications.append(med)

    def remove_medication(self, med: str) -> None:
        """Remove a medication from the pet if it exists."""
        if med in self.medications:
            self.medications.remove(med)

    def add_feeding(self, feeding: str) -> None:
        """Add a feeding schedule entry."""
        self.feeding_schedule.append(feeding)

    def remove_feeding(self, feeding: str) -> None:
        """Remove a feeding schedule entry if present."""
        if feeding in self.feeding_schedule:
            self.feeding_schedule.remove(feeding)

    def add_walking(self, walking: str) -> None:
        """Add a walking schedule entry."""
        self.walking_schedule.append(walking)

    def remove_walking(self, walking: str) -> None:
        """Remove a walking schedule entry if present."""
        if walking in self.walking_schedule:
            self.walking_schedule.remove(walking)

    def get_medication_schedule(self) -> List[str]:
        """Return the medication schedule."""
        return self.medications

    def get_feeding_schedule(self) -> List[str]:
        """Return the feeding schedule."""
        return self.feeding_schedule

    def get_walking_schedule(self) -> List[str]:
        """Return the walking schedule."""
        return self.walking_schedule
