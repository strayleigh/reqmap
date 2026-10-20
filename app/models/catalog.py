from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class QualityMeasure:
    id: Optional[int] = None
    subcharacteristic_id: int = 0
    measure_id: str = ""
    name: str = ""
    description: str = ""
    formula: str = ""
    unit: str = ""
    direction: str = ""
    verification_method: str = ""
    reference_source: str = "ISO/IEC 25023:2016"


@dataclass
class QualitySubcharacteristic:
    id: Optional[int] = None
    characteristic_id: int = 0
    code: str = ""
    name: str = ""
    description: str = ""
    measures: List[QualityMeasure] = field(default_factory=list)


@dataclass
class QualityCharacteristic:
    id: Optional[int] = None
    iso_number: int = 0
    code: str = ""
    name: str = ""
    description: str = ""
    subcharacteristics: List[QualitySubcharacteristic] = field(default_factory=list)
