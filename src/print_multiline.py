from colorama import Fore, Style
from typing import Union
import shutil
from datetime import datetime
from src.error_handler import add_error

MESSAGE_TYPES = {
    "INFO": {"color": Fore.GREEN, "prefix": "[INFO]"},
    "WARNING": {"color": Fore.YELLOW, "prefix": "[WARNING]"},
    "ERROR": {"color": Fore.RED, "prefix": "[ERROR]"},
    "SUCCESS": {"color": Fore.GREEN, "prefix": "[SUCCESS]"},
    "FAILURE": {"color": Fore.RED, "prefix": "[FAILURE]"},
    "DEBUG": {"color": Fore.CYAN, "prefix": "[DEBUG]"},
    "CRITICAL": {"color": Fore.RED, "prefix": "[CRITICAL]"},
    "EXCEPTION": {"color": Fore.RED, "prefix": "[EXCEPTION]"},
}

def print_multiline(
    text: str,
    color: str = Fore.RESET,
    alignment: str = "left",
    fill_char: str = " ",
    show_time: bool = False,
    message_type: Union[str, None] = None,
) -> None:
    """
    Prints multiline text with optional color, alignment, and time prefix.
    Args:
        text (str): The multiline text to print.
        color (str, optional): The color to apply to the text. Defaults to Fore.RESET.
        alignment (str, optional): The alignment of the text. Defaults to "left".
        fill_char (str, optional): The character used for filling in case of alignment "fill". Defaults to " ".
        show_time (bool, optional): Whether to show the current time prefix. Defaults to False.
        message_type (Union[str, None], optional): The type of message for applying a prefix. Defaults to None.
    """
    try:
        console_width = shutil.get_terminal_size((80, 20)).columns
        lines = text.splitlines()
        max_line_length = max(len(line) for line in lines) if lines else 0
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

        if lines:
            if len(lines) > 1:
                for line in lines:
                    if alignment == "fill":
                        line = line.ljust(max_line_length, fill_char)
                    print(" " * padding + color + line + Style.RESET_ALL)
            else:
                print(" " * padding + color + message + Style.RESET_ALL)

    except Exception as e:
        add_error("print_multiline", str(e))

if __name__ == "__main__":
  print_multiline("Hello World!", Fore.RED, "left", show_time=False, message_type="INFO")