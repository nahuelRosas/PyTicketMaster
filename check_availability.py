import configparser
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pygame

config = configparser.ConfigParser()
config.read('config.ini')
CHROMEDRIVER_PATH = config.get('Main', 'chromedriver_path')

def check_availability():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
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

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        # Initialize Chrome browser

        # Open the web page
        driver.get('https://www.allaccess.com.ar/event/taylor-swift-the-eras-tour')

        # Wait for the page to fully load
        time.sleep(5)

        # Extract the page source
        page_source = driver.page_source

        # Create BeautifulSoup object for parsing the page source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find all div elements on the page
        div_elements = soup.find_all('div')

        # Check if any div contains the text "Agotado"
        agotado_found = False
        for div in div_elements:
            if 'Agotado' in div.text:
                agotado_found = True
                break

        # Emit a sound if "Agotado" text is not found
        if not agotado_found:
            print("Available!")
            # Add your code here to emit a sound
            pygame.mixer.init()
            pygame.mixer.music.load('./mp3/Taylor.mp3')  # Replace with the location of your sound file
            pygame.mixer.music.play()

        # Close the browser
        driver.quit()
    except Exception as e:
        print("An error occurred:", str(e))

# Countdown timer function
def countdown_timer(seconds):
    while seconds > 0:
        minutes, secs = divmod(seconds, 60)
        timer = f"{minutes:02d}:{secs:02d}"
        print("Next check in:", timer)
        time.sleep(1)
        seconds -= 1

# Check availability every 30 minutes
check_interval = 1800  # 30 minutes in seconds

while True:
    os.system("cls" if os.name == "nt" else "clear")
    check_availability()
    countdown_timer(check_interval)
