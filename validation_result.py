from dataclasses import dataclass
from typing import List

@dataclass
class ValidationResult:
    passed: bool
    issues: List[str]
    notes: List[str]
