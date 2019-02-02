"""Login page"""

from pages.base_page import Page
from util import LOGGER


class Login(Page):
    """Page user passes credentials in for authorization."""

    PATH = 'goform/login'

    def login(self):
        """Login in to router admin"""
        LOGGER.info('LOGGING IN...')
        self.post()
        LOGGER.info('LOGGED IN...')
