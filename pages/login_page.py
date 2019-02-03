"""Login page"""
from enum import Enum

from requests_html import Element, HTMLResponse

from pages.base_page import Page
from util import LOGGER


class ConnectivityState(Enum):
    OK = "OK"


class Login(Page):
    """Page user passes credentials in for authorization."""

    PATH = 'goform/login'

    def login(self) -> HTMLResponse:
        """Login in to router admin"""
        LOGGER.info('LOGGING IN...')
        response: HTMLResponse = self.post()
        rows = response.html.find(self.TABLE_ROWS)
        assert rows, f"Table rows but none found. HTML: \n{response.html.html}"
        connectivity_state_row: Element = rows[1]
        connectivity_state: str = connectivity_state_row.find('td')[1].text
        assert connectivity_state == ConnectivityState.OK.value, (
            f"Expected Connectivity State: {ConnectivityState.OK.value}"
            f"actual: {connectivity_state}"
        )
        LOGGER.info('LOGGED IN...')
        return response
