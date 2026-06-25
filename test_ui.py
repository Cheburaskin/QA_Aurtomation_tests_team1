"""
test_ui.py — 16 UI tests chosen from the test bank.

Chosen: 

Each test generates a fresh unique user so re-runs never clash.
Run with:  pytest test_ui.py -v
To see the browser run: pytest test_ui.py --headed
"""
import time
import pytest
from playwright.sync_api import Page, expect
import os
import re


BASE_URL = os.environ.get("BASE_URL", "https://sv-students-recommend.onrender.com")

pytestmark = pytest.mark.ui


# ── U1 · Positive — Login flow ───────────────────────────────────────

@pytest.mark.positive
def test_U1_ui_login(fast_logged_in_page: Page):
    """
    U1 · Positive
    Navigate to the login page and log in with valid credentials.
    Expected: redirected to Home page.
    SRS 3.1.1
    """
    # 1. Log in with valid credentials
    page = fast_logged_in_page 

    #2. Assert that the login was successful and the user is redirected to the home page
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")

# ── U9 · Negative — Invalid login ─────────────────────────────

@pytest.mark.negative
def test_U9_ui_login_invalid_credentials(page: Page, make_unique_email_f: str):
    """
    U9 · Negative
    Attempt to log in with invalid credentials.
    Verify the error message appears and the user is not redirected.
    SRS 3.1.1
    """
    # 1. Navigate to the login page
    page.goto(f"{BASE_URL}/pages/login.html")

    # 2. Fill the login form with invalid credentials
    fake_email = make_unique_email_f
    page.get_by_label("Email").fill(fake_email)
    page.locator('[data-test="input-password"]').fill("DoesNotMatter123!")
    
    # 3. Click Submit
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_load_state("networkidle")

    # 4. The Assertions 
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
    SRS 3.2.1 / 3.4.1
    """
    # 1. Log in with valid credentials and verify the user is on the home page
    page = fast_logged_in_page
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html") 

    # 2. Click the logout button and verify the user is redirected to the login page
    page.locator("[data-test=\"nav-logout\"]").click()
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(f"{BASE_URL}/pages/login.html")

# ── U17 · Positive — Password min - valid 6 (chars) ───────────────────────────── 

@pytest.mark.positive
def test_U17_ui_password_min_valid_6_chars(page: Page, make_unique_email_f: str):
    """
    U17 · Positive
    Register a new user with a password of exactly 6 characters.
    Verify the registration is successful and the user can log in.
    SRS 3.1.2
    """
    # 1. Navigate to the registration page
    page.goto(f"{BASE_URL}/pages/register.html")
    page.wait_for_load_state("networkidle")
    
    # 2. Fill the registration form with a valid password of 6 characters
    unique_email = make_unique_email_f
    page.get_by_label("Student Name").fill("Test User")
    page.get_by_label("Email").fill(unique_email)
    page.locator('[data-test="input-password"]').fill("123456")  
    page.get_by_role("button", name="Create Account").click()
    page.wait_for_load_state("networkidle")

    # 3. Assert that the registration was successful
    expect(page).to_have_url(f"{BASE_URL}/pages/login.html?registered=true")
    expect(page.locator('[data-test=\"registered-banner\"]')).to_be_visible()
    expect(page.locator('[data-test=\"registered-banner\"]')).to_have_text("Account created successfully! Please sign in.")

# ── U18 · Positive — Password min - invalid 3 (chars) ───────────────────────────── 
# ── U18 · Negative — Password min - invalid 3 (chars) ─────────────────────────────

@pytest.mark.negative
def test_U18_ui_password_min_invalid_3_chars(page: Page, make_unique_email_f: str):
    """
    U18 · Negative
    Register a new user with a password of exactly 3 characters.
    Verify the registration fails and an error message is displayed.
    SRS 3.1.2

    BUG FOUND: SRS 3.1.2 states minimum 6 characters,
    but the app error message says 'Password must be at least 4 characters.'
    Test asserts the actual app behavior.
    """
    # 1. Navigate to the registration page
    page.goto(f"{BASE_URL}/pages/register.html")
    page.wait_for_load_state("networkidle")

    # 2. Fill the registration form with an invalid password of 3 characters
    unique_email = make_unique_email_f
    page.get_by_label("Student Name").fill("Test User")
    page.get_by_label("Email").fill(unique_email)
    page.locator('[data-test="input-password"]').fill("123")   # 3 chars — below minimum
    page.get_by_role("button", name="Create Account").click()
    page.wait_for_load_state("networkidle")

    # 3. Assert that the registration failed
    expect(page).to_have_url(f"{BASE_URL}/pages/register.html")
    expect(page.locator('[data-test="error-message"]')).to_be_visible()
    # 🐛 Bug: SRS says min 6 chars but app error message says 4
    expect(page.locator('[data-test="error-message"]')).to_have_text("Password must be at least 4 characters.")

# ── U12 · Negative — Access control via URL ───────────────────────────── 

@pytest.mark.negative 
def test_U12_ui_access_control_via_url(fast_logged_in_page: Page):
    """
    U12 · Negative
    Attempt to access a protected page with the url without valid authentication.
    Verify the user is denied.
    SRS 2.2 / 3.4.2
    """
    # 1. Log in with valid credentials and verify the user is on the home page
    page = fast_logged_in_page
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")  

    # 2. Attempt to access the admin page directly via URL
    page.goto(f"{BASE_URL}/pages/admin.html")
    page.wait_for_load_state("networkidle")

    # 3. Assert that the user is denied access and redirected to the login page
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html") 

# ── U3 · Positive — Create recommendation ───────────────────────────── 

@pytest.mark.positive
def test_U3_ui_create_recommendation(fast_logged_in_page: Page):
    """
    U3 · Positive
    Create a new recommendation via the UI.
    Verify the recommendation is created successfully.
    SRS 3.3.3
    """
    # 1. Log in with valid credentials and verify the user is on the home page
    page = fast_logged_in_page
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")  

    # 2. Navigate to the "Add Recommendation" page and confirm
    page.locator("[data-test=\"nav-signup-recommendations\"]").click()
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(f"{BASE_URL}/pages/add-recommendation.html") 

    # 3. Fill the recommendation form with valid data and submit
    page.get_by_label("Recommendation Name").fill("Test12345")
    page.get_by_label("Description").fill("test")
    page.get_by_label("Website Link").fill("https://www.goodreads.com/book/show/865.The_Alchemist")
    page.get_by_role("button", name="Submit").click()
    page.wait_for_load_state("networkidle")
    
    # 4. Assert that the recommendation was created successfully   
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")
    expect(page.get_by_text("Test12345").first).to_be_visible()
    
    # 5. Clean up by deleting the created recommendation
    page.get_by_text("Test12345").first.click()
    page.wait_for_load_state("networkidle")
    page.locator("[data-test=\"btn-delete-recommendation\"]").click()
    page.locator("[data-test=\"btn-confirm-delete\"]").click()

# ── U4 · Positive — Logo Navigation ───────────────────────────── 

@pytest.mark.positive
def test_U4_ui_logo_navigation(fast_logged_in_page: Page):
    """
    U4 · Positive
    Click the logo to navigate back to the home page.
    Verify the navigation is successful.
    SRS 3.2.1
    """
    # 1. Log in with valid credentials and verify the user is on the home page
    page = fast_logged_in_page
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")  

    # 2. Head to My Profile page 
    page.locator("[data-test=\"nav-profile\"]").click()
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(f"{BASE_URL}/pages/profile.html") 

    # 3. Click the logo to navigate back to the home page and validate the navigation
    page.get_by_role("link", name="SV College SV Recommend ").click()
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html") 

# ── U5 · Positive — Register then login ─────────────────────────────

@pytest.mark.positive
def test_U5_ui_register_then_login(page: Page, make_unique_email_f: str):
    """
    U5 · Positive
    Register a new user via the UI and then log in with the new credentials.
    Verify both registration and login are successful.
    SRS 3.1.2
    """
    # 1. Navigate to the registration page
    page.goto(f"{BASE_URL}/pages/register.html")
    page.wait_for_load_state("networkidle")

    # 2. Fill the registration form with a valid password of 6 characters
    unique_email = make_unique_email_f
    page.get_by_label("Student Name").fill("Test User")
    page.get_by_label("Email").fill(unique_email)
    page.locator('[data-test="input-password"]').fill("123456") 
    page.get_by_role("button", name="Create Account").click()
    page.wait_for_load_state("networkidle")

    # 3. Assert that the registration was successful
    expect(page).to_have_url(f"{BASE_URL}/pages/login.html?registered=true")
    expect(page.locator('[data-test=\"registered-banner\"]')).to_be_visible()
    expect(page.locator('[data-test=\"registered-banner\"]')).to_have_text("Account created successfully! Please sign in.")
    
    # 4. Log in with the new credentials
    page.get_by_label("Email").fill(unique_email)
    page.locator('[data-test="input-password"]').fill("123456")
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_load_state("networkidle")

    # 5. Assert that the login was successful
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")

# ── U6 · Positive — Filter Recommendations ─────────────────────────────

@pytest.mark.positive
def test_U6_ui_filter_recommendations(fast_logged_in_page: Page):
    """
    U6 · Positive
    Filter recommendations by a specific keyword.
    Verify the filtered results are displayed correctly.
    SRS 3.3.1
    """
    # 1. Log in with valid credentials and verify the user is on the home page
    page = fast_logged_in_page
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")  

    #2. Click the "Movie" filter button and verify that the recommendations are filtered accordingly
    movie_button = page.locator('[data-test="filter-movie"]')
    movie_button.click()
    expect(movie_button).to_have_class(re.compile(r"active"))  

# ── U7 · Positive — Add to cart updates counter ─────────────────────────────

@pytest.mark.positive
def test_U7_ui_add_to_cart_updates_counter(fast_logged_in_page: Page):
    """
    U7 · Positive
    Add an item to the cart and verify that the cart counter updates correctly.
    SRS 3.5.1
    """
    # 1. Log in with valid credentials and verify the user is on the home page
    page = fast_logged_in_page
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")  

    #2. Add an item to the cart and verify that the cart counter updates correctly
    page.locator("[data-test=\"nav-store\"]").click()
    page.wait_for_load_state("networkidle")
    page.locator("[data-test=\"btn-add-tshirt\"]").click()
    expect(page.locator("[data-test=\"cart-badge\"]")).to_have_text("1") 
    
    #3. Clean up by removing the item from the cart and verifying the counter resets
    page.locator("[data-test=\"nav-cart\"]").click() 
    page.wait_for_load_state("networkidle")
    page.get_by_role("button", name="Remove").click()   
    expect(page.get_by_text("Your cart is empty.")).to_be_visible()

# ── U10 · Negative — Payment validation - empty card ─────────────────────────────
@pytest.mark.focus
@pytest.mark.negative
def test_U10_ui_payment_validation_empty_card(fast_logged_in_page: Page):
    """
    U10 · Negative
    Attempt to proceed with payment with an empty card.
    Verify that the payment is not processed and an error message is displayed.
    SRS 3.5.3
    """
    # 1. Log in with valid credentials and verify the user is on the home page
    page = fast_logged_in_page
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html") 

    # 2. Add an item to the cart and proceed to payment
    page.locator("[data-test=\"nav-store\"]").click()
    page.wait_for_load_state("networkidle")
    page.locator("[data-test=\"btn-add-tshirt\"]").click()
    page.locator("[data-test=\"nav-cart\"]").click()
    page.wait_for_load_state("networkidle")
    page.get_by_role("button", name="Proceed to Payment").click()
    page.wait_for_load_state("networkidle")

    # 3. Attempt to submit the payment form with empty card details and verify that an error message is displayed
    page.get_by_label("Full Name").fill("Test Guy")  
    page.get_by_label("Address").fill("123 Test St")
    page.get_by_role("button", name="Place Order").click()
    page.wait_for_load_state("networkidle")
    expect(page.get_by_text("Please fill in all required fields.")).to_be_visible()
    expect(page).to_have_url(f"{BASE_URL}/pages/payment.html")
    
    # 4. Clean up by removing the item from the cart and verifying the counter resets
    page.locator("[data-test=\"nav-cart\"]").click() 
    page.wait_for_load_state("networkidle")
    page.get_by_role("button", name="Remove").click()   
    expect(page.get_by_text("Your cart is empty.")).to_be_visible()

# ── U2 · Positive — Store checkout flow ─────────────────────────────────────

@pytest.mark.positive
def test_U2_ui_store_checkout_flow(fast_logged_in_page: Page):
    """
    U2 · Positive
    Store → add T-Shirt → Cart → Proceed to Payment → fill mandatory fields → Place Order.
    Expected: order placed / confirmation shown.

    """
    page = fast_logged_in_page
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")

    # add T-Shirt to cart
    page.locator("[data-test='nav-store']").click()
    page.wait_for_load_state("networkidle")
    page.locator("[data-test='btn-add-tshirt']").click()

    # go to cart and proceed to payment
    page.locator("[data-test='nav-cart']").click()
    page.wait_for_load_state("networkidle")
    page.get_by_role("button", name="Proceed to Payment").click()
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(f"{BASE_URL}/pages/payment.html")

    # fill mandatory fields
    page.get_by_label("Full Name").fill("Test Buyer")
    page.get_by_label("Address").fill("123 Test Street")
    page.get_by_label("Credit Card Number").fill("4111111111111111")
    page.get_by_label("CVV / Secret Code").fill("123")
    page.locator("[data-test='input-expiry']").fill("2026-12")
    page.get_by_role("button", name="Place Order").click()
    page.wait_for_timeout(3000)

    # confirm order success
    expect(page.locator("[data-test='order-success-message']")).to_be_visible(timeout=10_000)



# ── U11 · Negative — Add Recommendation missing Your Name ────────────────────

@pytest.mark.negative
def test_U11_ui_add_recommendation_missing_your_name(fast_logged_in_page: Page):
    """
    U11 · Negative
    Submit Add Recommendation without filling 'Your Name'.
    Expected: form not submitted; stays on add-recommendation page.
    SRS 3.3.3
    """
    page = fast_logged_in_page
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")

    page.locator("[data-test='nav-signup-recommendations']").click()
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(f"{BASE_URL}/pages/add-recommendation.html")

    # fill mandatory fields EXCEPT Your Name
    page.locator("select").first.select_option("Book")
    page.locator("[data-test='input-recommendation-name']").fill("Missing Author Book")
    # Your Name intentionally left empty

    page.locator("[data-test='btn-submit-recommendation']").click()
    page.wait_for_timeout(2000)

    # should stay on add-recommendation page
    expect(page).to_have_url(f"{BASE_URL}/pages/add-recommendation.html")


# ── U21 · Feature — Password show/hide ───────────────────────────────────────

@pytest.mark.positive
def test_U21_ui_password_show_hide(page: Page):
    """
    U21 · Specific UI feature
    On Login page, type a password, click the eye icon → password visible.
    Click again → password hidden.
    Expected: input type toggles between 'password' and 'text'.
    SRS 3.1.1
    """
    page.goto(f"{BASE_URL}/pages/login.html")
    page.wait_for_load_state("networkidle")

    pwd_input = page.locator("[data-test='input-password']")
    pwd_input.fill("mypassword")

    # confirm starts hidden
    assert pwd_input.get_attribute("type") == "password", (
        "Password field should start as type='password'"
    )

    # click eye icon to show
    page.locator("[data-test='btn-toggle-password']").click()
    expect(pwd_input).to_have_attribute("type", "text")

    # click again to hide
    page.locator("[data-test='btn-toggle-password']").click()
    expect(pwd_input).to_have_attribute("type", "password")


# ── U23 · Feature — Cart math recalculation ──────────────────────────────────

@pytest.mark.positive
def test_U23_ui_cart_math_recalculation(fast_logged_in_page: Page):
    """
    U23 · Specific UI feature
    Add a Cup (20 NIS) to cart, change quantity to 2.
    Expected: line total and Grand Total update to 40 NIS.
    SRS 3.5.2
    """
    page = fast_logged_in_page
    expect(page).to_have_url(f"{BASE_URL}/pages/home.html")

    # go to store and add Cup (second item)
    page.locator("[data-test='nav-store']").click()
    page.wait_for_load_state("networkidle")

    add_buttons = page.get_by_role("button", name="Add to cart").all()
    add_buttons[1].click()   # Cup — 20 NIS

    # go to cart
    page.locator("[data-test='nav-cart']").click()
    page.wait_for_load_state("networkidle")

    # increase quantity to 2 using + button
    page.locator("button:has-text('+')").first.click()
    page.wait_for_timeout(2000)

    # 40 NIS should appear on the page
    expect(page.locator("[data-test='cart-subtotal-cup']")).to_have_text("40 NIS")
    expect(page.locator("[data-test='cart-total']")).to_have_text("40 NIS")


# ── Mobile — Login responsive test ───────────────────────────────────────────

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