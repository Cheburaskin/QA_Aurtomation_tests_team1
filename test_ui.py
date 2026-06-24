"""
test_api.py — 14 UI tests chosen from the test bank.

Chosen: 

Each test generates a fresh unique user so re-runs never clash.
Run with:  pytest test_ui.py -v
To see the browser run: pytest test_ui.py --headed
"""
import time
import pytest
from playwright.sync_api import Page, expect
import os

from conftest import fresh_user


BASE_URL = os.environ.get("BASE_URL", "https://sv-students-recommend.onrender.com")

pytestmark = pytest.mark.ui


# ── U1 · Positive — Login flow ───────────────────────────────────────

@pytest.mark.positive
def test_U1_ui_login(page: Page, fresh_user: dict):
    """
    U1 · Positive
    Navigate to the login page and log in via the UI using a freshly 
    registered API user.
    """
    # 1. Navigate to the page
    page.goto(f"{BASE_URL}/pages/login.html")

    # 2. Interact with UI elements
    page.get_by_label("Email").fill(fresh_user["email"])
    page.locator('[data-test="input-password"]').fill(fresh_user["password"])
    page.get_by_role("button", name="Sign In").click()

    # 3. Assert the UI state changed correctly
    # expect() automatically waits for the URL to change
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")

# ── U9 · Negative — Invalid login ─────────────────────────────

@pytest.mark.negative
def test_U9_ui_login_invalid_credentials(page: Page):
    """
    U9 · Negative
    Attempt to log in with invalid credentials.
    Verify the error message appears and the user is not redirected.
    """
    # 1. Navigate to the login page
    page.goto(f"{BASE_URL}/pages/login.html")

    # 2. Generate a totally fake email using the current clock time 
    # to guarantee it has never been registered
    fake_email = f"ghost_user_{int(time.time())}@example.com"

    # 3. Fill the form (using the strict-mode safe password locator you just fixed!)
    page.get_by_label("Email").fill(fake_email)
    page.locator('[data-test="input-password"]').fill("DoesNotMatter123!")
    
    # 4. Click Submit
    page.get_by_role("button", name="Sign In").click()

    # 5. The Assertions (The Referee)
    
    # First, verify the page did NOT redirect to home.html
    expect(page).to_have_url(f"{BASE_URL}/pages/login.html")

    # Second, verify an error message is visible on the screen.
    error_popup = page.locator('[data-test="error-message"]')  
    expect(error_popup).to_be_visible()

# ── U8 · Positive — Logout ─────────────────────────────

@pytest.mark.positive
def test_U8_ui_logout(fast_logged_in_page: Page):
    """
    U8 · Positive
    Log out of the application via the UI.
    Verify the user is redirected to the login page.
    """
    expect(fast_logged_in_page).to_have_url(f"{BASE_URL}/pages/home.html") 
    fast_logged_in_page.locator("[data-test=\"nav-logout\"]").click()
    expect(fast_logged_in_page).to_have_url(f"{BASE_URL}/pages/login.html")

# ── U17 · Positive — Password min - valid 6 (chars) ───────────────────────────── 

@pytest.mark.positive
def test_U17_ui_password_min_valid_6_chars(page: Page):
    """
    U17 · Positive
    Register a new user with a password of exactly 6 characters.
    Verify the registration is successful and the user can log in.
    """
    # 1. Navigate to the registration page
    page.goto(f"{BASE_URL}/pages/register.html")
    #page.pause()  # Optional: Pause to see the page before filling the form
    # 2. Fill the registration form with a valid password of 6 characters
    unique_email = f"user{int(time.time())}@example.com"
    page.get_by_label("Name").fill("Test User")
    page.get_by_label("Email").fill(unique_email)
    page.locator('[data-test="input-password"]').fill("123456")  # 6 chars
    page.get_by_role("button", name="Create Account").click()

    # 3. Assert that the registration was successful
    expect(page).to_have_url(f"{BASE_URL}/pages/login.html?registered=true")
    expect(page.locator('[data-test=\"registered-banner\"]')).to_be_visible()
    expect(page.locator('[data-test=\"registered-banner\"]')).to_have_text("Account created successfully! Please sign in.")

# ── U18 · Positive — Password min - invalid 3 (chars) ───────────────────────────── 

@pytest.mark.negative
def test_U18_ui_password_min_invalid_3_chars(page: Page):
    """
    U18 · Negative
    Register a new user with a password of exactly 3 characters.
    Verify the registration fails and an error message is displayed.
    """
    # 1. Navigate to the registration page
    page.goto(f"{BASE_URL}/pages/register.html")
    #page.pause()  # Optional: Pause to see the page before filling the form
    # 2. Fill the registration form with an invalid password of 3 characters
    unique_email = f"user{int(time.time())}@example.com"
    page.get_by_label("Name").fill("Test User")
    page.get_by_label("Email").fill(unique_email)
    page.locator('[data-test="input-password"]').fill("123")  # 3 chars
    page.get_by_role("button", name="Create Account").click()

    # 3. Assert that the registration failed
    expect(page).to_have_url(f"{BASE_URL}/pages/register.html")
    expect(page.locator('[data-test="error-message"]')).to_be_visible()
    expect(page.locator('[data-test="error-message"]')).to_have_text("Password must be at least 4 characters.")
