"""Logout page"""

from pages.base_page import Page
from util import LOGGER


class Logout(Page):
    """Page user passes credentials in for authorization."""

    PATH = 'logout.asp'

    def logout(self):
        """Login in to router admin"""
        LOGGER.info('LOGGING OUT...')
        self.get()
        LOGGER.info('LOGGED OUT...')
