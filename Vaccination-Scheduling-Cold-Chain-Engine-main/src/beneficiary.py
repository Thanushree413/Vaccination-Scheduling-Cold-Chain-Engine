"""
Beneficiary Management Module
Handles add, view, update, delete for vaccination beneficiaries.
Preserves original in-memory register_beneficiary() for test compatibility.
"""

from datetime import date
from src.database import connect_db


# ─────────────────────────────────────────────────────────────────────────────
# IN-MEMORY FUNCTION (kept for test_engine.py compatibility)
# ─────────────────────────────────────────────────────────────────────────────

def register_beneficiary(beneficiaries, beneficiary_id, name, date_of_birth, guardian_name=""):
    """Register a new vaccination beneficiary into an in-memory dict."""

    if not beneficiary_id or not beneficiary_id.strip():
        raise ValueError("Beneficiary ID is required")

    if not name or not name.strip():
        raise ValueError("Beneficiary name is required")

    if beneficiary_id in beneficiaries:
        raise ValueError("Beneficiary ID already exists")

    try:
        if isinstance(date_of_birth, str):
            dob = date.fromisoformat(date_of_birth)
        elif isinstance(date_of_birth, date):
            dob = date_of_birth
        else:
            raise ValueError("Invalid date of birth")
    except ValueError:
        raise ValueError("Date of birth must use YYYY-MM-DD format")

    if dob > date.today():
        raise ValueError("Date of birth cannot be in the future")

    beneficiaries[beneficiary_id] = {
        "beneficiary_id": beneficiary_id,
        "name": name.strip(),
        "date_of_birth": dob.isoformat(),
        "guardian_name": guardian_name.strip()
    }
    return beneficiaries[beneficiary_id]


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def db_add_beneficiary(beneficiary_id, name, date_of_birth, gender="",
                       guardian_name="", phone="", address=""):
    """Add a new beneficiary to the database."""

    if not beneficiary_id or not beneficiary_id.strip():
        raise ValueError("Beneficiary ID is required")
    if not name or not name.strip():
        raise ValueError("Beneficiary name is required")

    try:
        dob = date.fromisoformat(str(date_of_birth))
    except ValueError:
        raise ValueError("Date of birth must use YYYY-MM-DD format")

    if dob > date.today():
        raise ValueError("Date of birth cannot be in the future")

    conn = connect_db()
    try:
        conn.execute(
            """INSERT INTO beneficiaries
               (beneficiary_id, name, date_of_birth, gender, guardian_name, phone, address)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (beneficiary_id.strip(), name.strip(), dob.isoformat(),
             gender.strip(), guardian_name.strip(), phone.strip(), address.strip())
        )
        conn.commit()
        return {"status": "success", "beneficiary_id": beneficiary_id.strip()}
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Could not add beneficiary: {e}")
    finally:
        conn.close()


def db_get_all_beneficiaries():
    """Return all beneficiaries as a list of dicts."""
    conn = connect_db()
    rows = conn.execute(
        "SELECT * FROM beneficiaries ORDER BY name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_get_beneficiary(beneficiary_id):
    """Return a single beneficiary dict or None."""
    conn = connect_db()
    row = conn.execute(
        "SELECT * FROM beneficiaries WHERE beneficiary_id = ?",
        (beneficiary_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def db_update_beneficiary(beneficiary_id, name=None, date_of_birth=None,
                          gender=None, guardian_name=None, phone=None, address=None):
    """Update beneficiary fields. Only provided (non-None) fields are changed."""
    conn = connect_db()
    existing = conn.execute(
        "SELECT * FROM beneficiaries WHERE beneficiary_id = ?",
        (beneficiary_id,)
    ).fetchone()

    if not existing:
        conn.close()
        raise ValueError("Beneficiary not found")

    ex = dict(existing)
    new_name         = name.strip()          if name         is not None else ex["name"]
    new_dob          = date_of_birth         if date_of_birth is not None else ex["date_of_birth"]
    new_gender       = gender.strip()        if gender       is not None else ex["gender"]
    new_guardian     = guardian_name.strip() if guardian_name is not None else ex["guardian_name"]
    new_phone        = phone.strip()         if phone        is not None else ex["phone"]
    new_address      = address.strip()       if address      is not None else ex["address"]

    try:
        dob = date.fromisoformat(str(new_dob))
    except ValueError:
        conn.close()
        raise ValueError("Date of birth must use YYYY-MM-DD format")

    conn.execute(
        """UPDATE beneficiaries
           SET name=?, date_of_birth=?, gender=?, guardian_name=?, phone=?, address=?
           WHERE beneficiary_id=?""",
        (new_name, dob.isoformat(), new_gender, new_guardian,
         new_phone, new_address, beneficiary_id)
    )
    conn.commit()
    conn.close()
    return {"status": "updated", "beneficiary_id": beneficiary_id}


def db_delete_beneficiary(beneficiary_id):
    """Delete a beneficiary by ID."""
    conn = connect_db()
    cur = conn.execute(
        "DELETE FROM beneficiaries WHERE beneficiary_id = ?",
        (beneficiary_id,)
    )
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if affected == 0:
        raise ValueError("Beneficiary not found")
    return {"status": "deleted", "beneficiary_id": beneficiary_id}