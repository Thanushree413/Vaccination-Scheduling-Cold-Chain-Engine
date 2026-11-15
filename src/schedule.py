from datetime import date


def calculate_dose_status(
    due_date,
    today=None,
    completed=False,
    eligible=True
):
    """
    Calculate vaccination dose status.

    Possible results:
    COMPLETED, INELIGIBLE, NOT_YET, DUE, OVERDUE
    """

    if completed:
        return "COMPLETED"

    if not eligible:
        return "INELIGIBLE"

    if today is None:
        today = date.today()

    try:
        if isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)

        if isinstance(today, str):
            today = date.fromisoformat(today)

    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    if not isinstance(due_date, date):
        raise TypeError("due_date must be a date or YYYY-MM-DD string")

    if not isinstance(today, date):
        raise TypeError("today must be a date or YYYY-MM-DD string")

    if due_date > today:
        return "NOT_YET"

    days_late = (today - due_date).days

    if days_late > 28:
        return "OVERDUE"

    return "DUE"