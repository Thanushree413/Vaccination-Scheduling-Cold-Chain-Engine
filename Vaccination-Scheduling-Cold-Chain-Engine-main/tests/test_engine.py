from src.schedule import calculate_dose_status
from src.beneficiary import register_beneficiary


# VACCINATION SCHEDULING TESTS

def test_completed():
    assert calculate_dose_status(
        "2026-11-01", "2026-11-14", completed=True
    ) == "COMPLETED"


def test_ineligible():
    assert calculate_dose_status(
        "2026-11-01", "2026-11-14", eligible=False
    ) == "INELIGIBLE"


def test_not_yet():
    assert calculate_dose_status(
        "2026-11-20", "2026-11-14"
    ) == "NOT_YET"


def test_due():
    assert calculate_dose_status(
        "2026-11-14", "2026-11-14"
    ) == "DUE"


def test_overdue():
    assert calculate_dose_status(
        "2026-10-01", "2026-11-14"
    ) == "OVERDUE"


def test_exactly_28_days_late():
    assert calculate_dose_status(
        "2026-10-17", "2026-11-14"
    ) == "DUE"


# BENEFICIARY REGISTRATION TESTS

def test_register_beneficiary():
    beneficiaries = {}
    result = register_beneficiary(
        beneficiaries, "B001", "Anu", "2020-05-10", "Parent"
    )
    assert result["name"] == "Anu"
    assert "B001" in beneficiaries


def test_duplicate_beneficiary():
    beneficiaries = {}
    register_beneficiary(
        beneficiaries, "B002", "Ravi", "2019-01-10"
    )

    try:
        register_beneficiary(
            beneficiaries, "B002", "Ravi", "2019-01-10"
        )
        assert False
    except ValueError:
        assert True


def test_future_birth_date():
    beneficiaries = {}

    try:
        register_beneficiary(
            beneficiaries, "B003", "Maya", "2030-01-01"
        )
        assert False
    except ValueError:
        assert True