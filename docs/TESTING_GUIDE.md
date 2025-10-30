# Testing Guide

## Test Structure

The GeneWeb Python port uses a multi-tiered testing strategy with tests organized by scope and purpose:

```
modernProject/tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Fast, isolated function tests
├── integration/          # Module interaction tests
├── functional/           # Complete workflow tests
└── e2e/                  # Browser-based UI tests
```

## Test Categories

### Unit Tests

**Location:** `modernProject/tests/unit/`

**Purpose:** Test individual functions and methods in isolation

**Characteristics:**
- No database or network calls
- Mock external dependencies
- Execute in milliseconds
- Run on every commit

**Run:**
```bash
make unit-test
```

**Example:**
```python
def test_crush_name():
    assert name.crush("John") == "john"
    assert name.crush("O'Brien") == "obrien"
```

### Integration Tests

**Location:** `modernProject/tests/integration/`

**Purpose:** Test multiple modules working together with real components

**Characteristics:**
- Real database interactions
- Module-to-module communication
- Execute in seconds
- Run before merge to main

**Run:**
```bash
make integration-test
```

**Example:**
```python
def test_database_person_lifecycle(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "test_base")

    def check_persons(base):
        person = driver.poi(base, 0)
        first_name = driver.sou(base, driver.get_first_name(person))
        assert first_name.decode() == "John"
        return True

    result = database.with_database(gwb_path, check_persons)
    assert result is True
```

### Functional Tests

**Location:** `modernProject/tests/functional/`

**Purpose:** Test complete user workflows from end to end

**Characteristics:**
- Complete features from user perspective
- Real components (database, file system)
- Execute in seconds
- Run before release

**Run:**
```bash
make functional-test
```

**Example:**
```python
def test_name_search_workflow(temp_dir):
    secure.add_assets(temp_dir)
    gwb_path = create_minimal_gwb(temp_dir, "search_test")

    def search_by_name(base):
        target_name = "John"
        crushed_target = name.crush(target_name)
        found_persons = []

        person_count = driver.nb_of_persons(base)
        for i in range(person_count):
            person = driver.poi(base, i)
            first_name = driver.sou(base, driver.get_first_name(person))
            if name.crush(first_name.decode()) == crushed_target:
                found_persons.append((i, first_name))

        assert len(found_persons) >= 1
        return True

    result = database.with_database(gwb_path, search_by_name)
    assert result is True
```

### E2E Tests

**Location:** `modernProject/tests/e2e/`

**Purpose:** Test through actual browser with real server

**Characteristics:**
- Browser-based testing using Selenium
- Starts real gwd server
- Tests actual HTTP responses and HTML rendering
- Slowest tests (seconds to minutes)
- Run before release only
- Requires Selenium and Chrome/Firefox webdriver

**Run:**
```bash
make e2e-test
```

**Run with visible browser (for debugging):**
```bash
SELENIUM_HEADLESS=false PYTHONPATH=modernProject python -m pytest modernProject/tests/e2e/ -v -s
```

**Prerequisites:**
```bash
pip install selenium
pip install webdriver-manager
```

Or install Chrome/Firefox webdriver manually.

**Example:**
```python
def test_welcome_page_loads(server_with_database, browser):
    base_url, temp_dir = server_with_database
    browser.get(f"{base_url}/test_base")

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "html"))
    )

    page_source = browser.page_source
    assert page_source is not None
    assert len(page_source) > 0
```

**Tests verify complete workflow:**
- Database generation (gwb_generator creates test database)
- Database file existence on filesystem
- Server loads generated database correctly
- Person count displays correctly (2 persons)
- John Doe data displays (first + last name)
- Jane Smith data displays (first + last name)
- Both persons appear in person list
- Link navigation works (clicking person links)

**Status:** Complete end-to-end testing from database generation through browser display. Will expand as display modules are completed.

## Running Tests

### Run All Tests
```bash
make test
```

### Run Specific Category
```bash
make unit-test
make integration-test
make functional-test
make e2e-test
```

### Run with Coverage
```bash
make coverage
```

Coverage report: `modernProject/htmlcov/index.html`

## Writing Tests

### Test File Naming
- Unit: `test_<module>.py` in `tests/unit/`
- Integration: `test_<feature>.py` in `tests/integration/`
- Functional: `test_<workflow>_workflow.py` in `tests/functional/`

### Test Function Naming
Use descriptive names that explain what is being tested:

**Good:**
```python
def test_name_search_finds_person_by_first_name():
    ...

def test_database_returns_error_for_invalid_magic():
    ...
```

**Bad:**
```python
def test_1():
    ...

def test_something():
    ...
```

### Shared Fixtures

Use fixtures from `conftest.py`:

```python
def test_with_temp_dir(temp_dir):
    # temp_dir is automatically created and cleaned up
    path = os.path.join(temp_dir, "test.txt")
    ...
```

## CI/CD Integration

**On Pull Request:**
- Unit tests (required)
- Integration tests (required)
- Coverage report (required)

**On Merge to Main:**
- All tests including functional

**Before Release:**
- Manual testing including e2e

## Test Data

### GWB Test Generator

Use `gwb_generator` to create minimal test databases:

```python
from tests.gwb_generator import create_minimal_gwb

gwb_path = create_minimal_gwb(temp_dir, "test_base")
```

Creates database with:
- 2 persons: John Doe (male), Jane Smith (female)
- 1 family: John + Jane
- All necessary index files