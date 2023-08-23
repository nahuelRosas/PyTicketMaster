from src.config import read_config
from src.print_title import print_title
from src.print_multiline import print_multiline
from src.process_profile import process_profile
from colorama import Fore
import os
import sys


def get_valid_profile_selection(num_profiles):
    selected_profile_message_type = "INFO"
    while True:
        try:
            print_multiline("Select a profile (1-{}):".format(num_profiles), message_type=selected_profile_message_type)
            selected_profile = int(input())
            if selected_profile < 1 or selected_profile > num_profiles:
                raise ValueError
            return selected_profile
        except ValueError:
            selected_profile_message_type = "ERROR"


def start_scraping_all_profiles(num_profiles, profiles_dir):
    for profile_index in range(num_profiles):
        process_profile(profile_index,profiles_dir)
        # process_results_data()
        continue


def main() -> None:
    profiles_dir, num_profiles, start_time, URL = read_config("config.ini")
    os.system("cls" if os.name == "nt" else "clear")
    print_title()

    while True:
        user_choice_profile = None
        user_choice_message_type = "INFO"

        while user_choice_profile is None:
            print_multiline("Do you want to select a profile? (y/n):", message_type=user_choice_message_type)
            user_choice_profile = input().lower()

            if user_choice_profile == "y":
                selected_profile = get_valid_profile_selection(num_profiles)

                process_profile(selected_profile - 1)
                process_results_data()
                
                print_multiline("Press enter for continue", message_type="INFO")
                break_function = input()

                if break_function == "":
                    continue                

            elif user_choice_profile == "n":
                automatic_scraping_choice = None
                automatic_scraping_choice_message_type = "INFO"
                while automatic_scraping_choice is None:
                    print_multiline("Starting all profiles...", Fore.MAGENTA, "center")
                    print_multiline(
                        "Selecting the automatic option causes the system to start in headless mode and assumes that Queue has no human verification system.",
                        message_type="WARNING"
                    )
                    print_multiline(
                        "Recommendation: start the first interval in manual mode and the subsequent ones automatically",
                        message_type="INFO"
                    )
                    print_multiline(
                        "Do you want to start automatic scraping? (y/n):",
                        message_type=automatic_scraping_choice_message_type
                    )
                    automatic_scraping_choice = input().lower()
                    break_function_message_type = "INFO"

                    if automatic_scraping_choice == "y":
                        print("Y")
                        # executor = ThreadPoolExecutor(max_workers=1)
                        # futures = []

                        # for i in range(num_profiles):
                        #     process_profile(i, True)
                        #     process_results_data()
                        # process_results_data()

                        break

                    elif automatic_scraping_choice == "n":
                        start_scraping_all_profiles(num_profiles, profiles_dir)
                        print_multiline("Press enter to restart scraping, or press R to restart from init, or Q to Exit...", message_type=break_function_message_type)
                        break_function = input()
                        if break_function == "":
                            continue
                        elif break_function.lower() == "r":
                            user_choice_message_type = "ERROR"
                            break
                        elif break_function.lower() == "q":
                            sys.exit()
                        else:
                            break_function_message_type = "ERROR"
                            continue

                    else:
                        automatic_scraping_choice = None
                        automatic_scraping_choice_message_type = "ERROR"
                        continue

            else:
                user_choice_message_type="ERROR"
                user_choice_profile = None

if __name__ == "__main__":
    main()
