from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Project:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
