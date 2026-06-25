# Pytest Commands Guide
## SV Students Recommend — QA Automation Project

---

## Basic runs

```bash
# Run all tests
pytest -v

# Run with visible browser
pytest -v --headed

# Run in slow motion (easier to follow)
pytest -v --headed --slowmo 500
```

---

## Run by file

```bash
pytest test_api.py -v
pytest test_ui_positive.py -v --headed
pytest test_ui_negative.py -v --headed
pytest test_ui_boundary.py -v --headed
pytest test_ui_features.py -v --headed
```

---

## Run by marker

```bash
# Only API tests
pytest -m api -v

# Only UI tests
pytest -m ui -v

# Only smoke tests (quick sanity check)
pytest -m smoke -v

# Only sanity tests
pytest -m sanity -v

# Only error handling tests
pytest -m errors_handling -v

# Only boundary value tests
pytest -m boundary -v

# Only mobile tests
pytest -m mobile -v

# Only regression tests
pytest -m regression -v

# Combine markers (API AND sanity)
pytest -m "api and sanity" -v

# Exclude a marker (all except mobile)
pytest -m "not mobile" -v
```

---

## Run a single test

```bash
pytest test_api.py::test_A7_list_all_recommendations -v
pytest test_ui_positive.py::test_U1_login_success -v --headed
```

---

## Parallel execution

```bash
# Install first:
pip install pytest-xdist

# Run 4 tests in parallel
pytest -n 4 -v

# Run 2 in parallel
pytest -n 2 -v
```

---

## Reports

```bash
# Generate HTML report (install first: pip install pytest-html)
pytest -v --html=test-results/report.html --self-contained-html

# Generate JUnit XML (for CI/CD)
pytest -v --junitxml=test-results/results.xml

# Show summary only (no full output)
pytest -v --tb=short

# Show only failures
pytest -v --tb=long -q
```

---

## Browser options

```bash
# Run on Firefox
pytest --browser firefox -v --headed

# Run on WebKit (Safari)
pytest --browser webkit -v --headed

# Run on all browsers
pytest --browser chromium --browser firefox --browser webkit -v
```

---

## Useful combinations

```bash
# Quick smoke check (fast, no browser window)
pytest -m smoke -v

# Full regression run with report
pytest -m regression -v --html=test-results/report.html --self-contained-html

# Debug a failing test (headed + slow)
pytest test_ui_positive.py::test_U1_login_success -v --headed --slowmo 800

# API tests only, fast
pytest -m api -v --tb=short
```

---

## Environment variables (set before running)

```powershell
# Windows PowerShell:
$env:ADMIN_PASSWORD = "test1234"
$env:ADMIN_USER     = "admin@svcollege.co.il"

# Or just use the .env file (already configured)
```
