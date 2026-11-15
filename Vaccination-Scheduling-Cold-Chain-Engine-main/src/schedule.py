"""
Vaccination Scheduling Module
Calculates dose status and manages schedule records in the database.
Preserves original calculate_dose_status() for test compatibility.
"""

from datetime import date
from src.database import connect_db


# ─────────────────────────────────────────────────────────────────────────────
# BUSINESS LOGIC (kept for test compatibility)
# ─────────────────────────────────────────────────────────────────────────────

def calculate_dose_status(due_date, today=None, completed=False, eligible=True):
    """
    Calculate vaccination dose status.

    Possible results: COMPLETED, INELIGIBLE, NOT_YET, DUE, OVERDUE
    """
    if completed:
        return "COMPLETED"

    if not eligible:
        return "INELIGIBLE"

    if today is None:
        today = date.today()

    try:
        if isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)
        if isinstance(today, str):
            today = date.fromisoformat(today)
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    if not isinstance(due_date, date):
        raise TypeError("due_date must be a date or YYYY-MM-DD string")
    if not isinstance(today, date):
        raise TypeError("today must be a date or YYYY-MM-DD string")

    if due_date > today:
        return "NOT_YET"

    days_late = (today - due_date).days

    if days_late > 28:
        return "OVERDUE"

    return "DUE"


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def db_add_schedule(beneficiary_id, vaccine_name, dose_number, due_date, notes=""):
    """Add a vaccination schedule entry to the database."""
    beneficiary_id = str(beneficiary_id).strip()
    vaccine_name   = str(vaccine_name).strip()

    if not beneficiary_id or not vaccine_name:
        raise ValueError("Beneficiary ID and vaccine name are required.")

    try:
        d = date.fromisoformat(str(due_date))
    except ValueError:
        raise ValueError("Due date must be in YYYY-MM-DD format.")

    try:
        dose_number = int(dose_number)
    except (ValueError, TypeError):
        raise ValueError("Dose number must be an integer.")

    # Determine initial status
    status = calculate_dose_status(d)

    conn = connect_db()
    try:
        conn.execute(
            """INSERT INTO schedules (beneficiary_id, vaccine_name, dose_number, due_date, status, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (beneficiary_id, vaccine_name, dose_number, d.isoformat(), status, notes)
        )
        conn.commit()
        return {"status": "success", "schedule_status": status}
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Could not add schedule: {e}")
    finally:
        conn.close()


def db_get_all_schedules():
    """Return all schedule entries with fresh status."""
    conn = connect_db()
    rows = conn.execute(
        """SELECT s.*, b.name AS beneficiary_name
           FROM schedules s
           LEFT JOIN beneficiaries b ON s.beneficiary_id = b.beneficiary_id
           ORDER BY s.due_date"""
    ).fetchall()
    conn.close()

    today = date.today()
    result = []
    for r in rows:
        d = dict(r)
        if d["status"] not in ("COMPLETED", "INELIGIBLE"):
            d["status"] = calculate_dose_status(d["due_date"], today)
        result.append(d)
    return result


def db_get_schedules_for_beneficiary(beneficiary_id):
    """Return schedule entries for a specific beneficiary."""
    conn = connect_db()
    rows = conn.execute(
        "SELECT * FROM schedules WHERE beneficiary_id=? ORDER BY due_date",
        (beneficiary_id,)
    ).fetchall()
    conn.close()
    today = date.today()
    result = []
    for r in rows:
        d = dict(r)
        if d["status"] not in ("COMPLETED", "INELIGIBLE"):
            d["status"] = calculate_dose_status(d["due_date"], today)
        result.append(d)
    return result


def db_update_schedule_status(schedule_id, status):
    """Manually update a schedule entry's status."""
    allowed = {"COMPLETED", "INELIGIBLE", "NOT_YET", "DUE", "OVERDUE"}
    if status not in allowed:
        raise ValueError(f"Status must be one of: {', '.join(allowed)}")

    conn = connect_db()
    cur = conn.execute(
        "UPDATE schedules SET status=? WHERE id=?",
        (status, schedule_id)
    )
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if affected == 0:
        raise ValueError("Schedule entry not found")
    return {"status": "updated", "id": schedule_id, "new_status": status}


def db_delete_schedule(schedule_id):
    """Delete a schedule entry by ID."""
    conn = connect_db()
    cur = conn.execute("DELETE FROM schedules WHERE id=?", (schedule_id,))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if affected == 0:
        raise ValueError("Schedule entry not found")
    return {"status": "deleted", "id": schedule_id}


def db_refresh_all_statuses():
    """Refresh DUE/NOT_YET/OVERDUE statuses for all pending schedules."""
    conn = connect_db()
    rows = conn.execute(
        "SELECT id, due_date FROM schedules WHERE status NOT IN ('COMPLETED','INELIGIBLE')"
    ).fetchall()
    today = date.today()
    for row in rows:
        new_status = calculate_dose_status(row["due_date"], today)
        conn.execute("UPDATE schedules SET status=? WHERE id=?", (new_status, row["id"]))
    conn.commit()
    conn.close()
    return {"refreshed": len(rows)}