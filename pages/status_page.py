"""Status page"""

from requests_html import HTMLResponse

from pages.base_page import Page
from util import LOGGER


class Configuration(Page):
    """Residential Gateway Configuration: Status - Security"""

    PATH = 'goform/RgConfiguration'

    def reboot(self) -> HTMLResponse:
        """Send command to reboot router"""
        LOGGER.info('Rebooting....')
        response: HTMLResponse = self.post()
        LOGGER.info('Reboot command completed.')
        return response
