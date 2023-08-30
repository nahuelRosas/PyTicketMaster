from bs4 import BeautifulSoup, Tag, NavigableString, ResultSet


class HTMLData:
    def __init__(self, html: BeautifulSoup) -> None:
        self.html: BeautifulSoup = html

    def find_element(self, element_id, element_type) -> Tag | NavigableString | ResultSet | None:
        return self.html.find(name=element_type, id=element_id)


def collect_data(html: BeautifulSoup) -> dict[str, Tag | NavigableString | ResultSet | None]:
    data = HTMLData(html=html)

    element_ids: dict[str, str] = {
        "progress_div": "MainPart_divProgressbar",
        "link_to_queue_ticket": "hlLinkToQueueTicket2",
        "last_update_time": "MainPart_lbLastUpdateTimeText",
        "which_is_in": "MainPart_lbWhichIsIn",
        "message_on_queue_ticket": "MainPart_pMessageOnQueueTicket",
        "users_in_line_ahead_of_you": "MainPart_lbUsersInLineAheadOfYou",
        "message_on_queue_ticket_time": "MainPart_h2MessageOnQueueTicketTimeText",
    }

    collected_elements: dict[str, Tag |
                             NavigableString | ResultSet | None] = {}

    for var_name, element_id in element_ids.items():
        collected_elements[var_name] = data.find_element(
            element_id=element_id, element_type=(Tag, NavigableString, ResultSet))

    return collected_elements
