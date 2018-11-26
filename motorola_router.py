"""Accessing home router via local control because for some reason the WiFi
   drops unexpectedly and I would like to restart router programmatically.
"""
import argparse
import logging
from typing import List
import sys

import configparser
from retrying import retry
from requests_html import (
    Element,
    HTML,
    HTMLResponse,
    HTMLSession,
    TimeoutError
)


parser = argparse.ArgumentParser(
    description='Command line tool to send commands to the local '
                'router (reboot, list devices).'
)
parser.add_argument(
    '-V', '--version', action='version', version='%(prog)s 1.0'
)
parser.add_argument(
    '-R', '--reboot', action='store_true', default=False, dest='reboot_switch',
    help='Use -R or --reboot to send reboot command to router.'
)
command_line_args = parser.parse_args()

config = configparser.ConfigParser()
config.read('config.txt')
ROUTER_USERNAME = config.get('configuration', 'user')
ROUTER_PASSWORD = config.get('configuration', 'password')
ROUTER_URL = config.get('configuration', 'router_url')
LOCAL_IP = ROUTER_URL.replace('http://', '')
FORWARDING_URL = f'{ROUTER_URL}/goform/RgForwarding'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s: %(message)s',
    stream=sys.stdout,
)

LOG = logging.getLogger('')

headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                      'image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            # 'Connection': 'keep-alive',
            # 'Content-Length': '175',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/67.0.3396.99 Safari/537.36',
        }


def save_page(html: HTML, file_name: str = "test.html"):
    """Helper function to save page as an html file."""
    with open(file_name, "w") as f:
        f.write(html.html)


def get_page_selected_selects_as_dict(html: HTML) -> dict:
    """Finds all of the selects on page and parses the select name as key
    and the selected option as the value"""
    return {
        e.attrs['name']: e.find(
            'option[selected="selected"]', first=True).text
        for e in html.find('select')
    }


class Router:
    """Motorola Router"""

    TABLE_HEADER = 'tr[bgcolor="#4E97B9"]'
    TABLE_ROWS = 'tr[bgcolor="#E7DAAC"]'

    def __init__(self):
        super(Router, self).__init__()
        self.session: HTMLSession = HTMLSession()

    def __enter__(self):
        """Login in to router admin"""
        self.session.get(url=ROUTER_URL)
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

    @retry(wait_fixed=500, stop_max_attempt_number=5)
    def logout(self):
        """Logout in to router admin"""
        LOG.info('LOGGING OUT...')
        logout_request_url = f'{ROUTER_URL}/logout.asp'
        try:
            self.session.get(url=logout_request_url)
        except TimeoutError as e:
            LOG.info(f'Error: {e} attempting to log out.')

    def reboot(self):
        """Send command to reboot router"""
        LOG.info('Rebooting')
        reboot_url = f'{ROUTER_URL}/goform/RgConfiguration'
        try:
            self.session.post(url=reboot_url, timeout=5)
        except TimeoutError as e:
            LOG.info(f'Error: {e} attempting to log out.')

    def disable_wifi(self):
        """Disable WiFi"""
        LOG.info('DISABLING WIFI...')
        wireless_url = f'{ROUTER_URL}/wlanRadio.asp'
        wireless_form = f'{ROUTER_URL}/goform/wlanRadio'
        response: HTMLResponse = self.session.get(wireless_url)
        html = response.html
        current_params = get_page_selected_selects_as_dict(html=html)
        current_params.update({'WirelessEnable': '0'})
        # current_params = {'WirelessEnable': '0'}
        post_response: HTMLResponse = self.session.post(
            url=wireless_form, data=current_params
        )
        post_response.raise_for_status()
        response: HTMLResponse = self.session.get(wireless_url)
        next_page = response.html
        current_params = get_page_selected_selects_as_dict(html=next_page)
        assert current_params['WirelessEnable'] == '0'

    def enable_wifi(self):
        """Disable WiFi"""
        LOG.info('DISABLING WIFI...')
        wireless_url = f'{ROUTER_URL}/wlanRadio.asp'
        wireless_form = f'{ROUTER_URL}/goform/wlanRadio'
        response: HTMLResponse = self.session.get(wireless_url)
        html = response.html
        current_params = get_page_selected_selects_as_dict(html=html)
        current_params.update({'WirelessEnable': '1'})
        response: HTMLResponse = self.session.post(
            url=wireless_form, data=current_params
        )
        next_page = response.html
        current_params = get_page_selected_selects_as_dict(html=next_page)
        assert current_params['WirelessEnable'] == '1'

    def list_devices(self):
        """List all the devices and statuses of the internal
           DHCP server for the LAN
        """
        LOG.info('Getting list of devices on network.')
        rhdcp_url: str = f'{ROUTER_URL}/RgDhcp.asp'
        response: HTMLResponse = self.session.get(url=rhdcp_url)
        html: HTML = response.html
        header_row: Element = html.find(self.TABLE_HEADER, first=True)
        rows: List[Element] = html.find(self.TABLE_ROWS)
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
            # r.reboot()
            # r.disable_wifi()
        else:
            LOG.info('GETTING LIST OF DEVICES')
            r.list_devices()
