"""
test_bonus.py — Bonus challenge tests.

Bonus 1 (B1): Admin blacklists an email → that email cannot register.
Bonus 2 (B2): Admin suspends new recommendations → a user cannot create one.

Both use:
  - login_as_admin fixture from conftest.py
  - data-test selectors confirmed from class example test_positive_suspend_recomendation.py
  - validate_* functions (class style: URL + content check)
  - @pytest.mark decorators + docstrings

Run:  .\\venv\\Scripts\\python.exe -m pytest test_bonus.py -v --headed
      .\\venv\\Scripts\\python.exe -m pytest test_bonus.py -m system -v
"""

import os
import time
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, Playwright, expect

load_dotenv()

BASE           = os.getenv("BASE_URL",       "https://sv-students-recommend.onrender.com")
ADMIN_EMAIL    = os.getenv("ADMIN_USER",      "admin@svcollege.co.il")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD",  "")


# ── validation functions ───────────────────────────────────────────────────────

def validate_registration_rejected(page: Page) -> bool:
    """
    Return True if registration was rejected.
    Checks that error message is visible OR user is still on register page.
    """
    try:
        page.wait_for_load_state("networkidle")
        stayed  = "register" in page.url
        errored = page.locator("[data-test='error-message']").count() > 0
        assert stayed or errored, (
            f"Registration should be rejected but got URL: {page.url}"
        )
        return True
    except AssertionError:
        return False


def validate_suspend_error(page: Page) -> bool:
    """
    Return True if the suspend error message is visible.
    Expected text: 'New recommendations are currently disabled by the administrator.'
    Selector confirmed from class example: test_positive_suspend_recomendation.py
    """
    try:
        error_msg_locator = page.locator("[data-test='error-message']")
        expect(error_msg_locator).to_have_text(
            "New recommendations are currently disabled by the administrator.",
            timeout=5000
        )
        return True
    except AssertionError:
        return False


def validate_email_in_blacklist(page: Page, email: str) -> bool:
    """Return True if the blocked email appears in the blacklist table."""
    try:
        expect(page.get_by_text(email, exact=False)).to_be_visible(timeout=5000)
        return True
    except AssertionError:
        return False


def remove_email_from_blacklist(playwright: Playwright, email: str) -> None:
    """Best-effort cleanup for emails added by B1."""
    api = playwright.request.new_context(base_url=BASE)
    try:
        login = api.post("/auth/login", data={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
        })
        if login.status != 200:
            return

        body = login.json()
        token = body.get("access_token") or body.get("token")
        if not token:
            return

        headers = {"authorization": f"Bearer {token}"}
        blacklist = api.get("/api/admin/blacklist", headers=headers)
        if blacklist.status != 200:
            return

        data = blacklist.json()
        entries = data if isinstance(data, list) else (
            data.get("blacklist") or data.get("items") or data.get("emails") or []
        )

        for entry in entries:
            if not isinstance(entry, dict) or entry.get("email") != email:
                continue

            entry_id = entry.get("id") or entry.get("entry_id")
            if entry_id:
                api.delete(f"/api/admin/blacklist/{entry_id}", headers=headers)
            return
    finally:
        api.dispose()


# ── B1 · Blacklist test ───────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.system
def test_B1_blacklisted_email_cannot_register(login_as_admin: Page,
                                             playwright: Playwright):
    """
    Bonus 1 — SRS 3.4.2
    Admin blocks an email via System page → that email cannot register.

    Steps:
      1. Login as Admin (via login_as_admin fixture).
      2. Go to System page → Email Blacklist → block a unique test email.
      3. Verify email appears in blacklist table.
      4. Logout.
      5. Try to register with the blocked email.
      6. Cleanup: remove the blocked email from the blacklist.
    Expected: registration is rejected.

    Selectors from live admin page (confirmed from class screenshot):
      - input placeholder 'email@example.com' for blacklist input
      - 'Block Email' button
    """
    page = login_as_admin

    # unique email so blacklist doesn't grow with junk on every run
    blocked_email = f"blocked_{int(time.time())}@example.com"

    try:
        # ── Step 2: go to System page and block the email ─────────────────────
        page.locator("[data-test='nav-system']").click()
        page.wait_for_load_state("networkidle")

        page.locator("input[placeholder*='email@example.com'], "
                     "[data-test='input-blacklist-email']").first.fill(blocked_email)
        page.get_by_role("button", name="Block Email").click()
        expect(page.get_by_text(blocked_email, exact=False)).to_be_visible(timeout=5000)

        # ── Step 3: verify email is in the blacklist table ────────────────────
        assert validate_email_in_blacklist(page, blocked_email), (
            f"Expected '{blocked_email}' to appear in blacklist table"
        )

        # ── Step 4: logout ─────────────────────────────────────────────────────
        page.locator("[data-test='nav-logout']").click()
        page.wait_for_load_state("networkidle")

        # ── Step 5: try to register with the blocked email ────────────────────
        page.goto(f"{BASE}/pages/register.html")
        page.wait_for_load_state("networkidle")

        page.locator("[data-test='input-name']").fill("Blocked User")
        page.locator("[data-test='input-email']").fill(blocked_email)
        page.locator("[data-test='input-password']").fill("abcdef")
        page.locator("[data-test='btn-register']").click()

        assert validate_registration_rejected(page), (
            f"Blacklisted email '{blocked_email}' should be rejected at registration"
        )
    finally:
        remove_email_from_blacklist(playwright, blocked_email)


# ── B2 · Suspend test ─────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.system
def test_B2_suspended_recommendations_blocks_creation(login_as_admin: Page):
    """
    Bonus 2 — SRS 3.4.2
    Admin suspends new recommendations → a user cannot create one.

    Steps:
      1. Login as Admin (via login_as_admin fixture).
      2. Go to System page → click Suspend/Toggle recommendations button.
      3. Navigate to Add Recommendation page.
      4. Fill mandatory fields and try to submit.
      5. Verify creation is blocked with error message.
      6. Cleanup: re-enable recommendations (toggle back).

    Selectors confirmed from class example: test_positive_suspend_recomendation.py
      - [data-test='nav-system']
      - [data-test='btn-toggle-recommendations']
      - [data-test='nav-signup-recommendations'] (+ Add Recommendation)
      - [data-test='input-recommendation-name']
      - [data-test='btn-submit-recommendation']
      - [data-test='error-message']
    """
    page = login_as_admin
    recommendations_suspended = False

    # ── Step 2: go to System and suspend recommendations ─────────────────────
    page.locator("[data-test='nav-system']").click()
    page.wait_for_load_state("networkidle")
    with page.expect_response(lambda r: r.ok and r.status != 304):
        page.locator("[data-test='btn-toggle-recommendations']").click()
    recommendations_suspended = True

    try:
        # ── Step 3 & 4: go to Add Recommendation and try to submit ───────────
        page.goto(f"{BASE}/pages/home.html")
        page.wait_for_load_state("networkidle")
        page.locator("[data-test='nav-signup-recommendations']").click()
        page.wait_for_load_state("networkidle")

        page.locator("[data-test='input-recommendation-name']").fill("Should Be Blocked")
        page.get_by_label("Description").fill("test description")
        page.get_by_label("Website Link").fill("https://example.com")
        page.locator("[data-test='btn-submit-recommendation']").click()

        # ── Step 5: verify error message ─────────────────────────────────────
        assert validate_suspend_error(page), (
            "Expected error 'New recommendations are currently disabled by the administrator.' "
            "but it was not shown"
        )
    finally:
        # ── Step 6: cleanup — re-enable recommendations ───────────────────────
        if recommendations_suspended:
            page.locator("[data-test='nav-system']").click()
            page.wait_for_load_state("networkidle")
            with page.expect_response(lambda r: r.ok and r.status != 304):
                page.locator("[data-test='btn-toggle-recommendations']").click()
