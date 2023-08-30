# profile_manager.py

from queue import Queue
import keyboard
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

from utils import (
    calculate_completion_time,
    format_message_ticket,
    print_multiline,
)

results_queue: Queue[dict[str, Union[int, str]]] = Queue()
results_profile: list[int] = []

ERRORS: list[str] = []
MESSAGE_TICKET: str = "N/A"
TIME_MESSAGE_TICKET: str = "N/A"


def get_valid_profile_selection(num_profiles) -> int:
    selected_profile_message_type = "INFO"
    while True:
        try:
            print_multiline("Select a profile (1-{}):".format(num_profiles),
                            message_type=selected_profile_message_type)
            selected_profile = int(input())
            if selected_profile < 1 or selected_profile > num_profiles:
                raise ValueError
            return selected_profile
        except ValueError:
            selected_profile_message_type = "ERROR"


def start_scraping_all_profiles(num_profiles, profiles_dir):
    for profile_index in range(num_profiles):
        process_profile(profile_index, profiles_dir)
        # process_results_data()
        continue


def getDriver(headless: bool) -> Optional[webdriver.Chrome]:
    """
    Create a Chrome driver instance with the specified options.

    Args:
        headless (bool): Flag indicating whether to run Chrome in headless mode or not.

    Returns:
        Optional[webdriver.Chrome]: The Chrome driver instance or None if an error occurred.
    """
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(
            "--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        if headless:
            chrome_options.add_argument("--headless")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error creating Chrome driver: {str(e)}")
        return None


def process_profile(profile_index: int, quit_event: bool = False) -> None:
    chrome_options: webdriver.ChromeOptions = webdriver.ChromeOptions()
    chrome_options.add_argument(
        "--user-data-dir=" + PROFILES_DIR + "/profile" + str(profile_index)
    )
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    if quit_event:
        chrome_options.add_argument("--headless")
    service: Service = Service(CHROMEDRIVER_PATH)
    driver: webdriver.Chrome = webdriver.Chrome(
        service=service, options=chrome_options)

    try:
        driver.get(str(URL))
        page_status: str = "OK" if driver.current_url == str(URL) else "Error"
        current_html: str = driver.page_source
        soup: BeautifulSoup = BeautifulSoup(current_html, "html.parser")
        div_challenge: bs4.Tag = soup.find("div", id="divChallenge")
        if (
            div_challenge and quit_event
        ):  # IMG captcha-code INPUT CaptchaCode AUDIOaudioPlayer
            # https://cariverplate.queue-it.net/?c=cariverplate&e=rivervsestgeneral&cid=es-CL&scv=%7B%22sessionId%22%3A%222e7dd331-6451-495e-b0f8-737abb1fe960%22%2C%22timestamp%22%3A%222023-07-13T20%3A16%3A20.2268167Z%22%2C%22checksum%22%3A%22wxpyupC29xQUwrz8oaNiJF%2F%2Bh3%2BJdXxv%2FmaB%2BBEdk7s%3D%22%2C%22sourceIp%22%3A%22186.158.255.59%22%2C%22challengeType%22%3A%22botdetect%22%2C%22version%22%3A6%2C%22customerId%22%3A%22cariverplate%22%2C%22waitingRoomId%22%3A%22rivervsestgeneral%22%7D
            quit_event = False
            print_multiline("Challenge found", Fore.RED)
            process_profile(profile_index, False)

        if div_challenge:
            try:
                print_multiline(
                    "Challenge found, please solve it and press enter to continue:",
                    Fore.RED,
                )
                keyboard.wait("enter")
            except KeyboardInterrupt:
                print_multiline("Exiting...", Fore.RED)
                sys.exit(0)

        progress_div: bs4.Tag = soup.find("div", id="MainPart_divProgressbar")
        link_to_queue_ticket: bs4.Tag = soup.find(
            "span", id="hlLinkToQueueTicket2")
        last_update_time: bs4.Tag = soup.find(
            "span", id="MainPart_lbLastUpdateTimeText"
        )
        which_is_in: bs4.Tag = soup.find("span", id="MainPart_lbWhichIsIn")
        message_on_queue_ticket: bs4.Tag = soup.find(
            "p", id="MainPart_pMessageOnQueueTicket"
        )
        users_in_line_ahead_of_you: bs4.Tag = soup.find(
            "span", id="MainPart_lbUsersInLineAheadOfYou"
        )

        message_on_queue_ticket_time: bs4.Tag = soup.find(
            "span", id="MainPart_h2MessageOnQueueTicketTimeText"
        )
        link_to_queue_ticket_text: str = (
            link_to_queue_ticket.text if link_to_queue_ticket else "N/A"
        )
        progress_now: Union[str, None] = None
        if progress_div:
            if isinstance(progress_div, bs4.Tag):
                progress_now = progress_div.get("aria-valuenow")
        last_update_time_text: str = (
            last_update_time.text if last_update_time else "N/A"
        )
        which_is_in_text: str = which_is_in.text if which_is_in else "N/A"
        message_on_queue_ticket_text: str = (
            message_on_queue_ticket.text if message_on_queue_ticket else "N/A"
        )
        message_on_queue_ticket_time_text: str = (
            message_on_queue_ticket_time.text if message_on_queue_ticket_time else "N/A"
        )

        if progress_now:
            estimated_time: str = calculate_completion_time(
                START_TIME, progress_now)
        else:
            estimated_time = "N/A"

        users_in_line_ahead_of_you_text: str = (
            users_in_line_ahead_of_you.text if users_in_line_ahead_of_you else "N/A"
        )

        result: dict[str, Union[int, str]] = {
            "Profile": profile_index + 1,
            "Status": page_status,
            "UID": link_to_queue_ticket_text,
            "LU": last_update_time_text,
            "Progress": progress_now if progress_now else "N/A",
            "WhichIsIn": which_is_in_text,
            "EstTime": estimated_time,
            "Users": users_in_line_ahead_of_you_text,
        }

        if (profile_index + 1) in results_profile:
            existing_result: Union[dict[str, Union[int, str]], None] = next(
                (
                    result
                    for result in results_queue.queue
                    if result["Profile"] == profile_index + 1
                ),
                None,
            )
            if existing_result:
                if existing_result["UID"] == link_to_queue_ticket_text:
                    existing_result.update(result)
                else:
                    results_queue.put(result)
                    results_profile.append(profile_index + 1)
        else:
            results_queue.put(result)
            results_profile.append(profile_index + 1)

        global MESSAGE_TICKET, TIME_MESSAGE_TICKET
        if message_on_queue_ticket_text != "N/A":
            MESSAGE_TICKET = message_on_queue_ticket_text
        if message_on_queue_ticket_time_text != "N/A":
            TIME_MESSAGE_TICKET = message_on_queue_ticket_time_text
        quit_event_text: Union[str, None] = None

        while quit_event is False:
            try:
                quit_event_text = input(
                    "Press enter to quit profile " +
                    str(profile_index + 1) + " "
                )
                if quit_event_text == "":
                    quit_event = True
                    break
                else:
                    print("Invalid input")
            except KeyboardInterrupt:
                quit_event = True
                break

    except Exception as e:
        ERRORS.append(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error while processing profile {profile_index}: {str(e)}"
        )
    finally:
        if quit_event:
            driver.quit()
