# Project Overview — VacciTrack
## Vaccination Scheduling and Cold-Chain Engine
**Problem Statement ID:** PS-065 | **Team:** T113

---

## 1. Introduction

VacciTrack is a healthcare information system designed to digitalise and automate vaccination programme management for primary health centres and immunisation teams. It addresses the gap between paper-based registers and modern digital health needs.

## 2. Problem Statement

Immunisation programmes in many regions still rely on paper registers, manual temperature logs, and verbal reminders. This leads to:

- Missed or duplicate vaccine doses
- Stockouts and expired vaccine wastage
- Cold-chain breaches going undetected
- No consolidated view of coverage or adverse events
- Inability to identify overdue beneficiaries quickly

## 3. Objectives

1. Register beneficiaries and maintain their complete vaccination history
2. Schedule vaccinations and auto-calculate due/overdue status
3. Track dose administration and prevent invalid entries
4. Manage vaccine inventory using FEFO (First Expiry, First Out)
5. Monitor cold-chain temperature and generate automatic alerts
6. Record Adverse Events Following Immunisation (AEFI)
7. Provide a real-time analytics dashboard and coverage reports

## 4. System Architecture

```
┌────────────────────────────────────────────────┐
│               Flask Web Application            │
│                    app.py                      │
│  ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ Templates│ │  Routes  │ │   Business    │  │
│  │  (Jinja2)│ │(HTTP/GET │ │    Logic      │  │
│  │          │ │  /POST)  │ │  (src/*.py)   │  │
│  └──────────┘ └──────────┘ └───────────────┘  │
└────────────────────────────────────────────────┘
                        │
              ┌─────────▼──────────┐
              │   SQLite Database  │
              │  vaccination.db    │
              │  (6 tables)        │
              └────────────────────┘
```

## 5. Module Descriptions

### database.py
Provides `connect_db()` and `create_tables()`. All 6 tables are created here with proper primary keys, foreign keys, and default values.

### beneficiary.py
Full CRUD for vaccination beneficiaries. Validates ID uniqueness, name, and date of birth (not in future). Both in-memory and DB-backed functions.

### dose.py
Records administered doses. Validates dose number (≥1), date format, and auto-marks related schedule entries as COMPLETED.

### schedule.py
Creates and manages vaccination schedules. Status engine: `calculate_dose_status()` returns `NOT_YET`, `DUE`, `OVERDUE`, `COMPLETED`, or `INELIGIBLE` based on today's date and 28-day grace window.

### inventory.py
Tracks vaccine batches. Issues stock using FEFO logic. Prevents adding expired stock. Supports batch upsert (adding to existing batch increases quantity).

### cold_chain.py
Logs temperature readings and evaluates:
- `SAFE` — normal conditions
- `QUARANTINE` — cumulative heat hours > 48
- `DISCARD` — VVM stage ≥3, or freeze-sensitive vaccine below 0°C

### aefi.py
Records Adverse Events Following Immunisation. MILD and MODERATE events auto-clear; SEVERE events require explicit medical clearance.

### reports.py
Aggregates statistics: beneficiary counts, dose totals, schedule distribution, inventory, AEFI breakdown, cold-chain alerts, and vaccination coverage per vaccine.

## 6. Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Web Framework | Flask 3.x |
| Database | SQLite 3 (Python stdlib) |
| ORM | None (raw sqlite3 with Row factory) |
| Templating | Jinja2 (Flask built-in) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Testing | pytest |
| Design | Dark-mode dashboard, Inter font, CSS variables |

## 7. Database Schema

### beneficiaries
```sql
id INTEGER PK, beneficiary_id TEXT UNIQUE, name TEXT,
date_of_birth TEXT, gender TEXT, guardian_name TEXT,
phone TEXT, address TEXT, created_at TEXT
```

### doses
```sql
id INTEGER PK, beneficiary_id TEXT FK→beneficiaries,
vaccine_name TEXT, dose_number INTEGER, administered_date TEXT,
notes TEXT, created_at TEXT
```

### schedules
```sql
id INTEGER PK, beneficiary_id TEXT FK→beneficiaries,
vaccine_name TEXT, dose_number INTEGER, due_date TEXT,
status TEXT (NOT_YET/DUE/OVERDUE/COMPLETED/INELIGIBLE),
notes TEXT, created_at TEXT
```

### inventory
```sql
id INTEGER PK, vaccine_name TEXT, batch_number TEXT UNIQUE,
quantity INTEGER, expiry_date TEXT, storage_temp REAL,
created_at TEXT
```

### cold_chain
```sql
id INTEGER PK, vaccine_name TEXT, temperature REAL,
cumulative_heat_hours REAL, freeze_sensitive INTEGER,
vvm_stage INTEGER, status TEXT (SAFE/QUARANTINE/DISCARD),
recorded_at TEXT
```

### aefi
```sql
id INTEGER PK, beneficiary_id TEXT FK→beneficiaries,
vaccine_name TEXT, event_description TEXT,
severity TEXT (MILD/MODERATE/SEVERE),
medical_clearance INTEGER, report_date TEXT
```

## 8. Future Enhancements

1. SMS/email reminders for due vaccinations
2. Multi-centre support with role-based access
3. PDF certificate generation
4. Offline-first PWA for field workers
5. HL7 FHIR API for interoperability
6. Machine learning for dropout prediction
7. GIS mapping of vaccination coverage
8. Barcode scanning for batch tracking