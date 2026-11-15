"""
Dose Management Module
Records and retrieves vaccination doses.
Preserves original in-memory record_dose() for test compatibility.
"""

from datetime import date
from src.database import connect_db


# ─────────────────────────────────────────────────────────────────────────────
# IN-MEMORY FUNCTION (kept for existing test compatibility)
# ─────────────────────────────────────────────────────────────────────────────

def record_dose(dose_events, beneficiary_id, vaccine_name, dose_number, administered_date):
    """Record a vaccination dose into an in-memory list."""

    beneficiary_id = str(beneficiary_id).strip()
    vaccine_name   = str(vaccine_name).strip()

    if not beneficiary_id or not vaccine_name:
        raise ValueError("Beneficiary ID and vaccine are required.")

    if not isinstance(dose_number, int) or dose_number < 1:
        raise ValueError("Dose number must be a positive integer.")

    try:
        given_date = date.fromisoformat(str(administered_date))
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")

    event = {
        "beneficiary_id":   beneficiary_id,
        "vaccine_name":     vaccine_name,
        "dose_number":      dose_number,
        "administered_date": given_date.isoformat()
    }
    dose_events.append(event)
    return event


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def db_add_dose(beneficiary_id, vaccine_name, dose_number, administered_date, notes=""):
    """Add a dose record to the database."""
    beneficiary_id = str(beneficiary_id).strip()
    vaccine_name   = str(vaccine_name).strip()

    if not beneficiary_id or not vaccine_name:
        raise ValueError("Beneficiary ID and vaccine are required.")

    try:
        dose_number = int(dose_number)
    except (ValueError, TypeError):
        raise ValueError("Dose number must be an integer.")

    if dose_number < 1:
        raise ValueError("Dose number must be a positive integer.")

    try:
        given_date = date.fromisoformat(str(administered_date))
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")

    conn = connect_db()
    try:
        conn.execute(
            """INSERT INTO doses (beneficiary_id, vaccine_name, dose_number, administered_date, notes)
               VALUES (?, ?, ?, ?, ?)""",
            (beneficiary_id, vaccine_name, dose_number, given_date.isoformat(), notes)
        )
        # Mark related schedule entry as COMPLETED
        conn.execute(
            """UPDATE schedules SET status='COMPLETED'
               WHERE beneficiary_id=? AND vaccine_name=? AND dose_number=?""",
            (beneficiary_id, vaccine_name, dose_number)
        )
        conn.commit()
        return {"status": "success", "beneficiary_id": beneficiary_id,
                "vaccine_name": vaccine_name, "dose_number": dose_number}
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Could not record dose: {e}")
    finally:
        conn.close()


def db_get_all_doses():
    """Return all dose records."""
    conn = connect_db()
    rows = conn.execute(
        """SELECT d.*, b.name AS beneficiary_name
           FROM doses d
           LEFT JOIN beneficiaries b ON d.beneficiary_id = b.beneficiary_id
           ORDER BY d.administered_date DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_get_doses_for_beneficiary(beneficiary_id):
    """Return dose history for a specific beneficiary."""
    conn = connect_db()
    rows = conn.execute(
        """SELECT * FROM doses WHERE beneficiary_id=? ORDER BY administered_date""",
        (beneficiary_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_delete_dose(dose_id):
    """Delete a dose by its ID."""
    conn = connect_db()
    cur = conn.execute("DELETE FROM doses WHERE id=?", (dose_id,))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if affected == 0:
        raise ValueError("Dose record not found")
    return {"status": "deleted", "id": dose_id}