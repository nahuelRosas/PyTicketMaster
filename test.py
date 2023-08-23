import sys
import time
import configparser
from datetime import datetime
from typing import Union
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
from colorama import Fore, Style
import re
import keyboard
import shutil
import os

config = configparser.ConfigParser()
config.read("config.ini")

PROFILES_DIR: str = config.get("Main", "profiles_dir")
CHROMEDRIVER_PATH: str = config.get("Main", "chromedriver_path")
NUM_PROFILES: int = config.getint("Main", "num_profiles")
URL: str = config.get("Main", "URL")
WAIT_TIME: int = config.getint("Main", "waitTime")
START_TIME: str = config.get("Main", "startTime")


MESSAGE_TICKET: str = "N/A"
TIME_MESSAGE_TICKET: str = "N/A"
ERRORS: list[str] = []

MESSAGE_TYPES: dict[str, dict[str, Union[str, int]]] = {
    "INFO": {"color": Fore.GREEN, "prefix": "[INFO]"},
    "WARNING": {"color": Fore.YELLOW, "prefix": "[WARNING]"},
    "ERROR": {"color": Fore.RED, "prefix": "[ERROR]"},
}

results_queue: Queue[dict[str, Union[int, str]]] = Queue()
results_profile: list[int] = []


def process_profile(profile_index: int, quit_event: bool = False) -> None:
    chrome_options: webdriver.ChromeOptions = webdriver.ChromeOptions()
    chrome_options.add_argument(
        "--user-data-dir=" + PROFILES_DIR + "/profile" + str(profile_index)
    )
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
    if quit_event:
        chrome_options.add_argument("--headless")
    service: Service = Service(CHROMEDRIVER_PATH)
    driver: webdriver.Chrome = webdriver.Chrome(service=service, options=chrome_options)

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
        link_to_queue_ticket: bs4.Tag = soup.find("span", id="hlLinkToQueueTicket2")
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
            estimated_time: str = calculate_completion_time(START_TIME, progress_now)
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
                    "Press enter to quit profile " + str(profile_index + 1) + " "
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


def calculate_completion_time(start_time: str, progress_now: Union[str, None]) -> str:
    try:
        current_time: datetime = datetime.now().time()
        start_time: datetime = datetime.combine(
            datetime.today(), datetime.strptime(start_time, "%H:%M:%S").time()
        )
        elapsed_time: datetime = (
            datetime.combine(datetime.today(), current_time) - start_time
        )

        if progress_now is None or progress_now == "N/A":
            return "N/A"

        remaining_progress: float = 100 - float(progress_now)

        if remaining_progress == 0:
            return "Already at 100% progress"

        completion_time: datetime = elapsed_time / (float(progress_now) / 100)
        completion_time_hours: int = int(completion_time.total_seconds() // 3600)
        completion_time_minutes: int = int(
            (completion_time.total_seconds() % 3600) // 60
        )
        formatted_time: str = (
            f"{completion_time_hours:02d}:{completion_time_minutes:02d}"
        )
        return formatted_time
    except Exception as e:
        ERRORS.append(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error while calculating completion time: {str(e)}"
        )
        return "N/A"


def format_message_ticket(message_ticket: str) -> str:
    message_ticket = re.sub(r"\*\*(.*?)\*\*", r"\033[1m\1\033[0m", message_ticket)
    message_ticket = message_ticket.replace("\\", "\n")
    message_ticket = re.sub(r"\n{3,}", "\n\n", message_ticket)
    return message_ticket


def process_results_data() -> None:
    results_list: list[dict[str, Union[int, str]]] = list(results_queue.queue)
    df: pd.DataFrame = pd.DataFrame(results_list)

    os.system("cls" if os.name == "nt" else "clear")
    print_title()

    if MESSAGE_TICKET != "N/A":
        MESSAGE_TICKET_WITHFORMAT: str = format_message_ticket(MESSAGE_TICKET)
        print_multiline(f"LAST NEWS {TIME_MESSAGE_TICKET}\n", Fore.LIGHTWHITE_EX)
        print_multiline(f"{MESSAGE_TICKET_WITHFORMAT}\n", Fore.LIGHTGREEN_EX, "center")
        print_multiline(f"Results:\n", Fore.LIGHTWHITE_EX)

    if "Users" in df.columns:
        columns_with_data: pd.Index = df.columns[df.count() > 0]
        df_subset: pd.DataFrame = df[columns_with_data]
        df_order: pd.DataFrame = df_subset.sort_values(by=["Users"], ascending=False)
        print_multiline(
            df_order.to_markdown(numalign="center", stralign="center", index=False),
            Fore.LIGHTMAGENTA_EX,
            "center",
        )
    else:
        print_multiline(
            df.to_markdown(numalign="center", stralign="center", index=False),
            Fore.LIGHTMAGENTA_EX,
            "center",
        )

    if len(ERRORS) > 0:
        print_multiline("Errors:", Fore.LIGHTRED_EX)
        print_multiline("\n".join(ERRORS), Fore.LIGHTRED_EX, "center")


def print_title() -> None:
    title: str = r"""
 _____                _               _       ______                 _              _    
|_   _|              | |             ( )      | ___ \               (_)            | |  
  | |    __ _  _   _ | |  ___   _ __ |/  ___  | |_/ / _ __   ___     _   ___   ___ | |_ 
  | |   / _` || | | || | / _ \ | '__|   / __| |  __/ | '__| / _ \   | | / _ \ / __|| __|
  | |  | (_| || |_| || || (_) || |      \__ \ | |    | |   | (_) |  | ||  __/| (__ | |_ 
  \_/   \__,_| \__, ||_| \___/ |_|      |___/ \_|    |_|    \___/   | | \___| \___| \__|
                __/ |                                              _/ |                 
               |___/                                              |__/                  
               
            By: Nahuel Rosas - Github: https://github.com/nahuelRosas          
    """
    print_multiline(title, Fore.LIGHTCYAN_EX, "center")


def print_multiline(
    text: str,
    color: str = Fore.RESET,
    alignment: str = "left",
    fill_char: str = " ",
    show_time: bool = False,
    message_type: Union[str, None] = None,
) -> None:
    console_width: int = shutil.get_terminal_size((80, 20)).columns
    lines: list[str] = text.splitlines()
    max_line_length: int = max(len(line) for line in lines) if lines else 0
    padding: int = 0

    if alignment == "center":
        padding = (console_width - max_line_length) // 2
    elif alignment == "left":
        padding = 0
    elif alignment == "right":
        padding = console_width - max_line_length
    elif alignment == "fill":
        padding = 0
        if len(lines) > 1:
            max_line_length = console_width

    message: str = text

    if show_time:
        current_time: str = datetime.now().strftime("[%H:%M:%S]")
        message = f"{current_time} - {message}"

    if message_type is not None and message_type in MESSAGE_TYPES:
        message_data: dict[str, Union[str, int]] = MESSAGE_TYPES[message_type]
        color = message_data["color"]
        prefix = message_data["prefix"]
        message = f"{prefix} - {message}"
    elif message_type is not None:
        print(f"Invalid message type: {message_type}")
        return

    if lines:
        if len(lines) > 1:
            for line in lines:
                if alignment == "fill":
                    line = line.ljust(max_line_length, fill_char)
                print(" " * padding + color + line + Style.RESET_ALL)
        else:
            print(" " * padding + color + message + Style.RESET_ALL)


def initialize_config() -> tuple:
    config = configparser.ConfigParser()
    config.read("config.ini")

    profiles_dir = config.get("Main", "profiles_dir")
    chromedriver_path = config.get("Main", "chromedriver_path")
    num_profiles = config.getint("Main", "num_profiles")
    url = config.get("Main", "URL")
    wait_time = config.getint("Main", "waitTime")
    start_time = config.get("Main", "startTime")

    return profiles_dir, chromedriver_path, num_profiles, url, wait_time, start_time


def main() -> None:
    (
        profiles_dir,
        chromedriver_path,
        num_profiles,
        url,
        wait_time,
        start_time,
    ) = initialize_config()

    os.system("cls" if os.name == "nt" else "clear")
    print_title()

    while True:
        selected_profile_text: Union[str, None] = None
        selected_profile: Union[int, None] = None

        while selected_profile_text is None:
            selected_profile_text = input(
                "Do you want to select a profile? (y/n): "
            ).lower()

            if selected_profile_text == "y":
                try:
                    selected_profile = int(
                        input("Select a profile (1-{}): ".format(num_profiles))
                    )

                    if selected_profile < 1 or selected_profile > num_profiles:
                        raise ValueError
                except ValueError:
                    print("Error. Select a profile (1-{}).".format(num_profiles))
                    selected_profile = None
                    continue

                process_profile(selected_profile - 1)
                process_results_data()

                input("Press enter to continue...")

            elif selected_profile_text == "n":
                automatic_scraping: Union[str, None] = None

                while automatic_scraping is None:
                    print_multiline("Starting all profiles...", Fore.LIGHTWHITE_EX)
                    print_multiline(
                        "Selecting the automatic option causes the system to start in headless mode and assumes that Queue has no human verification system."
                    )
                    print(
                        "Recommendation: start the first interval in manual mode and the subsequent ones automatically"
                    )

                    automatic_scraping = input(
                        "Do you want to start automatic scraping? (y/n): "
                    ).lower()

                    if automatic_scraping == "y":
                        executor = ThreadPoolExecutor(max_workers=1)
                        futures = []

                        for i in range(num_profiles):
                            process_profile(i, True)
                            process_results_data()
                        process_results_data()

                        break

                    elif automatic_scraping == "n":
                        for i in range(num_profiles):
                            process_profile(i)
                            process_results_data()

                        breakFunction = input(
                            "Press enter to restart scraping, or press R to restart from init, or Q to Exit..."
                        )

                        if breakFunction == "":
                            continue
                        elif breakFunction.lower() == "r":
                            break
                        elif breakFunction.lower() == "q":
                            sys.exit()
                        else:
                            raise ValueError
                    else:
                        automatic_scraping = None
                        print("Error. Do you want to start automatic scraping? (y/n):")

            else:
                print("Error. Select a profile (1-{}).".format(num_profiles))
                selected_profile = None
                continue


if __name__ == "__main__":
    main()
