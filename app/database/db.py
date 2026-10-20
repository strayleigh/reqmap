"""
SQLite Database Connection and Initialization for ReqMap.
Provides transactional access and manages catalog & sample data seeding.
"""
import sqlite3
import os
from pathlib import Path
from typing import Optional
from app.database.seed_data import (
    ISO_QUALITY_CHARACTERISTICS,
    FR_CHARACTERISTICS_DATA,
    SAMPLE_PROJECT_DATA,
)
from app.core.constants import TABLE_III_RULES


class Database:
    _instance: Optional["Database"] = None

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to workspace data folder
            base_dir = Path(__file__).resolve().parent.parent.parent
            data_dir = base_dir / "data"
            data_dir.mkdir(exist_ok=True)
            self.db_path = str(data_dir / "reqmap.db")
        else:
            self.db_path = db_path

        self._conn: Optional[sqlite3.Connection] = None
        self.initialize_schema()

    @classmethod
    def get_instance(cls, db_path: Optional[str] = None) -> "Database":
        if cls._instance is None:
            cls._instance = Database(db_path)
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON;")
        return self._conn

    def initialize_schema(self):
        """Creates tables if they do not exist, and seeds catalog and default data."""
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        conn = self.get_connection()
        with conn:
            conn.executescript(schema_sql)

        # Populate ISO catalog, Table III rules, and initial sample project if empty
        self.seed_catalog_and_rules()
        self.seed_sample_project_if_needed()

    def seed_catalog_and_rules(self):
        """Populates ISO/IEC 25023 catalog and Table III mapping rules if not present."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if quality characteristics are already populated
        cursor.execute("SELECT COUNT(*) FROM quality_characteristics")
        qc_count = cursor.fetchone()[0]

        if qc_count == 0:
            with conn:
                for qc in ISO_QUALITY_CHARACTERISTICS:
                    cursor.execute(
                        """
                        INSERT INTO quality_characteristics (iso_number, code, name, description)
                        VALUES (?, ?, ?, ?)
                        """,
                        (qc["iso_number"], qc["code"], qc["name"], qc["description"])
                    )
                    qc_id = cursor.lastrowid

                    for sub in qc.get("subcharacteristics", []):
                        cursor.execute(
                            """
                            INSERT INTO quality_subcharacteristics (characteristic_id, code, name, description)
                            VALUES (?, ?, ?, ?)
                            """,
                            (qc_id, sub["code"], sub["name"], sub["description"])
                        )
                        sub_id = cursor.lastrowid

                        for m in sub.get("measures", []):
                            cursor.execute(
                                """
                                INSERT INTO quality_measures (
                                    subcharacteristic_id, measure_id, name, description,
                                    formula, unit, direction, verification_method, reference_source
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    sub_id,
                                    m["measure_id"],
                                    m["name"],
                                    m["description"],
                                    m["formula"],
                                    m["unit"],
                                    m["direction"],
                                    m["verification_method"],
                                    "ISO/IEC 25023:2016"
                                )
                            )

        # Seed FR characteristics
        cursor.execute("SELECT COUNT(*) FROM fr_characteristics")
        frc_count = cursor.fetchone()[0]
        if frc_count == 0:
            with conn:
                for frc in FR_CHARACTERISTICS_DATA:
                    cursor.execute(
                        """
                        INSERT INTO fr_characteristics (code, name, description)
                        VALUES (?, ?, ?)
                        """,
                        (frc["code"], frc["name"], frc["description"])
                    )

        # Seed Table III Mapping Rules
        cursor.execute("SELECT COUNT(*) FROM mapping_rules")
        rule_count = cursor.fetchone()[0]
        if rule_count == 0:
            with conn:
                for rule_def in TABLE_III_RULES:
                    # Look up fr_characteristic_id
                    cursor.execute(
                        "SELECT id FROM fr_characteristics WHERE name = ?",
                        (rule_def["fr_characteristic"],)
                    )
                    frc_row = cursor.fetchone()
                    if not frc_row:
                        continue
                    frc_id = frc_row[0]

                    # Look up quality_characteristic_id
                    cursor.execute(
                        "SELECT id FROM quality_characteristics WHERE name = ?",
                        (rule_def["iso_characteristic"],)
                    )
                    qc_row = cursor.fetchone()
                    if not qc_row:
                        continue
                    qc_id = qc_row[0]

                    # Look up default subcharacteristic id
                    cursor.execute(
                        "SELECT id FROM quality_subcharacteristics WHERE name = ? AND characteristic_id = ?",
                        (rule_def["default_subcharacteristic"], qc_id)
                    )
                    sub_row = cursor.fetchone()
                    sub_id = sub_row[0] if sub_row else None

                    cursor.execute(
                        """
                        INSERT INTO mapping_rules (
                            fr_characteristic_id, quality_characteristic_id, default_subcharacteristic_id,
                            rule_name, rule_source, explanation
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            frc_id,
                            qc_id,
                            sub_id,
                            f"Rule: {rule_def['fr_characteristic']} -> {rule_def['iso_characteristic']}",
                            rule_def["rule_source"],
                            rule_def["explanation"]
                        )
                    )

    def seed_sample_project_if_needed(self):
        """Creates sample Indonesian project and requirements if database has 0 projects."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM projects")
        if cursor.fetchone()[0] > 0:
            return

        with conn:
            cursor.execute(
                """
                INSERT INTO projects (name, description)
                VALUES (?, ?)
                """,
                (SAMPLE_PROJECT_DATA["name"], SAMPLE_PROJECT_DATA["description"])
            )
            project_id = cursor.lastrowid

            for req in SAMPLE_PROJECT_DATA["requirements"]:
                cursor.execute(
                    """
                    INSERT INTO requirements (
                        project_id, req_code, type, title, description, priority, status, mapping_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project_id,
                        req["req_code"],
                        req["type"],
                        req["title"],
                        req["description"],
                        req["priority"],
                        req["status"],
                        req["mapping_status"]
                    )
                )
                req_id = cursor.lastrowid

                # Link FR Characteristics
                for frc_code in req.get("fr_characteristics", []):
                    cursor.execute("SELECT id FROM fr_characteristics WHERE code = ?", (frc_code,))
                    frc_row = cursor.fetchone()
                    if frc_row:
                        frc_id = frc_row[0]
                        cursor.execute(
                            """
                            INSERT OR IGNORE INTO requirement_fr_characteristics (requirement_id, fr_characteristic_id)
                            VALUES (?, ?)
                            """,
                            (req_id, frc_id)
                        )

                        # Create mappings based on mapping_rules for demo
                        cursor.execute(
                            """
                            SELECT id, quality_characteristic_id, default_subcharacteristic_id
                            FROM mapping_rules WHERE fr_characteristic_id = ?
                            """,
                            (frc_id,)
                        )
                        rule = cursor.fetchone()
                        if rule:
                            # Also pick first quality measure of default subcharacteristic
                            cursor.execute(
                                "SELECT id FROM quality_measures WHERE subcharacteristic_id = ? LIMIT 1",
                                (rule["default_subcharacteristic_id"],)
                            )
                            qm_row = cursor.fetchone()
                            qm_id = qm_row[0] if qm_row else None

                            cursor.execute(
                                """
                                INSERT INTO requirement_mappings (
                                    requirement_id, quality_characteristic_id, quality_subcharacteristic_id,
                                    quality_measure_id, fr_characteristic_id, mapping_rule_id,
                                    status, rational_note
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    req_id,
                                    rule["quality_characteristic_id"],
                                    rule["default_subcharacteristic_id"],
                                    qm_id,
                                    frc_id,
                                    rule["id"],
                                    "Confirmed" if req["mapping_status"] in ("Confirmed", "Terkonfirmasi") else "Suggested",
                                    f"Mapped from characteristic '{frc_code}' via mapping rules."
                                )
                            )

                            # If a quality measure exists, create a dummy target
                            if qm_id:
                                cursor.execute(
                                    """
                                    INSERT OR IGNORE INTO measure_targets (
                                        requirement_id, quality_measure_id, operator, target_value,
                                        target_unit, rational_note, is_dummy
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                                    """,
                                    (
                                        req_id,
                                        qm_id,
                                        "<=",
                                        "300",
                                        "ms / ratio",
                                        "Default simulation target baseline for requirement evaluation.",
                                        1
                                    )
                                )

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
