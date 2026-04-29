import calendar
from datetime import datetime, date, time
import streamlit as st
from owner import Owner
from pet import Pet
from task import Task
from recurring_task_proposal import RecurringTaskProposal
from ai_retrieval import retrieve_relevant_docs
from ai_validation import validate_schedule_explanation

st.set_page_config(page_title="PawPal+ — Care with Joy", page_icon="🐾", layout="centered")

st.markdown(
    """
<style>
    body, div[data-testid="stAppViewContainer"], section[data-testid="stSidebar"], div[data-testid="stMain"], main, .stMarkdown, .stText, .stAlert {
        color: #0d3a7d !important;
    }
    section[data-testid="stMain"] label,
    section[data-testid="stSidebar"] label,
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stDateInput label,
    .stTimeInput label {
        color: #0d3a7d !important;
    }
    header, div[data-testid="stToolbar"], div[data-testid="stAppViewContainer"] > header, section[data-testid="stMain"] > header {
        background-color: #0d3a7d !important;
        color: #ffffff !important;
    }
    div[data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #ffffff 0%, #e6f0ff 45%, #d8e8ff 100%);
    }
    section[data-testid="stSidebar"] {
        width: 250px;
        max-width: 250px;
        min-width: 220px;
        background: linear-gradient(180deg, #f8fbff 0%, #e9f3ff 100%);
        border-right: 1px solid rgba(148, 176, 213, 0.35);
        color: #0d3a7d !important;
    }
    section[data-testid="stSidebar"] * {
        color: #0d3a7d !important;
    }
    div[data-testid="stMain"], main {
        background: transparent;
    }
    div.stButton>button, div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #4f7cff, #7fb8ff) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 8px 18px rgba(79, 124, 255, 0.18);
        border-radius: 16px !important;
    }
    button[data-baseweb="button"] {
        font-weight: 600;
    }
    input, textarea, select,
    .stTextInput>div>div>input,
    .stNumberInput>div>input,
    .stDateInput>div>div>input,
    .stTimeInput>div>div>input,
    .stSelectbox>div>div>div>div {
        border-radius: 0px !important;
        border: 1px solid #ffffff !important;
        color: #0d3a7d !important;
        background-color: #ffffff !important;
    }
    
    input::placeholder, textarea::placeholder {
        color: rgba(13, 58, 125, 0.5) !important;
    }
    .stTable td, .stTable th,
    section[data-testid="stMain"] table td,
    section[data-testid="stMain"] table th {
        color: #0d3a7d !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #0f172a !important;
    }
    .stAlert {
        border-left: 4px solid #4f7cff;
    }
    .stSelectbox > div > div {
        border: 1px solid #ffffff !important;
        background-color: #ffffff !important;
    }
    [data-baseweb="select"] [role="listbox"],
    [data-baseweb="popover"] ul {
        background-color: #ffffff !important;
        color: #0d3a7d !important;
    }
    [data-baseweb="select"] [role="option"],
    [data-baseweb="menu"] li {
        color: #0d3a7d !important;
    }
    div[data-testid="stSelectbox"] *:not(svg) {
        color: #0d3a7d !important;
    }
    div[data-testid="stSelectbox"] svg,
    div[data-testid="stSelectbox"] svg path {
        fill: #0d3a7d !important;
        stroke: none !important;
        opacity: 1 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+**, your joyful pet care companion.

Create smart routines filled with thoughtful care for every furry friend.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a loving pet care planner designed to help busy owners build happy, healthy routines.
It balances priorities, timing, and pet preferences so every walk, meal, and moment feels intentional.
"""
    )

if "show_schedule" not in st.session_state:
    st.session_state.show_schedule = False
if "pending_conflict_fixes" not in st.session_state:
    st.session_state.pending_conflict_fixes = []
if "pending_proposals" not in st.session_state:
    st.session_state.pending_proposals = []
if "selected_calendar_date" not in st.session_state:
    st.session_state.selected_calendar_date = date.today()
if "calendar_month" not in st.session_state:
    st.session_state.calendar_month = date.today().month
if "calendar_year" not in st.session_state:
    st.session_state.calendar_year = date.today().year

st.divider()

st.sidebar.title("PawPal+ Menu")
selected_tab = st.sidebar.radio("Navigate", ["Home", "Schedule", "AI Assistant"], index=0)

if selected_tab == "Home":
    st.subheader("Create Your Care Crew")
    owner_name = st.text_input("Owner name", value="Jordan")

    if st.button("Create Owner", key="create-owner"):
        if "owner" not in st.session_state:
            st.session_state.owner = Owner(owner_name)
            st.success("Yay! Owner created — your pet care journey starts now.")
        else:
            st.info("You already have an owner saved. Ready for more pet magic?")

    st.subheader("Add Pet")
    pet_name = st.text_input("Pet name", value="Mochi")
    breed = st.text_input("Breed", value="Golden Retriever")
    age = st.number_input("Age", min_value=0, max_value=30, value=1)
    activity_level = st.selectbox("Activity Level", ["low", "medium", "high"], index=1)

    if st.button("Add Pet", key="add-pet"):
        if "owner" in st.session_state:
            pet = Pet(name=pet_name, breed=breed, age=age, activity_level=activity_level)
            st.session_state.owner.add_pet(pet)
            st.success(f"Awesome! {pet_name} is now part of your care family.")
        else:
            st.error("Please create an owner first so your pet has a home.")

    if "owner" in st.session_state:
        st.write(f"Saved Owner: {st.session_state.owner.name}")
        if st.session_state.owner.pets:
            st.write("Pets in your care:")
            for pet in st.session_state.owner.pets:
                st.write(f"- {pet.name} ({pet.breed}, age {pet.age}, activity {pet.activity_level})")
        else:
            st.info("No pets yet — add a furry friend to begin the adventure.")
    else:
        st.info("Create an owner to get started and unlock joyful pet planning.")

elif selected_tab == "Schedule":
    st.subheader("Design a Happy Care Plan")

    selected_pet_name = None
    if "owner" in st.session_state and st.session_state.owner.pets:
        pet_names = [p.name for p in st.session_state.owner.pets]
        selected_pet_name = st.selectbox("Select pet for task", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning adventure")
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

    if st.button("Add care moment", key="add-task"):
        if "owner" in st.session_state and st.session_state.owner.pets:
            selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
            task_datetime = datetime.combine(task_date, task_time)
            task = Task(pet=selected_pet, description=task_title, time=task_datetime, frequency=frequency, priority=priority)
            selected_pet.tasks.append(task)
            st.session_state.owner.scheduler.add_task(task)
            st.success(f"Task added for {selected_pet_name}! Your pet's day just got brighter.")
        else:
            st.error("Create an owner and add a pet first so your care plan can begin.")

    if "owner" in st.session_state and st.session_state.owner.pets:
        for pet in st.session_state.owner.pets:
            if pet.tasks:
                st.write(f"Tasks for {pet.name}:")
                task_data = [{
                    "description": t.description,
                    "time": t.time.strftime("%Y-%m-%d %H:%M"),
                    "frequency": t.frequency,
                    "priority": t.priority,
                    "completed": t.completed,
                } for t in pet.tasks]
                st.table(task_data)
            else:
                st.info(f"No tasks for {pet.name} yet — add one to create a caring routine.")

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
    else:
        st.info("Create an owner and add a pet in the Home tab to use the scheduler.")

else:
    st.subheader("Smart Care Suggestions")
    if st.button("Inspire recurring care", key="propose-recurring"):
        docs = retrieve_relevant_docs("recommend recurring care tasks", top_k=5)
        proposals = st.session_state.owner.scheduler.generate_recurring_task_proposals(st.session_state.owner, docs)
        st.session_state.pending_proposals = [proposal.__dict__ for proposal in proposals]

    pending_proposals = st.session_state.get("pending_proposals", [])
    if pending_proposals:
        st.write("Heartfelt care suggestions:")
        for proposal in pending_proposals:
            st.markdown(f"**{proposal['pet_name']}** — {proposal['description']} at {proposal['proposed_time'].strftime('%Y-%m-%d %H:%M')}")
            st.write(proposal['reason'])
            if proposal['source_docs']:
                st.write("Source docs:")
                for doc in proposal['source_docs']:
                    st.write(f"- {doc}")

        if st.button("Approve all proposals", key="approve-proposals"):
            approved = [RecurringTaskProposal(**proposal) for proposal in pending_proposals]
            created_tasks = st.session_state.owner.scheduler.apply_recurring_proposals(st.session_state.owner, approved)
            fixes = st.session_state.owner.scheduler.fix_time_conflicts()
            st.success(f"Added {len(created_tasks)} thoughtful task(s) to your care plan.")
            for message in fixes:
                st.info(message)
            st.session_state.pending_proposals = []

    st.divider()
    st.subheader("Build a Loving Schedule")

    generate_schedule = st.button("Create my joyful schedule", key="generate-schedule")
    if generate_schedule:
        st.session_state.show_schedule = True

    if st.session_state.show_schedule:
        if "owner" in st.session_state:
            owner = st.session_state.owner
            scheduler = owner.scheduler

            today = date.today()
            todays_tasks = scheduler.get_daily_tasks(today)

            if not todays_tasks:
                st.info("No tasks scheduled for today yet — every pet deserves a thoughtful routine.")
            else:
                sorted_tasks = scheduler.sort_tasks_by_time(todays_tasks)
                conflict_warnings = scheduler.detect_time_conflicts()

                if conflict_warnings:
                    for warning in conflict_warnings:
                        st.warning(warning)

                    if not st.session_state.pending_conflict_fixes:
                        st.session_state.pending_conflict_fixes = scheduler.suggest_time_conflict_fixes(sorted_tasks)

                    if st.session_state.pending_conflict_fixes:
                        st.info("Suggested fixes are shown below to keep your care plan calm and consistent.")
                        for fix in st.session_state.pending_conflict_fixes:
                            st.write(
                                f"- {fix['pet_name']} ({fix['description']}, priority {fix['priority']}) from {fix['old_time'].strftime('%H:%M')} to {fix['new_time'].strftime('%H:%M')}"
                            )

                        if st.button("Approve proposed fixes", key="approve-conflict-fixes"):
                            applied_messages = scheduler.apply_time_conflict_fixes(st.session_state.pending_conflict_fixes)
                            st.session_state.pending_conflict_fixes = []
                            st.session_state.show_schedule = True
                            if applied_messages:
                                st.success("Conflict fixes applied — your pets are set for a smoother day.")
                                for msg in applied_messages:
                                    st.info(msg)
                            else:
                                st.warning("No fixes were applied. The schedule may already be balanced.")

                            todays_tasks = scheduler.get_daily_tasks(today)
                            sorted_tasks = scheduler.sort_tasks_by_time(todays_tasks)
                            conflict_warnings = scheduler.detect_time_conflicts()
                else:
                    st.success("No conflicts detected in your current schedule.")
                    st.session_state.pending_conflict_fixes = []

                st.caption(f"Showing {len(sorted_tasks)} task(s) for today ({today.strftime('%B %d, %Y')})")
                task_rows = []
                for task in sorted_tasks:
                    task_rows.append({
                        "Time": task.time.strftime("%Y-%m-%d %H:%M"),
                        "Pet": task.pet.name,
                        "Task": task.description,
                        "Frequency": task.frequency,
                        "Priority": task.priority,
                        "Completed": "✅" if task.completed else "❌",
                    })

                st.subheader("Your Care Plan")
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

                st.subheader("Why this plan matters")
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
