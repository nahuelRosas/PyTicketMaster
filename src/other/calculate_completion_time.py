from datetime import datetime, timedelta
from typing import Union
from error_handler import add_error, get_errors


def calculate_completion_time(start_time: Union[str, datetime], progress_percentage: Union[str, int, None]):
    """
    The `calculate_completion_time` function calculates the remaining time and estimated completion time
    based on the start time and progress percentage.
    @param {Union[str, datetime]} start_time - The `start_time` parameter can be either a string in the
    format "%H:%M:%S" representing a specific time, or a `datetime` object representing a specific point
    in time.
    @param {Union[str, int, None]} progress_percentage - The `progress_percentage` parameter represents
    the current progress of a task as a percentage. It can be a string, integer, or None.
    @returns The calculate_completion_time function returns a tuple containing three values:
    remaining_time_hours, estimated_completion_time, and remaining_progress.
    """
    
    try:
        current_time = datetime.now()

        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%H:%M:%S")
        elapsed_time = current_time - start_time

        if isinstance(progress_percentage, str):
            progress_percentage = int(progress_percentage)

        if progress_percentage <= 0 or progress_percentage >= 100:
            raise ValueError("Progress percentage must be between 0 and 100")

        total_estimated_time = elapsed_time / (progress_percentage / 100)
        remaining_time = total_estimated_time - elapsed_time
        estimated_completion_time = current_time + remaining_time

        remaining_progress = 100 - progress_percentage
        remaining_time_hours = str(remaining_time).split(".")[0]
        estimated_completion_time = estimated_completion_time.strftime("%H:%M")

        return remaining_time_hours, estimated_completion_time, remaining_progress

    except Exception as e:
        add_error("Calculate_Completion_Time", str(e))


if __name__ == "__main__":
    current_time = datetime.now() - timedelta(hours=1)
    progress_now = "50"

    result = calculate_completion_time(current_time, progress_now)

    print("Result:", result)
    print("Errors:", get_errors())
