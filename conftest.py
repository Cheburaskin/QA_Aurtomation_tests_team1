"""
conftest.py — shared fixtures and hooks for all tests.

Credentials are loaded from the .env file:
  BASE_URL        — the app URL
  ADMIN_USER      — admin email
  ADMIN_PASSWORD  — admin password

Student credentials are no longer needed — fresh_user and
fast_logged_in_page fixtures create a new unique user every run.
"""

import os
import uuid
import pytest
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import Page, Playwright

load_dotenv()

BASE           = os.getenv("BASE_URL",        "https://sv-students-recommend.onrender.com")
ADMIN_EMAIL    = os.getenv("ADMIN_USER",       "admin@svcollege.co.il")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD",   "")

# ── screenshot / results folder ───────────────────────────────────────────────
SHOTS = Path(__file__).parent / "test-results"
SHOTS.mkdir(parents=True, exist_ok=True)
RESULTS = []


# ── helper: register a fresh unique user via API ──────────────────────────────

def _register_fresh_user(playwright: Playwright) -> dict:
    """
    Register a brand-new unique user via the API.
    Returns dict with email, password, name.
    Used by fresh_user and fast_logged_in_page fixtures.
    """
    email    = f"test_{uuid.uuid4().hex[:12]}@example.com"
    password = "abcdef"
    name     = "Fresh Student"

    api = playwright.request.new_context(base_url=BASE)
    res = api.post("/auth/register", data={
        "name": name, "email": email, "password": password
    })
    status = res.status
    text   = res.text()
    api.dispose()
    assert status in (200, 201), f"Registration failed: HTTP {status} — {text}"
    return {"email": email, "password": password, "name": name}


# ── UI fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def login_as_admin(page: Page) -> Page:
    """Log in as admin and yield the authenticated page."""
    page.goto(f"{BASE}/pages/login.html")
    page.wait_for_load_state("networkidle")
    page.get_by_label("Email").fill(ADMIN_EMAIL)
    page.locator("[data-test='input-password']").fill(ADMIN_PASSWORD)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_load_state("networkidle")
    yield page


@pytest.fixture()
def fast_logged_in_page(page: Page, playwright: Playwright) -> Page:
    """
    Register a fresh unique user via API, log in via UI,
    and yield the authenticated page.
    Used by Ron's tests in test_ui.py.
    Fresh user every run — no dependency on .env student credentials.
    """
    user = _register_fresh_user(playwright)

    page.goto(f"{BASE}/pages/login.html")
    page.wait_for_load_state("networkidle")
    page.get_by_label("Email").fill(user["email"])
    page.locator("[data-test='input-password']").fill(user["password"])
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_load_state("networkidle")
    yield page


@pytest.fixture()
def make_unique_email_f() -> str:
    """Return a unique email address for each test run."""
    return f"test{uuid.uuid4().hex[:12]}@example.com"


# ── API fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def auth_token(playwright: Playwright) -> str:
    """Log in as admin via API and return the Bearer token."""
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


@pytest.fixture()
def fresh_user(playwright: Playwright) -> dict:
    """
    Register a brand-new unique user via the API and return
    dict with email, password, name, token.
    Used by API tests.
    """
    user  = _register_fresh_user(playwright)

    # log in to get token
    api = playwright.request.new_context(base_url=BASE)
    res = api.post("/auth/login", data={
        "email":    user["email"],
        "password": user["password"],
    })
    status = res.status
    body   = res.json()
    api.dispose()
    assert status == 200, f"Login failed: {body}"
    token = body.get("access_token")
    assert token, f"No token: {body}"
    user["token"] = token
    return user


@pytest.fixture()
def fresh_user_token(fresh_user: dict) -> str:
    """Return just the token from the fresh_user fixture."""
    return fresh_user["token"]


# ── screenshot + results table hooks ─────────────────────────────────────────

@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """Take a screenshot after each test and collect results."""
    report = yield

    if report.when != "call":
        return report

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
    return report


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
