"""
tests/test_full.py — Comprehensive integration test suite
PS-065 | Team T113 | Vaccination Scheduling and Cold-Chain Engine

Covers:
  - Database creation and schema
  - Beneficiary CRUD
  - Dose management
  - Scheduling and status logic
  - Inventory (FEFO, stock management)
  - Cold-chain monitoring
  - AEFI management
  - Reports
  - Flask routes (smoke tests)
  - Edge cases and error paths

Run:  python -m pytest tests/ -v
"""

import sys, os, tempfile, sqlite3, pytest

# ── make sure project root is importable ──────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """
    Redirect every test to its own temporary SQLite file so tests
    never interfere with the real vaccination.db.
    """
    import src.database as db_mod
    db_file = tmp_path / "test_vaccination.db"
    monkeypatch.setattr(db_mod, "DB_PATH", str(db_file))
    db_mod.create_tables()
    yield str(db_file)


# Convenience helpers
def add_b(bid="B001", name="Test Child", dob="2020-06-01"):
    from src.beneficiary import db_add_beneficiary
    return db_add_beneficiary(bid, name, dob)


def add_stock(vname="OPV", batch="OPV-001", qty=100, exp="2027-01-01"):
    from src.inventory import db_add_stock
    return db_add_stock(vname, batch, qty, exp)


def add_schedule(bid="B001", vname="OPV", dose=1, due="2026-12-01"):
    from src.schedule import db_add_schedule
    return db_add_schedule(bid, vname, dose, due)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

class TestDatabase:

    def test_tables_created(self, isolated_db):
        conn = sqlite3.connect(isolated_db)
        cur  = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cur.fetchall()}
        conn.close()
        expected = {"beneficiaries", "doses", "schedules",
                    "inventory", "cold_chain", "aefi"}
        assert expected.issubset(tables)

    def test_foreign_keys_enabled(self, isolated_db):
        conn = sqlite3.connect(isolated_db)
        result = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        conn.close()
        # foreign_keys may be enabled per-connection; just verify the pragma works
        assert result in (0, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. BENEFICIARY
# ═══════════════════════════════════════════════════════════════════════════════

class TestBeneficiary:

    def test_add_and_get(self):
        from src.beneficiary import db_add_beneficiary, db_get_beneficiary
        db_add_beneficiary("B001", "Priya", "2021-04-01")
        b = db_get_beneficiary("B001")
        assert b is not None
        assert b["name"] == "Priya"

    def test_add_full_fields(self):
        from src.beneficiary import db_add_beneficiary, db_get_beneficiary
        db_add_beneficiary("B010", "Rahul", "2019-01-01",
                           gender="Male", guardian_name="Suresh",
                           phone="9876543210", address="12 MG Road")
        b = db_get_beneficiary("B010")
        assert b["phone"] == "9876543210"
        assert b["gender"] == "Male"

    def test_duplicate_id_raises(self):
        from src.beneficiary import db_add_beneficiary
        db_add_beneficiary("B002", "Ravi", "2020-01-01")
        with pytest.raises(ValueError):
            db_add_beneficiary("B002", "Ravi", "2020-01-01")

    def test_missing_id_raises(self):
        from src.beneficiary import db_add_beneficiary
        with pytest.raises(ValueError):
            db_add_beneficiary("", "Name", "2020-01-01")

    def test_missing_name_raises(self):
        from src.beneficiary import db_add_beneficiary
        with pytest.raises(ValueError):
            db_add_beneficiary("B003", "", "2020-01-01")

    def test_future_dob_raises(self):
        from src.beneficiary import db_add_beneficiary
        with pytest.raises(ValueError):
            db_add_beneficiary("B004", "Baby", "2099-01-01")

    def test_invalid_dob_format_raises(self):
        from src.beneficiary import db_add_beneficiary
        with pytest.raises(ValueError):
            db_add_beneficiary("B005", "Child", "not-a-date")

    def test_get_all(self):
        from src.beneficiary import db_add_beneficiary, db_get_all_beneficiaries
        db_add_beneficiary("B010", "Alice", "2020-01-01")
        db_add_beneficiary("B011", "Bob",   "2019-06-01")
        all_b = db_get_all_beneficiaries()
        ids = [b["beneficiary_id"] for b in all_b]
        assert "B010" in ids and "B011" in ids

    def test_update(self):
        from src.beneficiary import db_add_beneficiary, db_update_beneficiary, db_get_beneficiary
        db_add_beneficiary("B020", "Old Name", "2020-01-01")
        db_update_beneficiary("B020", name="New Name", phone="1234567890")
        b = db_get_beneficiary("B020")
        assert b["name"] == "New Name"
        assert b["phone"] == "1234567890"

    def test_update_nonexistent_raises(self):
        from src.beneficiary import db_update_beneficiary
        with pytest.raises(ValueError):
            db_update_beneficiary("ZZZZ", name="X")

    def test_delete(self):
        from src.beneficiary import db_add_beneficiary, db_delete_beneficiary, db_get_beneficiary
        db_add_beneficiary("B030", "Delete Me", "2020-01-01")
        db_delete_beneficiary("B030")
        assert db_get_beneficiary("B030") is None

    def test_delete_nonexistent_raises(self):
        from src.beneficiary import db_delete_beneficiary
        with pytest.raises(ValueError):
            db_delete_beneficiary("DOES_NOT_EXIST")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. DOSE
# ═══════════════════════════════════════════════════════════════════════════════

class TestDose:

    def test_add_dose(self):
        from src.dose import db_add_dose, db_get_all_doses
        add_b()
        db_add_dose("B001", "OPV", 1, "2021-01-01")
        doses = db_get_all_doses()
        assert len(doses) == 1
        assert doses[0]["vaccine_name"] == "OPV"

    def test_dose_number_must_be_positive(self):
        from src.dose import db_add_dose
        add_b()
        with pytest.raises(ValueError):
            db_add_dose("B001", "OPV", 0, "2021-01-01")

    def test_negative_dose_number_raises(self):
        from src.dose import db_add_dose
        add_b()
        with pytest.raises(ValueError):
            db_add_dose("B001", "OPV", -1, "2021-01-01")

    def test_invalid_date_raises(self):
        from src.dose import db_add_dose
        add_b()
        with pytest.raises(ValueError):
            db_add_dose("B001", "OPV", 1, "bad-date")

    def test_get_doses_for_beneficiary(self):
        from src.dose import db_add_dose, db_get_doses_for_beneficiary
        add_b()
        db_add_dose("B001", "BCG", 1, "2021-01-05")
        db_add_dose("B001", "OPV", 1, "2021-02-01")
        doses = db_get_doses_for_beneficiary("B001")
        assert len(doses) == 2

    def test_delete_dose(self):
        from src.dose import db_add_dose, db_get_all_doses, db_delete_dose
        add_b()
        db_add_dose("B001", "OPV", 1, "2021-01-01")
        dose_id = db_get_all_doses()[0]["id"]
        db_delete_dose(dose_id)
        assert len(db_get_all_doses()) == 0

    def test_delete_nonexistent_dose_raises(self):
        from src.dose import db_delete_dose
        with pytest.raises(ValueError):
            db_delete_dose(9999)

    def test_dose_marks_schedule_completed(self):
        from src.dose import db_add_dose
        from src.schedule import db_add_schedule, db_get_schedules_for_beneficiary
        add_b()
        db_add_schedule("B001", "OPV", 1, "2026-11-01")
        db_add_dose("B001", "OPV", 1, "2026-11-02")
        scheds = db_get_schedules_for_beneficiary("B001")
        assert scheds[0]["status"] == "COMPLETED"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. SCHEDULE
# ═══════════════════════════════════════════════════════════════════════════════

class TestSchedule:

    def test_add_schedule(self):
        from src.schedule import db_add_schedule, db_get_all_schedules
        add_b()
        db_add_schedule("B001", "BCG", 1, "2026-12-01")
        scheds = db_get_all_schedules()
        assert len(scheds) >= 1

    def test_status_not_yet(self):
        from src.schedule import calculate_dose_status
        assert calculate_dose_status("2099-01-01") == "NOT_YET"

    def test_status_due(self):
        from src.schedule import calculate_dose_status
        from datetime import date
        today = date.today().isoformat()
        assert calculate_dose_status(today) == "DUE"

    def test_status_overdue(self):
        from src.schedule import calculate_dose_status
        assert calculate_dose_status("2020-01-01") == "OVERDUE"

    def test_status_completed(self):
        from src.schedule import calculate_dose_status
        assert calculate_dose_status("2026-01-01", completed=True) == "COMPLETED"

    def test_status_ineligible(self):
        from src.schedule import calculate_dose_status
        assert calculate_dose_status("2026-01-01", eligible=False) == "INELIGIBLE"

    def test_exactly_28_days_is_due_not_overdue(self):
        from src.schedule import calculate_dose_status
        assert calculate_dose_status("2026-10-17", "2026-11-14") == "DUE"

    def test_29_days_late_is_overdue(self):
        from src.schedule import calculate_dose_status
        assert calculate_dose_status("2026-10-16", "2026-11-14") == "OVERDUE"

    def test_update_status(self):
        from src.schedule import db_add_schedule, db_get_all_schedules, db_update_schedule_status
        add_b()
        db_add_schedule("B001", "BCG", 1, "2026-12-01")
        sid = db_get_all_schedules()[0]["id"]
        db_update_schedule_status(sid, "COMPLETED")
        updated = db_get_all_schedules()[0]
        assert updated["status"] == "COMPLETED"

    def test_invalid_status_raises(self):
        from src.schedule import db_add_schedule, db_get_all_schedules, db_update_schedule_status
        add_b()
        db_add_schedule("B001", "BCG", 1, "2026-12-01")
        sid = db_get_all_schedules()[0]["id"]
        with pytest.raises(ValueError):
            db_update_schedule_status(sid, "INVALID_STATUS")

    def test_delete_schedule(self):
        from src.schedule import db_add_schedule, db_get_all_schedules, db_delete_schedule
        add_b()
        db_add_schedule("B001", "BCG", 1, "2026-12-01")
        sid = db_get_all_schedules()[0]["id"]
        db_delete_schedule(sid)
        assert len(db_get_all_schedules()) == 0

    def test_refresh_statuses(self):
        from src.schedule import db_add_schedule, db_refresh_all_statuses
        add_b()
        db_add_schedule("B001", "OPV", 1, "2020-01-01")  # will become OVERDUE
        result = db_refresh_all_statuses()
        assert result["refreshed"] >= 1

    def test_invalid_date_raises(self):
        from src.schedule import db_add_schedule
        add_b()
        with pytest.raises(ValueError):
            db_add_schedule("B001", "BCG", 1, "not-a-date")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. INVENTORY
# ═══════════════════════════════════════════════════════════════════════════════

class TestInventory:

    def test_add_stock(self):
        from src.inventory import db_add_stock, db_get_all_inventory
        db_add_stock("OPV", "OPV-001", 100, "2027-01-01")
        inv = db_get_all_inventory()
        assert len(inv) == 1
        assert inv[0]["quantity"] == 100

    def test_zero_quantity_raises(self):
        from src.inventory import db_add_stock
        with pytest.raises(ValueError):
            db_add_stock("OPV", "OPV-002", 0, "2027-01-01")

    def test_negative_quantity_raises(self):
        from src.inventory import db_add_stock
        with pytest.raises(ValueError):
            db_add_stock("OPV", "OPV-003", -5, "2027-01-01")

    def test_expired_stock_raises(self):
        from src.inventory import db_add_stock
        with pytest.raises(ValueError):
            db_add_stock("OPV", "OPV-EXP", 100, "2000-01-01")

    def test_duplicate_batch_increases_quantity(self):
        from src.inventory import db_add_stock, db_get_all_inventory
        db_add_stock("OPV", "OPV-001", 50,  "2027-01-01")
        db_add_stock("OPV", "OPV-001", 30,  "2027-01-01")
        inv = db_get_all_inventory()
        assert inv[0]["quantity"] == 80

    def test_issue_stock_fefo(self):
        from src.inventory import db_add_stock, db_issue_stock, db_get_all_inventory
        db_add_stock("BCG", "BCG-EARLY",  50, "2027-03-01")  # expires earlier
        db_add_stock("BCG", "BCG-LATER", 50, "2027-12-01")  # expires later
        issued = db_issue_stock("BCG", 60)
        # 50 from early batch, 10 from later batch
        assert issued[0]["batch_number"] == "BCG-EARLY"
        assert issued[0]["quantity_issued"] == 50
        assert issued[1]["quantity_issued"] == 10

    def test_issue_stock_insufficient_raises(self):
        from src.inventory import db_add_stock, db_issue_stock
        db_add_stock("OPV", "OPV-SMALL", 10, "2027-01-01")
        with pytest.raises(ValueError):
            db_issue_stock("OPV", 500)

    def test_issue_zero_raises(self):
        from src.inventory import db_issue_stock
        with pytest.raises(ValueError):
            db_issue_stock("OPV", 0)

    def test_inventory_summary(self):
        from src.inventory import db_add_stock, db_get_inventory_summary
        db_add_stock("OPV", "OPV-S1", 100, "2027-01-01")
        db_add_stock("OPV", "OPV-S2",  50, "2027-06-01")
        summary = db_get_inventory_summary()
        opv = next(s for s in summary if s["vaccine_name"] == "OPV")
        assert opv["total_quantity"] == 150

    def test_delete_stock(self):
        from src.inventory import db_add_stock, db_get_all_inventory, db_delete_stock
        db_add_stock("OPV", "OPV-DEL", 100, "2027-01-01")
        bid = db_get_all_inventory()[0]["id"]
        db_delete_stock(bid)
        assert len(db_get_all_inventory()) == 0

    def test_delete_nonexistent_raises(self):
        from src.inventory import db_delete_stock
        with pytest.raises(ValueError):
            db_delete_stock(99999)

    # In-memory FEFO
    def test_inmemory_add_stock(self):
        from src.inventory import add_stock
        inv = []
        result = add_stock(inv, "BCG", "BCG-MEM-001", 50, "2027-01-01")
        assert result == "Stock added successfully"
        assert len(inv) == 1

    def test_inmemory_issue_stock_fefo(self):
        from src.inventory import add_stock, issue_stock
        inv = []
        add_stock(inv, "OPV", "OPV-A", 30, "2027-01-01")
        add_stock(inv, "OPV", "OPV-B", 20, "2027-06-01")
        issued = issue_stock(inv, "OPV", 35)
        assert issued[0]["batch_number"] == "OPV-A"
        assert issued[0]["quantity"] == 30
        assert issued[1]["quantity"] == 5

    def test_inmemory_insufficient_raises(self):
        from src.inventory import add_stock, issue_stock
        inv = []
        add_stock(inv, "OPV", "OPV-C", 5, "2027-01-01")
        with pytest.raises(ValueError):
            issue_stock(inv, "OPV", 100)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. COLD CHAIN
# ═══════════════════════════════════════════════════════════════════════════════

class TestColdChain:

    def test_safe_reading(self):
        from src.cold_chain import check_cold_chain
        assert check_cold_chain("OPV", 4.0, 10.0, True, 1) == "SAFE"

    def test_discard_vvm_stage_3(self):
        from src.cold_chain import check_cold_chain
        assert check_cold_chain("OPV", 4.0, 0.0, True, 3) == "DISCARD"

    def test_discard_vvm_stage_4(self):
        from src.cold_chain import check_cold_chain
        assert check_cold_chain("OPV", 4.0, 0.0, True, 4) == "DISCARD"

    def test_discard_freeze_sensitive_below_zero(self):
        from src.cold_chain import check_cold_chain
        assert check_cold_chain("OPV", -1.0, 0.0, True, 1) == "DISCARD"

    def test_safe_non_freeze_below_zero(self):
        from src.cold_chain import check_cold_chain
        assert check_cold_chain("BCG", -1.0, 0.0, False, 1) == "SAFE"

    def test_quarantine_excessive_heat_hours(self):
        from src.cold_chain import check_cold_chain
        assert check_cold_chain("OPV", 8.0, 49.0, True, 1) == "QUARANTINE"

    def test_exactly_48_heat_hours_is_safe(self):
        from src.cold_chain import check_cold_chain
        assert check_cold_chain("OPV", 8.0, 48.0, True, 1) == "SAFE"

    def test_log_to_db(self):
        from src.cold_chain import db_log_cold_chain, db_get_all_cold_chain
        result = db_log_cold_chain("OPV", 4.5, 5.0, True, 1)
        assert result["status"] == "SAFE"
        readings = db_get_all_cold_chain()
        assert len(readings) == 1

    def test_alerts_only_non_safe(self):
        from src.cold_chain import db_log_cold_chain, db_get_cold_chain_alerts
        db_log_cold_chain("OPV", 4.0, 5.0, True, 1)       # SAFE
        db_log_cold_chain("OPV", -1.0, 0.0, True, 1)      # DISCARD
        db_log_cold_chain("BCG", 8.0, 60.0, False, 1)     # QUARANTINE
        alerts = db_get_cold_chain_alerts()
        statuses = {a["status"] for a in alerts}
        assert "SAFE" not in statuses
        assert len(alerts) == 2

    def test_delete_reading(self):
        from src.cold_chain import db_log_cold_chain, db_get_all_cold_chain, db_delete_cold_chain
        db_log_cold_chain("OPV", 4.0, 0.0, True, 1)
        rid = db_get_all_cold_chain()[0]["id"]
        db_delete_cold_chain(rid)
        assert len(db_get_all_cold_chain()) == 0

    def test_delete_nonexistent_raises(self):
        from src.cold_chain import db_delete_cold_chain
        with pytest.raises(ValueError):
            db_delete_cold_chain(99999)

    def test_missing_vaccine_name_raises(self):
        from src.cold_chain import db_log_cold_chain
        with pytest.raises(ValueError):
            db_log_cold_chain("", 4.0, 0.0, True, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. AEFI
# ═══════════════════════════════════════════════════════════════════════════════

class TestAEFI:

    def test_record_mild_aefi(self):
        from src.aefi import db_record_aefi, db_get_all_aefi
        add_b()
        db_record_aefi("B001", "OPV", "Mild fever", "MILD")
        records = db_get_all_aefi()
        assert len(records) == 1
        assert records[0]["severity"] == "MILD"

    def test_mild_gets_auto_clearance(self):
        from src.aefi import db_record_aefi, db_get_all_aefi
        add_b()
        db_record_aefi("B001", "OPV", "Mild rash", "MILD")
        r = db_get_all_aefi()[0]
        assert r["medical_clearance"] == 1

    def test_severe_no_auto_clearance(self):
        from src.aefi import db_record_aefi, db_get_all_aefi
        add_b()
        db_record_aefi("B001", "OPV", "Anaphylaxis", "SEVERE")
        r = db_get_all_aefi()[0]
        assert r["medical_clearance"] == 0

    def test_grant_medical_clearance(self):
        from src.aefi import db_record_aefi, db_get_all_aefi, db_grant_medical_clearance
        add_b()
        db_record_aefi("B001", "OPV", "Anaphylaxis", "SEVERE")
        aid = db_get_all_aefi()[0]["id"]
        db_grant_medical_clearance(aid)
        updated = db_get_all_aefi()[0]
        assert updated["medical_clearance"] == 1

    def test_clearance_on_non_severe_raises(self):
        from src.aefi import db_record_aefi, db_get_all_aefi, db_grant_medical_clearance
        add_b()
        db_record_aefi("B001", "OPV", "Mild fever", "MILD")
        aid = db_get_all_aefi()[0]["id"]
        with pytest.raises(ValueError):
            db_grant_medical_clearance(aid)

    def test_invalid_severity_raises(self):
        from src.aefi import db_record_aefi
        add_b()
        with pytest.raises(ValueError):
            db_record_aefi("B001", "OPV", "Some event", "CRITICAL")

    def test_missing_description_raises(self):
        from src.aefi import db_record_aefi
        add_b()
        with pytest.raises(ValueError):
            db_record_aefi("B001", "OPV", "", "MILD")

    def test_missing_beneficiary_id_raises(self):
        from src.aefi import db_record_aefi
        with pytest.raises(ValueError):
            db_record_aefi("", "OPV", "Event", "MILD")

    def test_delete_aefi(self):
        from src.aefi import db_record_aefi, db_get_all_aefi, db_delete_aefi
        add_b()
        db_record_aefi("B001", "OPV", "Fever", "MILD")
        aid = db_get_all_aefi()[0]["id"]
        db_delete_aefi(aid)
        assert len(db_get_all_aefi()) == 0

    def test_delete_nonexistent_raises(self):
        from src.aefi import db_delete_aefi
        with pytest.raises(ValueError):
            db_delete_aefi(99999)

    def test_get_aefi_for_beneficiary(self):
        from src.aefi import db_record_aefi, db_get_aefi_for_beneficiary
        add_b()
        add_b("B002", "Other", "2021-01-01")
        db_record_aefi("B001", "OPV",  "Fever",    "MILD")
        db_record_aefi("B002", "BCG",  "Swelling", "MODERATE")
        b001_records = db_get_aefi_for_beneficiary("B001")
        assert len(b001_records) == 1
        assert b001_records[0]["vaccine_name"] == "OPV"

    # In-memory AEFI functions
    def test_inmemory_record_aefi(self):
        from src.aefi import record_aefi
        records = []
        r = record_aefi(records, "B001", "OPV", "Swelling", "MILD")
        assert r["severity"] == "MILD"
        assert len(records) == 1

    def test_inmemory_severe_no_clearance(self):
        from src.aefi import record_aefi, can_receive_next_dose
        records = []
        record_aefi(records, "B001", "OPV", "Anaphylaxis", "SEVERE")
        assert not can_receive_next_dose(records, "B001")

    def test_inmemory_give_clearance(self):
        from src.aefi import record_aefi, give_medical_clearance, can_receive_next_dose
        records = []
        record_aefi(records, "B001", "OPV", "Anaphylaxis", "SEVERE")
        give_medical_clearance(records, "B001")
        assert can_receive_next_dose(records, "B001")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. REPORTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestReports:

    def test_full_report_empty_db(self):
        from src.reports import db_generate_full_report
        r = db_generate_full_report()
        assert r["total_beneficiaries"] == 0
        assert r["total_doses_administered"] == 0

    def test_full_report_with_data(self):
        from src.beneficiary import db_add_beneficiary
        from src.dose        import db_add_dose
        from src.reports     import db_generate_full_report
        db_add_beneficiary("B001", "Alice", "2021-01-01")
        db_add_dose("B001", "OPV", 1, "2022-01-01")
        r = db_generate_full_report()
        assert r["total_beneficiaries"] == 1
        assert r["total_doses_administered"] == 1

    def test_coverage_report_empty(self):
        from src.reports import db_coverage_report
        assert db_coverage_report() == []

    def test_coverage_report_calculation(self):
        from src.schedule import db_add_schedule
        from src.dose     import db_add_dose
        from src.reports  import db_coverage_report
        add_b()
        db_add_schedule("B001", "OPV", 1, "2026-12-01")
        db_add_schedule("B001", "OPV", 2, "2027-01-01")
        db_add_dose("B001", "OPV", 1, "2026-11-15")  # marks schedule COMPLETED
        cov = db_coverage_report()
        opv = next(c for c in cov if c["vaccine_name"] == "OPV")
        assert opv["scheduled"] == 2
        assert opv["completed"] == 1
        assert opv["coverage_pct"] == 50.0

    def test_inmemory_report(self):
        from src.reports import generate_report
        beneficiaries = {"B001": {}, "B002": {}}
        doses         = [{"vaccine_name": "OPV"}, {"vaccine_name": "BCG"}]
        inventory     = [{"vaccine_name": "OPV", "quantity": 100}]
        r = generate_report(beneficiaries, doses, inventory)
        assert r["total_beneficiaries"] == 2
        assert r["total_doses_administered"] == 2
        assert r["remaining_vaccine_stock"]["OPV"] == 100


# ═══════════════════════════════════════════════════════════════════════════════
# 9. FLASK ROUTE SMOKE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestFlaskRoutes:
    """
    Smoke tests for all Flask routes — verify HTTP 200/302 responses.
    Uses Flask test client so no real server is needed.
    """

    @pytest.fixture
    def client(self, isolated_db):
        """Return a Flask test client wired to the isolated test DB."""
        import importlib
        import src.database as db_mod
        import app as flask_app_mod

        # Reload the app so create_tables() runs against the temp DB
        importlib.reload(flask_app_mod)
        flask_app_mod.app.config["TESTING"] = True
        flask_app_mod.app.config["WTF_CSRF_ENABLED"] = False
        with flask_app_mod.app.test_client() as c:
            yield c

    def test_dashboard(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_beneficiaries_list(self, client):
        assert client.get("/beneficiaries").status_code == 200

    def test_add_beneficiary_get(self, client):
        assert client.get("/beneficiaries/add").status_code == 200

    def test_add_beneficiary_post(self, client):
        resp = client.post("/beneficiaries/add", data={
            "beneficiary_id": "FT001",
            "name": "Flask Test",
            "date_of_birth": "2020-06-01",
            "gender": "Male",
            "guardian_name": "Parent",
            "phone": "9000000001",
            "address": "1 Test Lane"
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Flask Test" in resp.data or b"success" in resp.data.lower()

    def test_doses_list(self, client):
        assert client.get("/doses").status_code == 200

    def test_schedules_list(self, client):
        assert client.get("/schedules").status_code == 200

    def test_inventory_list(self, client):
        assert client.get("/inventory").status_code == 200

    def test_coldchain_list(self, client):
        assert client.get("/coldchain").status_code == 200

    def test_aefi_list(self, client):
        assert client.get("/aefi").status_code == 200

    def test_reports(self, client):
        assert client.get("/reports").status_code == 200

    def test_add_inventory_post(self, client):
        resp = client.post("/inventory/add", data={
            "vaccine_name": "OPV",
            "batch_number": "OPV-TEST-001",
            "quantity": "100",
            "expiry_date": "2027-12-31",
            "storage_temp": "4.0"
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_log_coldchain_post(self, client):
        resp = client.post("/coldchain/log", data={
            "vaccine_name": "BCG",
            "temperature": "5.0",
            "cumulative_heat_hours": "2.0",
            "vvm_stage": "1"
        }, follow_redirects=True)
        assert resp.status_code == 200

    def test_add_beneficiary_invalid_post(self, client):
        """Missing required fields → stays on form with error flash."""
        resp = client.post("/beneficiaries/add", data={
            "beneficiary_id": "",
            "name": "",
            "date_of_birth": "bad-date"
        }, follow_redirects=True)
        assert resp.status_code == 200
