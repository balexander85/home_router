"""Accessing home router via local control because for some reason the WiFi
   drops unexpectedly and I would like to restart router programmatically.
"""
import argparse
import logging
from typing import List
import sys

import configparser
from requests_html import HTML, Element, HTMLResponse, HTMLSession


parser = argparse.ArgumentParser(
    description='Command line tool to send commands to the local '
                'router (reboot, list devices).'
)
parser.add_argument('--version', action='version', version='%(prog)s 1.0')
parser.add_argument('-R', action='store_true', default=False,
                    dest='reboot_switch',
                    help='Use -R to send reboot command to router.')
command_line_args = parser.parse_args()

config = configparser.ConfigParser()
config.read('config.txt')
ROUTER_USERNAME = config.get('configuration', 'user')
ROUTER_PASSWORD = config.get('configuration', 'password')
ROUTER_URL = config.get('configuration', 'router_url')
LOCAL_IP = ROUTER_URL.replace('http://', '')
FORWARDING_URL = f'{ROUTER_URL}/goform/RgForwarding'

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)7s: %(message)s',
    stream=sys.stdout,
)

LOG = logging.getLogger('')


class Router:
    """Motorola Router"""

    def __init__(self):
        super(Router, self).__init__()
        self.session: HTMLSession = HTMLSession()

    def __enter__(self):
        """Login in to router admin"""
        self.login()
        LOG.info('LOGGED IN...')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Logout in to router admin"""
        self.logout()

    def login(self):
        """Login in to router admin"""
        LOG.info('LOGGING IN...')
        login_request_url = f'{ROUTER_URL}/goform/login'
        self.session.post(url=login_request_url)

    def logout(self):
        """Logout in to router admin"""
        LOG.info('LOGGING OUT...')
        logout_request_url = f'{ROUTER_URL}/logout.asp'
        self.session.get(url=logout_request_url)

    def _reboot(self):
        """Send command to reboot router"""
        LOG.info('Rebooting')
        reboot_url = f'{ROUTER_URL}/goform/RgConfiguration'
        self.session.post(url=reboot_url)
        exit('Rebooting.....')

    def list_devices(self):
        """List all the devices and statuses of the internal
           DHCP server for the LAN
        """
        LOG.info('Getting list of devices on network.')
        rhdcp_url = f'{ROUTER_URL}/RgDhcp.asp'
        table_header_bgcolor = '#4E97B9'
        table_row_bgcolor = '#E7DAAC'
        response: HTMLResponse = self.session.get(url=rhdcp_url)
        html: HTML = response.html
        header_row: Element = html.find(
            f'tr[bgcolor="{table_header_bgcolor}"]', first=True
        )
        rows: List[Element] = html.find(f'tr[bgcolor="{table_row_bgcolor}"]')
        table_header_map: dict = {
            str(i): x.text for i, x in enumerate(header_row.find('td'))
        }
        print('    '.join(table_header_map.values()))
        for row in rows:
            print('    '.join([e.text for e in row.find('td')]))


if __name__ == '__main__':

    with Router() as r:
        if command_line_args.reboot_switch:
            LOG.info('REBOOTING.....')
            # r._reboot()
        else:
            LOG.info('GETTING LIST OF DEVICES')
            r.list_devices()
