"""
test_api.py — 8 API tests chosen from the test bank.
Chosen: A1, A2, A3, A4, A7, A8, A9, A10

Follows class standards:
  - @pytest.mark.api marker on every test
  - Docstrings on every test
  - Response body validation (not just status code)
  - read status + body BEFORE api.dispose()
  - multipart= for POST /api/recommendations (confirmed working)
  - Fresh unique user generated every run

Run:  .\\venv\\Scripts\\python.exe -m pytest test_api.py -v
      .\\venv\\Scripts\\python.exe -m pytest test_api.py -m api -v
"""

import os
import time
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Playwright

load_dotenv()

BASE = os.getenv("BASE_URL", "https://sv-students-recommend.onrender.com")
pytestmark = pytest.mark.api

# ── A1 · Positive — Register a new user ───────────────────────────────────────


@pytest.mark.sanity
def test_A1_register_new_user(playwright: Playwright):
    """
    A1 · Positive — SRS 3.1.2
    POST /auth/register with valid name, unique email and password (min 6 chars).
    Expected: 201 Created; response body contains the new user's email.

    BUG FOUND: SRS says minimum 4 characters but API enforces minimum 6.
    """
    api      = playwright.request.new_context(base_url=BASE)
    email    = f"test{int(time.time())}@example.com"
    password = f"pw_{int(time.time())}"

    res    = api.post("/auth/register", data={
        "name":     "Test Student",
        "email":    email,
        "password": password,
    })
    status = res.status
    body   = res.json()
    api.dispose()

    assert status == 201, f"Expected 201, got {status}. Body: {body}"
    # ✅ body validation
    assert "id" in body or "email" in body or "message" in body, (
        f"Response body should confirm creation: {body}"
    )


# ── A2 · Positive — Login success ─────────────────────────────────────────────


@pytest.mark.sanity
@pytest.mark.smoke
def test_A2_login_success(playwright: Playwright, fresh_user: dict):
    """
    A2 · Positive — SRS 3.1.1
    POST /auth/login with correct credentials.
    Expected: 200 OK; response body contains an access_token.
    """
    api = playwright.request.new_context(base_url=BASE)
    res = api.post("/auth/login", data={
        "email":    fresh_user["email"],
        "password": fresh_user["password"],
    })
    status = res.status
    body   = res.json()
    api.dispose()

    assert status == 200, f"Expected 200, got {status}. Body: {body}"
    # ✅ body validation — token must exist
    token = body.get("access_token") or body.get("token")
    assert token, f"No token in login response: {body}"
    assert isinstance(token, str) and len(token) > 10, (
        f"Token looks invalid: {token}"
    )


# ── A3 · Positive — Create recommendation (mandatory fields only) ──────────────


@pytest.mark.regression
def test_A3_create_recommendation_mandatory_only(playwright: Playwright,
                                                  fresh_user_token: str):
    """
    A3 · Positive — SRS 3.3.3
    POST /api/recommendations with only the three mandatory fields + valid token.
    Expected: 201 Created; response body contains the new recommendation id and name.

    NOTE: API requires multipart form (confirmed from class example test_api_sanity.py).
    Field name confirmed as 'recommender_name' (not 'your_name').
    """
    api = playwright.request.new_context(base_url=BASE)
    rec_name = f"API Test Book {int(time.time())}"

    res = api.post(
        "/api/recommendations",
        headers={"authorization": f"Bearer {fresh_user_token}"},
        multipart={
            "category":         "Book",
            "name":             rec_name,
            "recommender_name": "API Tester",
        },
    )
    status = res.status
    body   = res.json()
    api.dispose()

    assert status == 201, f"Expected 201, got {status}. Body: {body}"
    # ✅ body validation
    assert "id" in body,       f"Missing 'id' in response: {body}"
    assert body["name"] == rec_name, (
        f"Expected name '{rec_name}', got '{body.get('name')}'"
    )
    assert body["category"] == "Book", (
        f"Expected category 'Book', got '{body.get('category')}'"
    )

# ── A4 · Negative — Create recommendation with empty category ─────────────────


@pytest.mark.errors_handling
def test_A4_create_recommendation_empty_category(playwright: Playwright,
                                                   fresh_user_token: str):
    """
    A4 · Negative — SRS 3.3.3
    POST /api/recommendations with category left empty.
    Expected: 400 or 422 — validation error; recommendation not created.

    BUG FOUND: API does not validate empty category.
    Instead of rejecting with 400/422, the API returns 201 and defaults
    category to 'Movie'. This violates SRS 3.3.3 which states:
    "empty mandatory field blocks submit".
    """
    api = playwright.request.new_context(base_url=BASE)
    res = api.post(
        "/api/recommendations",
        headers={"authorization": f"Bearer {fresh_user_token}"},
        multipart={
            "category":         "",            # intentionally empty
            "name":             "Should Fail",
            "recommender_name": "Tester",
        },
    )
    status = res.status
    body   = res.json()
    api.dispose()

    assert status in (400, 422), (
        f"BUG: Expected 400/422 for empty category, got {status}. "
        f"API defaulted category to '{body.get('category')}' instead of rejecting. "
        f"SRS 3.3.3 requires validation to block empty mandatory fields."
    )

# ── A7 · Positive — List all recommendations ──────────────────────────────────


@pytest.mark.sanity
@pytest.mark.smoke
def test_A7_list_all_recommendations(playwright: Playwright):
    """
    A7 · Positive — SRS 3.3.1
    GET /api/recommendations — no authentication required.
    Expected: 200 OK; response is a non-empty list; each item has required fields.
    """
    api = playwright.request.new_context(base_url=BASE)
    res = api.get("/api/recommendations")
    status = res.status
    body   = res.json()
    api.dispose()

    assert status == 200, f"Expected 200, got {status}. Body: {body}"
    # ✅ body validation
    items = body if isinstance(body, list) else body.get("recommendations", [])
    assert isinstance(items, list), f"Expected list, got: {type(body)}"
    assert len(items) > 0, "Expected at least one recommendation in the list"

    first = items[0]
    assert "id"       in first, f"Missing 'id' in first item: {first}"
    assert "name"     in first, f"Missing 'name' in first item: {first}"
    assert "category" in first, f"Missing 'category' in first item: {first}"


# ── A8 · Negative — Login with wrong password ─────────────────────────────────


@pytest.mark.errors_handling
def test_A8_login_wrong_password(playwright: Playwright, fresh_user: dict):
    """
    A8 · Negative — SRS 3.1.1
    POST /auth/login with correct email but wrong password.
    Expected: 401 Unauthorized; no token in response body.
    """
    api = playwright.request.new_context(base_url=BASE)
    res = api.post("/auth/login", data={
        "email":    fresh_user["email"],
        "password": "WRONG_PASSWORD_XYZ",
    })
    status = res.status
    body   = res.json()
    api.dispose()

    assert status in (400, 401, 403), (
        f"Expected error status for wrong password, got {status}. Body: {body}"
    )
    # ✅ body validation — no token should be present
    token = body.get("access_token") or body.get("token")
    assert not token, f"Token should NOT be returned on wrong password: {token}"
    assert "detail" in body or "message" in body, (
        f"Expected error detail in body: {body}"
    )


# ── A9 · Positive — Get current user profile ─────────────────────────────────


@pytest.mark.sanity
@pytest.mark.regression
def test_A9_get_current_user_profile(playwright: Playwright, fresh_user: dict):
    """
    A9 · Positive — Profile endpoint
    GET /api/profile/me with a valid Bearer token.
    Expected: 200 OK; response body contains the logged-in user's profile data.
    """
    api = playwright.request.new_context(base_url=BASE)
    res = api.get(
        "/api/profile/me",
        headers={"authorization": f"Bearer {fresh_user['token']}"},
    )
    status = res.status
    body = res.json()
    api.dispose()

    assert status == 200, f"Expected 200, got {status}. Body: {body}"
    assert body.get("email") == fresh_user["email"], (
        f"Expected email '{fresh_user['email']}', got '{body.get('email')}'"
    )
    assert body.get("name") == fresh_user["name"], (
        f"Expected name '{fresh_user['name']}', got '{body.get('name')}'"
    )
    assert "id" in body, f"Missing 'id' in profile response: {body}"
    assert "is_admin" in body, f"Missing 'is_admin' in profile response: {body}"


# ── A10 · Positive — Get current Bearer token ────────────────────────────────


@pytest.mark.sanity
@pytest.mark.regression
def test_A10_get_current_bearer_token(playwright: Playwright, fresh_user: dict):
    """
    A10 · Positive — Profile token endpoint
    GET /api/profile/token with a valid Bearer token.
    Expected: 200 OK; response body contains the current access_token.
    """
    api = playwright.request.new_context(base_url=BASE)
    res = api.get(
        "/api/profile/token",
        headers={"authorization": f"Bearer {fresh_user['token']}"},
    )
    status = res.status
    body = res.json()
    api.dispose()

    assert status == 200, f"Expected 200, got {status}. Body: {body}"
    token = body.get("access_token") or body.get("token")
    assert token, f"No token in response: {body}"
    assert token == fresh_user["token"], (
        "Token endpoint should return the same token used for authorization"
    )
    assert isinstance(token, str) and len(token) > 10, (
        f"Token looks invalid: {token}"
    )
