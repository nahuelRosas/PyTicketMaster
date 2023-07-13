from colorama import Fore, Style
from typing import Union
import os


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
