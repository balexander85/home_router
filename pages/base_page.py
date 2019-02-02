"""Base page object containing boilerplate code to be used with all pages"""

from furl import furl
from requests_html import HTMLSession


class Page:
    """Page that displays Hosts with IP's that are connected to network

    This page allows configuration and status of the optional
    internal DHCP server for the LAN.
    """
    PATH = ''

    def __init__(self, base_url: furl, session: HTMLSession):
        self.session = session
        self.url = base_url.add(path=self.PATH)
