import os
import re
import sys
import base64
import shutil
import configparser
from datetime import datetime
from typing import Union, Dict, Optional, Any
import requests
import speech_recognition as sr
from speech_recognition import AudioData
from colorama import Fore, Style
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, ResultSet
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
# from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from pandas import DataFrame
from tqdm import tqdm


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
        self.news = {}

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
        text: Any,
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
            return config_values[0][2], config_values[1][2], config_values[2][2]

        except (ValueError, Exception) as error:
            error_message = str(object=error)
            self.handle_error(origin_file="load_configuration",
                              error_message=error_message)
            return None

    def format_message_ticket(self, message_ticket: str) -> str:
        message_ticket = re.sub(
            r"\*\*(.*?)\*\*", r"\033[1m\1\033[0m", message_ticket)
        message_ticket = message_ticket.replace("\\", "\n")
        message_ticket = re.sub(r"\n{3,}", "\n\n", message_ticket)
        return message_ticket

    def perform_web_scraping(self) -> None:
        while True:
            self.display_title()
            if self.news:
                self.display_news()
            if self.errors:
                self.display_errors()
            if self.info:
                self.display_data()
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

    def display_data(self, with_by_pass: bool = False) -> None:
        if self.info:
            data_frame: DataFrame = pd.DataFrame.from_dict(
                data=self.info, orient='index')
            data_frame.drop(labels=['message_on_ticket', 'message_on_ticket_time'],
                            axis=1, inplace=True)
            data_frame.sort_values(by=['progress', 'users_ahead', 'which_is_in'], ascending=[
                                   True, True, True], inplace=True)
            self.display_title()
            self.display_news()
            self.display(text="Results:", message_type="INFO")
            result_markdown = data_frame.to_markdown(
                numalign="center", stralign="center", index=False)
            self.display(text=result_markdown, color=Fore.LIGHTMAGENTA_EX,
                         alignment="center")
            with open(file="results.txt", mode="w", encoding="utf-8") as function:
                function.write(result_markdown)

            if with_by_pass:
                self.get_input(prompt="Press enter to continue",
                               any_key=True, message_type="WARNING")

    def manual_scraping(self) -> None:
        if self.news:
            self.display_news()
        if self.errors:
            self.display_errors()
        if self.new_data:
            profile_index = int(self.get_input(
                prompt=f"Enter profile index (1-{self.new_data[1]}) :", default_value=0, requires_value=True
            ))

            data = self.profile_processor(
                profile_index=profile_index-1, headless=False, recaptcha=True)
            if data:
                self.info[f"Profile-{profile_index-1}"] = data
            self.display(
                text="Profile processed successfully", message_type="SUCCESS")
            self.display(
                text="Press enter to continue", message_type="INFO")
            input()

    # def display_news(self) -> None:
        # if self.news:
            # message = self.format_message_ticket(
            #     message_ticket=self.news['message'])
            # self.display(
            #     text=f"Last news: \n{message}", alignment="left", color=Fore.LIGHTRED_EX,

            # )
            # self.display(
            #     text=f"Time at which the last news was given: {self.news['time']}", alignment="left", color=Fore.LIGHTRED_EX,)

    def auto_scraping(self) -> None:
        # if self.news:
        #     self.display_news()
        if self.errors:
            self.display_errors()
        headless = self.get_input(
            prompt="Do you want to start with headless mode? (y/n):", default_value=False,  requires_value=False
        )
        if self.new_data:
            progress_bar = tqdm(
                total=self.new_data[1], desc="Progress", unit="profiles")
            for profile_index in range(self.new_data[1]):
                if self.info:
                    self.display_data(with_by_pass=True)
                data = self.profile_processor(
                    profile_index=profile_index, headless=bool(headless), progress_bar=progress_bar
                )
                if data:
                    data['profile'] = profile_index + 1
                    self.info[f"Profile {profile_index + 1}"] = data

            progress_bar.close()
        self.display(
            text="All profiles processed successfully", message_type="SUCCESS")
        self.display_data()

    def profile_processor(self,
                          profile_index: int,
                          progress_bar: tqdm | None = None,
                          headless: bool = False,
                          recaptcha: bool = False,
                          attempts: int = 0,
                          ):
        try:
            self.display_title()
            if self.info:
                self.display_data(with_by_pass=True)
            if progress_bar:
                progress_bar.update(n=1)
            self.display(
                text=f"Processing profile: {profile_index+1}, please wait...", message_type="INFO")
            self.create_driver(profile_index=profile_index, headless=headless)
            if not self.driver or not self.new_data:
                self.display(
                    text=f"Error creating chrome driver for profile: {profile_index}", message_type="ERROR")
                sys.exit()
            self.driver.get(url=str(object=self.new_data[2]))
            self.driver.implicitly_wait(time_to_wait=10)
            html: str = self.driver.page_source
            soup: BeautifulSoup = BeautifulSoup(
                markup=html, features="html.parser")
            div_challenge: Tag | NavigableString | None = soup.find(
                name="div", id="divChallenge")

            if div_challenge:
                self.get_input(
                    prompt="Press enter to continue", any_key=True, message_type="WARNING"
                )
                # if recaptcha:
            #     div_challenge = None

            # if div_challenge:
            #     if attempts < 1:
            #         self.solve_captcha(html=html)
            #         self.driver.quit()
            #         self.profile_processor(
            #             profile_index=profile_index, headless=headless, attempts=attempts+1, progress_bar=None)
            #     else:
            #         self.driver.quit()
            #         self.profile_processor(
            #             profile_index=profile_index, headless=False,  attempts=0, recaptcha=True, progress_bar=None)
            else:
                data = self.collect_data(soup=soup)
                self.driver.quit()
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
        self.get_input(prompt="Press enter to continue", any_key=True)

        # try:

        #     self.display_title()
        #     self.display(
        #         text="Captcha detected, solving with Speech Recognition...", message_type='WARNING')

        #     if self.driver:
        #         soup = BeautifulSoup(markup=html, features='html.parser')
        #         audio_element: Tag | NavigableString | None = soup.find(
        #             name='audio', id='audioPlayer')
        #         frame = self.driver.find_elements(
        #             by=By.TAG_NAME, value="iframe")
        #         if audio_element:
        #             source_element: Tag | NavigableString | int | None = audio_element.find(
        #                 'source')
        #             if source_element and isinstance(source_element, Tag):
        #                 audio_base64: str = str(
        #                     object=source_element['src']).split(sep=',')[1]
        #                 self.save_audio_to_file(audio_base64=audio_base64)
        #                 corrected_text: str | None = self.recognize_audio()

        #                 if corrected_text:
        #                     captcha_code_input: List[WebElement] = self.driver.find_elements(
        #                         by=By.ID, value=self.captcha_input_id)

        #                     if captcha_code_input:
        #                         captcha_code_input[0].send_keys(corrected_text)
        #                         captcha_button: List[WebElement] = self.driver.find_elements(
        #                             by=By.XPATH, value=self.captcha_button_xpath)

        #                         if captcha_button:
        #                             captcha_button[0].click()
        #                             self.display(
        #                                 text="Captcha solved successfully", message_type='INFO')
        #                             self.get_input(
        #                                 prompt="Press enter to continue", any_key=True, message_type="WARNING"
        #                             )
        #                         else:
        #                             self.display(
        #                                 text="Captcha button not found", message_type='ERROR')
        #                             self.get_input(
        #                                 prompt="Press enter to continue", any_key=True, message_type="WARNING"
        #                             )
        #                     else:
        #                         self.display(
        #                             text="Captcha input not found", message_type='ERROR')
        #                         self.get_input(
        #                             prompt="Press enter to continue", any_key=True, message_type="WARNING"
        #                         )

        #         elif frame:
        #             self.driver.switch_to.frame(frame_reference=frame[0])
        #             self.driver.implicitly_wait(time_to_wait=5)
        #             box_captcha_xpath = '//*[@id="recaptcha-anchor"]/div[1]'
        #             box_captcha = self.driver.find_element(
        #                 By.XPATH, box_captcha_xpath)

        #             if box_captcha:
        #                 box_captcha.click()
        #                 self.driver.implicitly_wait(2)
        #                 audio_button_xpath = '//*[@id="recaptcha-audio-button"]'
        #                 audio_button = self.driver.find_element(
        #                     By.XPATH, audio_button_xpath)
        #                 if audio_button:
        #                     audio_button.click()
        #                     self.driver.implicitly_wait(5)
        #                     audio_button_download_xpath = '//*[@id="rc-audio"]/div[7]/a'
        #                     audio_button_download_href = self.driver.find_element(
        #                         By.XPATH, audio_button_download_xpath
        #                     ).get_attribute('href')
        #                     if audio_button_download_href:
        #                         self.download_audio(audio_button_download_href)
        #                         self.driver.implicitly_wait(5)
        #                         corrected_text = self.recognize_audio()
        #                         input_xpath = '//*[@id="audio-response"]'
        #                         input_captcha = self.driver.find_element(
        #                             By.XPATH, input_xpath)
        #                         if corrected_text and input_captcha:
        #                             input_captcha.send_keys(corrected_text)
        #                             button_verify_xpath = '//*[@id="recaptcha-verify-button"]'
        #                             button_verify = self.driver.find_element(
        #                                 By.XPATH, button_verify_xpath)
        #                             if button_verify:
        #                                 button_verify.click()
        #                                 self.display(
        #                                     text="Captcha solved successfully", message_type='INFO')
        #                                 self.get_input(
        #                                     prompt="Press enter to continue", any_key=True, message_type="WARNING")
        #                             else:
        #                                 self.display(
        #                                     text="Captcha verify button not found", message_type='ERROR')
        #                                 self.get_input(
        #                                     prompt="Press enter to continue", any_key=True, message_type="WARNING")
        #                         else:
        #                             self.display(
        #                                 text="Corrected text or input field not found", message_type='ERROR')
        #                 else:
        #                     self.display(
        #                         text="Audio button not found", message_type='ERROR')

        #             else:
        #                 self.display(
        #                     text="Captcha box not detected", message_type='INFO')

        #         else:
        #             self.display(
        #                 text="Captcha audio not detected", message_type='INFO')

        # except Exception as error:
        # self.display(text=f"Error while solving captcha: {error}",
        #              message_type='ERROR')
        # self.handle_error(origin_file="solve_captcha",
        #                   error_message=str(object=error))

    def download_audio(self, audio_url):
        if self.driver:
            self.driver.execute_script(script="window.open('');")
            self.driver.switch_to.window(
                window_name=self.driver.window_handles[1])
            self.driver.get(url=audio_url)
            request_audio = requests.get(url=audio_url, timeout=5)
            with open(file=self.audio_file_path, mode='wb') as file:
                file.write(request_audio.content)
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

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

        self.news["message"] = data["message_on_ticket"]
        self.news["time"] = data["message_on_ticket_time"]

        return data

if __name__ == "__main__":
    app = Application(config_path="config.ini")
    app.start()
