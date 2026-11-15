"""
AEFI Management Module
Adverse Events Following Immunisation.
Preserves original in-memory functions for test compatibility.
"""

from src.database import connect_db


# ─────────────────────────────────────────────────────────────────────────────
# IN-MEMORY FUNCTIONS (kept for test compatibility)
# ─────────────────────────────────────────────────────────────────────────────

def record_aefi(aefi_records, beneficiary_id, vaccine_name,
                event_description, severity):
    """Record an adverse event after vaccination into an in-memory list."""
    beneficiary_id = str(beneficiary_id).strip()
    vaccine_name   = str(vaccine_name).strip()

    if not beneficiary_id:
        raise ValueError("Beneficiary ID is required.")
    if not vaccine_name:
        raise ValueError("Vaccine name is required.")
    if not event_description.strip():
        raise ValueError("Event description is required.")

    severity = severity.upper()
    if severity not in ["MILD", "MODERATE", "SEVERE"]:
        raise ValueError("Severity must be MILD, MODERATE or SEVERE.")

    record = {
        "beneficiary_id":    beneficiary_id,
        "vaccine_name":      vaccine_name,
        "event_description": event_description,
        "severity":          severity,
        "medical_clearance": severity != "SEVERE"
    }
    aefi_records.append(record)
    return record


def can_receive_next_dose(aefi_records, beneficiary_id):
    """Check whether a beneficiary is cleared for another dose."""
    for event in aefi_records:
        if (event["beneficiary_id"] == beneficiary_id
                and event["severity"] == "SEVERE"
                and not event["medical_clearance"]):
            return False
    return True


def give_medical_clearance(aefi_records, beneficiary_id):
    """Record medical clearance for severe AEFI."""
    found = False
    for event in aefi_records:
        if (event["beneficiary_id"] == beneficiary_id
                and event["severity"] == "SEVERE"):
            event["medical_clearance"] = True
            found = True
    if not found:
        raise ValueError("No severe AEFI record found.")
    return "Medical clearance recorded successfully."


def display_aefi_records(aefi_records):
    """Display all recorded adverse events."""
    if not aefi_records:
        print("No AEFI records available.")
        return
    print("\nAEFI RECORDS")
    print("-----------------------------")
    for record in aefi_records:
        print("Beneficiary:", record["beneficiary_id"])
        print("Vaccine:",     record["vaccine_name"])
        print("Event:",       record["event_description"])
        print("Severity:",    record["severity"])
        print("Medical clearance:", record["medical_clearance"])
        print("-----------------------------")


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def db_record_aefi(beneficiary_id, vaccine_name, event_description, severity, report_date=None):
    """Record an AEFI event to the database."""
    beneficiary_id = str(beneficiary_id).strip()
    vaccine_name   = str(vaccine_name).strip()
    severity       = str(severity).upper().strip()

    if not beneficiary_id:
        raise ValueError("Beneficiary ID is required.")
    if not vaccine_name:
        raise ValueError("Vaccine name is required.")
    if not event_description or not event_description.strip():
        raise ValueError("Event description is required.")
    if severity not in ["MILD", "MODERATE", "SEVERE"]:
        raise ValueError("Severity must be MILD, MODERATE or SEVERE.")

    medical_clearance = 1 if severity != "SEVERE" else 0

    conn = connect_db()
    try:
        if report_date:
            conn.execute(
                """INSERT INTO aefi (beneficiary_id, vaccine_name, event_description, severity, medical_clearance, report_date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (beneficiary_id, vaccine_name, event_description.strip(),
                 severity, medical_clearance, report_date)
            )
        else:
            conn.execute(
                """INSERT INTO aefi (beneficiary_id, vaccine_name, event_description, severity, medical_clearance)
                   VALUES (?, ?, ?, ?, ?)""",
                (beneficiary_id, vaccine_name, event_description.strip(),
                 severity, medical_clearance)
            )
        conn.commit()
        return {
            "status":           "success",
            "severity":         severity,
            "medical_clearance": bool(medical_clearance)
        }
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Could not record AEFI: {e}")
    finally:
        conn.close()


def db_get_all_aefi():
    """Return all AEFI records with beneficiary name."""
    conn = connect_db()
    rows = conn.execute(
        """SELECT a.*, b.name AS beneficiary_name
           FROM aefi a
           LEFT JOIN beneficiaries b ON a.beneficiary_id = b.beneficiary_id
           ORDER BY a.report_date DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_get_aefi_for_beneficiary(beneficiary_id):
    """Return AEFI records for a specific beneficiary."""
    conn = connect_db()
    rows = conn.execute(
        "SELECT * FROM aefi WHERE beneficiary_id=? ORDER BY report_date DESC",
        (beneficiary_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_grant_medical_clearance(aefi_id):
    """Grant medical clearance for a severe AEFI record."""
    conn = connect_db()
    row = conn.execute(
        "SELECT * FROM aefi WHERE id=?", (aefi_id,)
    ).fetchone()
    if not row:
        conn.close()
        raise ValueError("AEFI record not found.")
    if row["severity"] != "SEVERE":
        conn.close()
        raise ValueError("Medical clearance is only needed for SEVERE AEFI.")

    conn.execute("UPDATE aefi SET medical_clearance=1 WHERE id=?", (aefi_id,))
    conn.commit()
    conn.close()
    return {"status": "cleared", "id": aefi_id}


def db_delete_aefi(aefi_id):
    """Delete an AEFI record by ID."""
    conn = connect_db()
    cur = conn.execute("DELETE FROM aefi WHERE id=?", (aefi_id,))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if affected == 0:
        raise ValueError("AEFI record not found")
    return {"status": "deleted", "id": aefi_id}