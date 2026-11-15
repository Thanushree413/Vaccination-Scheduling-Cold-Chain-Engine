State Diagram – Vaccination Scheduling and Cold-Chain Engine

1. Overview

The state diagram represents the different states of a beneficiary's vaccination process.

2. Beneficiary Vaccination States

1. Registered: Beneficiary details are entered into the system.
2. Eligibility Check: The system checks vaccination eligibility.
3. Eligible: Beneficiary satisfies the eligibility conditions.
4. Scheduled: Vaccination appointment is created.
5. Dose Administered: Vaccination dose is recorded.
6. Next Dose Pending: Another dose is required according to the configured schedule.
7. Completed: Required vaccination doses are completed.
8. Not Eligible: Beneficiary does not satisfy the eligibility conditions.

3. State Transitions

- Registered → Eligibility Check
- Eligibility Check → Eligible
- Eligibility Check → Not Eligible
- Eligible → Scheduled
- Scheduled → Dose Administered
- Dose Administered → Next Dose Pending
- Next Dose Pending → Scheduled
- Dose Administered → Completed

4. Cold-Chain States

- Normal: Temperature is within the configured permitted range.
- Alert: Temperature is outside the configured permitted range.
- Resolved: Temperature issue has been addressed and verified.

5. Conclusion

The state diagram explains how beneficiaries move through the vaccination process and how cold-chain conditions are monitored.