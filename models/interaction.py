from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class InteractionResult:
    drug_a: str
    drug_b: str

    severity: str
    severity_color: str

    clinical_effect: str
    recommendation: str
    monitoring: str
    mechanism: str

    evidence: str = ""
    confidence: float = 1.0

    source_text: Optional[str] = None
