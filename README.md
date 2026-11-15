# 💉 VacciTrack — Vaccination Scheduling & Cold-Chain Engine
### PS-065 | Team T113

A production-ready web application for healthcare administrators to manage vaccination programmes end-to-end: beneficiary registration, dose tracking, scheduling, vaccine inventory, cold-chain monitoring, AEFI reporting and analytics.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install flask
```

### 2. Seed demo data (first time only)
```bash
python seed_data.py
```

### 3. Run the application
```bash
python app.py
```

### 4. Open in browser
```
http://127.0.0.1:5000
```

---

## 🧪 Run Tests

```bash
# Original 9 tests (in-memory logic)
python -m pytest tests/test_engine.py -v

# Full suite — 70+ integration & Flask tests
python -m pytest tests/test_full.py -v

# All tests together
python -m pytest tests/ -v
```

---

## 📁 Project Structure

```
T113-PS-065/
├── app.py                  ← Flask web application (all routes)
├── seed_data.py            ← Loads realistic demo data
├── requirements.txt        ← pip install flask
├── vaccination.db          ← SQLite database (auto-created)
│
├── src/
│   ├── database.py         ← DB connection + create_tables()
│   ├── beneficiary.py      ← Beneficiary CRUD
│   ├── dose.py             ← Dose recording
│   ├── schedule.py         ← Scheduling + status engine
│   ├── inventory.py        ← FEFO stock management
│   ├── cold_chain.py       ← Temperature monitoring
│   ├── aefi.py             ← Adverse event management
│   └── reports.py          ← Analytics & coverage reports
│
├── templates/
│   ├── base.html           ← Dark sidebar layout
│   ├── dashboard.html      ← KPI cards + live charts
│   ├── beneficiaries.html  ← Beneficiary list
│   ├── add_beneficiary.html
│   ├── edit_beneficiary.html
│   ├── view_beneficiary.html
│   ├── doses.html
│   ├── add_dose.html
│   ├── schedules.html
│   ├── add_schedule.html
│   ├── inventory.html
│   ├── add_inventory.html
│   ├── coldchain.html
│   ├── log_coldchain.html
│   ├── aefi.html
│   ├── add_aefi.html
│   └── reports.html
│
├── tests/
│   ├── test_engine.py      ← 9 original logic tests
│   └── test_full.py        ← 70+ integration tests
│
└── docs/
    ├── project_overview.md
    ├── business_rules.md
    ├── installation_guide.md
    └── ...
```

---

## 🌐 Application Pages

| URL | Description |
|-----|-------------|
| `/` | Dashboard — KPIs, alerts, charts |
| `/beneficiaries` | List all beneficiaries |
| `/beneficiaries/add` | Register new beneficiary |
| `/beneficiaries/<id>` | View beneficiary profile |
| `/beneficiaries/<id>/edit` | Edit beneficiary |
| `/doses` | All dose records |
| `/doses/add` | Record a new dose |
| `/schedules` | Vaccination schedule (auto-refreshed status) |
| `/schedules/add` | Add new schedule entry |
| `/inventory` | Vaccine batch stock list |
| `/inventory/add` | Add new stock batch |
| `/coldchain` | Temperature readings + alerts |
| `/coldchain/log` | Log a temperature reading |
| `/aefi` | Adverse event records |
| `/aefi/add` | Report new AEFI |
| `/reports` | Analytics + coverage charts |

---

## 🗄️ Database Tables

| Table | Purpose |
|-------|---------|
| `beneficiaries` | Registered individuals |
| `doses` | Administered vaccine doses |
| `schedules` | Planned vaccinations with live status |
| `inventory` | Vaccine batches (FEFO ordering) |
| `cold_chain` | Temperature readings + alerts |
| `aefi` | Adverse events following immunisation |

---

## ⚙️ Business Rules

| Rule | Detail |
|------|--------|
| Schedule status | `NOT_YET` → `DUE` (day-of) → `OVERDUE` (>28 days) → `COMPLETED` |
| Inventory | FEFO — First Expiry, First Out |
| Cold-chain | `SAFE` / `QUARANTINE` (>48 heat-hours) / `DISCARD` (VVM≥3 or freeze) |
| AEFI clearance | SEVERE events require manual medical clearance |

---

## 🔧 Technology Stack

- **Backend**: Python 3.10+ · Flask 3.x
- **Database**: SQLite 3 (stdlib — no extra install)
- **Frontend**: HTML5 · CSS3 · Vanilla JS (no frameworks)
- **Testing**: pytest

---

## 👥 Team

**PS-065 · Team T113** — Vaccination Scheduling and Cold-Chain Engine
