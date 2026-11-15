Installation Guide

Vaccine Dose Management System

1. Introduction

This guide explains how to download, install, and run the Vaccine Dose Management System on a Windows computer.

2. Prerequisites

Install the following software:

- Python 3
- Visual Studio Code (recommended)
- Git (optional, for cloning the repository)

3. Download the Project

Clone the GitHub repository:

git clone https://github.com/Thanushree413/Vaccination-Scheduling-Cold-Chain-Engine.git

Alternatively, download the repository as a ZIP file from GitHub and extract it.

4. Open the Project

Open the extracted project folder in Visual Studio Code.

Open the VS Code terminal using:

Terminal → New Terminal

5. Create a Virtual Environment

Run:

python -m venv venv

6. Activate the Virtual Environment

For Windows PowerShell:

.\venv\Scripts\Activate.ps1

If PowerShell blocks activation, you can use Command Prompt:

venv\Scripts\activate.bat

7. Install Dependencies

Run:

pip install -r requirements.txt

8. Run the Application

Run:

python app.py

Wait until the Flask server starts.

9. Open the Application

Open Chrome, Edge, or another browser and visit:

http://127.0.0.1:5000

10. Stop the Application

Return to the terminal and press:

Ctrl + C

11. Troubleshooting

Python is not recognised

Check that Python is installed and added to the system PATH.

Required module is missing

Run:

pip install -r requirements.txt

Port is already in use

Close the other application using the port or configure the Flask application to use another available port.

12. Conclusion

Following these instructions allows users to set up and run the Vaccine Dose Management System locally.