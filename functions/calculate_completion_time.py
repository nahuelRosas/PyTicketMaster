def calculate_completion_time(start_time, progress_now):
    try:
        current_time = datetime.now().time()
        start_time = datetime.combine(
            datetime.today(), datetime.strptime(start_time, "%H:%M:%S").time()
        )
        elapsed_time = datetime.combine(datetime.today(), current_time) - start_time

        if progress_now is None or progress_now == "N/A":
            return "N/A"

        remaining_progress = 100 - float(progress_now)

        if remaining_progress == 0:
            return "Already at 100% progress"

        completion_time = elapsed_time / (float(progress_now) / 100)
        completion_time_hours = int(completion_time.total_seconds() // 3600)
        completion_time_minutes = int((completion_time.total_seconds() % 3600) // 60)
        formatted_time = f"{completion_time_hours:02d}:{completion_time_minutes:02d}"
        return formatted_time
    except Exception as e:
        ERRORS.append(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - Error while calculating completion time: {str(e)}"
        )
        return "N/A"
