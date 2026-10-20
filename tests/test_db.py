import pytest
import sqlite3
import os
import tempfile
from app.database.db import Database


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = Database(path)
    yield db
    db.close()
    if os.path.exists(path):
        os.remove(path)


def test_schema_initialization(temp_db):
    conn = temp_db.get_connection()
    cursor = conn.cursor()

    # Verify all expected tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}

    expected_tables = {
        "projects", "requirements", "fr_characteristics",
        "quality_characteristics", "quality_subcharacteristics",
        "quality_measures", "mapping_rules", "requirement_mappings",
        "measure_targets", "requirement_fr_characteristics"
    }
    assert expected_tables.issubset(tables)


def test_iso_catalog_seeding(temp_db):
    conn = temp_db.get_connection()
    cursor = conn.cursor()

    # Verify 8 ISO characteristics
    cursor.execute("SELECT COUNT(*) FROM quality_characteristics")
    assert cursor.fetchone()[0] == 8

    # Verify subcharacteristics exist
    cursor.execute("SELECT COUNT(*) FROM quality_subcharacteristics")
    assert cursor.fetchone()[0] >= 30

    # Verify measures exist with formulas
    cursor.execute("SELECT COUNT(*) FROM quality_measures WHERE formula IS NOT NULL")
    assert cursor.fetchone()[0] >= 30


def test_table_iii_rules_seeding(temp_db):
    conn = temp_db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM mapping_rules")
    assert cursor.fetchone()[0] == 8

    cursor.execute("SELECT COUNT(*) FROM fr_characteristics")
    assert cursor.fetchone()[0] == 8


def test_sample_indonesian_project_seeding(temp_db):
    conn = temp_db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM projects LIMIT 1")
    project_name = cursor.fetchone()[0]
    assert "Rumah Sakit" in project_name or "RME" in project_name

    cursor.execute("SELECT COUNT(*) FROM requirements")
    assert cursor.fetchone()[0] >= 8
