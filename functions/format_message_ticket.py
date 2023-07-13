import re


def format_message_ticket(message_ticket: str) -> str:
    message_ticket = re.sub(r"\*\*(.*?)\*\*", r"\033[1m\1\033[0m", message_ticket)
    message_ticket = message_ticket.replace("\\", "\n")
    message_ticket = re.sub(r"\n{3,}", "\n\n", message_ticket)
    return message_ticket
