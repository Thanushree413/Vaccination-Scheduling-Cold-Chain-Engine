"""
seed_data.py — Populate the database with realistic demo data
PS-065 | Team T113 | Vaccination Scheduling and Cold-Chain Engine

Run:  python seed_data.py
Safe to run multiple times — skips already-existing records.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import create_tables, connect_db
from src.beneficiary import db_add_beneficiary
from src.dose       import db_add_dose
from src.schedule   import db_add_schedule
from src.inventory  import db_add_stock
from src.cold_chain import db_log_cold_chain
from src.aefi       import db_record_aefi

# ── Helpers ──────────────────────────────────────────────────────────────────

def _exists(table, col, val):
    conn = connect_db()
    row  = conn.execute(f"SELECT 1 FROM {table} WHERE {col}=?", (val,)).fetchone()
    conn.close()
    return row is not None


def seed():
    create_tables()
    print("🌱  Seeding demo data …")

    # ── Beneficiaries ──────────────────────────────────────────────────────────
    beneficiaries = [
        ("B001", "Anjali Sharma",   "2022-03-14", "Female", "Ramesh Sharma",   "9876543210", "12 MG Road, Bangalore"),
        ("B002", "Rohan Mehta",     "2021-07-22", "Male",   "Suresh Mehta",    "9845123456", "45 Park Street, Mumbai"),
        ("B003", "Priya Nair",      "2023-01-05", "Female", "Deepa Nair",      "9900123456", "7 Beach Road, Chennai"),
        ("B004", "Arjun Patel",     "2020-11-18", "Male",   "Kavita Patel",    "9871234560", "88 Ring Road, Ahmedabad"),
        ("B005", "Sneha Reddy",     "2022-09-30", "Female", "Ravi Reddy",      "9988776655", "23 Jubilee Hills, Hyderabad"),
        ("B006", "Karan Singh",     "2021-05-12", "Male",   "Jaspreet Singh",  "9123456780", "56 Civil Lines, Delhi"),
        ("B007", "Meera Joshi",     "2023-06-01", "Female", "Anand Joshi",     "9000112233", "34 Shivaji Nagar, Pune"),
        ("B008", "Dev Kumar",       "2020-08-25", "Male",   "Vinod Kumar",     "9456781230", "9 Lake View, Kolkata"),
    ]

    for args in beneficiaries:
        bid = args[0]
        if not _exists("beneficiaries", "beneficiary_id", bid):
            try:
                db_add_beneficiary(*args)
                print(f"  ✔  Beneficiary {bid} — {args[1]}")
            except ValueError as e:
                print(f"  ⚠  Skip {bid}: {e}")
        else:
            print(f"  –  Beneficiary {bid} already exists")

    # ── Inventory ──────────────────────────────────────────────────────────────
    stocks = [
        ("BCG",          "BCG-2026-A1",   500,  "2027-06-30", 2.0),
        ("OPV",          "OPV-2026-B2",   800,  "2027-03-15", 2.0),
        ("Pentavalent",  "PENTA-2026-C3", 600,  "2027-09-01", 4.0),
        ("Rotavirus",    "ROTA-2026-D4",  400,  "2027-05-20", 4.0),
        ("Measles-Rubella","MR-2026-E5",  350,  "2027-12-31", 4.0),
        ("IPV",          "IPV-2026-F6",   200,  "2027-08-10", 4.0),
        ("Hepatitis-B",  "HEP-2026-G7",  450,  "2027-07-01", 4.0),
        ("DPT-Booster",  "DPT-2026-H8",  300,  "2027-10-15", 4.0),
    ]

    for args in stocks:
        if not _exists("inventory", "batch_number", args[1]):
            try:
                db_add_stock(*args)
                print(f"  ✔  Stock {args[1]} ({args[0]})")
            except ValueError as e:
                print(f"  ⚠  Skip stock {args[1]}: {e}")
        else:
            print(f"  –  Batch {args[1]} already exists")

    # ── Schedules ─────────────────────────────────────────────────────────────
    schedules = [
        ("B001", "BCG",           1, "2022-03-20", "At birth"),
        ("B001", "OPV",           1, "2022-05-14", "6 weeks"),
        ("B001", "Pentavalent",   1, "2022-05-14", "6 weeks"),
        ("B001", "OPV",           2, "2022-06-18", "10 weeks"),
        ("B001", "Pentavalent",   2, "2022-06-18", "10 weeks"),
        ("B001", "Measles-Rubella",1,"2023-03-14", "9 months"),
        ("B002", "BCG",           1, "2021-07-28", "At birth"),
        ("B002", "OPV",           1, "2021-09-22", "6 weeks"),
        ("B002", "Pentavalent",   1, "2021-09-22", "6 weeks"),
        ("B002", "Measles-Rubella",1,"2022-07-22", "9 months"),
        ("B003", "BCG",           1, "2023-01-10", "At birth"),
        ("B003", "OPV",           1, "2023-03-05", "6 weeks"),
        ("B004", "BCG",           1, "2020-11-25", "At birth"),
        ("B004", "Measles-Rubella",1,"2021-11-18", "9 months"),
        ("B004", "DPT-Booster",   1, "2026-11-18", "16-24 months booster"),
        ("B005", "BCG",           1, "2022-10-05", "At birth"),
        ("B005", "Rotavirus",     1, "2022-11-30", "6 weeks"),
        ("B005", "Rotavirus",     2, "2023-01-04", "10 weeks"),
        ("B006", "BCG",           1, "2021-05-18", "At birth"),
        ("B006", "IPV",           1, "2021-07-13", "14 weeks"),
        ("B007", "BCG",           1, "2023-06-07", "At birth"),
        ("B007", "Hepatitis-B",   1, "2023-06-07", "At birth"),
        ("B007", "OPV",           1, "2023-07-27", "6 weeks (overdue demo)"),
        ("B008", "BCG",           1, "2020-09-01", "At birth"),
        ("B008", "Measles-Rubella",1,"2021-08-25", "9 months"),
        ("B008", "DPT-Booster",   1, "2026-10-01", "Overdue demo"),
    ]

    # Count existing schedules — if none, insert all
    conn = connect_db()
    existing_sched_count = conn.execute("SELECT COUNT(*) FROM schedules").fetchone()[0]
    conn.close()

    if existing_sched_count == 0:
        for s in schedules:
            try:
                db_add_schedule(*s)
                print(f"  ✔  Schedule {s[0]} — {s[1]} dose {s[2]}")
            except ValueError as e:
                print(f"  ⚠  Skip schedule: {e}")
    else:
        print(f"  –  {existing_sched_count} schedules already exist, skipping")

    # ── Doses (mark some completed) ───────────────────────────────────────────
    doses = [
        ("B001", "BCG",           1, "2022-03-20", "Administered at birth"),
        ("B001", "OPV",           1, "2022-05-15", "6-week dose"),
        ("B001", "Pentavalent",   1, "2022-05-15", "6-week dose"),
        ("B001", "OPV",           2, "2022-06-20", "10-week dose"),
        ("B002", "BCG",           1, "2021-07-28", "Birth dose"),
        ("B002", "OPV",           1, "2021-09-23", "6-week dose"),
        ("B004", "BCG",           1, "2020-11-25", "Birth dose"),
        ("B004", "Measles-Rubella",1,"2021-11-20","9-month MR dose"),
        ("B006", "BCG",           1, "2021-05-18", "Birth dose"),
        ("B008", "BCG",           1, "2020-09-02", "Birth dose"),
        ("B008", "Measles-Rubella",1,"2021-08-26","9-month MR dose"),
    ]

    conn = connect_db()
    existing_dose_count = conn.execute("SELECT COUNT(*) FROM doses").fetchone()[0]
    conn.close()

    if existing_dose_count == 0:
        for d in doses:
            try:
                db_add_dose(*d)
                print(f"  ✔  Dose {d[0]} — {d[1]} #{d[2]}")
            except ValueError as e:
                print(f"  ⚠  Skip dose: {e}")
    else:
        print(f"  –  {existing_dose_count} doses already exist, skipping")

    # ── Cold-chain readings ───────────────────────────────────────────────────
    cc_readings = [
        ("BCG",         4.5,  2.0,  True,  1),   # SAFE
        ("OPV",         3.8,  5.0,  True,  1),   # SAFE
        ("Pentavalent", 7.9, 10.0,  False, 1),   # SAFE
        ("Rotavirus",  -1.5,  0.0,  True,  1),   # DISCARD (freeze)
        ("BCG",         6.0, 50.0,  True,  1),   # QUARANTINE (heat hours)
        ("Measles-Rubella", 8.5, 20.0, False, 2),# SAFE
        ("IPV",         4.0,  0.0,  False, 3),   # DISCARD (VVM stage)
        ("Hepatitis-B", 5.0,  3.0,  False, 1),  # SAFE
    ]

    conn = connect_db()
    existing_cc_count = conn.execute("SELECT COUNT(*) FROM cold_chain").fetchone()[0]
    conn.close()

    if existing_cc_count == 0:
        for r in cc_readings:
            try:
                result = db_log_cold_chain(*r)
                print(f"  ✔  Cold-chain {r[0]}: {result['status']}")
            except ValueError as e:
                print(f"  ⚠  Skip CC: {e}")
    else:
        print(f"  –  {existing_cc_count} CC readings already exist, skipping")

    # ── AEFI records ──────────────────────────────────────────────────────────
    aefis = [
        ("B001", "OPV",           "Mild fever and irritability",           "MILD",     "2022-05-18"),
        ("B002", "Pentavalent",   "Redness and swelling at injection site","MILD",     "2021-09-25"),
        ("B004", "Measles-Rubella","Fever 38.5°C, mild rash",             "MODERATE", "2021-11-22"),
        ("B006", "BCG",           "BCG lymphadenitis (enlarged node)",     "MODERATE", "2021-07-01"),
        ("B008", "Measles-Rubella","Severe anaphylaxis — hospitalised",    "SEVERE",   "2021-08-28"),
    ]

    conn = connect_db()
    existing_aefi_count = conn.execute("SELECT COUNT(*) FROM aefi").fetchone()[0]
    conn.close()

    if existing_aefi_count == 0:
        for a in aefis:
            try:
                db_record_aefi(*a)
                print(f"  ✔  AEFI {a[0]} — {a[3]}")
            except ValueError as e:
                print(f"  ⚠  Skip AEFI: {e}")
    else:
        print(f"  –  {existing_aefi_count} AEFI records already exist, skipping")

    print("\n✅  Seeding complete. Run:  python app.py")


if __name__ == "__main__":
    seed()
