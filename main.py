import threading
import time
import os
import configparser
from datetime import datetime
from typing import Union
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style
import re
import keyboard

config = configparser.ConfigParser()
config.read("config.ini")

PROFILES_DIR = config.get("Main", "profiles_dir")
CHROMEDRIVER_PATH = config.get("Main", "chromedriver_path")
NUM_PROFILES = config.getint("Main", "num_profiles")
URL = config.get("Main", "URL")
WAIT_TIME = config.getint("Main", "waitTime")
START_TIME = config.get("Main", "startTime")

RESULTS_LOCK = threading.Lock()
RESULTS_DATA = []
MESSAGE_TICKET = "N/A"
TIME_MESSAGE_TICKET = "N/A"
ERRORS = []

MESSAGE_TYPES = {
    "INFO": {"color": Fore.GREEN, "prefix": "[INFO]"},
    "WARNING": {"color": Fore.YELLOW, "prefix": "[WARNING]"},
    "ERROR": {"color": Fore.RED, "prefix": "[ERROR]"},
}


def process_profile(profile_index, quit_event=False):
    chrome_options = webdriver.ChromeOptions()
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
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(str(URL))
        page_status = "OK" if driver.current_url == str(URL) else "Error"
        current_html = driver.page_source
        soup = BeautifulSoup(current_html, "html.parser")

        divChallenge = soup.find("div", id="MainPart_divChallenge")

        if divChallenge:
            print("Challenge found")

        progress_div = soup.find("div", id="MainPart_divProgressbar")
        link_to_queue_ticket = soup.find("span", id="hlLinkToQueueTicket2")
        last_update_time = soup.find("span", id="MainPart_lbLastUpdateTimeText")
        which_is_in = soup.find("span", id="MainPart_lbWhichIsIn")
        message_on_queue_ticket = soup.find("p", id="MainPart_pMessageOnQueueTicket")
        users_in_line_ahead_of_you = soup.find(
            "span", id="MainPart_lbUsersInLineAheadOfYou"
        )

        message_on_queue_ticket_time = soup.find(
            "span", id="MainPart_h2MessageOnQueueTicketTimeText"
        )
        link_to_queue_ticket_text = (
            link_to_queue_ticket.text if link_to_queue_ticket else "N/A"
        )
        progress_now = "N/A"
        if progress_div:
            if isinstance(progress_div, bs4.Tag):
                progress_now = progress_div.get("aria-valuenow")

        last_update_time_text = last_update_time.text if last_update_time else "N/A"
        which_is_in_text = which_is_in.text if which_is_in else "N/A"
        message_on_queue_ticket_text = (
            message_on_queue_ticket.text if message_on_queue_ticket else "N/A"
        )
        message_on_queue_ticket_time_text = (
            message_on_queue_ticket_time.text if message_on_queue_ticket_time else "N/A"
        )
        estimated_time = calculate_completion_time(START_TIME, progress_now)
        users_in_line_ahead_of_you_text = (
            users_in_line_ahead_of_you.text if users_in_line_ahead_of_you else "N/A"
        )

        result = {
            "Profile": profile_index + 1,
            "Status": page_status,
            "UID": link_to_queue_ticket_text,
            "LU": last_update_time_text,
            "Progress": progress_now,
            "WhichIsIn": which_is_in_text,
            "EstTime": estimated_time,
            "Users": users_in_line_ahead_of_you_text,
        }

        with RESULTS_LOCK:
            while len(RESULTS_DATA) <= profile_index:
                RESULTS_DATA.append(None)
            RESULTS_DATA[profile_index] = result

        global MESSAGE_TICKET, TIME_MESSAGE_TICKET
        if message_on_queue_ticket_text != "N/A":
            MESSAGE_TICKET = message_on_queue_ticket_text
        if message_on_queue_ticket_time_text != "N/A":
            TIME_MESSAGE_TICKET = message_on_queue_ticket_time_text
        quit_event_text = None

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


def calculate_completion_time(start_time, progress_now):
    try:
        current_time = datetime.now().time()
        start_time = datetime.combine(
            datetime.today(), datetime.strptime(start_time, "%H:%M:%S").time()
        )
        elapsed_time = datetime.combine(datetime.today(), current_time) - start_time

        if progress_now is None or progress_now == "N/A":
            return "N/A"

        remaining_progress = 100 - float(progress_now)

        if remaining_progress == 0:
            return "Already at 100% progress"

        completion_time = elapsed_time / (float(progress_now) / 100)
        completion_time_hours = int(completion_time.total_seconds() // 3600)
        completion_time_minutes = int((completion_time.total_seconds() % 3600) // 60)
        formatted_time = f"{completion_time_hours:02d}:{completion_time_minutes:02d}"
        return formatted_time
    except Exception as e:
        ERRORS.append(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error while calculating completion time: {str(e)}"
        )
        return "N/A"


def print_title():
    title = r"""
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
):
    console_width = os.get_terminal_size().columns
    lines = text.splitlines()
    max_line_length = max(len(line) for line in lines)
    padding = 0

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

    message = text

    if show_time:
        current_time = datetime.now().strftime("[%H:%M:%S]")
        message = f"{current_time} - {message}"

    if message_type is not None and message_type in MESSAGE_TYPES:
        message_data = MESSAGE_TYPES[message_type]
        color = message_data["color"]
        prefix = message_data["prefix"]
        message = f"{prefix} - {message}"
    elif message_type is not None:
        print(f"Invalid message type: {message_type}")
        return

    if len(lines) > 1:
        for line in lines:
            if alignment == "fill":
                line = line.ljust(max_line_length, fill_char)
            print(" " * padding + color + line + Style.RESET_ALL)
    else:
        print(" " * padding + color + message + Style.RESET_ALL)


def format_message_ticket(message_ticket: str) -> str:
    message_ticket = re.sub(r"\*\*(.*?)\*\*", r"\033[1m\1\033[0m", message_ticket)
    message_ticket = message_ticket.replace("\\", "\n")
    message_ticket = re.sub(r"\n{3,}", "\n\n", message_ticket)
    return message_ticket


def process_results_data():
    with RESULTS_LOCK:
        df = pd.DataFrame(RESULTS_DATA)

    os.system("cls" if os.name == "nt" else "clear")
    print_title()

    if MESSAGE_TICKET != "N/A":
        MESSAGE_TICKET_WITHFORMAT = format_message_ticket(MESSAGE_TICKET)
        print_multiline(f"LAST NEWS {TIME_MESSAGE_TICKET}\n", Fore.LIGHTWHITE_EX)
        print_multiline(f"{MESSAGE_TICKET_WITHFORMAT}\n", Fore.LIGHTGREEN_EX, "center")
        print_multiline(f"Results:\n", Fore.LIGHTWHITE_EX)

    columns_with_data = df.columns[df.count() > 0]
    df_subset = df[columns_with_data]
    df_order = df_subset.sort_values(by=["Users"], ascending=False)
    print_multiline(
        df_order.to_markdown(numalign="center", stralign="center", index=False),
        Fore.LIGHTMAGENTA_EX,
        "center",
    )

    if len(ERRORS) > 0:
        print_multiline("Errors:", Fore.LIGHTRED_EX)
        print_multiline("\n".join(ERRORS), Fore.LIGHTRED_EX, "center")


def get_input(prompt):
    if sys.stdin.isatty():
        return input(prompt)
    else:
        return sys.stdin.readline().rstrip("\n")


def main():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print_title()
        selected_profile_text = None
        selected_profile = None

        while selected_profile_text is None:
            selected_profile_text = input(
                "Do you want to select a profile? (y/n): "
            ).lower()

            if selected_profile_text == "y":
                try:
                    selected_profile = int(
                        input("Select a profile (1-{}): ".format(NUM_PROFILES))
                    )

                    if selected_profile < 1 or selected_profile > NUM_PROFILES:
                        raise ValueError
                except ValueError:
                    print("Error. Select a profile (1-{}).".format(NUM_PROFILES))
                    selected_profile = None
                    continue

                process_profile(selected_profile - 1)
                process_results_data()

                breakFunction = input("Press enter to continue...")

                if breakFunction == "":
                    break

            elif selected_profile_text == "n":
                while True:
                    print_multiline("Starting all profiles...", Fore.LIGHTWHITE_EX)
                    print_multiline(
                        "Selecting the automatic option causes the system to start in headless mode and assumes that Queue has no human verification system."
                    )
                    print(
                        "Recommendation: start the first interval in manual mode and the subsequent ones automatically"
                    )

                    try:
                        automatic_scraping = input(
                            "Do you want to start automatic scraping? (y/n): "
                        ).lower()

                        if automatic_scraping == "y":
                            for i in range(NUM_PROFILES):
                                process_profile(i, True)
                                process_results_data()

                            break

                        elif automatic_scraping == "n":
                            for i in range(NUM_PROFILES):
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
                            raise ValueError

                    except ValueError:
                        print("Error. Do you want to start automatic scraping? (y/n):")

            else:
                print("Error. Select a profile (1-{}).".format(NUM_PROFILES))
                selected_profile = None
                continue


if __name__ == "__main__":
    main()
