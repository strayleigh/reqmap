from dataclasses import dataclass
from typing import Optional


@dataclass
class MeasureTarget:
    id: Optional[int] = None
    requirement_id: int = 0
    quality_measure_id: int = 0
    operator: str = "<="  # '<=', '>=', '=', '<', '>', 'range'
    target_value: str = ""
    target_unit: str = ""
    rational_note: str = ""
    is_dummy: int = 1  # 1 = Dummy/Simulasi, 0 = Empiris/Resmi
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    # Joined display fields
    measure_id_code: Optional[str] = None
    measure_name: Optional[str] = None
    formula: Optional[str] = None
    direction: Optional[str] = None
    subcharacteristic_name: Optional[str] = None
    characteristic_name: Optional[str] = None
