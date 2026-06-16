"""
test_api.py — 6 API tests chosen from the test bank.

Chosen: A1, A2, A3, A4, A7, A8

Each test generates a fresh unique user so re-runs never clash.
Run with:  pytest test_api.py -v
"""

import time
import pytest
from playwright.sync_api import Playwright

BASE = "https://sv-students-recommend.onrender.com"

pytestmark = pytest.mark.api


# ── A1 · Positive — Register a new user ───────────────────────────────────────

@pytest.mark.positive
def test_A1_register_new_user(playwright: Playwright):
    """
    A1 · Positive
    POST /auth/register with valid name, unique email and password.
    Expected: 200 or 201 — user created.
    SRS 3.1.2
    """
    api   = playwright.request.new_context(base_url=BASE)
    email = f"test_{int(time.time())}@example.com"

    res    = api.post("/auth/register", data={
        "name":     "Test Student",
        "email":    email,
        "password": "abcdef",
    })
    status = res.status          # ✅ read BEFORE dispose
    text   = res.text()
    api.dispose()

    assert status in (200, 201), (
        f"Expected 200/201 on registration, got {status}.\nBody: {text}"
    )


# ── A2 · Positive — Login success ─────────────────────────────────────────────

@pytest.mark.positive
def test_A2_login_success(playwright: Playwright, fresh_user: dict):
    """
    A2 · Positive
    POST /auth/login with correct credentials of a freshly registered user.
    Expected: 200 and a bearer token in the response body.
    SRS 3.1.1
    """
    api = playwright.request.new_context(base_url=BASE)
    res = api.post("/auth/login", data={
        "email":    fresh_user["email"],
        "password": fresh_user["password"],
    })
    status = res.status          # ✅ read BEFORE dispose
    body   = res.json()
    api.dispose()

    assert status == 200, (
        f"Expected 200 on login, got {status}.\nBody: {body}"
    )
    token = (body.get("token")
             or body.get("access_token")
             or body.get("accessToken"))
    assert token, f"No token found in login response: {body}"


# ── A3 · Positive — Create recommendation (mandatory fields only) ──────────────

@pytest.mark.positive
def test_A3_create_recommendation_mandatory_only(playwright: Playwright,
                                                  fresh_user_token: str):
    """
    A3 · Positive
    POST /api/recommendations with only the mandatory fields + a valid token.
    Expected: 200 or 201 — recommendation created.
    SRS 3.3.3
    """
    api = playwright.request.new_context(base_url=BASE)
    res = api.post(
        "/api/recommendations",
        form={
            "category":         "Book",
            "name":             f"API Test Book {int(time.time())}",
            "recommender_name": "API Tester",
        },
        headers={
            "Authorization": f"Bearer {fresh_user_token}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
    )
    status = res.status
    text   = res.text()
    api.dispose()

    assert status in (200, 201), (
        f"Expected 200/201 creating recommendation, got {status}.\nBody: {text}"
    )

# ── A4 · Negative — Create recommendation with empty category ─────────────────

@pytest.mark.negative
def test_A4_create_recommendation_empty_category(playwright: Playwright,
                                                   fresh_user_token: str):
    """
    A4 · Negative
    POST /api/recommendations with category left empty.
    Expected: 400 or 422 — validation error; nothing created.
    SRS 3.3.3
    """
    api = playwright.request.new_context(base_url=BASE)
    res = api.post(
        "/api/recommendations",
        data={
            "category":         "",
            "name":             "Should Fail",
            "recommender_name": "Tester",
        },
        headers={
            "Authorization": f"Bearer {fresh_user_token}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
    )
    status = res.status
    text   = res.text()
    api.dispose()

    assert status in (400, 422), (
        f"Expected 400/422 for empty category, got {status}.\nBody: {text}"
    )


# ── A7 · Positive — List all recommendations ──────────────────────────────────

@pytest.mark.positive
def test_A7_list_all_recommendations(playwright: Playwright):
    """
    A7 · Positive
    GET /api/recommendations — no authentication required.
    Expected: 200 and the response body is a list.
    SRS 3.3.1
    """
    api = playwright.request.new_context(base_url=BASE)
    res = api.get("/api/recommendations")
    status = res.status          # ✅ read BEFORE dispose
    body   = res.json()
    api.dispose()

    assert status == 200, (
        f"Expected 200 listing recommendations, got {status}.\nBody: {body}"
    )
    items = body if isinstance(body, list) else body.get("recommendations", body)
    assert isinstance(items, list), (
        f"Expected a list in the response body, got: {type(body)}"
    )


# ── A8 · Negative — Login with wrong password ─────────────────────────────────

@pytest.mark.negative
def test_A8_login_wrong_password(playwright: Playwright, fresh_user: dict):
    """
    A8 · Negative
    POST /auth/login with correct email but a wrong password.
    Expected: error status — no token returned.
    SRS 3.1.1
    """
    api = playwright.request.new_context(base_url=BASE)
    res = api.post("/auth/login", data={
        "email":    fresh_user["email"],
        "password": "WRONG_PASSWORD_XYZ",
    })
    status = res.status          # ✅ read BEFORE dispose
    body   = res.json()
    api.dispose()

    assert status in (400, 401, 403), (
        f"Expected error status for wrong password, got {status}.\nBody: {body}"
    )
    token = (body.get("token")
             or body.get("access_token")
             or body.get("accessToken"))
    assert not token, (
        f"Token should NOT be returned on wrong password, but got: {token}"
    )