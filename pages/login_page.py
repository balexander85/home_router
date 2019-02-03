"""Login page"""
from enum import Enum
from typing import List

from requests_html import Element, HTMLResponse

from pages.base_page import Page
from util import LOGGER


class ConnectivityState(Enum):
    OK = "OK"


class Login(Page):
    """Page user passes credentials in for authorization."""

    PATH = 'goform/login'
    USER_OR_PASSWORD_ERROR = (
        'The user name or password is invalid, please try again.'
    )

    def login(self) -> HTMLResponse:
        """Login in to router admin"""
        LOGGER.info('LOGGING IN...')
        response: HTMLResponse = self.post()
        rows: List[Element] = response.html.find(self.TABLE_ROWS)
        try:
            assert rows
        except AssertionError:
            error_element = response.html.find(
                'font[style="color: red"]', first=True
            )
            if error_element.text == self.USER_OR_PASSWORD_ERROR:
                raise PermissionError(self.USER_OR_PASSWORD_ERROR)
            else:
                raise Exception(
                    f"Table rows but none found. HTML: \n{response.html.html}"
                )
        LOGGER.info('LOGGED IN...')
        return response

    @staticmethod
    def check_connectivity_state(rows: List[Element]):
        """Don't really need this right now but saving code to method

        I may either transform to a property or remove all together.
        """
        connectivity_state_row: Element = rows[1]
        connectivity_state: str = connectivity_state_row.find('td')[1].text
        assert connectivity_state == ConnectivityState.OK.value, (
            f"Expected Connectivity State: {ConnectivityState.OK.value}"
            f"actual: {connectivity_state}"
        )
