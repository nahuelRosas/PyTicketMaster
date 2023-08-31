from typing import Union
import re
import shutil
import pandas as pd
from colorama import Fore, Style
from datetime import datetime

def process_results_data() -> None:
    """
    Processes the results data and prints the formatted results.
    """
    results_list = list(results_queue.queue)
    df = pd.DataFrame(results_list)

    os.system("cls" if os.name == "nt" else "clear")
    print_title()

    if MESSAGE_TICKET != "N/A":
        MESSAGE_TICKET_WITHFORMAT = format_message_ticket(MESSAGE_TICKET)
        print_multiline(f"LAST NEWS {TIME_MESSAGE_TICKET}\n", Fore.LIGHTWHITE_EX)
        print_multiline(f"{MESSAGE_TICKET_WITHFORMAT}\n", Fore.LIGHTGREEN_EX, "center")
        print_multiline(f"Results:\n", Fore.LIGHTWHITE_EX)

    if "Users" in df.columns:
        columns_with_data = df.columns[df.count() > 0]
        df_subset = df[columns_with_data]
        df_order: DataFrame = df_subset.sort_values(by=["Users"], ascending=False)
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
