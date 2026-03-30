from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from itertools import combinations
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
    due_time: Optional[str] = None    # "HH:MM" — time of day
    frequency: Optional[str] = None   # "daily", "weekly", or None
    due_date: Optional[str] = None    # "YYYY-MM-DD" — used to compute next occurrence

    def mark_complete(self) -> None:
        """Set the task status to COMPLETE."""
        self.status = TaskStatus.COMPLETE

    def update_task(self, **kwargs) -> None:
        """Update any task attribute by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def is_conflicting(self, other: "Task") -> bool:
        """Return True if this task's time window overlaps with another task on the same date."""
        if self.due_time is None or other.due_time is None:
            return False

        # --- Date guard ---
        # Works for all three cases:
        #   None != None      → False → fall through to time check (both undated)
        #   "2026-03-29" != "2026-03-29" → False → fall through (same day)
        #   anything else     → True  → no conflict (different days, or only one has a date)
        if self.due_date != other.due_date:
            return False

        # --- Time-window overlap ---
        def to_minutes(t: str) -> int:
            h, m = t.split(":")
            return int(h) * 60 + int(m)

        start_a, start_b = to_minutes(self.due_time), to_minutes(other.due_time)
        end_a,   end_b   = start_a + self.duration,   start_b + other.duration

        return start_a < end_b and start_b < end_a


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

    def get_tasks(self, status: TaskStatus = None) -> list[Task]:
        """Return this pet's tasks, optionally filtered by status.

        Examples:
            pet.get_tasks()                      # all tasks
            pet.get_tasks(TaskStatus.PENDING)    # only pending
            pet.get_tasks(TaskStatus.COMPLETE)   # only completed
        """
        if status is None:
            return list(self.tasks)
        return [t for t in self.tasks if t.status == status]


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

    def view_tasks(self, pet_name: str = None, status: TaskStatus = None) -> list[Task]:
        """Return tasks across all pets, with optional filters.

        Args:
            pet_name: If given, only include tasks belonging to that pet.
            status:   If given, only include tasks with that TaskStatus.

        Examples:
            owner.view_tasks()                                    # all tasks
            owner.view_tasks(pet_name="Buddy")                    # Buddy's tasks only
            owner.view_tasks(status=TaskStatus.PENDING)           # pending across all pets
            owner.view_tasks(pet_name="Luna", status=TaskStatus.COMPLETE)  # Luna's completed
        """
        all_tasks = []
        for pet in self.pets:
            if pet_name is None or pet.name == pet_name:
                all_tasks.extend(pet.get_tasks(status=status))
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

    def sort_by_time(self) -> list[Task]:
        """Return all tasks sorted by due_time (HH:MM); tasks with no time go last."""
        tasks = self.owner.view_tasks()
        return sorted(
            tasks,
            key=lambda t: t.due_time or "99:99"
        )

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return all pairs of tasks whose time windows overlap."""
        tasks = self.owner.view_tasks()
        return [
            (a, b)
            for a, b in combinations(tasks, 2)
            if a.is_conflicting(b)
        ]

    def warn_conflicts(self) -> list[str]:
        """Return a warning message for each conflicting task pair; returns [] if no conflicts."""
        warnings = []
        for a, b in self.detect_conflicts():
            warnings.append(
                f"WARNING: '{a.title}' starts at {a.due_time} and runs {a.duration} min — "
                f"overlaps with '{b.title}' starting at {b.due_time} ({b.duration} min)"
            )
        return warnings

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

    def mark_task_complete(self, task: Task, pet: Pet) -> Optional[Task]:
        """Mark a task complete and add the next occurrence to the pet if it is recurring."""
        task.mark_complete()

        if task.frequency not in ("daily", "weekly"):
            return None

        # Use the task's own due_date as the base; fall back to today
        base = date.fromisoformat(task.due_date) if task.due_date else date.today()

        delta = timedelta(days=1) if task.frequency == "daily" else timedelta(weeks=1)
        next_date = base + delta

        next_task = Task(
            title=task.title,
            task_type=task.task_type,
            duration=task.duration,
            priority=task.priority,
            recurring=task.recurring,
            due_time=task.due_time,
            frequency=task.frequency,
            due_date=next_date.isoformat(),   # e.g. "2026-03-30"
        )
        pet.add_task(next_task)
        return next_task

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
