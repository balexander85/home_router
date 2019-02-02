"""Base page object containing boilerplate code to be used with all pages"""
from typing import Dict

from furl import furl
from requests_html import HTML, HTMLResponse, HTMLSession
from retrying import retry

from util import LOGGER


class Page:

    PATH = ''

    def __init__(
            self,
            base_url: furl,
            session: HTMLSession,
            payload: Dict = None
    ):
        self.base_url: furl = base_url
        self.session: HTMLSession = session
        self.payload: Dict = payload
        self.url: str = self.base_url.set(path=self.PATH)

    @retry(wait_fixed=500, stop_max_attempt_number=5)
    def get(self) -> HTMLResponse:
        LOGGER.debug(msg=f"GETing url: {self.url}")
        response: HTMLResponse = self.session.get(url=self.url,
                                                  headers=self.session.headers)
        return response

    @property
    def html(self) -> HTML:
        return self.get().html

    def save_page(self, file_name: str = "test.html"):
        """Helper function to save page as an html file."""
        with open(file_name, "w") as f:
            f.write(self.html.html)

    @retry(wait_fixed=500, stop_max_attempt_number=5)
    def post(self) -> HTMLResponse:
        """Make post request to page."""
        LOGGER.debug(msg=f"POSTing to url: {self.url}")
        response: HTMLResponse = \
            self.session.post(url=self.url,
                              headers=self.session.headers,
                              data=self.payload)
        return response
