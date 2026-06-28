"""
test_ui.py — 16 UI tests + mobile parametrized test.

Chosen: U1, U2, U3, U4, U5, U6, U7, U8, U9, U10, U11, U12, U17, U18, U21, U23
Plus: mobile parametrized login test (iPhone 17, Samsung 26, Desktop Chrome)

Each test generates a fresh unique user so re-runs never clash.
Run with:  pytest test_ui.py -v
           pytest test_ui.py -v --headed
           pytest test_ui.py -m mobile -v --headed
"""

import os
import re
import uuid
import pytest
from operator import contains
from playwright.sync_api import Page, expect, Playwright

BASE_URL = os.environ.get("BASE_URL", "https://sv-students-recommend.onrender.com")

pytestmark = pytest.mark.ui


# ── validation functions (class style: URL + title + content) ─────────────────

def validate_home_page(page: Page) -> bool:
    """Return True if current page is the Home page (URL + title check)."""
    try:
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(f"{BASE_URL}/pages/home.html")
        title = page.title()
        assert contains(title.strip(), "Home"), (
            f"Expected 'Home' in title, got '{title}'"
        )
        return True
    except AssertionError:
        return False


def validate_login_page(page: Page) -> bool:
    """Return True if current page is the Login page (URL + title check)."""
    try:
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(f"{BASE_URL}/pages/login.html")
        title = page.title()
        assert contains(title.strip(), "Login"), (
            f"Expected 'Login' in title, got '{title}'"
        )
        return True
    except AssertionError:
        return False


def validate_error_message(page: Page, expected_text: str) -> bool:
    """Return True if [data-test='error-message'] is visible with expected text."""
    try:
        error = page.locator('[data-test="error-message"]')
        expect(error).to_be_visible(timeout=5000)
        expect(error).to_have_text(expected_text)
        return True
    except AssertionError:
        return False


def validate_url(page: Page, expected_url: str) -> bool:
    """Return True if current page URL matches expected URL."""
    try:
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(expected_url)
        return True
    except AssertionError:
        return False


def validate_element_visible(page: Page, selector: str) -> bool:
    """Return True if element with given selector is visible."""
    try:
        expect(page.locator(selector)).to_be_visible(timeout=5000)
        return True
    except AssertionError:
        return False


# ── mobile device definitions ─────────────────────────────────────────────────

CUSTOM_DEVICES = {
    "iPhone 17": {
        "viewport":            {"width": 402, "height": 874},
        "device_scale_factor": 3,
        "is_mobile":           True,
        "has_touch":           True,
        "default_browser_type": "webkit",
        "user_agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/18.0 Mobile/15E148 Safari/604.1"
        ),
    },
    "Samsung 26": {
        "viewport":            {"width": 384, "height": 832},
        "device_scale_factor": 3,
        "is_mobile":           True,
        "has_touch":           True,
        "default_browser_type": "chromium",
        "user_agent": (
            "Mozilla/5.0 (Linux; Android 15; SM-S931B) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Mobile Safari/537.36"
        ),
    },
}


def resolve_device(playwright, device_name):
    """Return a context-args dict for a device name.
    Looks in Playwright's built-in registry first, then our custom dict,
    and treats 'Desktop Chrome' as plain desktop (empty config)."""
    if device_name == "Desktop Chrome":
        return {}
    if device_name in playwright.devices:
        return playwright.devices[device_name]
    if device_name in CUSTOM_DEVICES:
        return CUSTOM_DEVICES[device_name]
    raise ValueError(f"Unknown device: {device_name!r}")


# ── U1 · Positive — Login flow ────────────────────────────────────────────────

@pytest.mark.positive
@pytest.mark.smoke
def test_U1_ui_login(fast_logged_in_page: Page):
    """
    U1 · Positive
    Navigate to the login page and log in with valid credentials.
    Expected: redirected to Home page.
    SRS 3.1.1
    """
    # 1. Log in with valid credentials (via fast_logged_in_page fixture)
    page = fast_logged_in_page

    # 2. Assert that the login was successful and the user is on the home page
    assert validate_home_page(page), (
        "U1 failed: expected Home page after login"
    )


# ── U2 · Positive — Store checkout flow ──────────────────────────────────────

@pytest.mark.positive
@pytest.mark.regression
def test_U2_ui_store_checkout_flow(fast_logged_in_page: Page):
    """
    U2 · Positive
    Store → add T-Shirt → Cart → Proceed to Payment → fill mandatory fields → Place Order.
    Expected: order placed / confirmation shown.
    SRS 3.5.1–3.5.3
    """
    # 1. Log in and verify on home page
    page = fast_logged_in_page
    assert validate_home_page(page), "U2 failed: expected Home page after login"

    # 2. Add T-Shirt to cart
    page.locator("[data-test='nav-store']").click()
    page.wait_for_load_state("networkidle")
    page.locator("[data-test='btn-add-tshirt']").click()

    # 3. Go to cart and proceed to payment
    page.locator("[data-test='nav-cart']").click()
    page.wait_for_load_state("networkidle")
    page.get_by_role("button", name="Proceed to Payment").click()
    page.wait_for_load_state("networkidle")

    assert validate_url(page, f"{BASE_URL}/pages/payment.html"), (
        "U2 failed: expected Payment page"
    )

    # 4. Fill mandatory payment fields
    page.get_by_label("Full Name").fill("Test Buyer")
    page.get_by_label("Address").fill("123 Test Street")
    page.get_by_label("Credit Card Number").fill("4111111111111111")
    page.get_by_label("CVV / Secret Code").fill("123")
    page.locator("[data-test='input-expiry']").fill("2026-12")
    page.get_by_role("button", name="Place Order").click()

    # 5. Assert order confirmation is shown
    assert validate_element_visible(page, "[data-test='order-success-message']"), (
        "U2 failed: expected order success message"
    )


# ── U3 · Positive — Create recommendation ────────────────────────────────────

@pytest.mark.positive
@pytest.mark.regression
def test_U3_ui_create_recommendation(fast_logged_in_page: Page):
    """
    U3 · Positive
    Create a new recommendation via the UI.
    Verify the recommendation is created successfully.
    SRS 3.3.3
    """
    # 1. Log in and verify on home page
    page = fast_logged_in_page
    assert validate_home_page(page), "U3 failed: expected Home page after login"

    # 2. Navigate to Add Recommendation page
    page.locator("[data-test='nav-signup-recommendations']").click()
    assert validate_url(page, f"{BASE_URL}/pages/add-recommendation.html"), (
        "U3 failed: expected Add Recommendation page"
    )

    # 3. Fill the recommendation form and submit
    recommendation_name = f"Test_{uuid.uuid4().hex[:8]}"
    page.get_by_label("Recommendation Name").fill(recommendation_name)
    page.get_by_label("Description").fill("test")
    page.get_by_label("Website Link").fill("https://www.goodreads.com/book/show/865.The_Alchemist")
    page.get_by_role("button", name="Submit").click()
   
    # 4. Assert recommendation appears on Home page
    assert validate_home_page(page), "U3 failed: expected Home page after submission"
    expect(page.get_by_text(recommendation_name).first).to_be_visible()

    # 5. Clean up — delete the created recommendation
    page.get_by_text(recommendation_name).first.click()
    page.locator("[data-test='btn-delete-recommendation']").click()
    page.locator("[data-test='btn-confirm-delete']").click()


# ── U4 · Positive — Logo navigation ──────────────────────────────────────────

@pytest.mark.positive
@pytest.mark.regression
def test_U4_ui_logo_navigation(fast_logged_in_page: Page):
    """
    U4 · Positive
    Click the SV College logo to navigate back to the Home page.
    Verify the navigation is successful.
    SRS 3.2.1
    """
    # 1. Log in and verify on home page
    page = fast_logged_in_page
    assert validate_home_page(page), "U4 failed: expected Home page after login"

    # 2. Navigate to My Profile page
    page.locator("[data-test='nav-profile']").click()
    page.wait_for_load_state("networkidle")
    assert validate_url(page, f"{BASE_URL}/pages/profile.html"), (
        "U4 failed: expected Profile page"
    )

    # 3. Click the logo and verify navigation back to Home
    page.get_by_role("link", name="SV College SV Recommend ").click()
    page.wait_for_load_state("networkidle")
    assert validate_home_page(page), (
        "U4 failed: expected Home page after clicking logo"
    )


# ── U5 · Positive — Register then login ──────────────────────────────────────

@pytest.mark.positive
@pytest.mark.regression
def test_U5_ui_register_then_login(page: Page, make_unique_email_f: str):
    """
    U5 · Positive
    Register a brand-new unique user via the UI, then log in with it.
    Expected: registration succeeds; login succeeds; lands on Home.
    SRS 3.1.2
    """
    # 1. Navigate to the registration page
    page.goto(f"{BASE_URL}/pages/register.html")
    page.wait_for_load_state("networkidle")

    # 2. Fill the registration form
    unique_email = make_unique_email_f
    page.get_by_label("Student Name").fill("Test User")
    page.get_by_label("Email").fill(unique_email)
    page.locator('[data-test="input-password"]').fill("123456")
    page.get_by_role("button", name="Create Account").click()
    page.wait_for_load_state("networkidle")

    # 3. Assert registration was successful
    assert validate_url(page, f"{BASE_URL}/pages/login.html?registered=true"), (
        "U5 failed: expected redirect to login with registered=true"
    )
    assert validate_element_visible(page, '[data-test="registered-banner"]'), (
        "U5 failed: expected registered banner to be visible"
    )

    # 4. Log in with the new credentials
    page.get_by_label("Email").fill(unique_email)
    page.locator('[data-test="input-password"]').fill("123456")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_load_state("networkidle")

    # 5. Assert login was successful
    assert validate_home_page(page), (
        "U5 failed: expected Home page after login"
    )


# ── U6 · Positive — Filter recommendations ───────────────────────────────────

@pytest.mark.positive
@pytest.mark.regression
def test_U6_ui_filter_recommendations(fast_logged_in_page: Page):
    """
    U6 · Positive
    On Home, click the 'Movie' filter button.
    Expected: Movie filter becomes active; only Movie cards shown.
    SRS 3.3.1
    """
    # 1. Log in and verify on home page
    page = fast_logged_in_page
    assert validate_home_page(page), "U6 failed: expected Home page after login"

    # 2. Click the Movie filter and verify it becomes active
    movie_button = page.locator('[data-test="filter-movie"]')
    movie_button.click()
    expect(movie_button).to_have_class(re.compile(r"active"))


# ── U7 · Positive — Add to cart updates counter ──────────────────────────────

@pytest.mark.positive
@pytest.mark.regression
def test_U7_ui_add_to_cart_updates_counter(fast_logged_in_page: Page):
    """
    U7 · Positive
    Add an item to the cart and verify the cart counter updates correctly.
    Expected: cart badge shows '1' after adding one item.
    SRS 3.5.1
    """
    # 1. Log in and verify on home page
    page = fast_logged_in_page
    assert validate_home_page(page), "U7 failed: expected Home page after login"

    # 2. Go to Store and add T-Shirt
    page.locator("[data-test='nav-store']").click()
    page.wait_for_load_state("networkidle")
    page.locator("[data-test='btn-add-tshirt']").click()

    # 3. Assert cart badge shows 1
    expect(page.locator("[data-test='cart-badge']")).to_have_text("1")

    # 4. Clean up — remove item from cart
    page.locator("[data-test='nav-cart']").click()
    page.wait_for_load_state("networkidle")
    page.get_by_role("button", name="Remove").click()
    expect(page.get_by_text("Your cart is empty.")).to_be_visible()


# ── U8 · Positive — Logout ───────────────────────────────────────────────────

@pytest.mark.positive
@pytest.mark.smoke
def test_U8_ui_logout(fast_logged_in_page: Page):
    """
    U8 · Positive
    While logged in, click Logout.
    Expected: session ends; redirected to Login page (URL + title verified).
    SRS 3.2.1 / 3.4.1
    """
    # 1. Log in and verify on home page
    page = fast_logged_in_page
    assert validate_home_page(page), "U8 failed: expected Home page after login"

    # 2. Click logout
    page.locator("[data-test='nav-logout']").click()
    page.wait_for_load_state("networkidle")

    # 3. Assert redirected to login page
    assert validate_login_page(page), (
        "U8 failed: expected Login page after logout"
    )


# ── U9 · Negative — Invalid login ────────────────────────────────────────────

@pytest.mark.negative
@pytest.mark.errors_handling
@pytest.mark.smoke
def test_U9_ui_login_invalid_credentials(page: Page, make_unique_email_f: str):
    """
    U9 · Negative
    Attempt to log in with invalid credentials.
    Expected: stays on Login page; error message visible.
    SRS 3.1.1
    """
    # 1. Navigate to the login page
    page.goto(f"{BASE_URL}/pages/login.html")
    page.wait_for_load_state("networkidle")

    # 2. Fill login form with invalid credentials
    page.get_by_label("Email").fill(make_unique_email_f)
    page.locator('[data-test="input-password"]').fill("DoesNotMatter123!")

    # 3. Click Sign In
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_load_state("networkidle")

    # 4. Assert stayed on login page and error shown
    assert validate_login_page(page), (
        "U9 failed: should stay on Login page after invalid credentials"
    )
    assert validate_element_visible(page, '[data-test="error-message"]'), (
        "U9 failed: expected error message to be visible"
    )


# ── U10 · Negative — Payment validation — empty card ─────────────────────────

@pytest.mark.negative
@pytest.mark.errors_handling
def test_U10_ui_payment_validation_empty_card(fast_logged_in_page: Page):
    """
    U10 · Negative
    Attempt to place order with empty Credit Card Number.
    Expected: payment blocked; error message shown; stays on payment page.
    SRS 3.5.3
    """
    # 1. Log in and verify on home page
    page = fast_logged_in_page
    assert validate_home_page(page), "U10 failed: expected Home page after login"

    # 2. Add item to cart and proceed to payment
    page.locator("[data-test='nav-store']").click()
    page.wait_for_load_state("networkidle")
    page.locator("[data-test='btn-add-tshirt']").click()
    page.locator("[data-test='nav-cart']").click()
    page.wait_for_load_state("networkidle")
    page.get_by_role("button", name="Proceed to Payment").click()
    page.wait_for_load_state("networkidle")

    # 3. Fill form but leave card number empty → Place Order
    page.get_by_label("Full Name").fill("Test Guy")
    page.get_by_label("Address").fill("123 Test St")
    page.get_by_role("button", name="Place Order").click()
    page.wait_for_load_state("networkidle")

    # 4. Assert error shown and still on payment page
    expect(page.get_by_text("Please fill in all required fields.")).to_be_visible()
    assert validate_url(page, f"{BASE_URL}/pages/payment.html"), (
        "U10 failed: should stay on Payment page when card is empty"
    )

    # 5. Clean up — remove item from cart
    page.locator("[data-test='nav-cart']").click()
    page.wait_for_load_state("networkidle")
    page.get_by_role("button", name="Remove").click()
    expect(page.get_by_text("Your cart is empty.")).to_be_visible()


# ── U11 · Negative — Add Recommendation missing Your Name ────────────────────

@pytest.mark.negative
@pytest.mark.errors_handling
def test_U11_ui_add_recommendation_missing_your_name(fast_logged_in_page: Page):
    """
    U11 · Negative
    Submit Add Recommendation without filling 'Your Name'.
    Expected: form not submitted; stays on add-recommendation page.
    SRS 3.3.3
    """
    # 1. Log in and verify on home page
    page = fast_logged_in_page
    assert validate_home_page(page), "U11 failed: expected Home page after login"

    # 2. Navigate to Add Recommendation page
    page.locator("[data-test='nav-signup-recommendations']").click()
    page.wait_for_load_state("networkidle")
    assert validate_url(page, f"{BASE_URL}/pages/add-recommendation.html"), (
        "U11 failed: expected Add Recommendation page"
    )

    # 3. Fill mandatory fields EXCEPT Your Name
    page.locator("select").first.select_option("Book")
    page.locator("[data-test='input-recommendation-name']").fill("Missing Author Book")
    # Your Name intentionally left empty

    # 4. Try to submit
    page.locator("[data-test='btn-submit-recommendation']").click()

    # 5. Assert stays on add-recommendation page
    assert validate_url(page, f"{BASE_URL}/pages/add-recommendation.html"), (
        "U11 failed: should stay on Add Recommendation page when Your Name is empty"
    )


# ── U12 · Negative — Access control via URL ──────────────────────────────────

@pytest.mark.negative
@pytest.mark.errors_handling
def test_U12_ui_access_control_via_url(fast_logged_in_page: Page):
    """
    U12 · Negative
    Regular user attempts to access /pages/admin.html directly via URL.
    Expected: access blocked; redirected back to Home page.
    SRS 2.2 / 3.4.2
    """
    # 1. Log in as regular user and verify on home page
    page = fast_logged_in_page
    assert validate_home_page(page), "U12 failed: expected Home page after login"

    # 2. Attempt to access admin page directly via URL
    page.goto(f"{BASE_URL}/pages/admin.html")
    page.wait_for_load_state("networkidle")

    # 3. Assert access is denied and user is back on home page
    assert validate_home_page(page), (
        "U12 failed: regular user should be redirected away from admin page"
    )


# ── U17 · Boundary — Password exactly 6 chars — valid ───────────────────────

@pytest.mark.positive
@pytest.mark.boundary
def test_U17_ui_password_min_valid_6_chars(page: Page, make_unique_email_f: str):
    """
    U17 · Boundary — valid boundary
    Register with a password of exactly 6 English characters (minimum).
    Expected: registration succeeds; redirected to login with success banner.
    SRS 3.1.2
    """
    # 1. Navigate to registration page
    page.goto(f"{BASE_URL}/pages/register.html")
    page.wait_for_load_state("networkidle")

    # 2. Fill form with exactly 6-character password
    page.get_by_label("Student Name").fill("Test User")
    page.get_by_label("Email").fill(make_unique_email_f)
    page.locator('[data-test="input-password"]').fill("123456")   # exactly 6 chars
    page.get_by_role("button", name="Create Account").click()
    page.wait_for_load_state("networkidle")

    # 3. Assert registration succeeded
    assert validate_url(page, f"{BASE_URL}/pages/login.html?registered=true"), (
        "U17 failed: registration with 6-char password should succeed"
    )
    assert validate_element_visible(page, '[data-test="registered-banner"]'), (
        "U17 failed: expected success banner after registration"
    )


# ── U18 · Boundary — Password exactly 3 chars — invalid ─────────────────────

@pytest.mark.negative
@pytest.mark.boundary
@pytest.mark.errors_handling
def test_U18_ui_password_min_invalid_3_chars(page: Page, make_unique_email_f: str):
    """
    U18 · Boundary — invalid boundary (3 below minimum)
    Register with a password of exactly 3 characters.
    Expected: registration rejected; error message shown.
    SRS 3.1.2

    BUG FOUND: SRS 3.1.2 states minimum 6 characters,
    but the app error message says 'Password must be at least 4 characters.'
    Test asserts the actual app behavior.
    """
    # 1. Navigate to registration page
    page.goto(f"{BASE_URL}/pages/register.html")
    page.wait_for_load_state("networkidle")

    # 2. Fill form with 3-character password (below minimum)
    page.get_by_label("Student Name").fill("Test User")
    page.get_by_label("Email").fill(make_unique_email_f)
    page.locator('[data-test="input-password"]').fill("123")      # 3 chars — below minimum
    page.get_by_role("button", name="Create Account").click()
    page.wait_for_load_state("networkidle")

    # 3. Assert registration was rejected
    assert validate_url(page, f"{BASE_URL}/pages/register.html"), (
        "U18 failed: should stay on register page with 3-char password"
    )
    # 🐛 Bug: SRS says min 6 chars but app error message says 4
    assert validate_error_message(page, "Password must be at least 4 characters."), (
        "U18 failed: expected error message about password length"
    )


# ── U21 · Feature — Password show/hide ───────────────────────────────────────

@pytest.mark.positive
@pytest.mark.regression
def test_U21_ui_password_show_hide(page: Page):
    """
    U21 · Specific UI feature
    On Login page, type a password (dots), click the eye icon → visible.
    Click again → hidden.
    Expected: input type toggles between 'password' and 'text'.
    SRS 3.1.1
    """
    # 1. Navigate to login page
    page.goto(f"{BASE_URL}/pages/login.html")
    page.wait_for_load_state("networkidle")

    pwd_input = page.locator("[data-test='input-password']")
    pwd_input.fill("mypassword")

    # 2. Confirm starts hidden (type='password')
    assert pwd_input.get_attribute("type") == "password", (
        "U21 failed: password field should start as type='password'"
    )

    # 3. Click eye icon to reveal password
    page.locator("[data-test='btn-toggle-password']").click()
    expect(pwd_input).to_have_attribute("type", "text")

    # 4. Click again to hide password
    page.locator("[data-test='btn-toggle-password']").click()
    expect(pwd_input).to_have_attribute("type", "password")


# ── U23 · Feature — Cart math recalculation ──────────────────────────────────

@pytest.mark.positive
@pytest.mark.regression
def test_U23_ui_cart_math_recalculation(fast_logged_in_page: Page):
    """
    U23 · Specific UI feature
    Add a Cup (20 NIS) to cart, change quantity to 2.
    Expected: line total = 40 NIS; Grand Total = 40 NIS.
    SRS 3.5.2
    """
    # 1. Log in and verify on home page
    page = fast_logged_in_page
    assert validate_home_page(page), "U23 failed: expected Home page after login"

    # 2. Go to store and add Cup (second item — 20 NIS)
    page.locator("[data-test='nav-store']").click()
    page.wait_for_load_state("networkidle")
    add_buttons = page.get_by_role("button", name="Add to cart").all()
    add_buttons[1].click()   # Cup — 20 NIS

    # 3. Go to cart and increase quantity to 2
    page.locator("[data-test='nav-cart']").click()
    page.wait_for_load_state("networkidle")
    page.locator("button:has-text('+')").first.click()

    # 4. Assert line total and grand total both show 40 NIS
    expect(page.locator("[data-test='cart-subtotal-cup']")).to_have_text("40 NIS")
    expect(page.locator("[data-test='cart-total']")).to_have_text("40 NIS")


# ── Mobile — Login responsive (parametrized) ──────────────────────────────────

@pytest.mark.mobile
@pytest.mark.positive
@pytest.mark.parametrize(
    "device_name",
    ["iPhone 17", "Samsung 26", "Desktop Chrome"],
)
def test_login_responsive(playwright, browser, device_name):
    """
    Mobile / Responsive — SRS 3.1.1
    Verify login works correctly on iPhone 17, Samsung 26, and Desktop Chrome.
    Expected: after login, redirected to home.html on all three devices.
    Parametrized test — runs 3 times, once per device.
    Pattern from class example: test_simple_login_as_mobile.py.
    """
    device  = resolve_device(playwright, device_name)
    context = browser.new_context(**device)
    page    = context.new_page()

    page.goto(BASE_URL)
    page.get_by_label("Email").fill(os.environ.get("ADMIN_USER", "admin@svcollege.co.il"))
    page.locator("[data-test='input-password']").fill(os.environ.get("ADMIN_PASSWORD", ""))
    page.get_by_role("button", name="Sign In").click()

    expect(page).to_have_url(f"{BASE_URL}/pages/home.html", timeout=15000)

    context.close()
