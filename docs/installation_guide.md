# Installation Guide — VacciTrack PS-065

## Prerequisites
- Python 3.10 or later
- pip

## Steps

```bash
# 1. Navigate to the project folder
cd "C:\Users\ACER\New folder (T113-PS-065)"

# 2. Install the only external dependency
pip install flask

# 3. (Optional) Verify Python and Flask
python --version
python -c "import flask; print('Flask OK')"

# 4. Load demo data
python seed_data.py

# 5. Start the application
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## Run Tests
```bash
python -m pytest tests/ -v
```

## Resetting the Database
Delete `vaccination.db` then restart — tables and seed data are recreated automatically.