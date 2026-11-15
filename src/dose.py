from datetime import date


def record_dose(
    dose_events,
    beneficiary_id,
    vaccine_name,
    dose_number,
    administered_date
):
    """Record a vaccination dose."""

    beneficiary_id = str(beneficiary_id).strip()
    vaccine_name = str(vaccine_name).strip()

    if not beneficiary_id or not vaccine_name:
        raise ValueError("Beneficiary ID and vaccine are required.")

    if not isinstance(dose_number, int) or dose_number < 1:
        raise ValueError("Dose number must be a positive integer.")

    try:
        given_date = date.fromisoformat(str(administered_date))
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")

    event = {
        "beneficiary_id": beneficiary_id,
        "vaccine_name": vaccine_name,
        "dose_number": dose_number,
        "administered_date": given_date.isoformat()
    }

    dose_events.append(event)

    return event