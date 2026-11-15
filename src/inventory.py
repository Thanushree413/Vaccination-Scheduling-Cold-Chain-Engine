from datetime import date


def add_stock(inventory, vaccine_name, batch_number, quantity, expiry_date):
    """Add a vaccine batch to inventory."""

    if quantity <= 0:
        raise ValueError("Quantity must be positive.")

    expiry = date.fromisoformat(str(expiry_date))

    if expiry <= date.today():
        raise ValueError("Cannot add expired stock.")

    inventory.append({
        "vaccine_name": vaccine_name,
        "batch_number": batch_number,
        "quantity": quantity,
        "expiry_date": expiry.isoformat()
    })

    return "Stock added successfully"


def issue_stock(inventory, vaccine_name, required_quantity, today=None):
    """Issue stock using First Expiry, First Out (FEFO)."""

    if required_quantity <= 0:
        raise ValueError("Required quantity must be positive.")

    if today is None:
        today = date.today()

    if isinstance(today, str):
        today = date.fromisoformat(today)

    available = [
        batch for batch in inventory
        if batch["vaccine_name"] == vaccine_name
        and date.fromisoformat(batch["expiry_date"]) > today
    ]

    available.sort(key=lambda batch: batch["expiry_date"])

    total = sum(batch["quantity"] for batch in available)

    if total < required_quantity:
        raise ValueError("Insufficient vaccine stock.")

    issued = []

    for batch in available:
        if required_quantity == 0:
            break

        amount = min(batch["quantity"], required_quantity)

        batch["quantity"] -= amount
        required_quantity -= amount

        issued.append({
            "batch_number": batch["batch_number"],
            "quantity": amount
        })

    return issued