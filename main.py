from src.aefi import (
    record_aefi,
    can_receive_next_dose,
    give_medical_clearance,
    display_aefi_records
)

aefi_records = []

# Record a severe adverse event
record_aefi(
    aefi_records,
    "B001",
    "Vaccine A",
    "Severe allergic reaction",
    "SEVERE"
)

print("AEFI recorded successfully!")

# Check before medical clearance
print(
    "Before clearance:",
    can_receive_next_dose(aefi_records, "B001")
)

# Give medical clearance
give_medical_clearance(aefi_records, "B001")

# Check after medical clearance
print(
    "After clearance:",
    can_receive_next_dose(aefi_records, "B001")
)

# Display records
display_aefi_records(aefi_records)