from datetime import date


def register_beneficiary(
    beneficiaries,
    beneficiary_id,
    name,
    date_of_birth,
    guardian_name=""
):
    """Register a new vaccination beneficiary."""

    if not beneficiary_id or not beneficiary_id.strip():
        raise ValueError("Beneficiary ID is required")

    if not name or not name.strip():
        raise ValueError("Beneficiary name is required")

    if beneficiary_id in beneficiaries:
        raise ValueError("Beneficiary ID already exists")

    try:
        if isinstance(date_of_birth, str):
            dob = date.fromisoformat(date_of_birth)
        elif isinstance(date_of_birth, date):
            dob = date_of_birth
        else:
            raise ValueError("Invalid date of birth")

    except ValueError:
        raise ValueError("Date of birth must use YYYY-MM-DD format")

    if dob > date.today():
        raise ValueError("Date of birth cannot be in the future")

    beneficiaries[beneficiary_id] = {
        "beneficiary_id": beneficiary_id,
        "name": name.strip(),
        "date_of_birth": dob.isoformat(),
        "guardian_name": guardian_name.strip()
    }

    return beneficiaries[beneficiary_id]