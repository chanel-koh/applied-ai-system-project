from __future__ import annotations
from typing import List

from pet import Pet
from scheduler import Scheduler
from task import Task

class Owner:
    def __init__(self, name: str):
        """Initialize an owner with a name, pet list, and scheduler."""
        self.name: str = name
        self.pets: List[Pet] = []
        self.scheduler: Scheduler = Scheduler()

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from the owner if present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def list_pets(self) -> List[Pet]:
        """Return the owner's list of pets."""
        return self.pets

    def get_all_pet_tasks(self) -> List[Task]:
        """Collect tasks from all owned pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks
