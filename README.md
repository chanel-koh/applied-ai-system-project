# PawPal+

This project builds **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet with agentic assistance.

## Scenario

A busy pet owner with one or more pets needs help staying consistent with care while balancing appointments, breed-specific needs, and shifting daily routines. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, vet visits, etc.)
- Consider constraints like available time, task priority, pet-specific preferences, and recurrence
- Recommend recurring care based on breed and pet-care documentation
- Detect schedule conflicts and suggest or apply lower-priority shifts
- Produce a daily plan and explain why it matched the pet's needs

This project workflow first designed the system (UML), then implemented the logic in Python, and finally connected it to a Streamlit UI.

## What Was Built

This final app now includes:

- Owner + pet intake so users can manage multiple pets and breed-specific care rules
- A task editor for adding and updating care tasks with `HH:MM` times, frequency, priority, and recurrence settings
- A planner that generates a daily schedule sorted chronologically, regardless of insertion order
- Built-in conflict detection and messaging when tasks share the same scheduled time
- Automatic next-occurrence creation when daily or weekly tasks are completed
- Recurring-care proposal generation from local pet care reference docs, with owner approval before task creation
- A calendar-style view for inspecting tasks by day and approving changes visually
- Test coverage for scheduling behavior, recurrence, conflict handling, and explanation validation

Note: This app was an extension of the CodePath AI110 Module 2 PawPal+ app which had the same goal as this extended app included the following behaviors:
- Let a user enter basic owner + pet info
- Let a user add tasks (duration + priority)
- Generate a daily schedule/plan based on priorities

## Architecture
![alt text](assets/PawPal_system_diagram.png)

This app has four main components: 
1. QA: human approval and automated testing.
2. Inputs: user input for tasks and a reference doc for agentic scheduling actions
3. Processing: The AI gathers information from the reference doc to make suggestions, then reflects on all suggestions it makes. The system also detects if there are any schedule conflicts and reports this to the user. 
4. Outputs: calendar view with scheduled tasks, a list of the daily schedule, and explanations when the AI offers scheduling suggestions.

## Design Decisions
Whether a person has one or multiple pets, it's difficult to keep track of tasks for pet care in addition to other tasks throughout the day. The aim of PawPal+ is to simplify this by integrating features such as task suggestions and conflict detection, then alerting the user. These two features were made to take the mental load off of users. Additionally, a calendar view was implemented so users can plan tasks in advance or set recurring tasks, like grooming appointments. Human validation was also put at multiple steps (approving conflict resolution of task suggestions) to ensure that the user always knows what's going on with their pet's schedule and why. The main tradeoff I considered is that not requiring human validation would probably be faster for the user, but they would be less in control if a siggestion is inaccurate.

## Getting started

### Setup and Running

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Smarter Scheduling
The app now includes a smarter task planner and scheduling engine that does more than just display tasks. Key capabilities include:

- Chronological schedule ordering by `HH:MM` so tasks appear in the order they happen, even if they were entered out of order
- Automatic recurrence creation for completed `daily` and `weekly` tasks, so the next occurrence is generated without re-entry
- Time conflict detection for tasks with the same timestamp, producing clear warnings and enabling resolution
- Lower-priority conflict resolution that can shift tasks forward when high-priority items collide
- Recurring proposal generation using local pet care guidance, then requiring owner approval before adding recurring tasks
- Calendar-style day inspection so users can click a date and review that day's scheduled tasks

## Features

### RAG-powered schedule guidance
The app now uses a local pet care reference file (`pet_care_docs.md`) to retrieve relevant guidance about appointments and breed-specific care.
This helps the assistant explain scheduling decisions and recommend recurring tasks grounded in documented pet care rules.

### Human-approved recurring care proposals
The app can propose recurring care tasks (for example, a poodle grooming every 4 weeks) and show those proposals for owner approval before creating them.
After approval, the scheduler places approved tasks in the calendar and resolves conflicts automatically.

### Calendar view with clickable days
A month-style calendar view lets owners click a day to inspect tasks scheduled for that date.
This makes it easier to review daily care plans and approve schedule changes with a clear visual interface.

### Chronological Schedule Sorting
Tasks are sorted by their `HH:MM` time string using Python's built-in `sorted()` with a key function, ensuring the schedule always displays in chronological order regardless of insertion order.

### Time Conflict Detection
The scheduler groups tasks by their exact timestamp using a `defaultdict`, then scans for groups with more than one task. Any conflicts surface as human-readable warning messages displayed in the UI before the schedule renders.

### Automatic Task Recurrence on Completion
Marking a `daily` or `weekly` task complete triggers the scheduler to calculate the next occurrence (`+1 day` or `+7 days`) and automatically create and append a new `Task` instance to both the pet's task list and the scheduler.

### Recurring Task Proposal Approval
Breed- and care-document-guided recurring proposals are generated first, and only approved proposals become actual scheduled tasks.

### Conflict Resolution
Lower-priority tasks can be shifted when a time conflict occurs, preserving higher-priority care while still keeping the schedule feasible.

### Testing PawPal+
To run tests, use:

```bash
python -m pytest
```

Current coverage includes:
- Sorting correctness: `test_sort_tasks_by_time_ascending_order`, `test_sort_tasks_reverse_order`, `test_sort_tasks_ignores_date_sorts_by_time_only`
- Recurrence logic: `test_complete_daily_task_creates_next_day_occurrence`, `test_complete_weekly_task_creates_next_week_occurrence`, `test_complete_task_frequency_case_insensitive`
- Conflict detection: `test_detect_time_conflicts_two_tasks_same_time`, `test_detect_time_conflicts_three_tasks_same_time`, `test_fix_time_conflicts_shifts_lower_priority_tasks`
- Agentic reasoning: `tests/test_agentic.py` covers document retrieval, recurring proposal generation, and schedule explanation validation

Summary:
Unit tests for sorting and conflict detectionw ere reliable and gave fast feedback. Agentic tests in 'test_agentic.py' validated the retrieval pipeline, confirming that explanations were checked against reference docs. What didn't work very well was keyword-based retrieval in 'ai_retrieval.py': synonyms like 'coat maintenance' vs. 'grooming' aren't picked up, and relevant docs weren't always surfaced as a result. I learned that separating retrieval, validation, and scheduling into their own modules made each piece easy to test in isolation. 

## Sample Interactions
Example 1: Adding pet and pet list
![alt text](<assets/Add pet.png>)

Example 2: RAG-powered schedule suggestions based on internal reference doc, 'pet_care_docs.md'
![alt text](<assets/AI-assisted scheduling.png>)

Example 3: Agentic reasoning and reflection
![alt text](<assets/Agentic reasoning and reflection.png>)

Example 4: Calendar view with clickable days
![alt text](<assets/Calendar view.png>)

Example 5: Conflict detection and fix suggestions
![alt text](<assets/Conflict detection.png>)

## Reflection
This project taught me that positive, action-oriented prompts were much more effective than telling the LLM what not to do. For example, when changing the color of the UI, saying a prompt such as 'make the background color of input boxes white" yeilded the desired result much more than 'don't use black for the background color." I also learned that implementing a way for the AI agent in the application to check itself was useful in notifying the user if it had any uncertainty about its recommendations. In order to investigate a bug before simply sending the LLM to fix it, it is useful to ask something in the format of "I see that [description of bug] is happening at [location / when a certain action is made], where in the code is this stemming from?"

## Reliability and Evaluation
- Limitations and Bias: the system's keyword-based retrieval as a built-in bias towards breeds and care terms that appear in 'pet_care_docs.md', such as poodles and puppies. This means less documented breeds receive less specific and/or less accurate care proposals. 
- Risk of misuse: misuse risk is low given the pet care domain and because the RAG specifically references internal docs, further constraining output. However, a user could approve a poor task proposal, putting the task on their schedule and giving subpar care to their pet. 
- Surprises while testing AI reliability: Even when a pet breed appeared in the internal referece doc, the AI suggested opted for a more general explanation, such as "Enrichment tasks can be scheduled around regular feeding or walking routines" rather than a higher match in the doc such as "Poodles should be groomed every 4 weeks." This is likely due to an error in the retrieval ranking system.
- In terms of AI collaboration, Copilot was mainly used for refactoring code and adding RAG functionality, while Claude was used for brainstorming in summarizing newly added features. An instance where Copilot gave a helpful suggestion is when it explained that since Streamlit was putting an automatic UI wrapper on dropdown fields, an explicit override had to be included in the CSS style part of the app code. An unhelpful suggestion it made was when it suggested to only make task suggestions when the pet breed was poodle.