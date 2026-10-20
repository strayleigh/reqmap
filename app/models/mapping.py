from dataclasses import dataclass
from typing import Optional


@dataclass
class MappingRule:
    id: Optional[int] = None
    fr_characteristic_id: int = 0
    quality_characteristic_id: int = 0
    default_subcharacteristic_id: Optional[int] = None
    rule_name: str = ""
    rule_source: str = ""
    explanation: str = ""
    # Joined fields for presentation
    fr_characteristic_name: Optional[str] = None
    quality_characteristic_name: Optional[str] = None
    subcharacteristic_name: Optional[str] = None


@dataclass
class RequirementMapping:
    id: Optional[int] = None
    requirement_id: int = 0
    quality_characteristic_id: int = 0
    quality_subcharacteristic_id: Optional[int] = None
    quality_measure_id: Optional[int] = None
    fr_characteristic_id: Optional[int] = None
    mapping_rule_id: Optional[int] = None
    status: str = "Disarankan"  # 'Disarankan', 'Terkonfirmasi', 'Ditolak', 'Perlu Ditinjau'
    rational_note: str = ""
    created_at: Optional[str] = None

    # Joined display fields
    qc_name: Optional[str] = None
    qsc_name: Optional[str] = None
    measure_name: Optional[str] = None
    measure_id_code: Optional[str] = None
    measure_unit: Optional[str] = None
    fr_char_name: Optional[str] = None
    rule_source: Optional[str] = None
