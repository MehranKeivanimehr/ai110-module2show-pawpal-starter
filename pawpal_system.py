from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETE = "complete"
    SKIPPED = "skipped"


@dataclass
class Task:
    title: str
    task_type: str
    duration: int
    priority: int
    recurring: bool
    status: TaskStatus = TaskStatus.PENDING
    due_time: Optional[str] = None

    def mark_complete(self) -> None:
        """Set the task status to COMPLETE."""
        self.status = TaskStatus.COMPLETE

    def update_task(self, **kwargs) -> None:
        """Update any task attribute by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def is_conflicting(self, other: "Task") -> bool:
        """Return True if this task shares the same due_time as another task."""
        if self.due_time is None or other.due_time is None:
            return False
        return self.due_time == other.due_time


@dataclass
class Pet:
    name: str
    species: str
    age: int
    notes: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)


class Owner:
    def __init__(self, name: str, available_time: int, preferences: dict = None):
        """Initialize an Owner with a name, available time in minutes, and optional preferences."""
        self.name: str = name
        self.available_time: int = available_time
        self.preferences: dict = preferences if preferences is not None else {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def update_preferences(self, preferences: dict) -> None:
        """Merge new key-value pairs into the owner's preferences."""
        self.preferences.update(preferences)

    def view_tasks(self) -> list[Task]:
        """Return all tasks across every pet owned by this owner."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    def __init__(self, owner: Owner):
        """Initialize the Scheduler with an Owner to source tasks and available time from."""
        self.owner: Owner = owner
        self.planned_tasks: list[Task] = []

    def sort_tasks(self) -> list[Task]:
        """Return all owner tasks sorted by priority descending, then due_time ascending."""
        tasks = self.owner.view_tasks()
        return sorted(
            tasks,
            key=lambda t: (-t.priority, t.due_time or "")
        )

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return all pairs of tasks that share the same due_time."""
        tasks = self.sort_tasks()
        conflicts = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                if tasks[i].is_conflicting(tasks[j]):
                    conflicts.append((tasks[i], tasks[j]))
        return conflicts

    def generate_daily_plan(self) -> list[Task]:
        """Build a daily plan of pending tasks that fit within the owner's available time."""
        sorted_tasks = self.sort_tasks()
        time_remaining = self.owner.available_time
        self.planned_tasks = []

        for task in sorted_tasks:
            if task.status == TaskStatus.COMPLETE:
                continue
            if task.duration <= time_remaining:
                self.planned_tasks.append(task)
                time_remaining -= task.duration

        return self.planned_tasks

    def explain_plan(self) -> str:
        """Return a formatted string summarizing the daily plan and any conflicts."""
        if not self.planned_tasks:
            self.generate_daily_plan()

        if not self.planned_tasks:
            return "No tasks scheduled for today."

        total_time = sum(t.duration for t in self.planned_tasks)
        lines = [
            f"Daily Plan for {self.owner.name}",
            f"Total time: {total_time} min / {self.owner.available_time} min available",
            ""
        ]
        for i, task in enumerate(self.planned_tasks, 1):
            due = f" (due {task.due_time})" if task.due_time else ""
            lines.append(f"{i}. [{task.priority}] {task.title} — {task.duration} min{due}")

        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("\nConflicts detected:")
            for a, b in conflicts:
                lines.append(f"  - '{a.title}' and '{b.title}' share the same due time ({a.due_time})")

        return "\n".join(lines)
