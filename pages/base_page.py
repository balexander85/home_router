"""Base page object containing boilerplate code to be used with all pages"""
from typing import Dict

from furl import furl
from requests_html import HTML, HTMLResponse, HTMLSession
from retrying import retry

from util import LOGGER, save_page


class Page:

    PATH = ''
    TABLE_HEADER = 'tr[bgcolor="#4E97B9"]'
    TABLE_ROWS = 'tr[bgcolor="#E7DAAC"]'

    def __init__(
            self,
            base_url: furl,
            session: HTMLSession,
            payload: Dict = None
    ):
        self.base_url: furl = base_url
        self.session: HTMLSession = session
        self.payload: Dict = payload

    def __repr__(self) -> str:
        """String representation of Page object."""
        return f"<class {self.__class__.__name__} base_url='{self.base_url}'>"

    @property
    def html(self) -> HTML:
        return self.get().html

    @property
    def url(self) -> str:
        """Create URL on demand"""
        return self.base_url.set(path=self.PATH)

    @retry(wait_fixed=500, stop_max_attempt_number=5)
    def get(self) -> HTMLResponse:
        LOGGER.debug(msg=f"GETing url: {self.url}")
        response: HTMLResponse = self.session.get(url=self.url,
                                                  headers=self.session.headers)
        return response

    @retry(wait_fixed=500, stop_max_attempt_number=5)
    def post(self) -> HTMLResponse:
        """Make post request to page."""
        LOGGER.debug(msg=f"POSTing to url: {self.url}")
        response: HTMLResponse = \
            self.session.post(url=self.url,
                              headers=self.session.headers,
                              data=self.payload)
        return response

    def save_page(self, file_name: str = "test.html"):
        """Helper function to save page as an html file."""
        save_page(html=self.html, file_name=file_name)
