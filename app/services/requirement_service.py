"""
Requirement Service for managing Functional and Non-Functional Requirements.
"""
from typing import List, Optional
from app.database.db import Database
from app.models.requirement import Requirement, FRCharacteristic


class RequirementService:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database.get_instance()

    def get_all_fr_characteristics(self) -> List[FRCharacteristic]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, code, name, description FROM fr_characteristics ORDER BY id ASC")
        return [
            FRCharacteristic(
                id=r["id"],
                code=r["code"],
                name=r["name"],
                description=r["description"] or ""
            )
            for r in cursor.fetchall()
        ]

    def get_requirements(
        self,
        project_id: int,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> List[Requirement]:
        conn = self.db.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, project_id, req_code, type, title, description,
                   priority, status, mapping_status, created_at, updated_at
            FROM requirements
            WHERE project_id = ?
        """
        params = [project_id]

        if type_filter and type_filter in ("FR", "NFR"):
            query += " AND type = ?"
            params.append(type_filter)

        if status_filter:
            query += " AND status = ?"
            params.append(status_filter)

        if search_query:
            query += " AND (req_code LIKE ? OR title LIKE ? OR description LIKE ?)"
            wildcard = f"%{search_query}%"
            params.extend([wildcard, wildcard, wildcard])

        query += " ORDER BY CASE WHEN type = 'FR' THEN 0 ELSE 1 END, req_code ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        result = []
        for r in rows:
            req = Requirement(
                id=r["id"],
                project_id=r["project_id"],
                req_code=r["req_code"],
                type=r["type"],
                title=r["title"],
                description=r["description"] or "",
                priority=r["priority"],
                status=r["status"],
                mapping_status=r["mapping_status"],
                created_at=r["created_at"],
                updated_at=r["updated_at"]
            )
            req.fr_characteristics = self.get_characteristics_for_requirement(req.id)
            result.append(req)

        return result

    def get_requirement_by_id(self, req_id: int) -> Optional[Requirement]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, project_id, req_code, type, title, description,
                   priority, status, mapping_status, created_at, updated_at
            FROM requirements
            WHERE id = ?
            """,
            (req_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None

        req = Requirement(
            id=row["id"],
            project_id=row["project_id"],
            req_code=row["req_code"],
            type=row["type"],
            title=row["title"],
            description=row["description"] or "",
            priority=row["priority"],
            status=row["status"],
            mapping_status=row["mapping_status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
        req.fr_characteristics = self.get_characteristics_for_requirement(req_id)
        return req

    def get_characteristics_for_requirement(self, req_id: int) -> List[FRCharacteristic]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
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
        return [
            FRCharacteristic(
                id=r["id"],
                code=r["code"],
                name=r["name"],
                description=r["description"] or ""
            )
            for r in cursor.fetchall()
        ]

    def create_requirement(self, req: Requirement, fr_char_ids: Optional[List[int]] = None) -> Requirement:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO requirements (
                    project_id, req_code, type, title, description,
                    priority, status, mapping_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    req.project_id,
                    req.req_code,
                    req.type,
                    req.title,
                    req.description,
                    req.priority,
                    req.status,
                    req.mapping_status
                )
            )
            req_id = cursor.lastrowid
            if fr_char_ids:
                self.set_requirement_fr_characteristics(req_id, fr_char_ids)

            return self.get_requirement_by_id(req_id)

    def update_requirement(self, req: Requirement, fr_char_ids: Optional[List[int]] = None) -> Optional[Requirement]:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE requirements
                SET req_code = ?, type = ?, title = ?, description = ?,
                    priority = ?, status = ?, mapping_status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    req.req_code,
                    req.type,
                    req.title,
                    req.description,
                    req.priority,
                    req.status,
                    req.mapping_status,
                    req.id
                )
            )
            if fr_char_ids is not None:
                self.set_requirement_fr_characteristics(req.id, fr_char_ids)

            return self.get_requirement_by_id(req.id)

    def delete_requirement(self, req_id: int) -> bool:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM requirements WHERE id = ?", (req_id,))
            return cursor.rowcount > 0

    def set_requirement_fr_characteristics(self, req_id: int, fr_char_ids: List[int]):
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM requirement_fr_characteristics WHERE requirement_id = ?", (req_id,))
            for char_id in fr_char_ids:
                cursor.execute(
                    """
                    INSERT INTO requirement_fr_characteristics (requirement_id, fr_characteristic_id)
                    VALUES (?, ?)
                    """,
                    (req_id, char_id)
                )
                # When assigning or re-assigning a characteristic, clear any previously rejected rule mappings
                # so the recommendation becomes active and appears again fresh
                cursor.execute(
                    """
                    DELETE FROM requirement_mappings
                    WHERE requirement_id = ? AND fr_characteristic_id = ? AND status IN ('Rejected', 'Ditolak')
                    """,
                    (req_id, char_id)
                )

    def generate_next_code(self, project_id: int, req_type: str) -> str:
        """Generates sequential ID like FR-008 or NFR-004"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        prefix = "FR" if req_type == "FR" else "NFR"
        cursor.execute(
            """
            SELECT req_code FROM requirements
            WHERE project_id = ? AND type = ?
            ORDER BY id DESC
            """,
            (project_id, prefix)
        )
        codes = [row[0] for row in cursor.fetchall()]
        max_num = 0
        for code in codes:
            try:
                num = int(code.split("-")[-1])
                if num > max_num:
                    max_num = num
            except (ValueError, IndexError):
                pass
        return f"{prefix}-{max_num + 1:03d}"
