from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class RecurringTaskProposal:
    pet_name: str
    description: str
    proposed_time: datetime
    reason: str
    source_docs: List[str]
