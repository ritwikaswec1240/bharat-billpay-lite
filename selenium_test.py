"""
Optional UI smoke test using Selenium, to demonstrate automation-testing
familiarity from the JD (Selenium / TestNG / Postman / REST Assured bullet).

Not run in CI by default because it needs a real browser + driver. Run it
locally against a running server:

    uvicorn app.main:app &
    python selenium_test.py
"""
from selenium import webdriver
from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:8000"


def test_lookup_page_loads():
    driver = webdriver.Chrome()
    try:
        driver.get(BASE_URL)
        assert "Bharat BillPay Lite" in driver.title
        heading = driver.find_element(By.TAG_NAME, "h1")
        assert "Bill Lookup" in heading.text
        print("Selenium smoke test passed: lookup page renders correctly.")
    finally:
        driver.quit()


if __name__ == "__main__":
    test_lookup_page_loads()
