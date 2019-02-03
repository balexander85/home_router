"""Logout page"""

from requests_html import HTMLResponse

from pages.base_page import Page
from util import LOGGER


class Logout(Page):
    """Page user passes credentials in for authorization."""

    PATH = 'logout.asp'

    def logout(self) -> HTMLResponse:
        """Login in to router admin"""
        LOGGER.info('LOGGING OUT...')
        response: HTMLResponse = self.get()
        assert response.html.search('You are {} logged out.'), (
            f'Failed to logout. HTML: {response.html}'
        )
        LOGGER.info('LOGGED OUT...')
        return response
