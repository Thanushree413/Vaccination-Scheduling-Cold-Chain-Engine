def check_cold_chain(
    vaccine_name,
    temperature,
    cumulative_heat_hours,
    freeze_sensitive=True,
    vvm_stage=1
):
    """
    Check vaccine cold-chain condition.

    Results:
    SAFE, QUARANTINE, DISCARD
    """

    # VVM stage 3 or 4 means discard
    if vvm_stage >= 3:
        return "DISCARD"

    # Freeze-sensitive vaccines exposed below 0°C
    if freeze_sensitive and temperature < 0:
        return "DISCARD"

    # More than 48 cumulative heat hours
    if cumulative_heat_hours > 48:
        return "QUARANTINE"

    return "SAFE"