"""
Metric Target Service
Manages user-configurable target values for ISO/IEC 25023 quality measures.
Clearly separates dummy simulation baselines from official metric definitions.
"""
from typing import List, Optional, Dict, Any
from app.database.db import Database
from app.models.target import MeasureTarget


class MetricTargetService:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database.get_instance()

    def get_targets_for_requirement(self, req_id: int) -> List[MeasureTarget]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT mt.id, mt.requirement_id, mt.quality_measure_id,
                   mt.operator, mt.target_value, mt.target_unit,
                   mt.rational_note, mt.is_dummy, mt.created_at, mt.updated_at,
                   qm.measure_id as measure_id_code, qm.name as measure_name,
                   qm.formula, qm.direction,
                   qsc.name as subcharacteristic_name,
                   qc.name as characteristic_name
            FROM measure_targets mt
            JOIN quality_measures qm ON mt.quality_measure_id = qm.id
            JOIN quality_subcharacteristics qsc ON qm.subcharacteristic_id = qsc.id
            JOIN quality_characteristics qc ON qsc.characteristic_id = qc.id
            WHERE mt.requirement_id = ?
            ORDER BY mt.id ASC
            """,
            (req_id,)
        )
        return [
            MeasureTarget(
                id=r["id"],
                requirement_id=r["requirement_id"],
                quality_measure_id=r["quality_measure_id"],
                operator=r["operator"],
                target_value=r["target_value"],
                target_unit=r["target_unit"] or "",
                rational_note=r["rational_note"] or "",
                is_dummy=r["is_dummy"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
                measure_id_code=r["measure_id_code"],
                measure_name=r["measure_name"],
                formula=r["formula"],
                direction=r["direction"],
                subcharacteristic_name=r["subcharacteristic_name"],
                characteristic_name=r["characteristic_name"]
            )
            for r in cursor.fetchall()
        ]

    def set_target(
        self,
        req_id: int,
        quality_measure_id: int,
        operator: str,
        target_value: str,
        target_unit: str = "",
        rational_note: str = "",
        is_dummy: int = 1
    ) -> MeasureTarget:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO measure_targets (
                    requirement_id, quality_measure_id, operator, target_value,
                    target_unit, rational_note, is_dummy, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(requirement_id, quality_measure_id) DO UPDATE SET
                    operator = excluded.operator,
                    target_value = excluded.target_value,
                    target_unit = excluded.target_unit,
                    rational_note = excluded.rational_note,
                    is_dummy = excluded.is_dummy,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (req_id, quality_measure_id, operator, target_value, target_unit, rational_note, is_dummy)
            )

        targets = self.get_targets_for_requirement(req_id)
        for t in targets:
            if t.quality_measure_id == quality_measure_id:
                return t
        raise ValueError("Gagal menyimpan target nilai metrik.")

    def delete_target(self, target_id: int) -> bool:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM measure_targets WHERE id = ?", (target_id,))
            return cursor.rowcount > 0

    def reset_to_dummy_target(self, req_id: int, quality_measure_id: int) -> MeasureTarget:
        """Resets target to standard dummy benchmark data."""
        return self.set_target(
            req_id=req_id,
            quality_measure_id=quality_measure_id,
            operator="<=",
            target_value="300",
            target_unit="ms",
            rational_note="Default simulation target baseline for early requirement evaluation.",
            is_dummy=1
        )
