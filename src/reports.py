def generate_report(beneficiaries, dose_events, inventory):
    """Generate a basic vaccination summary report."""

    total_beneficiaries = len(beneficiaries)
    total_doses = len(dose_events)

    vaccine_stock = {}

    for batch in inventory:
        name = batch["vaccine_name"]
        vaccine_stock[name] = (
            vaccine_stock.get(name, 0) + batch["quantity"]
        )

    report = {
        "total_beneficiaries": total_beneficiaries,
        "total_doses_administered": total_doses,
        "remaining_vaccine_stock": vaccine_stock
    }

    return report