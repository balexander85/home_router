"""Collection of page objects that are located under the Basic tab"""
from logging import basicConfig, DEBUG, getLogger
from sys import stdout
from typing import List

from requests_html import (
    Element,
    HTML,
    HTMLResponse,
)

from pages.base_page import Page

basicConfig(
    level=DEBUG,
    format='%(levelname)7s: %(message)s',
    stream=stdout,
)
LOG = getLogger('')


class Setup:
    pass


class DHCP(Page):
    """Page that displays Hosts with IP's that are connected to network

    This page allows configuration and status of the optional
    internal DHCP server for the LAN.
    """
    PATH = 'RgDhcp.asp'
    TABLE_HEADER = 'tr[bgcolor="#4E97B9"]'
    TABLE_ROWS = 'tr[bgcolor="#E7DAAC"]'

    def list_devices(self):
        """List devices & statuses of the internal DHCP server for the LAN"""
        LOG.info('Getting list of devices on network.')
        response: HTMLResponse = self.session.get(url=self.url)
        html: HTML = response.html
        header_row: Element = html.find(self.TABLE_HEADER, first=True)
        rows: List[Element] = html.find(self.TABLE_ROWS)
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
