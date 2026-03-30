from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    title: str
    task_type: str
    duration: int
    priority: int
    recurring: bool
    status: str
    due_time: Optional[str] = None

    def mark_complete(self) -> None:
        pass

    def update_task(self) -> None:
        pass

    def is_conflicting(self, other: "Task") -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    notes: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass


class Owner:
    def __init__(self, name: str, available_time: int, preferences: dict = None):
        self.name: str = name
        self.available_time: int = available_time
        self.preferences: dict = preferences if preferences is not None else {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def update_preferences(self, preferences: dict) -> None:
        pass

    def view_tasks(self) -> None:
        pass


class Scheduler:
    def __init__(self, available_time: int):
        self.tasks: list[Task] = []
        self.available_time: int = available_time
        self.planned_tasks: list[Task] = []

    def sort_tasks(self) -> list[Task]:
        pass

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        pass

    def generate_daily_plan(self) -> list[Task]:
        pass

    def explain_plan(self) -> str:
        pass
