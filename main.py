import sys
import os
import base64
import shutil
import configparser
from datetime import datetime
from typing import Union, Dict,  List, Optional
import speech_recognition as sr
from speech_recognition import AudioData
from colorama import Fore, Style
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, ResultSet
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class Application:
    def __init__(self, config_path: str) -> None:
        self.title = r"""
        ███████╗ ██╗   ██╗████████╗██╗ ██████╗██╗  ██╗███████╗████████╗███╗   ███╗ █████╗ ███████╗████████╗███████╗██████╗ 
        ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║██╔════╝██║ ██╔╝██╔════╝╚══██╔══╝████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
        ███████╔╝ ╚████╔╝    ██║   ██║██║     █████╔╝ █████╗     ██║   ██╔████╔██║███████║███████╗   ██║   █████╗  ██████╔╝
        ██╔═══╝   ╚██╔╝     ██║   ██║██║     ██╔═██╗ ██╔══╝     ██║   ██║╚██╔╝██║██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗
        ██║        ██║      ██║   ██║╚██████╗██║  ██╗███████╗   ██║   ██║ ╚═╝ ██║██║  ██║███████║   ██║   ███████╗██║  ██║
        ╚═╝        ╚═╝      ╚═╝   ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
                                                                                                                        
                    By: Nahuel Rosas - Github: https://github.com/nahuelRosas        
                    Twitter: https://twitter.com/queue_express              
        """
        self.config_path: str = config_path
        self.errors: list[tuple[str, str]] = []
        self.data = None
        self.new_data: tuple[str | int, int, str | int] | None = None
        self.message_type: dict[str, dict[str, str]] = {
            "INFO": {"color": Fore.GREEN, "prefix": "[INFO]"},
            "WARNING": {"color": Fore.YELLOW, "prefix": "[WARNING]"},
            "ERROR": {"color": Fore.RED, "prefix": "[ERROR]"},
            "SUCCESS": {"color": Fore.GREEN, "prefix": "[SUCCESS]"},
            "FAILURE": {"color": Fore.RED, "prefix": "[FAILURE]"},
            "DEBUG": {"color": Fore.CYAN, "prefix": "[DEBUG]"},
            "CRITICAL": {"color": Fore.RED, "prefix": "[CRITICAL]"},
            "EXCEPTION": {"color": Fore.RED, "prefix": "[EXCEPTION]"},
        }
        self.color: str = Fore.LIGHTCYAN_EX
        self.alignment = "center"
        self.audio_file_path: str = './audio/audio.wav'
        self.driver: Optional[WebDriver] = None
        self.captcha_input_id: str = 'solution'
        self.captcha_button_xpath: str = '//*[@id="challenge-container"]/button'
        self.info = {}

    def start(self) -> None:
        self.display_title()
        self.load_config()
        self.prepare_environment()
        self.perform_web_scraping()
        if self.errors:
            self.display_errors()

    def display_title(self) -> None:
        os.system(command="cls" if os.name == "nt" else "clear")
        self.display(text=self.title, color=self.color,
                     alignment=self.alignment)

    def load_config(self) -> None:
        self.data: tuple[str, int, str] | None = self.load_configuration(
            config_path=self.config_path)

    def load_configuration(self, config_path: str) -> tuple[str, int, str] | None:
        try:
            config_parser = configparser.ConfigParser()
            config_parser.read(filenames=config_path)
            return (
                config_parser.get(section="Main", option="profiles_directory"),
                config_parser.getint(
                    section="Main", option="number_of_profiles"),
                config_parser.get(section="Main", option="base_url")
            )
        except configparser.Error as error:
            error_message = str(object=error)
            self.handle_error(origin_file="load_configuration",
                              error_message=error_message)
            return None

    def prepare_environment(self) -> None:
        if self.data:
            self.new_data: tuple[str | int, int, str |
                                 int] | None = self.setup_environment()

    def handle_error(self, origin_file, error_message) -> None:
        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error: tuple[str, str] = (
            timestamp, f"Error while processing {origin_file}: {error_message}")
        self.errors.append(error)

    def display_errors(self) -> None:
        for error in self.errors:
            self.display(text=error[1], message_type="ERROR")

    def display(
        self,
        text: str,
        color: str = Fore.RESET,
        alignment: str = "left",
        fill_char: str = " ",
        show_time: bool = False,
        message_type: Union[str, None] = None,
    ) -> None:

        try:
            console_width: int = shutil.get_terminal_size(
                fallback=(80, 20)).columns
            lines: list[str] = text.splitlines()
            max_line_length = max(len(line) for line in lines) if lines else 0
            padding = 0

            if alignment == "center":
                padding: int = (console_width - max_line_length) // 2
            elif alignment == "left":
                padding = 0
            elif alignment == "right":
                padding = console_width - max_line_length
            elif alignment == "fill":
                padding = 0
                if len(lines) > 1:
                    max_line_length: int = console_width

            message = text

            if show_time:
                current_time: str = datetime.now().strftime("[%H:%M:%S]")
                message = f"{current_time} - {message}"

            if message_type is not None and message_type in self.message_type:
                message_data: dict[str, str] = self.message_type[message_type]
                color = message_data["color"]
                prefix: str = message_data["prefix"]
                message: str = f"{prefix} - {message}"
            elif message_type is not None:
                print(f"Invalid message type: {message_type}")
                return

            if lines:
                if len(lines) > 1:
                    for line in lines:
                        if alignment == "fill":
                            line: str = line.ljust(max_line_length, fill_char)
                        print(" " * padding + color +
                              line + Style.RESET_ALL)
                else:
                    print(" " * padding + color +
                          message + Style.RESET_ALL)

        except Exception as error:
            self.handle_error(origin_file="print_multiline",
                              error_message=str(object=error))

    def get_input(self, prompt: str, default_value: str | int | bool = False,  requires_value: bool = False, any_key: bool = False, message_type: str = "INFO"):
        if any_key:
            self.display(text=prompt, message_type=message_type)
            input()
            return True

        while True:
            self.display(text=prompt, message_type="WARNING")
            response: str = input().lower()
            if requires_value:
                if not response:
                    self.display(
                        text="Invalid input, please try again.", message_type="ERROR")
                    return self.get_input(prompt=prompt, default_value=default_value, requires_value=requires_value)
                else:
                    return response
            elif not requires_value:
                if response == "y":
                    return True
                elif response == "n":
                    return False
                else:
                    self.display(
                        text="Invalid input, please try again.", message_type="ERROR")
                    return self.get_input(prompt=prompt, default_value=default_value,  requires_value=requires_value)

    def setup_environment(self) -> tuple[str, int, str] | None:
        try:
            profiles_directory, number_of_profiles, base_url = self.data or (
                "./profiles", 1, "https://www.google.com/"
            )
            config_values = [
                ("profiles_directory", "Profiles directory", profiles_directory),
                ("number_of_profiles", "Number of profiles", number_of_profiles),
                ("base_url", "Base url", base_url)
            ]
            for config_name, prompt, default_value in config_values:
                self.display(text=f"{prompt}: {default_value}",
                             message_type="INFO")
            response: str | int = self.get_input(prompt="Do you want to change any of the above values? (y/n)",
                                                 default_value=False,  requires_value=False)
            if not response:
                return profiles_directory, number_of_profiles, base_url

            for config_name, prompt, default_value in config_values:
                response = bool(self.get_input(
                    prompt=f"Do you want to change {config_name.replace('_', ' ')}? (y/n)",
                    default_value=False,
                ))
                print(response, config_name, prompt, default_value)
                if response:
                    new_value = self.get_input(
                        prompt=f"Enter new value for {config_name.replace('_', ' ')}:", default_value=default_value, requires_value=True
                    )
                    if config_name == "number_of_profiles":
                        new_value = int(new_value)
                    config_values[config_values.index(
                        (config_name, prompt, default_value))] = (config_name, prompt, new_value)
                else:
                    continue

            self.display_title()
            self.display(text="Environment setup completed successfully.",
                         message_type="SUCCESS")
            for config_name, prompt, default_value in config_values:
                self.display(text=f"{prompt}: {default_value}",
                             message_type="INFO")
            self.get_input(prompt="Press any key to continue",
                           any_key=True, message_type="WARNING")
            return profiles_directory, number_of_profiles, base_url

        except (ValueError, Exception) as error:
            error_message = str(object=error)
            self.handle_error(origin_file="load_configuration",
                              error_message=error_message)
            return None

    def perform_web_scraping(self) -> None:
        while True:
            self.display_title()
            if self.errors:
                self.display_errors()
            self.display(text="Starting all profiles...",
                         message_type="INFO", show_time=True)
            response = self.get_input(
                prompt="Do you want to start automatic scraping? (y/n):", default_value=False, requires_value=False
            )

            if response:
                self.display_title()
                self.display(text="Starting automatic scraping...",
                             message_type="INFO", show_time=True)
                self.auto_scraping()

            else:
                self.display_title()
                self.display(text="Starting manual scraping...",
                             message_type="INFO", show_time=True)
                self.manual_scraping()

    def manual_scraping(self) -> None:
        if self.new_data:
            headless = self.get_input(
                prompt="Do you want to start with headless mode? (y/n):", default_value=False, requires_value=False
            )

            profile_index = int(self.get_input(
                prompt=f"Enter profile index (1-{self.new_data[1]}) :", default_value=0, requires_value=True
            ))

            data = self.profile_processor(
                profile_index=profile_index-1, headless=bool(headless))
            if data:
                self.info[f"Profile-{profile_index-1}"] = data
            self.display(
                text="Profile processed successfully", message_type="SUCCESS")
            self.display(
                text="Press enter to continue", message_type="INFO")
            input()

    def auto_scraping(self) -> None:
        headless = self.get_input(
            prompt="Do you want to start with headless mode? (y/n):", default_value=False,  requires_value=False
        )
        if self.new_data:
            for profile_index in range(self.new_data[1]):
                data = self.profile_processor(
                    profile_index=profile_index, headless=bool(headless))
                if data:
                    self.info[f"Profile-{profile_index}"] = data
        self.display(
            text="All profiles processed successfully", message_type="SUCCESS")
        self.display(
            text="Press enter to continue", message_type="INFO")
        input()

    def profile_processor(self,
                          profile_index: int,
                          headless: bool = False
                          ):
        try:
            self.display_title()
            self.display(
                text=f"Processing profile: {profile_index+1}, please wait...", message_type="INFO")
            self.create_driver(profile_index=profile_index, headless=headless)
            if not self.driver or not self.new_data:
                self.display(
                    text=f"Error creating chrome driver for profile: {profile_index}", message_type="ERROR")
                sys.exit()
            self.driver.get(url=str(self.new_data[2]))
            html: str = self.driver.page_source
            soup: BeautifulSoup = BeautifulSoup(
                markup=html, features="html.parser")
            div_challenge: Tag | NavigableString | None = soup.find(
                name="div", id="divChallenge")

            if div_challenge:
                self.solve_captcha(html=html)
                self.driver.quit()
                self.profile_processor(
                    profile_index=profile_index, headless=headless)
            else:
                data = self.collect_data(soup=soup)
                return data

        except Exception as error:
            self.display(
                text=f"Error while processing profile {profile_index+1}:\n {error}", message_type="ERROR")
            self.handle_error(origin_file="process",
                              error_message=str(object=error))

    def create_driver(self, profile_index, headless) -> None:
        self.driver = None
        if self.new_data:
            profile_path: str = f"{self.new_data[0]}/profile{profile_index}"
            try:
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument(argument="--disable-dev-shm-usage")
                chrome_options.add_argument(
                    argument="--disable-blink-features=AutomationControlled")
                chrome_options.add_argument(argument="--disable-extensions")
                chrome_options.add_argument(argument="--disable-plugins")
                chrome_options.add_argument(argument="--start-maximized")
                chrome_options.add_argument(argument="--no-sandbox")
                chrome_options.add_argument(argument="--disable-infobars")
                chrome_options.add_argument(argument="--disable-notifications")
                chrome_options.add_argument(
                    argument="--disable-popup-blocking")
                chrome_options.add_experimental_option(
                    name="excludeSwitches", value=["enable-automation"])
                chrome_options.add_experimental_option(
                    name="useAutomationExtension", value=False)
                if profile_path:
                    chrome_options.add_argument(
                        argument=f"--user-data-dir={profile_path}")
                if headless:
                    chrome_options.add_argument(argument="--headless")
                service = Service(
                    executable_path=ChromeDriverManager().install())
                self.driver = webdriver.Chrome(
                    service=service, options=chrome_options)
            except Exception as error:
                self.display(
                    text=f"Error creating chrome driver for profile: {profile_index}. Error:\n {error}", message_type="ERROR")
                self.handle_error(origin_file="create_driver",
                                  error_message=str(object=error))
                sys.exit()

    def save_audio_to_file(self, audio_base64: str) -> None:
        try:
            audio_bytes: bytes = base64.b64decode(s=audio_base64)
            with open(file=self.audio_file_path, mode='wb') as file:
                file.write(audio_bytes)
        except Exception as error:
            self.display(
                text=f"Error while saving audio to file: {error}", message_type="ERROR")
            self.handle_error(origin_file="save_audio_to_file",
                              error_message=str(object=error))

    def recognize_audio(self) -> str | None:
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(filename_or_fileobject=self.audio_file_path) as source:
                audio: AudioData = recognizer.record(source=source)
                text = recognizer.recognize_google(audio_data=audio)
                corrected_text: str = str(
                    object=text).replace(" ", "").upper()
                return corrected_text
        except sr.UnknownValueError:
            self.display(text="Speech Recognition could not understand audio",
                         message_type='ERROR')
            return None
        except sr.RequestError as error:
            self.display(text=f"Could not request results from Speech Recognition service; {error}",
                         message_type='ERROR')
            return None
        except Exception as error:
            self.display(text=f"Error while recognizing audio: {error}",
                         message_type='ERROR')
            return None

    def solve_captcha(self, html: str) -> None:
        try:
            self.display_title()
            self.display(
                text="Captcha detected, solving with Speech Recognition...", message_type='WARNING')

            if self.driver:
                soup = BeautifulSoup(markup=html, features='html.parser')
                audio_element: Tag | NavigableString | None = soup.find(
                    name='audio', id='audioPlayer')

                if audio_element:
                    source_element: Tag | NavigableString | int | None = audio_element.find(
                        'source')
                    if source_element and isinstance(source_element, Tag):
                        audio_base64: str = str(
                            object=source_element['src']).split(sep=',')[1]
                        self.save_audio_to_file(audio_base64=audio_base64)
                        corrected_text: str | None = self.recognize_audio()

                        if corrected_text:
                            captcha_code_input: List[WebElement] = self.driver.find_elements(
                                by=By.ID, value=self.captcha_input_id)

                            if captcha_code_input:
                                captcha_code_input[0].send_keys(corrected_text)
                                captcha_button: List[WebElement] = self.driver.find_elements(
                                    by=By.XPATH, value=self.captcha_button_xpath)

                                if captcha_button:
                                    captcha_button[0].click()
                                    self.display(
                                        text="Captcha solved successfully", message_type='INFO')
        except Exception as error:
            self.display(text=f"Error while solving captcha: {error}",
                         message_type='ERROR')
            self.handle_error(origin_file="solve_captcha",
                              error_message=str(object=error))

    def find_element(self, element_id: str, soup: BeautifulSoup) -> Tag | NavigableString | None:
        return soup.find(id=element_id)

    def collect_data(self,  soup: BeautifulSoup) -> Dict[str, Union[int, Tag, NavigableString, ResultSet, None]]:
        element_ids: Dict[str, str] = {
            "uid": "hlLinkToQueueTicket2",
            "progress": "MainPart_divProgressbar",
            "last_update_time": "MainPart_lbLastUpdateTimeText",
            "users_ahead": "MainPart_lbUsersInLineAheadOfYou",
            "which_is_in": "MainPart_lbWhichIsIn",
            "message_on_ticket": "MainPart_pMessageOnQueueTicket",
            "message_on_ticket_time": "MainPart_h2MessageOnQueueTicketTimeText",
        }
        collected_elements: Dict[str, Union[Tag,
                                            NavigableString, ResultSet, None]] = {}

        for var_name, element_id in element_ids.items():
            collected_elements[var_name] = self.find_element(
                element_id=element_id, soup=soup)
        data = {}

        for key, value in collected_elements.items():
            if isinstance(value, Tag):
                if value.find(name="arial-valuenow"):
                    data[key] = value.get("arial-valuenow")
                data[key] = value.get_text()
            elif isinstance(value, NavigableString):
                data[key] = value
            elif isinstance(value, ResultSet):
                data[key] = [item.get_text() for item in value]
            else:
                data[key] = None
        return data


if __name__ == "__main__":
    app = Application(config_path="config.ini")
    app.start()
