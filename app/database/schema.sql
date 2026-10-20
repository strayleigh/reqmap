-- ReqMap Normalized SQLite Schema
-- Compliant with ISO/IEC 25023:2016 and Table III FR-to-NFR Mapping rules

PRAGMA foreign_keys = ON;

-- 1. Project Table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Requirement Table (FR and NFR)
CREATE TABLE IF NOT EXISTS requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    req_code TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('FR', 'NFR')),
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT NOT NULL DEFAULT 'Medium',
    status TEXT NOT NULL DEFAULT 'Draft',
    mapping_status TEXT NOT NULL DEFAULT 'Not Analyzed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE (project_id, req_code)
);

-- 3. FR Characteristics Table (Reference taxonomy from Table III)
CREATE TABLE IF NOT EXISTS fr_characteristics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT
);

-- 4. Requirement to FR Characteristic Many-to-Many Association
CREATE TABLE IF NOT EXISTS requirement_fr_characteristics (
    requirement_id INTEGER NOT NULL,
    fr_characteristic_id INTEGER NOT NULL,
    PRIMARY KEY (requirement_id, fr_characteristic_id),
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    FOREIGN KEY (fr_characteristic_id) REFERENCES fr_characteristics(id) ON DELETE CASCADE
);

-- 5. ISO/IEC 25023 Top-Level Quality Characteristics (8 categories)
CREATE TABLE IF NOT EXISTS quality_characteristics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    iso_number INTEGER NOT NULL UNIQUE,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT
);

-- 6. ISO/IEC 25023 Quality Subcharacteristics
CREATE TABLE IF NOT EXISTS quality_subcharacteristics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    characteristic_id INTEGER NOT NULL,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (characteristic_id) REFERENCES quality_characteristics(id) ON DELETE CASCADE,
    UNIQUE (characteristic_id, code)
);

-- 7. ISO/IEC 25023 Quality Measures Catalog
CREATE TABLE IF NOT EXISTS quality_measures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subcharacteristic_id INTEGER NOT NULL,
    measure_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    formula TEXT,
    unit TEXT,
    direction TEXT, -- e.g. "Higher is better", "Lower is better", "Target match"
    verification_method TEXT,
    reference_source TEXT DEFAULT 'ISO/IEC 25023:2016',
    FOREIGN KEY (subcharacteristic_id) REFERENCES quality_subcharacteristics(id) ON DELETE CASCADE,
    UNIQUE (subcharacteristic_id, measure_id)
);

-- 8. Table III Mapping Rules
CREATE TABLE IF NOT EXISTS mapping_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fr_characteristic_id INTEGER NOT NULL,
    quality_characteristic_id INTEGER NOT NULL,
    default_subcharacteristic_id INTEGER,
    rule_name TEXT NOT NULL,
    rule_source TEXT NOT NULL,
    explanation TEXT,
    FOREIGN KEY (fr_characteristic_id) REFERENCES fr_characteristics(id) ON DELETE CASCADE,
    FOREIGN KEY (quality_characteristic_id) REFERENCES quality_characteristics(id) ON DELETE CASCADE,
    FOREIGN KEY (default_subcharacteristic_id) REFERENCES quality_subcharacteristics(id) ON DELETE SET NULL
);

-- 9. Requirement Mappings (Confirmed / Suggested FR-to-NFR links)
CREATE TABLE IF NOT EXISTS requirement_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id INTEGER NOT NULL,
    quality_characteristic_id INTEGER NOT NULL,
    quality_subcharacteristic_id INTEGER,
    quality_measure_id INTEGER,
    fr_characteristic_id INTEGER,
    mapping_rule_id INTEGER,
    status TEXT NOT NULL DEFAULT 'Suggested', -- 'Suggested', 'Confirmed', 'Rejected', 'Needs Review'
    rational_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    FOREIGN KEY (quality_characteristic_id) REFERENCES quality_characteristics(id) ON DELETE CASCADE,
    FOREIGN KEY (quality_subcharacteristic_id) REFERENCES quality_subcharacteristics(id) ON DELETE SET NULL,
    FOREIGN KEY (quality_measure_id) REFERENCES quality_measures(id) ON DELETE SET NULL,
    FOREIGN KEY (fr_characteristic_id) REFERENCES fr_characteristics(id) ON DELETE SET NULL,
    FOREIGN KEY (mapping_rule_id) REFERENCES mapping_rules(id) ON DELETE SET NULL
);

-- 10. Measure Target Configuration (User-defined targets per requirement / measure)
CREATE TABLE IF NOT EXISTS measure_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id INTEGER NOT NULL,
    quality_measure_id INTEGER NOT NULL,
    operator TEXT NOT NULL DEFAULT '<=',
    target_value TEXT NOT NULL,
    target_unit TEXT,
    rational_note TEXT,
    is_dummy INTEGER NOT NULL DEFAULT 1, -- Clearly flags dummy baseline data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
    FOREIGN KEY (quality_measure_id) REFERENCES quality_measures(id) ON DELETE CASCADE,
    UNIQUE (requirement_id, quality_measure_id)
);

-- Indexes for fast lookup & filtering
CREATE INDEX IF NOT EXISTS idx_req_project ON requirements(project_id);
CREATE INDEX IF NOT EXISTS idx_req_type ON requirements(type);
CREATE INDEX IF NOT EXISTS idx_req_status ON requirements(status);
CREATE INDEX IF NOT EXISTS idx_mapping_req ON requirement_mappings(requirement_id);
CREATE INDEX IF NOT EXISTS idx_mapping_qc ON requirement_mappings(quality_characteristic_id);
CREATE INDEX IF NOT EXISTS idx_target_req ON measure_targets(requirement_id);
