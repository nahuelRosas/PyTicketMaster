import sys
import base64
from typing import List, Optional, Union, Dict, Any
import speech_recognition as sr
from bs4 import BeautifulSoup, Tag, NavigableString, ResultSet
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from speech_recognition import AudioData
from utils.title_printer import print_title
from src.utils.print_multiline import print_multiline


class ProfileProcessor:
    def __init__(self, profile_index: int, profiles_directory: str, url: str, headless: bool = False) -> None:
        self.profile_index: int = profile_index
        self.profiles_directory: str = profiles_directory
        self.url: str = url
        self.headless: bool = headless
        self.driver: Optional[WebDriver] = None
        self.audio_file_path: str = './audio/audio.wav'
        self.captcha_input_id: str = 'solution'
        self.captcha_button_xpath: str = '//*[@id="challenge-container"]/button'
        self.html: str = ""
        self.data: Dict[str, int | Tag | NavigableString |
                        ResultSet[Any] | None] = {}
        self.process()

    def create_driver(self) -> None:
        profile_path: str = f"{self.profiles_directory}/profile{self.profile_index}"
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
            chrome_options.add_argument(argument="--disable-popup-blocking")
            chrome_options.add_experimental_option(
                name="excludeSwitches", value=["enable-automation"])
            chrome_options.add_experimental_option(
                name="useAutomationExtension", value=False)
            if profile_path:
                chrome_options.add_argument(
                    argument=f"--user-data-dir={profile_path}")
            if self.headless:
                chrome_options.add_argument(argument="--headless")
            service = Service(executable_path=ChromeDriverManager().install())
            self.driver = webdriver.Chrome(
                service=service, options=chrome_options)
        except Exception as error:
            print_multiline(
                text=f"Error creating chrome driver for profile: {self.profile_index}. Error:\n {error}", message_type="ERROR")
            sys.exit()

    def process(self) -> None:
        try:
            print_title()
            print_multiline(
                text=f"Processing profile: {self.profile_index+1}, please wait...", message_type="INFO")
            self.create_driver()
            if not self.driver:
                print_multiline(
                    text=f"Error creating chrome driver for profile: {self.profile_index}", message_type="ERROR")
                sys.exit()
            self.driver.get(url=self.url)
            self.html: str = self.driver.page_source
            self.soup: BeautifulSoup = BeautifulSoup(
                markup=self.html, features="html.parser")
            div_challenge: Tag | NavigableString | None = self.soup.find(
                name="div", id="divChallenge")

            if div_challenge:
                self.solve_captcha()
                self.driver.quit()
                self.process()
            else:
                self.data = self.collect_data()

        except Exception as error:
            print_multiline(
                text=f"Error processing profile: {self.profile_index}. Error:\n {error}", message_type="ERROR")
            if self.driver:
                self.driver.quit()
            sys.exit()

    def save_audio_to_file(self, audio_base64: str) -> None:
        try:
            audio_bytes: bytes = base64.b64decode(s=audio_base64)
            with open(file=self.audio_file_path, mode='wb') as file:
                file.write(audio_bytes)
        except Exception as error:
            print_multiline(
                text=f"Error while saving audio to file: {error}", message_type='ERROR')

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
            print_multiline(text="Speech Recognition could not understand audio",
                            message_type='ERROR')
            return None
        except sr.RequestError as error:
            print_multiline(text=f"Could not request results from Speech Recognition service; {error}",
                            message_type='ERROR')
            return None
        except Exception as error:
            print_multiline(text=f"Error while recognizing audio: {error}",
                            message_type='ERROR')
            return None

    def solve_captcha(self) -> None:
        try:
            print_title()
            print_multiline(
                text="Captcha detected, solving with Speech Recognition...", message_type='WARNING')

            if self.driver:
                soup = BeautifulSoup(markup=self.html, features='html.parser')
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
                                    print_multiline(
                                        text="Captcha solved successfully", message_type='INFO')
        except Exception as error:
            print_multiline(
                text=f"Error while solving captcha:\n {error}", message_type='ERROR')

    def find_element(self, element_id: str) -> Tag | NavigableString | None:
        return self.soup.find(id=element_id)

    def collect_data(self) -> Dict[str, Union[int, Tag, NavigableString, ResultSet, None]]:
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
                element_id=element_id)
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

    def get_data(self) -> Dict[str, int | Tag | NavigableString | ResultSet[Any] | None]:
        self.data["Profile"] = self.profile_index + 1
        return self.data
