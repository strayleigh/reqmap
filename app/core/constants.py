"""
ReqMap Core Constants & Enums
Based on ISO/IEC 25023:2016 and Mapping Rules.
"""
from enum import Enum


class RequirementType(str, Enum):
    FR = "FR"      # Functional Requirement
    NFR = "NFR"    # Non-Functional Requirement


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RequirementStatus(str, Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    IMPLEMENTED = "Implemented"


class MappingStatus(str, Enum):
    NOT_ANALYZED = "Not Analyzed"
    SUGGESTED = "Suggested"
    CONFIRMED = "Confirmed"
    NEEDS_REVIEW = "Needs Review"
    REJECTED = "Rejected"


class ComparisonOperator(str, Enum):
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    EQUAL = "="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    RANGE = "range"


# Mapping rules definition (based on Table III FR-character mapping)
TABLE_III_RULES = [
    {
        "fr_characteristic": "Runs according to the actor",
        "iso_characteristic": "Functional suitability",
        "default_subcharacteristic": "Functional completeness",
        "rule_source": "Mapping Rule (FR-character mapping based on ISO/IEC 25023)",
        "explanation": "Functions executing according to actor interactions directly affect functional completeness and appropriateness."
    },
    {
        "fr_characteristic": "CRUD / database process",
        "iso_characteristic": "Performance efficiency",
        "default_subcharacteristic": "Time behaviour",
        "rule_source": "Mapping Rule (FR-character mapping based on ISO/IEC 25023)",
        "explanation": "Database transactions and data manipulation (CRUD) significantly affect system response time, throughput, and capacity utilization."
    },
    {
        "fr_characteristic": "File transfer",
        "iso_characteristic": "Compatibility",
        "default_subcharacteristic": "Interoperability",
        "rule_source": "Mapping Rule (FR-character mapping based on ISO/IEC 25023)",
        "explanation": "File transfer processes require standard format compatibility, protocol integrity, and cross-component interoperability."
    },
    {
        "fr_characteristic": "Makes tasks easier for users and reduces human error",
        "iso_characteristic": "Usability",
        "default_subcharacteristic": "User error protection",
        "rule_source": "Mapping Rule (FR-character mapping based on ISO/IEC 25023)",
        "explanation": "Features simplifying user tasks and minimizing operational mistakes are tied directly to usability and user error protection."
    },
    {
        "fr_characteristic": "Failure/error detection in the system",
        "iso_characteristic": "Reliability",
        "default_subcharacteristic": "Fault tolerance",
        "rule_source": "Mapping Rule (FR-character mapping based on ISO/IEC 25023)",
        "explanation": "System fault detection and error handling relate to reliability, fault tolerance, and recoverability."
    },
    {
        "fr_characteristic": "Security of transfers, data, access rights, and controls",
        "iso_characteristic": "Security",
        "default_subcharacteristic": "Confidentiality",
        "rule_source": "Mapping Rule (FR-character mapping based on ISO/IEC 25023)",
        "explanation": "Protection of data transfers, access control enforcement, and authentication ensure confidentiality, integrity, and accountability."
    },
    {
        "fr_characteristic": "Module-related functions: reusability, logging, analysis, modification, testability",
        "iso_characteristic": "Maintainability",
        "default_subcharacteristic": "Analysability",
        "rule_source": "Mapping Rule (FR-character mapping based on ISO/IEC 25023)",
        "explanation": "Modular functionalities such as logging, analysability, and diagnostic testing directly contribute to maintainability and modularity."
    },
    {
        "fr_characteristic": "Application configuration and adaptation to other environments, applications, or software",
        "iso_characteristic": "Portability",
        "default_subcharacteristic": "Adaptability",
        "rule_source": "Mapping Rule (FR-character mapping based on ISO/IEC 25023)",
        "explanation": "Configuration and adaptation capabilities across target operating environments determine overall application portability and installability."
    }
]
