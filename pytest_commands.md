# Pytest Commands Guide
## SV Students Recommend — QA Automation Project

Use the project virtual environment on Windows:

```powershell
.\venv\Scripts\python.exe -m pytest ...
```

If your terminal already has the virtual environment activated, you can also use `pytest ...`.

---

## Basic Runs

```powershell
# Run all tests
.\venv\Scripts\python.exe -m pytest -v

# Run all tests with the browser visible
.\venv\Scripts\python.exe -m pytest -v --headed

# Run with slow motion for easier debugging
.\venv\Scripts\python.exe -m pytest -v --headed --slowmo 500

# Short traceback output
.\venv\Scripts\python.exe -m pytest -v --tb=short
```

---

## Run By File

```powershell
# API tests
.\venv\Scripts\python.exe -m pytest test_api.py -v

# UI tests
.\venv\Scripts\python.exe -m pytest test_ui.py -v

# UI tests with visible browser
.\venv\Scripts\python.exe -m pytest test_ui.py -v --headed

# Bonus tests
.\venv\Scripts\python.exe -m pytest test_bonus.py -v

# Bonus tests with visible browser
.\venv\Scripts\python.exe -m pytest test_bonus.py -v --headed
```

---

## Run By Marker

```powershell
# API tests
.\venv\Scripts\python.exe -m pytest -m api -v

# UI tests
.\venv\Scripts\python.exe -m pytest -m ui -v

# Mobile / responsive tests
.\venv\Scripts\python.exe -m pytest -m mobile -v

# Smoke tests
.\venv\Scripts\python.exe -m pytest -m smoke -v

# Sanity tests
.\venv\Scripts\python.exe -m pytest -m sanity -v

# Regression tests
.\venv\Scripts\python.exe -m pytest -m regression -v

# Error handling / validation tests
.\venv\Scripts\python.exe -m pytest -m errors_handling -v

# Boundary tests
.\venv\Scripts\python.exe -m pytest -m boundary -v

# Positive flows
.\venv\Scripts\python.exe -m pytest -m positive -v

# Negative flows
.\venv\Scripts\python.exe -m pytest -m negative -v

# System / bonus scenarios
.\venv\Scripts\python.exe -m pytest -m system -v

# Combine markers
.\venv\Scripts\python.exe -m pytest -m "api and sanity" -v

# Exclude mobile tests
.\venv\Scripts\python.exe -m pytest -m "not mobile" -v
```

---

## Run Single Tests

```powershell
# Single API test
.\venv\Scripts\python.exe -m pytest test_api.py::test_A7_list_all_recommendations -v

# Single UI test
.\venv\Scripts\python.exe -m pytest test_ui.py::test_U1_ui_login -v --headed

# Single bonus test
.\venv\Scripts\python.exe -m pytest test_bonus.py::test_B1_blacklisted_email_cannot_register -v --headed
```

---

## Reports

HTML reports are supported with `pytest-html`. The main report is created at `test-results/report.html` and can be opened in any browser.

```powershell
# HTML report
.\venv\Scripts\python.exe -m pytest -v --html=test-results/report.html --self-contained-html

# API report only
.\venv\Scripts\python.exe -m pytest test_api.py -v --html=test-results/api-report.html --self-contained-html

# UI report only
.\venv\Scripts\python.exe -m pytest test_ui.py -v --html=test-results/ui-report.html --self-contained-html

# JUnit XML report
.\venv\Scripts\python.exe -m pytest -v --junitxml=test-results/results.xml
```

`conftest.py` also writes a text summary to `test-results/results.txt` at the end of each run.

---

## Browser Options

```powershell
# Run on Chromium
.\venv\Scripts\python.exe -m pytest --browser chromium -v

# Run on Firefox
.\venv\Scripts\python.exe -m pytest --browser firefox -v --headed

# Run on WebKit
.\venv\Scripts\python.exe -m pytest --browser webkit -v --headed

# Run on all three browsers
.\venv\Scripts\python.exe -m pytest --browser chromium --browser firefox --browser webkit -v
```

---

## Parallel Execution

Parallel execution requires `pytest-xdist`.

```powershell
# Install if needed
.\venv\Scripts\python.exe -m pip install pytest-xdist

# Run 2 workers
.\venv\Scripts\python.exe -m pytest -n 2 -v

# Run 4 workers
.\venv\Scripts\python.exe -m pytest -n 4 -v
```

---

## Useful Combinations

```powershell
# Quick smoke check
.\venv\Scripts\python.exe -m pytest -m smoke -v

# API tests with short failure output
.\venv\Scripts\python.exe -m pytest test_api.py -v --tb=short

# Full regression with HTML report
.\venv\Scripts\python.exe -m pytest -m regression -v --html=test-results/regression-report.html --self-contained-html

# Debug a failing UI test
.\venv\Scripts\python.exe -m pytest test_ui.py::test_U1_ui_login -v --headed --slowmo 800
```

---

## Environment Variables

Credentials are normally read from `.env`.

```powershell
$env:BASE_URL = "https://sv-students-recommend.onrender.com"
$env:ADMIN_USER = "admin@svcollege.co.il"
$env:ADMIN_PASSWORD = "your_admin_password"
```
