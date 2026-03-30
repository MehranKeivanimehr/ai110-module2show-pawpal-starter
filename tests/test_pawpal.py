import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, TaskStatus, Pet


def test_mark_complete_changes_status():
    task = Task(title="Feed", task_type="feeding", duration=10, priority=2, recurring=True)
    assert task.status == TaskStatus.PENDING
    task.mark_complete()
    assert task.status == TaskStatus.COMPLETE


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog", age=3, notes="Energetic")
    task = Task(title="Walk", task_type="exercise", duration=30, priority=3, recurring=True)
    assert len(pet.get_tasks()) == 0
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1
