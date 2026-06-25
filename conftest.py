"""
conftest.py — shared fixtures and hooks for all tests.

Credentials are loaded from the .env file:
  BASE_URL        — the app URL
  ADMIN_USER      — admin email
  ADMIN_PASSWORD  — admin password
  STUDENT_USER    — regular user email
  STUDENT_PASSWORD — regular user password
"""

import os
import time
import pytest
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import Page, Playwright

load_dotenv()

BASE             = os.getenv("BASE_URL",          "https://sv-students-recommend.onrender.com")
ADMIN_EMAIL      = os.getenv("ADMIN_USER",         "admin@svcollege.co.il")
ADMIN_PASSWORD   = os.getenv("ADMIN_PASSWORD",     "")
STUDENT_EMAIL    = os.getenv("STUDENT_USER",       "")
STUDENT_PASSWORD = os.getenv("STUDENT_PASSWORD",   "")

# ── screenshot / results folder ───────────────────────────────────────────────
SHOTS = Path(__file__).parent / "test-results"
SHOTS.mkdir(parents=True, exist_ok=True)
RESULTS = []


# ── UI fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def login_as_admin(page: Page):
    """Log in as admin and yield the authenticated page."""
    page.goto(f"{BASE}/pages/login.html")
    page.wait_for_load_state("networkidle")
    page.get_by_label("Email").fill(ADMIN_EMAIL)
    page.locator("[data-test='input-password']").fill(ADMIN_PASSWORD)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_load_state("networkidle")
    yield page


@pytest.fixture
def login_as_student(page: Page):
    """Log in as a regular student user and yield the authenticated page."""
    page.goto(f"{BASE}/pages/login.html")
    page.wait_for_load_state("networkidle")
    page.get_by_label("Email").fill(STUDENT_EMAIL)
    page.locator("[data-test='input-password']").fill(STUDENT_PASSWORD)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_load_state("networkidle")
    yield page


# ── API fixture ───────────────────────────────────────────────────────────────

@pytest.fixture
def auth_token(playwright: Playwright) -> str:
    """Log in via API and return the Bearer token."""
    api = playwright.request.new_context(base_url=BASE)
    res = api.post("/auth/login", data={
        "email":    ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
    })
    status = res.status
    body   = res.json()
    api.dispose()
    assert status == 200, f"Login failed: {body}"
    token = body.get("access_token")
    assert token, f"No access_token in login response: {body}"
    return token


@pytest.fixture
def fresh_user(playwright: Playwright) -> dict:
    """Register a brand-new unique user via the API and return its credentials + token."""
    email    = f"test_{int(time.time())}@example.com"
    password = STUDENT_PASSWORD
    name     = "Fresh Student"

    api = playwright.request.new_context(base_url=BASE)
    res = api.post("/auth/register", data={
        "name": name, "email": email, "password": password
    })
    status = res.status
    text   = res.text()
    api.dispose()
    assert status in (200, 201), f"Registration failed: HTTP {status} — {text}"

    # log in to get token
    api2 = playwright.request.new_context(base_url=BASE)
    res2 = api2.post("/auth/login", data={"email": email, "password": password})
    s2   = res2.status
    b2   = res2.json()
    api2.dispose()
    assert s2 == 200, f"Login failed: {b2}"
    token = b2.get("access_token")
    assert token, f"No token: {b2}"
    return {"email": email, "password": password, "name": name, "token": token}


@pytest.fixture
def fresh_user_token(fresh_user: dict) -> str:
    return fresh_user["token"]


# ── screenshot + results table hooks ─────────────────────────────────────────

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Take a screenshot after each test and collect results."""
    outcome = yield
    report  = outcome.get_result()

    if report.when != "call":
        return

    page = item.funcargs.get("page")
    shot_path = ""
    if page is not None:
        prefix    = "failed_" if report.failed else ""
        safe_name = item.name.replace("/", "_").replace("[", "_").replace("]", "")
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        shot_path = SHOTS / f"{prefix}{safe_name}_{timestamp}.png"
        try:
            page.screenshot(path=str(shot_path), full_page=True)
        except Exception as e:
            shot_path = f"(screenshot failed: {e})"

    note = ""
    if report.failed:
        note = str(report.longrepr).splitlines()[-1][:120]

    RESULTS.append({
        "test":     item.name,
        "status":   "PASS" if report.passed else "FAIL",
        "note":     note,
        "snapshot": str(shot_path),
    })


def pytest_sessionfinish(session, exitstatus):
    """Print results table to console and write to test-results/results.txt."""
    if not RESULTS:
        return

    lines = []
    lines.append("=" * 70)
    lines.append(f"TEST RESULTS  ({datetime.now():%Y-%m-%d %H:%M})")
    lines.append("=" * 70)
    lines.append(f"{'TEST':<40} {'STATUS':<6} NOTE")
    lines.append("-" * 70)
    for r in RESULTS:
        lines.append(f"{r['test']:<40} {r['status']:<6} {r['note']}")
    lines.append("-" * 70)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    lines.append(f"{passed}/{len(RESULTS)} passed.  Snapshots in: {SHOTS.resolve()}")
    lines.append("=" * 70)

    report_text = "\n".join(lines)
    print("\n\n" + report_text)

    SHOTS.mkdir(parents=True, exist_ok=True)
    report_file = SHOTS / "results.txt"
    report_file.write_text(report_text, encoding="utf-8")
    print(f"\nResults written to: {report_file.resolve()}")
