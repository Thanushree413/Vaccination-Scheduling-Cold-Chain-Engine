Vaccine Dose Management System

Vaccination Scheduling and Cold Chain Management Engine

A web-based application designed to manage vaccination scheduling, beneficiary records, dose tracking, vaccine inventory, and cold-chain monitoring.

Project Overview

The Vaccine Dose Management System helps healthcare administrators manage vaccination activities in an organised way. It provides features for maintaining beneficiary information, recording vaccine doses, monitoring inventory, and viewing reports.

Key Features-

- Dashboard: View an overview of vaccination activities.
- Beneficiary Management: Register and manage beneficiary information.
- Dose Management: Record and track vaccine doses.
- Vaccination Scheduling: Manage vaccination appointments.
- Inventory Management: Monitor vaccine stock.
- Cold Chain Management: Support monitoring of vaccine storage conditions.
- Reports: View vaccination and inventory information.

Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- SQLite (if used by the project)
- Pytest for testing

Project Structure

Vaccination-Scheduling-Cold-Chain-Engine/
│
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── PROJECT_REPORT.md
│
├── src/
├── templates/
├── data/
├── docs/
└── tests/

Installation and Setup

1. Clone the repository

git clone https://github.com/Thanushree413/Vaccination-Scheduling-Cold-Chain-Engine.git

2. Open the project folder

cd Vaccination-Scheduling-Cold-Chain-Engine

3. Create a virtual environment (recommended)

python -m venv venv

4. Activate the virtual environment

Windows PowerShell:

.\venv\Scripts\Activate.ps1

5. Install dependencies

pip install -r requirements.txt

6. Run the application

python app.py

Open your browser and visit:

"http://127.0.0.1:5000"

Running Tests

Run the test suite using:

python -m pytest -q

The project previously completed 102 passing tests in the reported test run. Run the command again to verify the current version.

Documentation

Additional project documentation is available in the "docs/" folder, including:

- Project overview
- Installation guide
- Eligibility rules
- Business rules
- Testing guide
- Edge case tests
- State diagram
- Class diagram
- Decision log
- Glossary

Future Enhancements

- Automated appointment reminders
- Enhanced reporting and analytics
- Improved inventory alerts
- More detailed cold-chain monitoring
- Role-based access control

Conclusion

The Vaccine Dose Management System provides a structured approach to managing vaccination records, scheduling, dose tracking, and vaccine inventory. It is designed to support organised healthcare administration and can be extended with additional features in the future.

Repository

GitHub: https://github.com/Thanushree413/Vaccination-Scheduling-Cold-Chain-Engine