"""
conftest.py — shared fixtures for all tests.

Credentials are loaded from a .env file (see .env.example).
"""

import os
import time
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Playwright, Page, expect

# Load environment variables from a .env file (if present)
load_dotenv()

BASE_URL = os.environ.get("BASE_URL", "https://sv-students-recommend.onrender.com")

ADMIN_EMAIL    = os.environ.get("ADMIN_EMAIL", "hagai@svcollege.co.il")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if not ADMIN_EMAIL or not ADMIN_PASSWORD:
    raise RuntimeError(
        "ADMIN_EMAIL and ADMIN_PASSWORD must be set in a .env file "
        "(see .env.example)."
    )


def make_unique_email() -> str:
    return f"test_{int(time.time())}@example.com"


def api_login(playwright: Playwright, email: str, password: str) -> str:
    """POST /auth/login — read everything BEFORE dispose, then return token."""
    ctx = playwright.request.new_context(base_url=BASE_URL)
    res = ctx.post("/auth/login", data={"email": email, "password": password})

    # ✅ read status and body BEFORE dispose
    status = res.status
    body   = res.json()
    ctx.dispose()

    assert status == 200, f"Login failed for {email}: HTTP {status} — {body}"
    token = (body.get("token")
             or body.get("access_token")
             or body.get("accessToken"))
    assert token, f"No token in login response: {body}"
    return token


def api_register_and_login(playwright: Playwright) -> dict:
    """Register a brand-new unique user and return email, password, name, token."""
    email    = make_unique_email()
    password = "abcdef"
    name     = "Fresh Student"

    ctx = playwright.request.new_context(base_url=BASE_URL)
    res = ctx.post("/auth/register",
                   data={"name": name, "email": email, "password": password})

    # ✅ read BEFORE dispose
    status = res.status
    text   = res.text()
    ctx.dispose()

    assert status in (200, 201), f"Registration failed: HTTP {status} — {text}"

    token = api_login(playwright, email, password)
    return {"email": email, "password": password, "name": name, "token": token}


@pytest.fixture(scope="session")
def admin_token(playwright: Playwright) -> str:
    return api_login(playwright, ADMIN_EMAIL, ADMIN_PASSWORD)


@pytest.fixture()
def fresh_user(playwright: Playwright) -> dict:
    return api_register_and_login(playwright)


@pytest.fixture()
def fresh_user_token(fresh_user: dict) -> str:
    return fresh_user["token"]


@pytest.fixture()
def admin_page(page: Page) -> Page:
    page.goto(f"{BASE_URL}/pages/login.html")
    page.get_by_label("Email").fill(ADMIN_EMAIL)
    page.get_by_label("Password").fill(ADMIN_PASSWORD)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_url("**/home.html")
    return page


@pytest.fixture()
def fast_logged_in_page(page: Page, fresh_user: dict) -> Page:
    page.goto(f"{BASE_URL}/pages/login.html")
    page.get_by_label("Email").fill(fresh_user["email"])
    page.locator('[data-test="input-password"]').fill(fresh_user["password"])
    page.get_by_role("button", name="Sign In").click()
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")
    return page

@pytest.fixture()
def make_unique_email_f() -> str:
    return f"test{int(time.time())}@example.com"