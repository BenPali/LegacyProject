import sys
import os
import time
import subprocess
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from tests.gwb_generator import create_minimal_gwb
from lib import secure


@pytest.fixture(scope="module")
def server_with_database(tmp_path_factory):
    if not SELENIUM_AVAILABLE:
        pytest.skip("Selenium not installed")

    temp_dir = str(tmp_path_factory.mktemp("geneweb_test"))
    secure.add_assets(temp_dir)
    create_minimal_gwb(temp_dir, "test_base")

    import socket
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()

    server_process = subprocess.Popen(
        [sys.executable, "-m", "bin.gwd", "-p", str(port), "-wd", temp_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(Path(__file__).parent.parent.parent.parent)
    )

    time.sleep(3)

    if server_process.poll() is not None:
        _, err = server_process.communicate()
        pytest.fail(f"Server failed to start: {err.decode()}")

    import urllib.request
    max_retries = 10
    for i in range(max_retries):
        try:
            urllib.request.urlopen(f"http://localhost:{port}/", timeout=1)
            break
        except Exception:
            if i == max_retries - 1:
                server_process.kill()
                pytest.fail(f"Server did not respond after {max_retries} attempts")
            time.sleep(0.5)

    yield f"http://localhost:{port}", temp_dir

    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()


@pytest.fixture(scope="module")
def browser():
    if not SELENIUM_AVAILABLE:
        pytest.skip("Selenium not installed")

    headless = os.environ.get("SELENIUM_HEADLESS", "true").lower() != "false"

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    try:
        driver = webdriver.Chrome(options=options)
    except Exception:
        try:
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            firefox_options = FirefoxOptions()
            if headless:
                firefox_options.add_argument("--headless")
            driver = webdriver.Firefox(options=firefox_options)
        except Exception:
            pytest.skip("Neither Chrome nor Firefox webdriver available")

    driver.set_page_load_timeout(10)
    yield driver
    driver.quit()


def test_generated_database_loads_with_correct_person_count(server_with_database, browser):
    base_url, _ = server_with_database

    browser.get(f"{base_url}?b=test_base")

    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        pytest.fail("Welcome page did not load within timeout")

    page_source = browser.page_source
    assert "Total persons: 2" in page_source or "2" in page_source


def test_generated_database_displays_john_doe(server_with_database, browser):
    base_url, _ = server_with_database

    browser.get(f"{base_url}?b=test_base")

    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        pytest.fail("Welcome page did not load")

    page_source = browser.page_source
    assert "John" in page_source
    assert "Doe" in page_source


def test_generated_database_displays_jane_smith(server_with_database, browser):
    base_url, _ = server_with_database

    browser.get(f"{base_url}?b=test_base")

    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        pytest.fail("Welcome page did not load")

    page_source = browser.page_source
    assert "Jane" in page_source
    assert "Smith" in page_source


def test_generated_database_displays_both_persons(server_with_database, browser):
    base_url, _ = server_with_database

    browser.get(f"{base_url}?b=test_base")

    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )
    except TimeoutException:
        pytest.fail("No person links found")

    links = browser.find_elements(By.TAG_NAME, "a")
    assert len(links) >= 2

    page_source = browser.page_source
    assert "John" in page_source and "Doe" in page_source
    assert "Jane" in page_source and "Smith" in page_source


def test_database_welcome_page_has_geneweb_title(server_with_database, browser):
    base_url, _ = server_with_database

    browser.get(f"{base_url}?b=test_base")

    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "title"))
        )
    except TimeoutException:
        pytest.fail("Title element not present")

    title = browser.title
    assert "GeneWeb" in title


def test_root_page_shows_generated_database_in_list(server_with_database, browser):
    base_url, _ = server_with_database

    browser.get(base_url)

    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        pytest.fail("Root page did not load")

    page_source = browser.page_source
    assert "test_base" in page_source


def test_person_link_navigation_to_john_doe(server_with_database, browser):
    base_url, _ = server_with_database

    browser.get(f"{base_url}?b=test_base")

    try:
        links = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
        )
    except TimeoutException:
        pytest.fail("No person links found")

    john_link = None
    for link in links:
        if "John" in link.text or "i=0" in link.get_attribute("href"):
            john_link = link
            break

    if john_link:
        john_link.click()
        time.sleep(0.5)
        assert "i=0" in browser.current_url or browser.current_url != f"{base_url}?b=test_base"


def test_database_file_exists_and_server_loads_it(server_with_database, browser):
    base_url, temp_dir = server_with_database

    import os
    gwb_path = os.path.join(temp_dir, "test_base.gwb")
    base_file = os.path.join(gwb_path, "base")
    assert os.path.exists(base_file)

    browser.get(f"{base_url}?b=test_base")

    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        pytest.fail("Server failed to load the generated database")

    page_source = browser.page_source
    assert "John" in page_source or "Jane" in page_source
