import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, TaskStatus

# --- Session State Init ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", available_time=90, preferences={})

if "active_pet" not in st.session_state:
    st.session_state.active_pet = None

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Section 1: Owner Setup ---
st.subheader("Owner Setup")

owner_name = st.text_input("Your name", value=st.session_state.owner.name)
available_time = st.number_input(
    "Available time today (minutes)", min_value=10, max_value=480,
    value=st.session_state.owner.available_time
)

if st.button("Save Owner"):
    st.session_state.owner.name = owner_name
    st.session_state.owner.available_time = available_time
    st.success(f"Owner '{owner_name}' saved with {available_time} min available.")

st.divider()

# --- Section 2: Add a Pet ---
st.subheader("Add a Pet")

pet_name = st.text_input("Pet name")
species = st.selectbox("Species", ["dog", "cat", "rabbit", "other"])
age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
notes = st.text_input("Notes (optional)", value="")

if st.button("Add Pet"):
    if pet_name.strip() == "":
        st.warning("Please enter a pet name.")
    else:
        new_pet = Pet(name=pet_name, species=species, age=age, notes=notes)
        st.session_state.owner.add_pet(new_pet)       # <-- Owner.add_pet()
        st.session_state.active_pet = new_pet
        st.success(f"'{pet_name}' added to {st.session_state.owner.name}'s pets.")

# Show existing pets and let user select the active one
if st.session_state.owner.pets:
    st.markdown("**Pets on file:**")
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_name = st.selectbox("Select active pet for task entry", pet_names)
    st.session_state.active_pet = next(
        p for p in st.session_state.owner.pets if p.name == selected_name
    )

st.divider()

# --- Section 3: Add a Task to the Active Pet ---
st.subheader("Add a Task")

if st.session_state.active_pet is None:
    st.info("Add a pet above before scheduling tasks.")
else:
    st.caption(f"Adding tasks to: **{st.session_state.active_pet.name}**")

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.number_input("Priority (1–5)", min_value=1, max_value=5, value=3)

    task_type = st.text_input("Task type (e.g. exercise, feeding, grooming)", value="exercise")
    due_time = st.text_input("Due time (optional, e.g. 08:00)", value="")
    recurring = st.checkbox("Recurring task")

    if st.button("Add Task"):
        new_task = Task(
            title=task_title,
            task_type=task_type,
            duration=int(duration),
            priority=int(priority),
            recurring=recurring,
            due_time=due_time.strip() or None,
        )
        st.session_state.active_pet.add_task(new_task)   # <-- Pet.add_task()
        st.success(f"Task '{task_title}' added to {st.session_state.active_pet.name}.")

    # Show current tasks for active pet — sorted by priority then due time
    current_tasks = st.session_state.active_pet.get_tasks()   # <-- Pet.get_tasks()
    if current_tasks:
        st.markdown("**Current tasks (sorted by priority):**")
        # Use a temporary single-pet scheduler just to reuse sort_tasks logic
        from pawpal_system import Owner as _Owner
        _tmp_owner = _Owner(name="tmp", available_time=999)
        _tmp_owner.add_pet(st.session_state.active_pet)
        sorted_tasks = Scheduler(_tmp_owner).sort_tasks()
        st.table([
            {
                "Priority": t.priority,
                "Title": t.title,
                "Type": t.task_type,
                "Duration (min)": t.duration,
                "Due": t.due_time or "—",
                "Status": t.status.value,
            }
            for t in sorted_tasks
        ])

st.divider()

# --- Section 3.5: View & Filter All Tasks ---
st.subheader("View & Filter Tasks")

_owner = st.session_state.owner
if not _owner.view_tasks():
    st.info("No tasks yet. Add pets and tasks above.")
else:
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        pet_options = ["All Pets"] + [p.name for p in _owner.pets]
        filter_pet = st.selectbox("Filter by pet", pet_options, key="filter_pet")
    with fcol2:
        status_labels = {"All statuses": None, "Pending": TaskStatus.PENDING,
                         "Complete": TaskStatus.COMPLETE, "Skipped": TaskStatus.SKIPPED}
        filter_status_label = st.selectbox("Filter by status", list(status_labels.keys()), key="filter_status")
        filter_status = status_labels[filter_status_label]
    with fcol3:
        sort_by = st.radio("Sort by", ["Priority", "Time"], horizontal=True, key="sort_by")

    pet_name_arg = None if filter_pet == "All Pets" else filter_pet
    filtered_tasks = _owner.view_tasks(pet_name=pet_name_arg, status=filter_status)

    if not filtered_tasks:
        st.info("No tasks match the selected filters.")
    else:
        # Use Scheduler methods for sorting (Goals 1 & 2)
        _filter_sched = Scheduler(_owner)
        all_sorted = (_filter_sched.sort_by_time() if sort_by == "Time"
                      else _filter_sched.sort_tasks())
        filtered_ids = {id(t) for t in filtered_tasks}
        sorted_filtered = [t for t in all_sorted if id(t) in filtered_ids]

        # Map each task back to its pet name for the table
        task_to_pet = {id(t): p.name for p in _owner.pets for t in p.tasks}

        st.caption(f"{len(sorted_filtered)} task(s) shown")
        st.table([
            {
                "Pet": task_to_pet.get(id(t), "—"),
                "Priority": t.priority,
                "Title": t.title,
                "Type": t.task_type,
                "Duration (min)": t.duration,
                "Due": t.due_time or "—",
                "Status": t.status.value,
            }
            for t in sorted_filtered
        ])

st.divider()

# --- Section 4: Generate Schedule ---
st.subheader("Generate Daily Schedule")

if st.button("Generate Schedule"):
    owner = st.session_state.owner
    if not owner.name:
        st.warning("Please save an owner name first.")
    elif not owner.pets:
        st.warning("Please add at least one pet with tasks.")
    elif not owner.view_tasks():
        st.warning("No tasks found across your pets.")
    else:
        scheduler = Scheduler(owner)
        planned = scheduler.generate_daily_plan()
        conflicts = scheduler.warn_conflicts()

        # --- Conflict warnings (most urgent — show first) ---
        if conflicts:
            st.error("⚠️ Schedule Conflicts Detected", icon="🚨")
            for msg in conflicts:
                # Parse the warning string into a friendlier message
                # msg format: "WARNING: 'A' starts at HH:MM and runs N min — overlaps with 'B'..."
                friendly = msg.replace("WARNING: ", "")
                st.warning(friendly)
            st.caption(
                "Tip: adjust the due times or durations above so tasks don't overlap."
            )

        # --- Metrics row ---
        total_time = sum(t.duration for t in planned)
        remaining = owner.available_time - total_time
        col1, col2, col3 = st.columns(3)
        col1.metric("Tasks Scheduled", len(planned))
        col2.metric("Time Needed (min)", total_time)
        col3.metric("Time Remaining (min)", remaining)

        # --- Planned task table ---
        if planned:
            st.success(f"Here is {owner.name}'s daily plan!")
            # Use Scheduler.sort_by_time() to order the plan chronologically (Goal 2)
            planned_ids = {id(t) for t in planned}
            sorted_plan = [t for t in scheduler.sort_by_time() if id(t) in planned_ids]
            st.table([
                {
                    "Priority": t.priority,
                    "Title": t.title,
                    "Type": t.task_type,
                    "Duration (min)": t.duration,
                    "Due": t.due_time or "—",
                    "Recurring": "Yes" if t.recurring else "No",
                }
                for t in sorted_plan
            ])
        else:
            st.warning("No pending tasks fit within your available time.")
