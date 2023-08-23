from datetime import datetime
from typing import List, Tuple

ERRORS: List[Tuple[str, str]] = []


def add_error(origin_file: str, error_message: str) -> None:
    """
    Add an error message to the ERRORS array.

    Args:
        origin_file (str): The name or path of the file where the error occurred.
        error_message (str): The error message to add.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error = (timestamp, f"Error while processing {origin_file}: {error_message}")
    ERRORS.append(error)


def get_errors() -> List[Tuple[str, str]]:
    """
    Get the array of error messages.

    Returns:
        List[Tuple[str, str]]: The list of error messages, each represented as a tuple
        containing the timestamp and the error message.
    """
    return ERRORS
