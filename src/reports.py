"""
Reports Module
Generates summary statistics from the database.
Preserves original generate_report() for test compatibility.
"""

from src.database import connect_db


# ─────────────────────────────────────────────────────────────────────────────
# IN-MEMORY FUNCTION (kept for test compatibility)
# ─────────────────────────────────────────────────────────────────────────────

def generate_report(beneficiaries, dose_events, inventory):
    """Generate a basic vaccination summary report from in-memory data."""
    total_beneficiaries = len(beneficiaries)
    total_doses = len(dose_events)

    vaccine_stock = {}
    for batch in inventory:
        name = batch["vaccine_name"]
        vaccine_stock[name] = vaccine_stock.get(name, 0) + batch["quantity"]

    return {
        "total_beneficiaries":     total_beneficiaries,
        "total_doses_administered": total_doses,
        "remaining_vaccine_stock": vaccine_stock
    }


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def db_generate_full_report():
    """Generate a comprehensive summary from the database."""
    conn = connect_db()

    total_beneficiaries = conn.execute(
        "SELECT COUNT(*) AS c FROM beneficiaries"
    ).fetchone()["c"]

    total_doses = conn.execute(
        "SELECT COUNT(*) AS c FROM doses"
    ).fetchone()["c"]

    # Doses per vaccine
    doses_by_vaccine = conn.execute(
        """SELECT vaccine_name, COUNT(*) AS total
           FROM doses GROUP BY vaccine_name ORDER BY total DESC"""
    ).fetchall()

    # Schedules by status
    schedules_by_status = conn.execute(
        """SELECT status, COUNT(*) AS total
           FROM schedules GROUP BY status"""
    ).fetchall()

    # Inventory summary (non-expired)
    inventory_summary = conn.execute(
        """SELECT vaccine_name, SUM(quantity) AS total_quantity
           FROM inventory
           WHERE expiry_date > DATE('now')
           GROUP BY vaccine_name"""
    ).fetchall()

    # AEFI severity breakdown
    aefi_by_severity = conn.execute(
        "SELECT severity, COUNT(*) AS total FROM aefi GROUP BY severity"
    ).fetchall()

    # Cold-chain alerts in last 30 days
    cc_alerts = conn.execute(
        """SELECT status, COUNT(*) AS total
           FROM cold_chain
           WHERE status != 'SAFE' AND recorded_at >= DATE('now', '-30 days')
           GROUP BY status"""
    ).fetchall()

    # Overdue schedules (top 5 beneficiaries)
    overdue = conn.execute(
        """SELECT s.beneficiary_id, b.name, COUNT(*) AS overdue_count
           FROM schedules s
           LEFT JOIN beneficiaries b ON s.beneficiary_id = b.beneficiary_id
           WHERE s.status = 'OVERDUE'
           GROUP BY s.beneficiary_id
           ORDER BY overdue_count DESC
           LIMIT 5"""
    ).fetchall()

    conn.close()

    return {
        "total_beneficiaries":    total_beneficiaries,
        "total_doses_administered": total_doses,
        "doses_by_vaccine":       [dict(r) for r in doses_by_vaccine],
        "schedules_by_status":    [dict(r) for r in schedules_by_status],
        "inventory_summary":      [dict(r) for r in inventory_summary],
        "aefi_by_severity":       [dict(r) for r in aefi_by_severity],
        "cold_chain_alerts_30d":  [dict(r) for r in cc_alerts],
        "top_overdue":            [dict(r) for r in overdue]
    }


def db_coverage_report():
    """Calculate vaccination coverage per vaccine."""
    conn = connect_db()
    rows = conn.execute(
        """SELECT vaccine_name,
                  COUNT(*) AS scheduled,
                  SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed
           FROM schedules
           GROUP BY vaccine_name
           ORDER BY vaccine_name"""
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["coverage_pct"] = (
            round(d["completed"] / d["scheduled"] * 100, 1)
            if d["scheduled"] > 0 else 0
        )
        result.append(d)
    return result