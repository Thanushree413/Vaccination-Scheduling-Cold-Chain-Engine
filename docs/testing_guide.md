Testing Guide

Vaccine Dose Management System

1. Introduction

This document explains how to run and verify the tests for the Vaccine Dose Management System.

Testing helps identify errors and verify that the application's features work as expected.

2. Testing Framework

The project uses:

- Python
- Pytest

3. Prerequisites

Before running tests, ensure that:

- Python is installed.
- The project repository is downloaded.
- Required dependencies are installed.
- The terminal is opened in the project root directory.

4. Install Dependencies

Run:

pip install -r requirements.txt

If pytest is not included in the requirements file, install it using:

pip install pytest

5. Run All Tests

To run all tests with detailed output:

python -m pytest -v

To run tests with concise output:

python -m pytest -q

6. Test Categories

The test suite may cover the following areas, depending on the implemented tests:

- Beneficiary management
- Vaccine dose management
- Vaccination eligibility
- Scheduling and validation
- Inventory management
- Cold-chain rules
- Business rules
- Edge cases

7. Previous Test Result

The project previously produced the following result:

102 tests passed.

Run the test command again before final submission to confirm the current result.

8. Expected Result

A successful test run should show that all executed tests pass without failures or errors.

If a test fails:

1. Read the failure message.
2. Identify the affected module.
3. Correct the issue.
4. Run the tests again.

9. Conclusion

Testing is an important part of the Vaccine Dose Management System development process. It helps verify application behaviour and improves software reliability.