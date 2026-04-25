import calendar
from datetime import datetime, date, time
import streamlit as st
from owner import Owner
from pet import Pet
from task import Task
from recurring_task_proposal import RecurringTaskProposal
from ai_retrieval import retrieve_relevant_docs
from ai_validation import validate_schedule_explanation

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
"""
Welcome to the PawPal+ app.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

st.divider()

st.subheader("Create Owner")
owner_name = st.text_input("Owner name", value="Jordan")

if st.button("Create Owner"):
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(owner_name)
        st.success("Owner created and stored in session state!")
    else:
        st.info("Owner already exists in session state.")

st.subheader("Add Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Age", min_value=0, max_value=30, value=1)
activity_level = st.selectbox("Activity Level", ["low", "medium", "high"], index=1)

if st.button("Add Pet"):
    if "owner" in st.session_state:
        pet = Pet(name=pet_name, breed=species, age=age, activity_level=activity_level)
        st.session_state.owner.add_pet(pet)
        st.success(f"Pet {pet_name} added to owner!")
    else:
        st.error("Create owner first.")

if "owner" in st.session_state:
    st.write(f"Stored Owner: {st.session_state.owner.name}")
    if st.session_state.owner.pets:
        st.write("Pets:")
        for pet in st.session_state.owner.pets:
            st.write(f"- {pet.name} ({pet.breed}, age {pet.age}, activity {pet.activity_level})")
    else:
        st.info("No pets added yet.")

st.markdown("### Tasks")

if "owner" in st.session_state and st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Select pet for task", pet_names)

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    task_date = st.date_input("Date", value=date.today())
with col5:
    task_time = st.time_input("Time", value=time(8, 0))
with col6:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)

if st.button("Add task"):
    if "owner" in st.session_state and st.session_state.owner.pets:
        selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
        task_datetime = datetime.combine(task_date, task_time)
        task = Task(pet=selected_pet, description=task_title, time=task_datetime, frequency=frequency, priority=priority)
        selected_pet.tasks.append(task)
        st.session_state.owner.scheduler.add_task(task)
        st.success(f"Task added for {selected_pet_name} on {task_date.strftime('%b %d')} at {task_time.strftime('%H:%M')}!")
    else:
        st.error("Create owner and add a pet first.")

if "owner" in st.session_state and st.session_state.owner.pets:
    for pet in st.session_state.owner.pets:
        if pet.tasks:
            st.write(f"Tasks for {pet.name}:")
            task_data = [{"description": t.description, "time": t.time.strftime("%Y-%m-%d %H:%M"), "frequency": t.frequency, "priority": t.priority, "completed": t.completed} for t in pet.tasks]
            st.table(task_data)
        else:
            st.info(f"No tasks for {pet.name} yet.")

    if "selected_calendar_date" not in st.session_state:
        st.session_state.selected_calendar_date = date.today()

    if "calendar_month" not in st.session_state:
        st.session_state.calendar_month = date.today().month
    if "calendar_year" not in st.session_state:
        st.session_state.calendar_year = date.today().year

    st.divider()
    st.subheader("Calendar")
    month_names = list(calendar.month_name)[1:]

    nav_col1, nav_col2, nav_col3 = st.columns([1, 4, 1])
    current_year = date.today().year
    with nav_col2:
        selected_month_name = st.selectbox(
            "Month",
            month_names,
            index=st.session_state.calendar_month - 1,
            key="calendar_month_select",
        )
        selected_year = st.number_input(
            "Year",
            min_value=current_year,
            max_value=current_year + 10,
            value=st.session_state.calendar_year,
            step=1,
            key="calendar_year_input",
        )
        st.session_state.calendar_month = month_names.index(selected_month_name) + 1
        st.session_state.calendar_year = selected_year

    current_month = st.session_state.calendar_month
    current_year = st.session_state.calendar_year
    st.write(f"Viewing {calendar.month_name[current_month]} {current_year}")
    st.write(f"Selected date: {st.session_state.selected_calendar_date.strftime('%A, %B %d, %Y')}")

    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    header_cols = st.columns(7)
    for idx, day_name in enumerate(week_days):
        header_cols[idx].markdown(f"**{day_name}**")

    for week in calendar.monthcalendar(current_year, current_month):
        row_cols = st.columns(7)
        for idx, day in enumerate(week):
            if day == 0:
                row_cols[idx].write(" ")
            else:
                if row_cols[idx].button(str(day), key=f"calendar-day-{current_year}-{current_month}-{day}"):
                    st.session_state.selected_calendar_date = date(current_year, current_month, day)

    selected_day = st.session_state.selected_calendar_date
    selected_day_tasks = st.session_state.owner.scheduler.get_daily_tasks(selected_day)
    st.write(f"Tasks on {selected_day.strftime('%B %d, %Y')}:")
    if selected_day_tasks:
        day_rows = [{"Time": t.time.strftime("%H:%M"), "Pet": t.pet.name, "Task": t.description, "Priority": t.priority} for t in selected_day_tasks]
        st.table(day_rows)
    else:
        st.info("No tasks scheduled for this day.")

    st.divider()
    st.subheader("Recurring Care Proposals")
    if st.button("Propose recurring care tasks"):
        docs = retrieve_relevant_docs("recommend recurring care tasks", top_k=5)
        proposals = st.session_state.owner.scheduler.generate_recurring_task_proposals(st.session_state.owner, docs)
        st.session_state.pending_proposals = [proposal.__dict__ for proposal in proposals]

    pending_proposals = st.session_state.get("pending_proposals", [])
    if pending_proposals:
        st.write("Proposed recurring tasks:")
        for proposal in pending_proposals:
            st.markdown(f"**{proposal['pet_name']}** — {proposal['description']} at {proposal['proposed_time'].strftime('%Y-%m-%d %H:%M')}")
            st.write(proposal['reason'])
            if proposal['source_docs']:
                st.write("Source docs:")
                for doc in proposal['source_docs']:
                    st.write(f"- {doc}")

        if st.button("Approve all proposals"):
            approved = [RecurringTaskProposal(**proposal) for proposal in pending_proposals]
            created_tasks = st.session_state.owner.scheduler.apply_recurring_proposals(st.session_state.owner, approved)
            fixes = st.session_state.owner.scheduler.fix_time_conflicts()
            st.success(f"Added {len(created_tasks)} task(s) after approval.")
            for message in fixes:
                st.info(message)
            st.session_state.pending_proposals = []
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if "owner" in st.session_state:
        owner = st.session_state.owner
        scheduler = owner.scheduler

        today = date.today()
        todays_tasks = scheduler.get_daily_tasks(today)

        if not todays_tasks:
            st.info("No tasks scheduled for today. Add a task with today's date to see it here.")
        else:
            sorted_tasks = scheduler.sort_tasks_by_time(todays_tasks)
            conflict_warnings = scheduler.detect_time_conflicts()

            if conflict_warnings:
                for warning in conflict_warnings:
                    st.warning(warning)
            else:
                st.success("No conflicts detected in your current schedule.")

            st.caption(f"Showing {len(sorted_tasks)} task(s) for today ({today.strftime('%B %d, %Y')})")
            task_rows = []
            for task in sorted_tasks:
                task_rows.append({
                    "Time": task.time.strftime("%Y-%m-%d %H:%M"),
                    "Pet": task.pet.name,
                    "Task": task.description,
                    "Frequency": task.frequency,
                    "Priority": task.priority,
                    "Completed": "✅" if task.completed else "❌"
                })

            st.subheader("Sorted Schedule")
            st.table(task_rows)

            explanation = "Today’s schedule includes " + ", ".join(
                f"{task.description} for {task.pet.name} at {task.time.strftime('%H:%M')}" for task in sorted_tasks
            ) + "."
            docs = retrieve_relevant_docs("explain today's pet care schedule", top_k=3)
            validation = validate_schedule_explanation(explanation, sorted_tasks, docs)

            st.subheader("Schedule Explanation")
            st.write(explanation)

            st.subheader("Validation")
            if validation.passed:
                st.success("AI explanation validation passed.")
            else:
                for issue in validation.issues:
                    st.error(issue)
            for note in validation.notes:
                st.info(note)

            st.subheader("Retrieved Reference Docs")
            if docs:
                for doc in docs:
                    st.write(f"- {doc}")
            else:
                st.write("No reference docs found.")

            next_task = scheduler.get_next_task()
            if next_task:
                st.success(f"Next task: {next_task.description} for {next_task.pet.name} at {next_task.time.strftime('%H:%M')}")
            else:
                st.info("No upcoming tasks available.")
    else:
        st.error("Create owner and pet first.")
