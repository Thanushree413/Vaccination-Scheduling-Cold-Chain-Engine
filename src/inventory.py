"""
Inventory Management Module
Tracks vaccine batches using FEFO (First Expiry, First Out) strategy.
Preserves original add_stock() / issue_stock() for test compatibility.
"""

from datetime import date
from src.database import connect_db


# ─────────────────────────────────────────────────────────────────────────────
# IN-MEMORY FUNCTIONS (kept for test compatibility)
# ─────────────────────────────────────────────────────────────────────────────

def add_stock(inventory, vaccine_name, batch_number, quantity, expiry_date):
    """Add a vaccine batch to an in-memory inventory list."""
    if quantity <= 0:
        raise ValueError("Quantity must be positive.")

    expiry = date.fromisoformat(str(expiry_date))

    if expiry <= date.today():
        raise ValueError("Cannot add expired stock.")

    inventory.append({
        "vaccine_name":  vaccine_name,
        "batch_number":  batch_number,
        "quantity":      quantity,
        "expiry_date":   expiry.isoformat()
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
        issued.append({"batch_number": batch["batch_number"], "quantity": amount})

    return issued


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def db_add_stock(vaccine_name, batch_number, quantity, expiry_date, storage_temp=4.0):
    """Add a vaccine batch to the database."""
    if not vaccine_name or not batch_number:
        raise ValueError("Vaccine name and batch number are required.")

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        raise ValueError("Quantity must be an integer.")

    if quantity <= 0:
        raise ValueError("Quantity must be positive.")

    try:
        expiry = date.fromisoformat(str(expiry_date))
    except ValueError:
        raise ValueError("Expiry date must be in YYYY-MM-DD format.")

    if expiry <= date.today():
        raise ValueError("Cannot add expired stock.")

    conn = connect_db()
    try:
        # Upsert: if batch exists, increase quantity
        existing = conn.execute(
            "SELECT id, quantity FROM inventory WHERE batch_number=?",
            (batch_number,)
        ).fetchone()

        if existing:
            conn.execute(
                "UPDATE inventory SET quantity=quantity+? WHERE batch_number=?",
                (quantity, batch_number)
            )
        else:
            conn.execute(
                """INSERT INTO inventory (vaccine_name, batch_number, quantity, expiry_date, storage_temp)
                   VALUES (?, ?, ?, ?, ?)""",
                (vaccine_name, batch_number, quantity, expiry.isoformat(), storage_temp)
            )
        conn.commit()
        return {"status": "success", "batch_number": batch_number, "quantity": quantity}
    except Exception as e:
        conn.rollback()
        raise ValueError(f"Could not add stock: {e}")
    finally:
        conn.close()


def db_get_all_inventory():
    """Return all inventory batches."""
    conn = connect_db()
    rows = conn.execute(
        "SELECT * FROM inventory ORDER BY expiry_date"
    ).fetchall()
    conn.close()
    today = date.today().isoformat()
    result = []
    for r in rows:
        d = dict(r)
        d["expired"] = d["expiry_date"] <= today
        result.append(d)
    return result


def db_get_inventory_summary():
    """Return total quantity per vaccine (non-expired)."""
    conn = connect_db()
    rows = conn.execute(
        """SELECT vaccine_name, SUM(quantity) AS total_quantity
           FROM inventory
           WHERE expiry_date > DATE('now')
           GROUP BY vaccine_name
           ORDER BY vaccine_name"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def db_issue_stock(vaccine_name, required_quantity):
    """Issue vaccine stock using FEFO logic from the database."""
    try:
        required_quantity = int(required_quantity)
    except (ValueError, TypeError):
        raise ValueError("Required quantity must be an integer.")

    if required_quantity <= 0:
        raise ValueError("Required quantity must be positive.")

    conn = connect_db()
    rows = conn.execute(
        """SELECT id, batch_number, quantity
           FROM inventory
           WHERE vaccine_name=? AND expiry_date > DATE('now') AND quantity > 0
           ORDER BY expiry_date""",
        (vaccine_name,)
    ).fetchall()

    total = sum(r["quantity"] for r in rows)
    if total < required_quantity:
        conn.close()
        raise ValueError(f"Insufficient stock. Available: {total}")

    issued = []
    remaining = required_quantity
    for row in rows:
        if remaining == 0:
            break
        amount = min(row["quantity"], remaining)
        conn.execute(
            "UPDATE inventory SET quantity=quantity-? WHERE id=?",
            (amount, row["id"])
        )
        issued.append({"batch_number": row["batch_number"], "quantity_issued": amount})
        remaining -= amount

    conn.commit()
    conn.close()
    return issued


def db_delete_stock(batch_id):
    """Delete an inventory batch by ID."""
    conn = connect_db()
    cur = conn.execute("DELETE FROM inventory WHERE id=?", (batch_id,))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if affected == 0:
        raise ValueError("Inventory batch not found")
    return {"status": "deleted", "id": batch_id}