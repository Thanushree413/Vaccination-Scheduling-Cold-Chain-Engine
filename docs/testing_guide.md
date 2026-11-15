# Testing Guide — VacciTrack PS-065

## Test Suites

### 1. Original Logic Tests (`tests/test_engine.py`)
9 unit tests for the core scheduling and beneficiary in-memory functions.

```bash
python -m pytest tests/test_engine.py -v
```

Expected: **9 passed**

### 2. Full Integration Suite (`tests/test_full.py`)
70+ tests covering every module, DB integration, edge cases, and Flask routes.

```bash
python -m pytest tests/test_full.py -v
```

### 3. Run All Tests
```bash
python -m pytest tests/ -v
```

---

## Test Coverage Areas

| Module | Test Class | Key Scenarios |
|--------|-----------|---------------|
| Database | `TestDatabase` | Tables created, FK pragma |
| Beneficiary | `TestBeneficiary` | CRUD, duplicate ID, future DOB, blank fields |
| Dose | `TestDose` | Add/delete, invalid numbers, schedule auto-complete |
| Schedule | `TestSchedule` | Status engine, 28-day boundary, refresh, CRUD |
| Inventory | `TestInventory` | FEFO, upsert, expired stock, insufficient stock |
| Cold Chain | `TestColdChain` | SAFE/QUARANTINE/DISCARD rules, freeze, VVM stage |
| AEFI | `TestAEFI` | Severity, auto-clearance, medical clearance, edge cases |
| Reports | `TestReports` | Coverage %, empty DB, full report with data |
| Flask Routes | `TestFlaskRoutes` | All pages return 200/302, form submissions |

---

## Isolation Strategy
Every test uses a temporary SQLite file (via `pytest` `tmp_path` fixture + `monkeypatch`). The real `vaccination.db` is never touched during testing.

---

## Edge Cases Tested

- Duplicate beneficiary ID → `ValueError`
- Future date of birth → `ValueError`
- Dose number ≤ 0 → `ValueError`
- Adding expired vaccine stock → `ValueError`
- Issuing more stock than available → `ValueError`
- VVM stage ≥ 3 → DISCARD
- Heat hours > 48 → QUARANTINE
- Freeze-sensitive vaccine below 0°C → DISCARD
- SEVERE AEFI without medical clearance blocks next dose
- Exactly 28 days late → DUE (not OVERDUE)
- 29 days late → OVERDUE