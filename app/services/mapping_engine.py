"""
FR-to-NFR Mapping Engine
Implements an explainable, rule-based mapping engine based on Table III
('Function Character of NFR Attribute Based on ISO/IEC 25023').
"""
from typing import List, Optional, Dict, Any
from app.database.db import Database
from app.models.mapping import MappingRule, RequirementMapping


class MappingEngine:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database.get_instance()

    def get_rules(self) -> List[MappingRule]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT mr.id, mr.fr_characteristic_id, mr.quality_characteristic_id,
                   mr.default_subcharacteristic_id, mr.rule_name, mr.rule_source, mr.explanation,
                   fc.name as fr_char_name, qc.name as qc_name, qsc.name as qsc_name
            FROM mapping_rules mr
            JOIN fr_characteristics fc ON mr.fr_characteristic_id = fc.id
            JOIN quality_characteristics qc ON mr.quality_characteristic_id = qc.id
            LEFT JOIN quality_subcharacteristics qsc ON mr.default_subcharacteristic_id = qsc.id
            ORDER BY mr.id ASC
            """
        )
        return [
            MappingRule(
                id=r["id"],
                fr_characteristic_id=r["fr_characteristic_id"],
                quality_characteristic_id=r["quality_characteristic_id"],
                default_subcharacteristic_id=r["default_subcharacteristic_id"],
                rule_name=r["rule_name"],
                rule_source=r["rule_source"],
                explanation=r["explanation"] or "",
                fr_characteristic_name=r["fr_char_name"],
                quality_characteristic_name=r["qc_name"],
                subcharacteristic_name=r["qsc_name"]
            )
            for r in cursor.fetchall()
        ]

    def analyze_requirement(self, req_id: int) -> List[Dict[str, Any]]:
        """
        Analyzes the FR's assigned characteristics against Table III mapping rules.
        Returns suggested mappings with explanations and citations.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Find FR characteristics assigned to this requirement
        cursor.execute(
            """
            SELECT fc.id, fc.code, fc.name, fc.description
            FROM fr_characteristics fc
            JOIN requirement_fr_characteristics rfc ON fc.id = rfc.fr_characteristic_id
            WHERE rfc.requirement_id = ?
            ORDER BY fc.id ASC
            """,
            (req_id,)
        )
        assigned_chars = cursor.fetchall()

        suggestions = []
        for fc in assigned_chars:
            cursor.execute(
                """
                SELECT mr.id as rule_id, mr.rule_name, mr.rule_source, mr.explanation,
                       qc.id as qc_id, qc.name as qc_name, qc.code as qc_code,
                       qsc.id as qsc_id, qsc.name as qsc_name, qsc.code as qsc_code
                FROM mapping_rules mr
                JOIN quality_characteristics qc ON mr.quality_characteristic_id = qc.id
                LEFT JOIN quality_subcharacteristics qsc ON mr.default_subcharacteristic_id = qsc.id
                WHERE mr.fr_characteristic_id = ?
                """,
                (fc["id"],)
            )
            rules = cursor.fetchall()

            for rule in rules:
                # Find available quality measures for this subcharacteristic
                measures = []
                if rule["qsc_id"]:
                    cursor.execute(
                        """
                        SELECT id, measure_id, name, formula, unit, direction
                        FROM quality_measures
                        WHERE subcharacteristic_id = ?
                        """,
                        (rule["qsc_id"],)
                    )
                    measures = [dict(m) for m in cursor.fetchall()]

                # Check if this mapping is already saved in requirement_mappings
                cursor.execute(
                    """
                    SELECT id, status, rational_note
                    FROM requirement_mappings
                    WHERE requirement_id = ? AND fr_characteristic_id = ? AND quality_characteristic_id = ?
                    """,
                    (req_id, fc["id"], rule["qc_id"])
                )
                existing = cursor.fetchone()

                suggestions.append({
                    "fr_characteristic_id": fc["id"],
                    "fr_characteristic_code": fc["code"],
                    "fr_characteristic_name": fc["name"],
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["rule_name"],
                    "rule_source": rule["rule_source"],
                    "rule_explanation": rule["explanation"],
                    "quality_characteristic_id": rule["qc_id"],
                    "quality_characteristic_code": rule["qc_code"],
                    "quality_characteristic_name": rule["qc_name"],
                    "subcharacteristic_id": rule["qsc_id"],
                    "subcharacteristic_code": rule["qsc_code"],
                    "subcharacteristic_name": rule["qsc_name"],
                    "available_measures": measures,
                    "existing_mapping_id": existing["id"] if existing else None,
                    "current_status": existing["status"] if existing else "Not Analyzed",
                    "rational_note": existing["rational_note"] if existing else ""
                })

        return suggestions

    def get_mappings_for_requirement(self, req_id: int) -> List[RequirementMapping]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT rm.id, rm.requirement_id, rm.quality_characteristic_id,
                   rm.quality_subcharacteristic_id, rm.quality_measure_id,
                   rm.fr_characteristic_id, rm.mapping_rule_id, rm.status,
                   rm.rational_note, rm.created_at,
                   qc.name as qc_name, qsc.name as qsc_name,
                   qm.name as measure_name, qm.measure_id as measure_id_code, qm.unit as measure_unit,
                   fc.name as fr_char_name, mr.rule_source as rule_source
            FROM requirement_mappings rm
            JOIN quality_characteristics qc ON rm.quality_characteristic_id = qc.id
            LEFT JOIN quality_subcharacteristics qsc ON rm.quality_subcharacteristic_id = qsc.id
            LEFT JOIN quality_measures qm ON rm.quality_measure_id = qm.id
            LEFT JOIN fr_characteristics fc ON rm.fr_characteristic_id = fc.id
            LEFT JOIN mapping_rules mr ON rm.mapping_rule_id = mr.id
            WHERE rm.requirement_id = ?
            ORDER BY rm.id ASC
            """,
            (req_id,)
        )
        return [
            RequirementMapping(
                id=r["id"],
                requirement_id=r["requirement_id"],
                quality_characteristic_id=r["quality_characteristic_id"],
                quality_subcharacteristic_id=r["quality_subcharacteristic_id"],
                quality_measure_id=r["quality_measure_id"],
                fr_characteristic_id=r["fr_characteristic_id"],
                mapping_rule_id=r["mapping_rule_id"],
                status=r["status"],
                rational_note=r["rational_note"] or "",
                created_at=r["created_at"],
                qc_name=r["qc_name"],
                qsc_name=r["qsc_name"],
                measure_name=r["measure_name"],
                measure_id_code=r["measure_id_code"],
                measure_unit=r["measure_unit"],
                fr_char_name=r["fr_char_name"],
                rule_source=r["rule_source"]
            )
            for r in cursor.fetchall()
        ]

    def apply_auto_mapping_for_requirement(self, req_id: int) -> int:
        """
        Runs Table III rules for all assigned FR characteristics of this requirement.
        Creates suggested mappings and updates requirement mapping_status.
        """
        suggestions = self.analyze_requirement(req_id)
        if not suggestions:
            return 0

        conn = self.db.get_connection()
        created_count = 0
        with conn:
            cursor = conn.cursor()
            for s in suggestions:
                if not s["existing_mapping_id"]:
                    first_measure_id = s["available_measures"][0]["id"] if s["available_measures"] else None
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
                            s["quality_characteristic_id"],
                            s["subcharacteristic_id"],
                            first_measure_id,
                            s["fr_characteristic_id"],
                            s["rule_id"],
                            "Suggested",
                            f"Recommended from mapping rule: '{s['fr_characteristic_name']}'."
                        )
                    )
                    created_count += 1

            # Update requirement mapping_status if it was 'Not Analyzed'
            cursor.execute(
                """
                UPDATE requirements
                SET mapping_status = CASE
                    WHEN mapping_status IN ('Belum Dianalisis', 'Not Analyzed') THEN 'Suggested'
                    ELSE mapping_status
                END
                WHERE id = ?
                """,
                (req_id,)
            )

        return created_count

    def confirm_mapping(self, mapping_id: int, rational_note: Optional[str] = None) -> bool:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT requirement_id, fr_characteristic_id, quality_characteristic_id FROM requirement_mappings WHERE id = ?",
                (mapping_id,)
            )
            row = cursor.fetchone()
            if row and row["fr_characteristic_id"]:
                cursor.execute(
                    """
                    UPDATE requirement_mappings
                    SET status = 'Confirmed', rational_note = COALESCE(?, rational_note)
                    WHERE requirement_id = ? AND fr_characteristic_id = ? AND quality_characteristic_id = ?
                    """,
                    (rational_note, row["requirement_id"], row["fr_characteristic_id"], row["quality_characteristic_id"])
                )
            else:
                cursor.execute(
                    """
                    UPDATE requirement_mappings
                    SET status = 'Confirmed', rational_note = COALESCE(?, rational_note)
                    WHERE id = ?
                    """,
                    (rational_note, mapping_id)
                )

            # Update parent requirement status to 'Confirmed'
            if row:
                cursor.execute(
                    """
                    UPDATE requirements
                    SET mapping_status = 'Confirmed'
                    WHERE id = ?
                    """,
                    (row["requirement_id"],)
                )
            return True

    def reject_mapping(self, mapping_id: int, reason: Optional[str] = None) -> bool:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            note = f"Rejected: {reason}" if reason else "Rejected by user."
            cursor.execute(
                "SELECT requirement_id, fr_characteristic_id, quality_characteristic_id FROM requirement_mappings WHERE id = ?",
                (mapping_id,)
            )
            row = cursor.fetchone()
            if row and row["fr_characteristic_id"]:
                cursor.execute(
                    """
                    UPDATE requirement_mappings
                    SET status = 'Rejected', rational_note = ?
                    WHERE requirement_id = ? AND fr_characteristic_id = ? AND quality_characteristic_id = ?
                    """,
                    (note, row["requirement_id"], row["fr_characteristic_id"], row["quality_characteristic_id"])
                )
            else:
                cursor.execute(
                    """
                    UPDATE requirement_mappings
                    SET status = 'Rejected', rational_note = ?
                    WHERE id = ?
                    """,
                    (note, mapping_id)
                )
            return True

    def reject_rule_suggestion(
        self,
        req_id: int,
        fc_id: int,
        qc_id: int,
        qsc_id: Optional[int] = None,
        rule_id: Optional[int] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Rejects a rule recommendation. If a mapping row already exists, marks it Rejected.
        If no mapping row exists yet, inserts a record with status 'Rejected' so it will not reappear.
        """
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id FROM requirement_mappings
                WHERE requirement_id = ? AND fr_characteristic_id = ? AND quality_characteristic_id = ?
                """,
                (req_id, fc_id, qc_id)
            )
            existing = cursor.fetchone()
            note = f"Rejected: {reason}" if reason else "Rejected by user."
            if existing:
                return self.reject_mapping(existing["id"], reason)
            else:
                cursor.execute(
                    """
                    INSERT INTO requirement_mappings (
                        requirement_id, quality_characteristic_id, quality_subcharacteristic_id,
                        fr_characteristic_id, mapping_rule_id, status, rational_note
                    ) VALUES (?, ?, ?, ?, ?, 'Rejected', ?)
                    """,
                    (req_id, qc_id, qsc_id, fc_id, rule_id, note)
                )
                return True

    def restore_rule_suggestion(self, req_id: int, fc_id: int, qc_id: int) -> bool:
        """
        Restores a rejected rule recommendation so it can reappear as an active recommendation.
        """
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM requirement_mappings
                WHERE requirement_id = ? AND fr_characteristic_id = ? AND quality_characteristic_id = ?
                  AND status IN ('Rejected', 'Ditolak')
                """,
                (req_id, fc_id, qc_id)
            )
            return cursor.rowcount > 0

    def apply_rule_suggestion(
        self,
        req_id: int,
        fc_id: int,
        qc_id: int,
        qsc_id: Optional[int] = None,
        rule_id: Optional[int] = None,
        measure_ids: Optional[List[int]] = None,
        rational_note: str = ""
    ) -> List[int]:
        """
        Accepts and applies a mapping rule recommendation for a requirement.
        Links or creates requirement mappings with proper fr_characteristic_id and mapping_rule_id.
        """
        conn = self.db.get_connection()
        updated_or_created_ids = []
        with conn:
            cursor = conn.cursor()

            targets_to_map = measure_ids if (measure_ids and len(measure_ids) > 0) else [None]

            for qm_id in targets_to_map:
                if qm_id is not None:
                    cursor.execute(
                        """
                        SELECT id FROM requirement_mappings
                        WHERE requirement_id = ? AND quality_characteristic_id = ? AND quality_measure_id = ?
                        """,
                        (req_id, qc_id, qm_id)
                    )
                else:
                    cursor.execute(
                        """
                        SELECT id FROM requirement_mappings
                        WHERE requirement_id = ? AND quality_characteristic_id = ? AND fr_characteristic_id = ?
                        """,
                        (req_id, qc_id, fc_id)
                    )
                existing = cursor.fetchone()

                if existing:
                    cursor.execute(
                        """
                        UPDATE requirement_mappings
                        SET fr_characteristic_id = ?, mapping_rule_id = ?,
                            quality_subcharacteristic_id = COALESCE(?, quality_subcharacteristic_id),
                            status = 'Confirmed',
                            rational_note = COALESCE(NULLIF(?, ''), rational_note)
                        WHERE id = ?
                        """,
                        (
                            fc_id,
                            rule_id,
                            qsc_id,
                            rational_note or "Confirmed from mapping rule recommendation.",
                            existing["id"]
                        )
                    )
                    updated_or_created_ids.append(existing["id"])
                else:
                    cursor.execute(
                        """
                        INSERT INTO requirement_mappings (
                            requirement_id, quality_characteristic_id, quality_subcharacteristic_id,
                            quality_measure_id, fr_characteristic_id, mapping_rule_id,
                            status, rational_note
                        ) VALUES (?, ?, ?, ?, ?, ?, 'Confirmed', ?)
                        """,
                        (
                            req_id,
                            qc_id,
                            qsc_id,
                            qm_id,
                            fc_id,
                            rule_id,
                            rational_note or "Confirmed from mapping rule recommendation."
                        )
                    )
                    updated_or_created_ids.append(cursor.lastrowid)

            cursor.execute(
                "UPDATE requirements SET mapping_status = 'Confirmed' WHERE id = ?",
                (req_id,)
            )

        return updated_or_created_ids

    def add_manual_mapping(
        self,
        req_id: int,
        qc_id: int,
        qsc_id: Optional[int] = None,
        qm_id: Optional[int] = None,
        rational_note: str = ""
    ) -> int:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO requirement_mappings (
                    requirement_id, quality_characteristic_id, quality_subcharacteristic_id,
                    quality_measure_id, fr_characteristic_id, mapping_rule_id,
                    status, rational_note
                ) VALUES (?, ?, ?, ?, NULL, NULL, 'Confirmed', ?)
                """,
                (req_id, qc_id, qsc_id, qm_id, rational_note or "")
            )
            new_id = cursor.lastrowid
            cursor.execute(
                "UPDATE requirements SET mapping_status = 'Confirmed' WHERE id = ?",
                (req_id,)
            )
            return new_id

    def delete_mapping(self, mapping_id: int) -> bool:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT requirement_id FROM requirement_mappings WHERE id = ?", (mapping_id,))
            row = cursor.fetchone()
            req_id = row["requirement_id"] if row else None
            cursor.execute("DELETE FROM requirement_mappings WHERE id = ?", (mapping_id,))
            if req_id:
                cursor.execute(
                    "SELECT COUNT(*) as cnt FROM requirement_mappings WHERE requirement_id = ? AND status = 'Confirmed'",
                    (req_id,)
                )
                if cursor.fetchone()["cnt"] == 0:
                    cursor.execute("UPDATE requirements SET mapping_status = 'Not Analyzed' WHERE id = ?", (req_id,))
            return cursor.rowcount > 0

    def delete_rule_mapping(self, req_id: int, fc_id: int, qc_id: int) -> bool:
        """Deletes all mapping records associated with a rule recommendation for a requirement."""
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM requirement_mappings
                WHERE requirement_id = ? AND fr_characteristic_id = ? AND quality_characteristic_id = ?
                """,
                (req_id, fc_id, qc_id)
            )
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM requirement_mappings WHERE requirement_id = ? AND status = 'Confirmed'",
                (req_id,)
            )
            if cursor.fetchone()["cnt"] == 0:
                cursor.execute("UPDATE requirements SET mapping_status = 'Not Analyzed' WHERE id = ?", (req_id,))
            return cursor.rowcount > 0
