from pawpal_system import Owner, Pet, Task, Scheduler, TaskStatus


def main():
    owner = Owner("Mehran", available_time=90, preferences={"prefers_morning_walks": True})

    dog = Pet(name="Buddy", species="Dog", age=4, notes="Needs exercise")
    cat = Pet(name="Luna", species="Cat", age=2, notes="Takes medication")

    task1 = Task(
        title="Morning Walk",
        task_type="walk",
        duration=30,
        priority=3,
        recurring=True,
        due_time="08:00",
    )

    task2 = Task(
        title="Feed Buddy",
        task_type="feeding",
        duration=10,
        priority=2,
        recurring=True,
        due_time="07:30",
    )

    task3 = Task(
        title="Give Luna Medicine",
        task_type="medication",
        duration=5,
        priority=4,
        recurring=True,
        due_time="07:45",
    )

    task4 = Task(
        title="Playtime with Luna",
        task_type="enrichment",
        duration=20,
        priority=1,
        recurring=False,
        due_time="18:00",
    )

    dog.add_task(task1)
    dog.add_task(task2)
    cat.add_task(task3)
    cat.add_task(task4)

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_daily_plan()

    print("Today's Schedule")
    print("=" * 30)

    if not plan:
        print("No tasks scheduled for today.")
        return

    for i, task in enumerate(plan, start=1):
        due = task.due_time if task.due_time else "No due time"
        print(
            f"{i}. {task.title} | Type: {task.task_type} | "
            f"Duration: {task.duration} min | Priority: {task.priority} | Due: {due}"
        )

    print("\nExplanation:")
    print(scheduler.explain_plan())


if __name__ == "__main__":
    main()