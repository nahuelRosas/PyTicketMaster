from typing import Any, Dict
from bs4.element import Tag, NavigableString, ResultSet
from src.utils.print_multiline import print_multiline
from src.web_scraping.process_profile import ProfileProcessor


def get_user_input(prompt: str) -> bool:
    print_multiline(text=prompt, message_type="INFO")
    response: str = input().strip().lower()
    return response == "y"


def auto_scraping(data: tuple[str | int, int, str | int]) -> None:
    if get_user_input("Do you want to start with headless mode? (y/n):"):
        headless = True
    else:
        headless = False

    all_processed_data = {}

    for profile_index in range(data[1]):
        processor = ProfileProcessor(profile_index=profile_index,
                                     profiles_directory=str(object=data[0]),
                                     url=str(object=data[2]),
                                     headless=headless)

        processed_data: Dict[str, int | Tag | NavigableString |
                             ResultSet[Any] | None] = processor.get_data()
        all_processed_data[f"profile{profile_index}"] = processed_data

    print_multiline(text="All profiles processed successfully.",
                    message_type="INFO", show_time=True)

    if get_user_input("Do you want to save the results? (y/n):"):
        print_multiline(text="Saving results...",
                        message_type="INFO", show_time=True)
        save_results(data=all_processed_data)
        print_multiline(text="Results saved successfully.",
                        message_type="INFO", show_time=True)
    else:
        print_multiline(text="Results not saved.",
                        message_type="INFO", show_time=True)

    input("Press enter to continue")

    auto_scraping(data=data)


def save_results(data: dict[str, dict[str, int | Tag | NavigableString | ResultSet[Any] | None]]) -> None:
    for profile_name, profile_data in data.items():
        file_path: str = f"./results/{profile_name}.txt"
        with open(file=file_path, mode="w", encoding="utf-8") as file:
            for key, value in profile_data.items():
                file.write(f"{key}: {value}\n")
