from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from src.error_handler import add_error, get_errors


def create_chrome_driver(
    headless: Optional[bool] = False, user_data_dir: Optional[str] = None
) -> Optional[webdriver.Chrome]:
    """
    The `create_chrome_driver` function creates a Chrome driver instance with specified options and
    returns it, or returns None if an error occurred.
    @param {Optional[bool]} [headless=False] - The `headless` parameter is a boolean flag indicating
    whether to run Chrome in headless mode or not. When set to `True`, Chrome will run without a
    graphical user interface, which can be useful for running automated tests or scraping data without
    displaying the browser window. When set to `False`
    @param {Optional[str]} user_data_dir - The `user_data_dir` parameter is an optional parameter that
    specifies the path to the user data directory. If provided, Chrome will use this directory to store
    user profile data. This can include information such as bookmarks, history, cookies, and extensions.
    @returns The `create_chrome_driver` function returns an instance of `webdriver.Chrome` if the Chrome
    driver is successfully created with the specified options. If an error occurs during the creation of
    the Chrome driver, the function returns `None`.
    """
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        if user_data_dir:
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

        if headless:
            chrome_options.add_argument("--headless")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    except Exception as e:
        add_error("create_chrome_driver", str(e))
        return None


if __name__ == "__main__":
    driver = create_chrome_driver()
    if driver:
        try:
            driver.get("https://www.google.com")
            driver.quit()
            print(get_errors())
        except Exception as e:
            add_error("main", str(e))
    else:
        print("Chrome driver creation failed.")
        print(get_errors())
