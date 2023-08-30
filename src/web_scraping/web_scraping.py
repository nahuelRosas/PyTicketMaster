import os
from src.utils.print_multiline import print_multiline
from utils.title_printer import TitlePrinter
from src.web_scraping.auto_scraping import auto_scraping


def web_scraping(data: tuple[str | int, int, str | int]) -> None:
    TitlePrinter()
    print_multiline(text="Starting all profiles...",
                    message_type="INFO", show_time=True)
    print_multiline(text="Do you want to start automatic scraping? (y/n):",
                    message_type="INFO")
    response: str = input().lower()
    if response == "y":
        auto_scraping(data=data)

    elif response == "n":
        print("N")
    else:
        print_multiline(text="Invalid option, please try again.",
                        message_type="ERROR", show_time=True)
        web_scraping(data=data)
