"""
Flask Web Application — Vaccination Scheduling and Cold-Chain Engine
PS-065 | Team T113
"""

import sys
import os

# Ensure project root is on path so `src` package resolves correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from src.database import create_tables, DB_PATH
from src.beneficiary import (
    db_add_beneficiary, db_get_all_beneficiaries,
    db_get_beneficiary, db_update_beneficiary, db_delete_beneficiary
)
from src.dose import (
    db_add_dose, db_get_all_doses,
    db_get_doses_for_beneficiary, db_delete_dose
)
from src.schedule import (
    db_add_schedule, db_get_all_schedules,
    db_get_schedules_for_beneficiary, db_update_schedule_status,
    db_delete_schedule, db_refresh_all_statuses
)
from src.inventory import (
    db_add_stock, db_get_all_inventory,
    db_get_inventory_summary, db_issue_stock, db_delete_stock
)
from src.cold_chain import (
    db_log_cold_chain, db_get_all_cold_chain,
    db_get_cold_chain_alerts, db_delete_cold_chain
)
from src.aefi import (
    db_record_aefi, db_get_all_aefi,
    db_get_aefi_for_beneficiary, db_grant_medical_clearance, db_delete_aefi
)
from src.reports import db_generate_full_report, db_coverage_report

app = Flask(__name__)
app.secret_key = "vaccin@T113-PS065-secret"

# Initialise database on startup
create_tables()


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def dashboard():
    report     = db_generate_full_report()
    cc_alerts  = db_get_cold_chain_alerts()
    schedules  = db_get_all_schedules()
    overdue    = [s for s in schedules if s["status"] == "OVERDUE"]
    due_today  = [s for s in schedules if s["status"] == "DUE"]
    return render_template("dashboard.html",
                           report=report,
                           cc_alerts=cc_alerts[:5],
                           overdue=overdue[:5],
                           due_today=due_today[:5])


# ═══════════════════════════════════════════════════════════════════════════════
# BENEFICIARIES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/beneficiaries")
def beneficiaries():
    blist = db_get_all_beneficiaries()
    return render_template("beneficiaries.html", beneficiaries=blist)


@app.route("/beneficiaries/add", methods=["GET", "POST"])
def add_beneficiary():
    if request.method == "POST":
        try:
            db_add_beneficiary(
                beneficiary_id=request.form["beneficiary_id"],
                name=request.form["name"],
                date_of_birth=request.form["date_of_birth"],
                gender=request.form.get("gender", ""),
                guardian_name=request.form.get("guardian_name", ""),
                phone=request.form.get("phone", ""),
                address=request.form.get("address", "")
            )
            flash("Beneficiary added successfully.", "success")
            return redirect(url_for("beneficiaries"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("add_beneficiary.html")


@app.route("/beneficiaries/<bid>/edit", methods=["GET", "POST"])
def edit_beneficiary(bid):
    b = db_get_beneficiary(bid)
    if not b:
        flash("Beneficiary not found.", "error")
        return redirect(url_for("beneficiaries"))
    if request.method == "POST":
        try:
            db_update_beneficiary(
                beneficiary_id=bid,
                name=request.form["name"],
                date_of_birth=request.form["date_of_birth"],
                gender=request.form.get("gender", ""),
                guardian_name=request.form.get("guardian_name", ""),
                phone=request.form.get("phone", ""),
                address=request.form.get("address", "")
            )
            flash("Beneficiary updated successfully.", "success")
            return redirect(url_for("beneficiaries"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("edit_beneficiary.html", b=b)


@app.route("/beneficiaries/<bid>/delete", methods=["POST"])
def delete_beneficiary(bid):
    try:
        db_delete_beneficiary(bid)
        flash("Beneficiary deleted.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("beneficiaries"))


@app.route("/beneficiaries/<bid>")
def view_beneficiary(bid):
    b       = db_get_beneficiary(bid)
    if not b:
        flash("Beneficiary not found.", "error")
        return redirect(url_for("beneficiaries"))
    doses   = db_get_doses_for_beneficiary(bid)
    sched   = db_get_schedules_for_beneficiary(bid)
    aefis   = db_get_aefi_for_beneficiary(bid)
    return render_template("view_beneficiary.html", b=b, doses=doses, schedules=sched, aefis=aefis)


# ═══════════════════════════════════════════════════════════════════════════════
# DOSES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/doses")
def doses():
    dlist = db_get_all_doses()
    return render_template("doses.html", doses=dlist)


@app.route("/doses/add", methods=["GET", "POST"])
def add_dose():
    beneficiaries = db_get_all_beneficiaries()
    if request.method == "POST":
        try:
            db_add_dose(
                beneficiary_id=request.form["beneficiary_id"],
                vaccine_name=request.form["vaccine_name"],
                dose_number=int(request.form["dose_number"]),
                administered_date=request.form["administered_date"],
                notes=request.form.get("notes", "")
            )
            flash("Dose recorded successfully.", "success")
            return redirect(url_for("doses"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("add_dose.html", beneficiaries=beneficiaries)


@app.route("/doses/<int:dose_id>/delete", methods=["POST"])
def delete_dose(dose_id):
    try:
        db_delete_dose(dose_id)
        flash("Dose record deleted.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("doses"))


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEDULES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/schedules")
def schedules():
    db_refresh_all_statuses()
    slist = db_get_all_schedules()
    return render_template("schedules.html", schedules=slist)


@app.route("/schedules/add", methods=["GET", "POST"])
def add_schedule():
    beneficiaries = db_get_all_beneficiaries()
    if request.method == "POST":
        try:
            db_add_schedule(
                beneficiary_id=request.form["beneficiary_id"],
                vaccine_name=request.form["vaccine_name"],
                dose_number=int(request.form["dose_number"]),
                due_date=request.form["due_date"],
                notes=request.form.get("notes", "")
            )
            flash("Schedule added successfully.", "success")
            return redirect(url_for("schedules"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("add_schedule.html", beneficiaries=beneficiaries)


@app.route("/schedules/<int:sid>/status", methods=["POST"])
def update_schedule_status(sid):
    try:
        db_update_schedule_status(sid, request.form["status"])
        flash("Schedule status updated.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("schedules"))


@app.route("/schedules/<int:sid>/delete", methods=["POST"])
def delete_schedule(sid):
    try:
        db_delete_schedule(sid)
        flash("Schedule deleted.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("schedules"))


# ═══════════════════════════════════════════════════════════════════════════════
# INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/inventory")
def inventory():
    batches = db_get_all_inventory()
    summary = db_get_inventory_summary()
    return render_template("inventory.html", batches=batches, summary=summary)


@app.route("/inventory/add", methods=["GET", "POST"])
def add_inventory():
    if request.method == "POST":
        try:
            db_add_stock(
                vaccine_name=request.form["vaccine_name"],
                batch_number=request.form["batch_number"],
                quantity=int(request.form["quantity"]),
                expiry_date=request.form["expiry_date"],
                storage_temp=float(request.form.get("storage_temp", 4.0))
            )
            flash("Stock added successfully.", "success")
            return redirect(url_for("inventory"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("add_inventory.html")


@app.route("/inventory/issue", methods=["POST"])
def issue_inventory():
    try:
        issued = db_issue_stock(
            vaccine_name=request.form["vaccine_name"],
            required_quantity=int(request.form["quantity"])
        )
        flash(f"Issued successfully: {issued}", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("inventory"))


@app.route("/inventory/<int:bid>/delete", methods=["POST"])
def delete_inventory(bid):
    try:
        db_delete_stock(bid)
        flash("Batch deleted.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("inventory"))


# ═══════════════════════════════════════════════════════════════════════════════
# COLD CHAIN
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/coldchain")
def coldchain():
    readings = db_get_all_cold_chain()
    alerts   = db_get_cold_chain_alerts()
    return render_template("coldchain.html", readings=readings, alerts=alerts)


@app.route("/coldchain/log", methods=["GET", "POST"])
def log_coldchain():
    if request.method == "POST":
        try:
            result = db_log_cold_chain(
                vaccine_name=request.form["vaccine_name"],
                temperature=float(request.form["temperature"]),
                cumulative_heat_hours=float(request.form.get("cumulative_heat_hours", 0)),
                freeze_sensitive=request.form.get("freeze_sensitive") == "on",
                vvm_stage=int(request.form.get("vvm_stage", 1))
            )
            flash(f"Reading logged. Status: {result['status']}", "success")
            return redirect(url_for("coldchain"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("log_coldchain.html")


@app.route("/coldchain/<int:rid>/delete", methods=["POST"])
def delete_coldchain(rid):
    try:
        db_delete_cold_chain(rid)
        flash("Reading deleted.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("coldchain"))


# ═══════════════════════════════════════════════════════════════════════════════
# AEFI
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/aefi")
def aefi():
    records = db_get_all_aefi()
    return render_template("aefi.html", records=records)


@app.route("/aefi/add", methods=["GET", "POST"])
def add_aefi():
    beneficiaries = db_get_all_beneficiaries()
    if request.method == "POST":
        try:
            db_record_aefi(
                beneficiary_id=request.form["beneficiary_id"],
                vaccine_name=request.form["vaccine_name"],
                event_description=request.form["event_description"],
                severity=request.form["severity"],
                report_date=request.form.get("report_date") or None
            )
            flash("AEFI recorded successfully.", "success")
            return redirect(url_for("aefi"))
        except ValueError as e:
            flash(str(e), "error")
    return render_template("add_aefi.html", beneficiaries=beneficiaries)


@app.route("/aefi/<int:aid>/clear", methods=["POST"])
def clear_aefi(aid):
    try:
        db_grant_medical_clearance(aid)
        flash("Medical clearance granted.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("aefi"))


@app.route("/aefi/<int:aid>/delete", methods=["POST"])
def delete_aefi(aid):
    try:
        db_delete_aefi(aid)
        flash("AEFI record deleted.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect(url_for("aefi"))


# ═══════════════════════════════════════════════════════════════════════════════
# REPORTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/reports")
def reports():
    report   = db_generate_full_report()
    coverage = db_coverage_report()
    return render_template("reports.html", report=report, coverage=coverage)


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  VACCINATION SCHEDULING AND COLD-CHAIN ENGINE")
    print("  PS-065 | Team T113")
    print("=" * 60)
    print(f"  Database: {DB_PATH}")
    print("  Running at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)
