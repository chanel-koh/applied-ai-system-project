from datetime import datetime, date, time
from app import Pet, Task, Owner, RecurringTaskProposal
from ai_retrieval import load_documentation, retrieve_relevant_docs
from ai_validation import validate_schedule_explanation


def test_load_documentation_returns_non_empty_snippets():
    """Ensure documentation snippets are loaded and include pet care content."""
    docs = load_documentation()
    assert len(docs) > 0
    assert any("grooming" in snippet.lower() for snippet in docs)


def test_retrieve_relevant_docs_prefers_grooming_terms():
    """Verify relevant docs retrieval prioritizes grooming and poodle terms."""
    docs = retrieve_relevant_docs("poodle grooming appointment")
    assert len(docs) > 0
    assert any("groom" in snippet.lower() or "poodle" in snippet.lower() for snippet in docs)


def test_retrieve_relevant_docs_prefers_appointment_guidance():
    """Verify appointment-related queries return appointment guidance snippets."""
    docs = retrieve_relevant_docs("schedule a vet appointment")
    assert len(docs) > 0
    assert any("appointment" in snippet.lower() for snippet in docs)


def test_load_documentation_includes_section_labels():
    """Ensure the loader preserves section context to support RAG-based search."""
    docs = load_documentation()
    assert any(doc.lower().startswith("grooming:") for doc in docs)
    assert any(doc.lower().startswith("appointment guidance:") for doc in docs)


def test_validate_schedule_explanation_detects_missing_task_reference():
    """Confirm validation flags explanations that omit a specific scheduled task."""
    explanation = "This schedule is based on general pet care recommendations."
    pet = Pet(name="Mochi", breed="Poodle", age=2, activity_level="high")
    task = Task(pet=pet, description="Haircut", time=datetime.now(), frequency="once")
    result = validate_schedule_explanation(explanation, [task], ["Poodles usually need a haircut every 4 weeks."])
    assert not result.passed
    assert any("actual task" in issue.lower() for issue in result.issues)


def test_validate_schedule_explanation_passes_for_reasonable_explanation():
    """Verify validation passes for an explanation that references a task and documentation."""
    pet = Pet(name="Mochi", breed="Poodle", age=2, activity_level="high")
    task = Task(pet=pet, description="Grooming", time=datetime(2026, 4, 25, 10, 0), frequency="once")
    explanation = "The grooming task for Mochi is scheduled at 10:00 today because Poodle grooming typically takes 1.5 hours."
    docs = ["A grooming appointment typically takes 1.5 hours."]
    result = validate_schedule_explanation(explanation, [task], docs)
    assert result.passed


def test_generate_recurring_task_proposals_for_any_breed():
    """Ensure recurring proposals are generated for any breed without grooming tasks."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", breed="Golden Retriever", age=3, activity_level="high")
    owner.add_pet(pet)
    scheduler = owner.scheduler
    docs = ["All dogs need grooming regularly, especially high activity breeds."]

    proposals = scheduler.generate_recurring_task_proposals(owner, docs)
    assert len(proposals) == 1
    assert proposals[0].pet_name == "Mochi"
    assert "groom" in proposals[0].description.lower()
    assert "golden retriever" not in proposals[0].description.lower() or proposals[0].pet_name == "Mochi"


def test_apply_recurring_proposals_creates_tasks():
    """Verify approved recurring proposals are stored as scheduler tasks."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", breed="Poodle", age=3, activity_level="high")
    owner.add_pet(pet)
    scheduler = owner.scheduler
    proposal = RecurringTaskProposal(
        pet_name="Mochi",
        description="Grooming",
        proposed_time=datetime.combine(date.today(), time(10, 0)),
        reason="Poodle grooming every 4 weeks.",
        source_docs=["Poodles usually need a haircut every 4 weeks."]
    )

    created_tasks = scheduler.apply_recurring_proposals(owner, [proposal])
    assert len(created_tasks) == 1
    assert created_tasks[0].description == "Grooming"
    assert pet.tasks[-1].description == "Grooming"


def test_fix_time_conflicts_shifts_lower_priority_tasks():
    """Confirm lower-priority tasks are shifted forward when a time conflict occurs."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", breed="Poodle", age=3, activity_level="high")
    owner.add_pet(pet)
    scheduler = owner.scheduler
    t1 = Task(pet=pet, description="Walk", time=datetime(2026, 4, 25, 10, 0), frequency="daily", priority="high")
    t2 = Task(pet=pet, description="Grooming", time=datetime(2026, 4, 25, 10, 0), frequency="once", priority="low")
    scheduler.add_task(t1)
    scheduler.add_task(t2)

    messages = scheduler.fix_time_conflicts()
    assert len(messages) == 1
    assert t2.time > t1.time
