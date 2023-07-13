import pandas as pd
import os
from functions.print_title import print_title
from functions.format_message_ticket import format_message_ticket
from functions.print_multiline import print_multiline
from colorama import Fore, Style


def process_results_data(
    RESULTS_LOCK, RESULTS_DATA, MESSAGE_TICKET, TIME_MESSAGE_TICKET, ERRORS
):
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
    # if "Users" in df_subset.columns:
    #     df_order = df_subset.sort_values(by=["Users"], ascending=False)
    #     print_multiline(
    #         df_order.to_markdown(numalign="center", stralign="center", index=False),
    #         Fore.LIGHTMAGENTA_EX,
    #         "center",
    #     )
    # else:
    print_multiline(
        df_subset.to_markdown(numalign="center", stralign="center", index=False),
        Fore.LIGHTMAGENTA_EX,
        "center",
    )

    if len(ERRORS) > 0:
        print_multiline("Errors:", Fore.LIGHTRED_EX)
        print_multiline("\n".join(ERRORS), Fore.LIGHTRED_EX, "center")
