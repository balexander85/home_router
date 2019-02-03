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
        response = self.post()
        connectivity_state_row: Element = \
            response.html.find('tr[bgcolor="#E7DAAC"]')[1]
        connectivity_state: str = connectivity_state_row.find('td')[1].text
        assert connectivity_state == ConnectivityState.OK.value, (
            f"Expected Connectivity State: {ConnectivityState.OK.value}"
            f"actual: {connectivity_state}"
        )
        LOGGER.info('LOGGED IN...')
        return response
