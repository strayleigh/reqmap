"""
Project Service for managing projects and project statistics.
"""
from typing import List, Optional, Dict, Any
from app.database.db import Database
from app.models.project import Project


class ProjectService:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database.get_instance()

    def get_projects(self) -> List[Project]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, created_at, updated_at FROM projects ORDER BY id ASC")
        rows = cursor.fetchall()
        return [
            Project(
                id=r["id"],
                name=r["name"],
                description=r["description"] or "",
                created_at=r["created_at"],
                updated_at=r["updated_at"]
            )
            for r in rows
        ]

    def get_project(self, project_id: int) -> Optional[Project]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, created_at, updated_at FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Project(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    def create_project(self, name: str, description: str = "") -> Project:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO projects (name, description) VALUES (?, ?)",
                (name, description)
            )
            project_id = cursor.lastrowid
            return self.get_project(project_id)

    def update_project(self, project_id: int, name: str, description: str = "") -> Optional[Project]:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE projects
                SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (name, description, project_id)
            )
            return self.get_project(project_id)

    def delete_project(self, project_id: int) -> bool:
        conn = self.db.get_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            return cursor.rowcount > 0

    def get_project_stats(self, project_id: int) -> Dict[str, Any]:
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM requirements WHERE project_id = ? AND type = 'FR'", (project_id,))
        fr_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM requirements WHERE project_id = ? AND type = 'NFR'", (project_id,))
        nfr_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*) FROM requirement_mappings rm
            JOIN requirements r ON rm.requirement_id = r.id
            WHERE r.project_id = ? AND rm.status = 'Terkonfirmasi'
            """,
            (project_id,)
        )
        confirmed_mappings = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*) FROM requirement_mappings rm
            JOIN requirements r ON rm.requirement_id = r.id
            WHERE r.project_id = ? AND rm.status = 'Disarankan'
            """,
            (project_id,)
        )
        suggested_mappings = cursor.fetchone()[0]

        return {
            "fr_count": fr_count,
            "nfr_count": nfr_count,
            "total_requirements": fr_count + nfr_count,
            "confirmed_mappings": confirmed_mappings,
            "suggested_mappings": suggested_mappings
        }
