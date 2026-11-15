import sqlite3
import os

# Always resolve DB path relative to project root (one level up from src/)
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_SRC_DIR)
DB_PATH = os.path.join(_ROOT_DIR, "vaccination.db")


def connect_db():
    """Return a SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    """Create all tables if they do not exist."""
    conn = connect_db()
    cur = conn.cursor()

    # ── Beneficiaries ──────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS beneficiaries (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            beneficiary_id  TEXT    NOT NULL UNIQUE,
            name            TEXT    NOT NULL,
            date_of_birth   TEXT    NOT NULL,
            gender          TEXT    DEFAULT '',
            guardian_name   TEXT    DEFAULT '',
            phone           TEXT    DEFAULT '',
            address         TEXT    DEFAULT '',
            created_at      TEXT    DEFAULT (DATE('now'))
        )
    """)

    # ── Doses ──────────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS doses (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            beneficiary_id   TEXT    NOT NULL,
            vaccine_name     TEXT    NOT NULL,
            dose_number      INTEGER NOT NULL,
            administered_date TEXT   NOT NULL,
            notes            TEXT    DEFAULT '',
            created_at       TEXT    DEFAULT (DATE('now')),
            FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id)
        )
    """)

    # ── Vaccination Schedules ──────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            beneficiary_id  TEXT    NOT NULL,
            vaccine_name    TEXT    NOT NULL,
            dose_number     INTEGER NOT NULL,
            due_date        TEXT    NOT NULL,
            status          TEXT    DEFAULT 'NOT_YET',
            notes           TEXT    DEFAULT '',
            created_at      TEXT    DEFAULT (DATE('now')),
            FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id)
        )
    """)

    # ── Inventory ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            vaccine_name  TEXT    NOT NULL,
            batch_number  TEXT    NOT NULL UNIQUE,
            quantity      INTEGER NOT NULL,
            expiry_date   TEXT    NOT NULL,
            storage_temp  REAL    DEFAULT 4.0,
            created_at    TEXT    DEFAULT (DATE('now'))
        )
    """)

    # ── Cold-Chain Readings ────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cold_chain (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            vaccine_name          TEXT    NOT NULL,
            temperature           REAL    NOT NULL,
            cumulative_heat_hours REAL    DEFAULT 0,
            freeze_sensitive      INTEGER DEFAULT 1,
            vvm_stage             INTEGER DEFAULT 1,
            status                TEXT    NOT NULL,
            recorded_at           TEXT    DEFAULT (DATETIME('now'))
        )
    """)

    # ── AEFI Records ───────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS aefi (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            beneficiary_id    TEXT    NOT NULL,
            vaccine_name      TEXT    NOT NULL,
            event_description TEXT    NOT NULL,
            severity          TEXT    NOT NULL,
            medical_clearance INTEGER DEFAULT 0,
            report_date       TEXT    DEFAULT (DATE('now')),
            FOREIGN KEY (beneficiary_id) REFERENCES beneficiaries(beneficiary_id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("Database tables created / verified successfully!")
    print("DB location:", DB_PATH)