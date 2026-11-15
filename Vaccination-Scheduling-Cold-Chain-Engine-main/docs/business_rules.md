Business Rules

1. Beneficiary Registration

- Every beneficiary must have a unique Beneficiary ID.
- Required beneficiary details must be provided during registration.
- Duplicate beneficiary records must be prevented.
- Invalid or incomplete information must be rejected.

2. Vaccination Eligibility

- A beneficiary must satisfy the defined eligibility conditions before vaccination.
- The beneficiary's vaccination history must be checked.
- Only eligible beneficiaries should be scheduled for vaccination.

3. Dose Management

- Each vaccination record must contain a valid beneficiary ID.
- Vaccine names and dose numbers must be valid.
- Duplicate doses must not be recorded.
- Each administered dose must have a vaccination date.
- Dose intervals must follow the configured vaccination schedule.

4. Vaccination Scheduling

- Vaccination due dates must be calculated based on previous dose dates and configured intervals.
- Beneficiaries must be scheduled according to their eligibility.
- Overdue vaccinations should be identified.
- Catch-up scheduling should consider missed doses and vaccination history.

5. Inventory Management

- Vaccine stock must be recorded accurately.
- Expired vaccines must not be issued.
- Vaccine availability must be checked before recording usage.
- Stock quantities must be updated after vaccine usage.

6. Cold-Chain Monitoring

- Temperature events must be recorded with date and time.
- Temperature readings must be checked against configured acceptable limits.
- Out-of-range readings must generate an alert or warning.
- Affected vaccine stock must be flagged for review.

7. AEFI Management

- Adverse Events Following Immunization must be recorded.
- Each event should be linked to the relevant beneficiary and vaccination record when available.
- Event details and reporting dates must be maintained.

8. Reporting

- Vaccination reports must use recorded project data.
- Reports should include relevant beneficiary and dose information.
- Invalid or missing records should not be treated as completed vaccinations.

9. Data Integrity

- Unique identifiers must be maintained.
- Invalid records must be rejected.
- Existing vaccination records must be preserved.
- All modules must use consistent data formats.

10. Conclusion

These business rules establish the conditions for beneficiary registration, vaccination scheduling, dose recording, inventory management, cold-chain monitoring and reporting. They help maintain consistency and reliability throughout the system.