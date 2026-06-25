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
import re


BASE_URL = os.environ.get("BASE_URL", "https://sv-students-recommend.onrender.com")

pytestmark = pytest.mark.ui


# ── U1 · Positive — Login flow ───────────────────────────────────────

@pytest.mark.positive
def test_U1_ui_login(fast_logged_in_page: Page):
    """
    U1 · Positive
    Navigate to the login page and log in 
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
    """
    # 1. Navigate to the login page
    page.goto(f"{BASE_URL}/pages/login.html")

    # 2. Fill the login form with invalid credentials
    fake_email = make_unique_email_f
    page.get_by_label("Email").fill(fake_email)
    page.locator('[data-test="input-password"]').fill("DoesNotMatter123!")
    
    # 4. Click Submit
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_load_state("networkidle")

    # 5. The Assertions 
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

@pytest.mark.negative
def test_U18_ui_password_min_invalid_3_chars(page: Page, make_unique_email_f: str):
    """
    U18 · Negative
    Register a new user with a password of exactly 3 characters.
    Verify the registration fails and an error message is displayed.
    """
    # 1. Navigate to the registration page
    page.goto(f"{BASE_URL}/pages/register.html")
    page.wait_for_load_state("networkidle")

    # 2. Fill the registration form with an invalid password of 3 characters
    unique_email = make_unique_email_f
    page.get_by_label("Name").fill("Test User")
    page.get_by_label("Email").fill(unique_email)
    page.locator('[data-test="input-password"]').fill("123") 
    page.get_by_role("button", name="Create Account").click()
    page.wait_for_load_state("networkidle")

    # 3. Assert that the registration failed
    expect(page).to_have_url(f"{BASE_URL}/pages/register.html")
    expect(page.locator('[data-test="error-message"]')).to_be_visible()
    expect(page.locator('[data-test="error-message"]')).to_have_text("Password must be at least 4 characters.")

# ── U12 · Negative — Access control via URL ───────────────────────────── 

@pytest.mark.negative 
def test_U12_ui_access_control_via_url(fast_logged_in_page: Page):
    """
    U12 · Negative
    Attempt to access a protected page with the url without valid authentication.
    Verify the user is denied
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
    """
    # 1. Navigate to the registration page
    page.goto(f"{BASE_URL}/pages/register.html")
    page.wait_for_load_state("networkidle")

    # 2. Fill the registration form with a valid password of 6 characters
    unique_email = make_unique_email_f
    page.get_by_label("Name").fill("Test User")
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