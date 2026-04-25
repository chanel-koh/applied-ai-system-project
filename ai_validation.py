from typing import List

from task import Task
from validation_result import ValidationResult


def validate_schedule_explanation(explanation: str, tasks: List[Task], docs: List[str]) -> ValidationResult:
    """Validate schedule explanation output against tasks and retrieved docs."""
    issues: List[str] = []
    notes: List[str] = []
    text = explanation.lower()

    if not explanation.strip():
        issues.append("Explanation is empty.")

    if tasks:
        task_matches = [task for task in tasks if task.description.lower() in text or task.pet.name.lower() in text]
        if not task_matches:
            issues.append("The explanation does not reference any actual task or pet in the schedule.")
    else:
        notes.append("No scheduled tasks are available to explain.")

    schedule_keywords = ["time", "priority", "conflict", "today", "date", "duration", "schedule", "task"]
    if not any(keyword in text for keyword in schedule_keywords):
        issues.append("Explanation should reference schedule details like time, priority, or task ordering.")

    unsupported_phrases = ["skip", "ignore", "cancel", "remove", "auto-add", "automatic add", "without approval", "without permission"]
    for phrase in unsupported_phrases:
        if phrase in text:
            issues.append(f"This explanation includes unsupported wording: '{phrase}'.")

    if docs:
        doc_terms = {term for doc in docs for term in doc.lower().split() if len(term) > 3}
        if not any(term in text for term in doc_terms):
            notes.append("Retrieved docs are available but not clearly referenced in the explanation.")
        else:
            notes.append("Explanation appears to be grounded in the retrieved documentation.")

    passed = len(issues) == 0
    return ValidationResult(passed=passed, issues=issues, notes=notes)
