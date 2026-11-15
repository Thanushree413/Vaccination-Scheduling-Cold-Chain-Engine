# AEFI MANAGEMENT MODULE
# Adverse Events Following Immunisation


def record_aefi(
    aefi_records,
    beneficiary_id,
    vaccine_name,
    event_description,
    severity
):
    """Record an adverse event after vaccination."""

    beneficiary_id = str(beneficiary_id).strip()
    vaccine_name = str(vaccine_name).strip()

    if not beneficiary_id:
        raise ValueError("Beneficiary ID is required.")

    if not vaccine_name:
        raise ValueError("Vaccine name is required.")

    if not event_description.strip():
        raise ValueError("Event description is required.")

    severity = severity.upper()

    if severity not in ["MILD", "MODERATE", "SEVERE"]:
        raise ValueError("Severity must be MILD, MODERATE or SEVERE.")

    record = {
        "beneficiary_id": beneficiary_id,
        "vaccine_name": vaccine_name,
        "event_description": event_description,
        "severity": severity,
        "medical_clearance": severity != "SEVERE"
    }

    aefi_records.append(record)

    return record


def can_receive_next_dose(aefi_records, beneficiary_id):
    """Check whether a beneficiary is cleared for another dose."""

    for event in aefi_records:

        if (
            event["beneficiary_id"] == beneficiary_id
            and event["severity"] == "SEVERE"
            and not event["medical_clearance"]
        ):
            return False

    return True


def give_medical_clearance(aefi_records, beneficiary_id):
    """Record medical clearance for severe AEFI."""

    found = False

    for event in aefi_records:

        if (
            event["beneficiary_id"] == beneficiary_id
            and event["severity"] == "SEVERE"
        ):
            event["medical_clearance"] = True
            found = True

    if not found:
        raise ValueError("No severe AEFI record found.")

    return "Medical clearance recorded successfully."


def display_aefi_records(aefi_records):
    """Display all recorded adverse events."""

    if not aefi_records:
        print("No AEFI records available.")
        return

    print("\nAEFI RECORDS")
    print("-----------------------------")

    for record in aefi_records:
        print("Beneficiary:", record["beneficiary_id"])
        print("Vaccine:", record["vaccine_name"])
        print("Event:", record["event_description"])
        print("Severity:", record["severity"])
        print("Medical clearance:", record["medical_clearance"])
        print("-----------------------------")