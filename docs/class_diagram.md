Class Diagram – Vaccination Scheduling and Cold-Chain Engine

1. Overview

The system is designed using modular components to manage beneficiaries, vaccination doses, scheduling, inventory, cold-chain monitoring, AEFI records, and reports.

2. Main Classes and Responsibilities

Beneficiary

- Stores beneficiary details.
- Registers and manages beneficiary information.
- Checks beneficiary eligibility.

Dose

- Maintains vaccination dose details.
- Tracks dose number and vaccination status.
- Records completed doses.

Schedule

- Creates vaccination schedules.
- Manages appointment dates and times.
- Checks scheduling conflicts.

Inventory

- Tracks available vaccine stock.
- Updates stock after vaccination.
- Monitors vaccine availability.

ColdChain

- Records vaccine storage temperatures.
- Checks temperature limits.
- Identifies temperature-related alerts.

AEFI

- Records Adverse Events Following Immunization.
- Stores event details.
- Maintains AEFI records.

Reports

- Generates system reports.
- Provides beneficiary, dose, inventory, and cold-chain summaries.

Main

- Acts as the main entry point.
- Connects and executes the system modules.

3. Relationships

- Beneficiary is associated with Dose.
- Beneficiary is associated with Schedule.
- Schedule manages vaccination appointments.
- Inventory maintains vaccine stock.
- ColdChain monitors storage conditions.
- AEFI stores adverse event information.
- Reports collects information from the system modules.
- Main coordinates the application.

4. Conclusion

The modular class structure improves code organization, maintainability, and future expansion of the Vaccination Scheduling and Cold-Chain Engine.