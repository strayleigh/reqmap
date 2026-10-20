from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class FRCharacteristic:
    id: Optional[int] = None
    code: str = ""
    name: str = ""
    description: str = ""


@dataclass
class Requirement:
    id: Optional[int] = None
    project_id: int = 1
    req_code: str = ""
    type: str = "FR"  # "FR" or "NFR"
    title: str = ""
    description: str = ""
    priority: str = "Sedang"
    status: str = "Draf"
    mapping_status: str = "Belum Dianalisis"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    fr_characteristics: List[FRCharacteristic] = field(default_factory=list)
