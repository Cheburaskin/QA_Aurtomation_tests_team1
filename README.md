# SV Students Recommend — QA Automation Tests

Automated API and UI end-to-end tests for the [SV Students Recommend](https://sv-students-recommend.onrender.com) web application.
Built with **Playwright + Python + pytest** as part of a QA Automation course at SV College.

---

## Project structure

```
sv-recommend-qa/
  conftest.py              # shared fixtures, hooks, auto-screenshots
  pytest.ini               # markers definition
  pytest_commands.md       # all run options
  requirements.txt         # dependencies
  .env                     # credentials (not committed to Git)
  .env.example             # credentials template (safe to commit)
  .gitignore
  README.md
  │
  ├── test_api.py           # 8 API tests: A1 A2 A3 A4 A7 A8 A9 A10
  ├── test_ui.py            # 16 UI tests: U1 U2 U3 U4 U5 U6 U7 U8 U9 U10 U11 U12 U17 U18 U21 U23
  ├── test_bonus.py         # 2 bonus:     B1 blacklist, B2 suspend
  │
  └── test-results/         # auto-generated screenshots + results.txt
```

**Total: 8 API + 16 UI = 24 required tests + 2 bonus tests**
Plus: 3 parametrized mobile runs (iPhone 17 / Samsung 26 / Desktop Chrome)

---

## Tests chosen

### API tests (8)

| ID | Type | Test |
|----|------|------|
| A1 | Positive | Register a new user |
| A2 | Positive | Login success |
| A3 | Positive | Create recommendation (mandatory only) |
| A4 | Negative | Create recommendation — empty category |
| A7 | Positive | List all recommendations |
| A8 | Negative | Login with wrong password |
| A9 | Positive | Get current user profile |
| A10 | Positive | Get current Bearer token |

### UI tests (16 of 24)

| ID | Type | Test |
|----|------|------|
| U1 | Positive | Login flow |
| U2 | Positive | Store checkout flow |
| U3 | Positive | Create recommendation |
| U4 | Positive | Logo navigation back to Home |
| U5 | Positive | Register then login |
| U6 | Positive | Filter by Movie |
| U7 | Positive | Add to cart updates counter |
| U8 | Positive | Logout |
| U9 | Negative | Invalid login shows error |
| U10 | Negative | Payment — empty card number blocked |
| U11 | Negative | Add Recommendation — missing Your Name |
| U12 | Negative | Regular user cannot access Admin page directly |
| U17 | Boundary | Password exactly 6 chars — passes |
| U18 | Boundary | Password exactly 3 chars — rejected |
| U21 | Feature | Password show/hide (eye icon) |
| U23 | Feature | Cart math recalculation (Cup × 2 = 40 NIS) |

### Bonus tests

| ID | Type | Test |
|----|------|------|
| B1 | System | Blacklisted email cannot register |
| B2 | System | Suspended recommendations blocks creation |

---

## Pytest markers

The project uses the following markers in `pytest.ini`:

| Marker | Purpose |
|--------|---------|
| api | API-level tests |
| ui | UI-level tests |
| mobile | Mobile / responsive tests |
| smoke | Basic functionality checks |
| sanity | Quick validation checks |
| regression | Regression coverage |
| errors_handling | Error handling and validation |
| system | End-to-end system scenarios |
| boundary | Boundary value tests |
| positive | Positive flows |
| negative | Negative / blocked flows |
| focus | Tests currently being debugged |

---

## Setup

### 1. Clone
```bash
git clone https://github.com/<your-username>/sv-recommend-qa.git
cd sv-recommend-qa
```

### 2. Virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 3. Install
```bash
pip install -r requirements.txt
playwright install
```

Main dependencies:

```txt
playwright==1.60.0
pytest==9.0.3
pytest-playwright==0.8.0
pytest-base-url==2.1.0
python-dotenv
requests
```

### 4. Configure credentials
Copy the example file and fill in your credentials:
```bash
copy .env.example .env
```
Then edit `.env` with the real values:
```
BASE_URL=https://sv-students-recommend.onrender.com
ADMIN_USER=admin@svcollege.co.il
ADMIN_PASSWORD=your_admin_password
STUDENT_USER=your_email@example.com
STUDENT_PASSWORD=your_password
```

---

## Run the tests

```bash
# All tests
pytest -v

# With browser visible
pytest -v --headed

# API only
pytest test_api.py -v

# UI only
pytest test_ui.py -v

# Bonus only
pytest test_bonus.py -v

# By marker
pytest -m smoke -v
pytest -m errors_handling -v
pytest -m mobile -v
pytest -m boundary -v
pytest -m system -v

# Single test
pytest test_api.py::test_A7_list_all_recommendations -v
pytest test_bonus.py::test_B1_blacklisted_email_cannot_register -v --headed
```

See `pytest_commands.md` for full list of run options.

---

## Results table

Last full UI + bonus run: **2026-06-25 20:36-20:40**  
Last API run after adding A9 and A10: **2026-06-25 20:59**

```bash
.\venv\Scripts\python.exe -m pytest test_api.py -v
.\venv\Scripts\python.exe -m pytest test_ui.py -v
.\venv\Scripts\python.exe -m pytest test_bonus.py -v
```

### API tests

Result: **7/8 passed**

| Test ID | Test name | Pass / Fail | Notes |
|---------|-----------|-------------|-------|
| A1 | test_A1_register_new_user | ✅ Pass | |
| A2 | test_A2_login_success | ✅ Pass | |
| A3 | test_A3_create_recommendation_mandatory_only | ✅ Pass | |
| A4 | test_A4_create_recommendation_empty_category | ❌ Fail | 🐛 Bug: API returns 201 and defaults category to 'Movie' instead of rejecting. SRS 3.3.3 violated. |
| A7 | test_A7_list_all_recommendations | ✅ Pass | |
| A8 | test_A8_login_wrong_password | ✅ Pass | |
| A9 | test_A9_get_current_user_profile | ✅ Pass | |
| A10 | test_A10_get_current_bearer_token | ✅ Pass | |

### UI tests

Result: **19/19 passed**  
Includes 16 UI tests plus 3 responsive runs: iPhone 17, Samsung 26, Desktop Chrome.

| Test ID | Test name | Pass / Fail | Notes |
|---------|-----------|-------------|-------|
| U1 | test_U1_ui_login | ✅ Pass | |
| U2 | test_U2_ui_store_checkout_flow | ✅ Pass | |
| U3 | test_U3_ui_create_recommendation | ✅ Pass | |
| U4 | test_U4_ui_logo_navigation | ✅ Pass | |
| U5 | test_U5_ui_register_then_login | ✅ Pass | |
| U6 | test_U6_ui_filter_recommendations | ✅ Pass | |
| U7 | test_U7_ui_add_to_cart_updates_counter | ✅ Pass | |
| U8 | test_U8_ui_logout | ✅ Pass | |
| U9 | test_U9_ui_login_invalid_credentials | ✅ Pass | |
| U10 | test_U10_ui_payment_validation_empty_card | ✅ Pass | |
| U11 | test_U11_ui_add_recommendation_missing_your_name | ✅ Pass | |
| U12 | test_U12_ui_access_control_via_url | ✅ Pass | |
| U17 | test_U17_ui_password_min_valid_6_chars | ✅ Pass | |
| U18 | test_U18_ui_password_min_invalid_3_chars | ✅ Pass | |
| U21 | test_U21_ui_password_show_hide | ✅ Pass | |
| U23 | test_U23_ui_cart_math_recalculation | ✅ Pass | |

### Responsive tests

| Test ID | Test name | Pass / Fail | Notes |
|---------|-----------|-------------|-------|
| Mobile | test_login_responsive[iPhone 17] | ✅ Pass | |
| Mobile | test_login_responsive[Samsung 26] | ✅ Pass | |
| Mobile | test_login_responsive[Desktop Chrome] | ✅ Pass | |

### Bonus tests

Result: **2/2 passed**

| Test ID | Test name | Pass / Fail | Notes |
|---------|-----------|-------------|-------|
| B1 | test_B1_blacklisted_email_cannot_register | ✅ Pass | |
| B2 | test_B2_suspended_recommendations_blocks_creation | ✅ Pass | |

---

## Bugs found during testing

| # | Test | SRS says | App does | Verdict |
|---|------|----------|----------|---------|
| 1 | A1, U17, U18 | Password minimum **4** chars (English SRS 3.1.2) | API enforces minimum **6** chars — error: "Password should be at least 6 characters." | 🐛 Bug — SRS contradicts API |
| 2 | A4 | Empty category → **400** rejected, recommendation not created (SRS 3.3.3) | API returns **201** and defaults category to 'Movie' — mandatory field not validated | 🐛 Bug — API accepts invalid data |

## Technical notes

- All tests use `data-test` attributes for selectors (most reliable, confirmed from class examples)
- Fresh unique user generated every run via `conftest.py::fresh_user` fixture
- Screenshots taken automatically after every test (pass and fail) into `test-results/`
- Results summary written to `test-results/results.txt` after every run
- Mobile tests run on iPhone 17, Samsung 26, and Desktop Chrome via `@pytest.mark.parametrize`
- Bonus B1 verifies that an admin-blocked email cannot register.
- Bonus B2 verifies that suspended recommendations block new recommendation creation, then re-enables the feature during cleanup.
- Credentials stored in `.env` file — never committed to GitHub
