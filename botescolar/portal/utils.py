from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
)


# ==========================================================
# WAIT HELPERS
# ==========================================================

def wait_present(
    driver: WebDriver,
    xpath: str,
    timeout: int = 30,
) -> WebElement:

    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )


def wait_clickable(
    driver: WebDriver,
    xpath: str,
    timeout: int = 30,
) -> WebElement:

    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )


# ==========================================================
# FIND HELPERS
# ==========================================================

def safe_find(
    driver: WebDriver,
    xpath: str,
) -> Optional[WebElement]:

    try:
        return driver.find_element(By.XPATH, xpath)

    except NoSuchElementException:
        return None


def safe_find_all(
    parent: WebElement,
    xpath: str,
) -> list[WebElement]:

    try:
        return parent.find_elements(By.XPATH, xpath)

    except Exception:
        return []


# ==========================================================
# CLICK HELPERS
# ==========================================================

def js_click(
    driver: WebDriver,
    element: WebElement,
):

    driver.execute_script(
        "arguments[0].click();",
        element,
    )


def wait_and_click(
    driver: WebDriver,
    xpath: str,
    timeout: int = 30,
):

    element = wait_clickable(
        driver,
        xpath,
        timeout,
    )

    js_click(driver, element)

    return element


# ==========================================================
# PAGE HELPERS
# ==========================================================

def inject_focus(
    driver: WebDriver,
):

    driver.execute_script(
        """
        Object.defineProperty(document, 'hidden',
            {value:false,writable:true});

        Object.defineProperty(document, 'visibilityState',
            {value:'visible',writable:true});

        document.dispatchEvent(
            new Event('visibilitychange')
        );

        window.dispatchEvent(
            new Event('focus')
        );
        """
    )


# ==========================================================
# DOWNLOAD HELPERS
# ==========================================================

def wait_for_download(
    directory: Path,
    previous_files: set[str],
    timeout: int = 60,
) -> Optional[Path]:

    start = time.time()

    while time.time() - start < timeout:

        current = {
            f.name
            for f in directory.iterdir()
        }

        new_files = current - previous_files

        for filename in new_files:

            if filename.endswith(".crdownload"):
                continue

            if filename.endswith(".tmp"):
                continue

            return directory / filename

        time.sleep(0.25)

    return None


# ==========================================================
# DRIVER HEALTH
# ==========================================================

def driver_alive(
    driver: WebDriver,
) -> bool:

    try:

        _ = driver.current_url

        return True

    except Exception:

        return False