"""
Cold-Chain Monitoring Module
Checks vaccine temperature conditions and logs readings to database.
Preserves original check_cold_chain() for test compatibility.
"""

from src.database import connect_db


# ─────────────────────────────────────────────────────────────────────────────
# BUSINESS LOGIC (kept for test compatibility)
# ─────────────────────────────────────────────────────────────────────────────

def check_cold_chain(vaccine_name, temperature, cumulative_heat_hours,
                     freeze_sensitive=True, vvm_stage=1):
    """
    Check vaccine cold-chain condition.

    Results: SAFE, QUARANTINE, DISCARD
    """
    # VVM stage 3 or 4 means discard
    if vvm_stage >= 3:
        return "DISCARD"

    # Freeze-sensitive vaccines exposed below 0°C
    if freeze_sensitive and temperature < 0:
        return "DISCARD"

    # More than 48 cumulative heat hours
    if cumulative_heat_hours > 48:
        return "QUARANTINE"

    return "SAFE"


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def db_log_cold_chain(vaccine_name, temperature, cumulative_heat_hours=0,
                      freeze_sensitive=True, vvm_stage=1):
    """Log a cold-chain reading to the database and return its status."""
    if not vaccine_name:
        raise ValueError("Vaccine name is required.")

    try:
        temperature           = float(temperature)
        cumulative_heat_hours = float(cumulative_heat_hours)
        vvm_stage             = int(vvm_stage)
    except (ValueError, TypeError):
        raise ValueError("Temperature, heat hours, and VVM stage must be numeric.")

    status = check_cold_chain(
        vaccine_name, temperature, cumulative_heat_hours,
        freeze_sensitive=freeze_sensitive, vvm_stage=vvm_stage
    )

    conn = connect_db()
    try:
        conn.execute(
            """INSERT INTO cold_chain
               (vaccine_name, temperature, cumulative_heat_hours, freeze_sensitive, vvm_stage, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (vaccine_name, temperature, cumulative_heat_hours,
             1 if freeze_sensitive else 0, vvm_stage, status)
        )
        conn.commit()
        return {
            "vaccine_name":          vaccine_name,
            "temperature":           temperature,
            "cumulative_heat_hours": cumulative_heat_hours,
            "vvm_stage":             vvm_stage,
            "status":                status
        }
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Could not log cold chain reading: {e}")
    finally:
        conn.close()


def db_get_all_cold_chain():
    """Return all cold chain readings, newest first."""
    conn = connect_db()
    rows = conn.execute(
        "SELECT * FROM cold_chain ORDER BY recorded_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_get_cold_chain_alerts():
    """Return only QUARANTINE and DISCARD readings."""
    conn = connect_db()
    rows = conn.execute(
        "SELECT * FROM cold_chain WHERE status != 'SAFE' ORDER BY recorded_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_delete_cold_chain(reading_id):
    """Delete a cold chain reading by ID."""
    conn = connect_db()
    cur = conn.execute("DELETE FROM cold_chain WHERE id=?", (reading_id,))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if affected == 0:
        raise ValueError("Reading not found")
    return {"status": "deleted", "id": reading_id}