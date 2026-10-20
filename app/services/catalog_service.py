"""
Quality Catalog Service for ISO/IEC 25023:2016 characteristics, subcharacteristics, and measures.
"""
from typing import List, Optional, Dict, Any
from app.database.db import Database
from app.models.catalog import QualityCharacteristic, QualitySubcharacteristic, QualityMeasure


class QualityCatalogService:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database.get_instance()

    def get_all_characteristics(self) -> List[QualityCharacteristic]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, iso_number, code, name, description FROM quality_characteristics ORDER BY iso_number ASC")
        return [
            QualityCharacteristic(
                id=r["id"],
                iso_number=r["iso_number"],
                code=r["code"],
                name=r["name"],
                description=r["description"] or ""
            )
            for r in cursor.fetchall()
        ]

    def get_subcharacteristics(self, characteristic_id: int) -> List[QualitySubcharacteristic]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, characteristic_id, code, name, description
            FROM quality_subcharacteristics
            WHERE characteristic_id = ?
            ORDER BY id ASC
            """,
            (characteristic_id,)
        )
        return [
            QualitySubcharacteristic(
                id=r["id"],
                characteristic_id=r["characteristic_id"],
                code=r["code"],
                name=r["name"],
                description=r["description"] or ""
            )
            for r in cursor.fetchall()
        ]

    def get_measures_for_subcharacteristic(self, subcharacteristic_id: int) -> List[QualityMeasure]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, subcharacteristic_id, measure_id, name, description,
                   formula, unit, direction, verification_method, reference_source
            FROM quality_measures
            WHERE subcharacteristic_id = ?
            ORDER BY id ASC
            """,
            (subcharacteristic_id,)
        )
        return [
            QualityMeasure(
                id=r["id"],
                subcharacteristic_id=r["subcharacteristic_id"],
                measure_id=r["measure_id"],
                name=r["name"],
                description=r["description"] or "",
                formula=r["formula"] or "",
                unit=r["unit"] or "",
                direction=r["direction"] or "",
                verification_method=r["verification_method"] or "",
                reference_source=r["reference_source"] or "ISO/IEC 25023:2016"
            )
            for r in cursor.fetchall()
        ]

    def get_measures_for_characteristic(self, characteristic_id: int) -> List[QualityMeasure]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT qm.id, qm.subcharacteristic_id, qm.measure_id, qm.name, qm.description,
                   qm.formula, qm.unit, qm.direction, qm.verification_method, qm.reference_source
            FROM quality_measures qm
            JOIN quality_subcharacteristics qsc ON qm.subcharacteristic_id = qsc.id
            WHERE qsc.characteristic_id = ?
            ORDER BY qm.id ASC
            """,
            (characteristic_id,)
        )
        return [
            QualityMeasure(
                id=r["id"],
                subcharacteristic_id=r["subcharacteristic_id"],
                measure_id=r["measure_id"],
                name=r["name"],
                description=r["description"] or "",
                formula=r["formula"] or "",
                unit=r["unit"] or "",
                direction=r["direction"] or "",
                verification_method=r["verification_method"] or "",
                reference_source=r["reference_source"] or "ISO/IEC 25023:2016"
            )
            for r in cursor.fetchall()
        ]

    def get_measure_by_id(self, measure_id: int) -> Optional[QualityMeasure]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, subcharacteristic_id, measure_id, name, description,
                   formula, unit, direction, verification_method, reference_source
            FROM quality_measures
            WHERE id = ?
            """,
            (measure_id,)
        )
        r = cursor.fetchone()
        if not r:
            return None
        return QualityMeasure(
            id=r["id"],
            subcharacteristic_id=r["subcharacteristic_id"],
            measure_id=r["measure_id"],
            name=r["name"],
            description=r["description"] or "",
            formula=r["formula"] or "",
            unit=r["unit"] or "",
            direction=r["direction"] or "",
            verification_method=r["verification_method"] or "",
            reference_source=r["reference_source"] or "ISO/IEC 25023:2016"
        )

    def get_full_catalog_tree(self) -> List[Dict[str, Any]]:
        """Returns the full hierarchical catalog tree for navigation."""
        all_qc = self.get_all_characteristics()
        tree = []
        for qc in all_qc:
            subchars = self.get_subcharacteristics(qc.id)
            sub_list = []
            for sc in subchars:
                measures = self.get_measures_for_subcharacteristic(sc.id)
                sub_list.append({
                    "id": sc.id,
                    "code": sc.code,
                    "name": sc.name,
                    "description": sc.description,
                    "measures": [
                        {
                            "id": m.id,
                            "measure_id": m.measure_id,
                            "name": m.name,
                            "description": m.description,
                            "formula": m.formula,
                            "unit": m.unit,
                            "direction": m.direction,
                            "verification_method": m.verification_method,
                            "reference_source": m.reference_source
                        }
                        for m in measures
                    ]
                })
            tree.append({
                "id": qc.id,
                "iso_number": qc.iso_number,
                "code": qc.code,
                "name": qc.name,
                "description": qc.description,
                "subcharacteristics": sub_list
            })
        return tree
