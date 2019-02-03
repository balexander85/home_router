"""Collection of page objects that are located under the Basic tab"""
from typing import List

from requests_html import (
    Element,
)

from pages.base_page import Page
from util import LOGGER


class Setup:
    pass


class DHCP(Page):
    """Page that displays Hosts with IP's that are connected to network

    This page allows configuration and status of the optional
    internal DHCP server for the LAN.
    """
    PATH = 'RgDhcp.asp'

    def list_devices(self):
        """List devices & statuses of the internal DHCP server for the LAN"""
        LOGGER.info('Getting list of devices on network.')
        header_row: Element = self.html.find(self.TABLE_HEADER, first=True)
        rows: List[Element] = self.html.find(self.TABLE_ROWS)
        table_header_map: dict = {
            str(i): x.text for i, x in enumerate(header_row.find('td'))
        }
        print('    '.join(table_header_map.values()))
        for row in rows:
            print('    '.join([e.text for e in row.find('td')]))


class DDNS:
    pass


class Backup:
    pass
