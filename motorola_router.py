"""Module to access Motorola Router with python request_html

Accessing my home router via local control because for some reason the WiFi
drops unexpectedly and I would like to restart router programmatically.
"""
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from logging import basicConfig, DEBUG, getLogger
from pathlib import Path
from typing import List
from sys import stdout

from retrying import retry
from requests_html import (
    Element,
    HTML,
    HTMLResponse,
    HTMLSession,
)


basicConfig(
    level=DEBUG,
    format='%(levelname)7s: %(message)s',
    stream=stdout,
)
LOG = getLogger('')


def parse_args() -> Namespace:
    """Setting command line args and returning parsed args."""
    parser = ArgumentParser(
        description='Command line tool to send commands to the local '
                    'router (reboot, list devices).'
    )
    parser.add_argument(
        '-V', '--version', action='version', version='%(prog)s 1.0'
    )
    parser.add_argument(
        '-R', '--reboot', action='store_true', default=False,
        dest='reboot_switch',
        help='Use -R or --reboot to send reboot command to router.'
    )
    return parser.parse_args()


def load_config() -> ConfigParser:
    """Loading configuration file into ConfigParser object"""
    file_path = Path(__file__).parent
    config_file_path = file_path / 'config.txt'
    config_parser = ConfigParser()
    config_parser.read(config_file_path)
    return config_parser


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


config = load_config()
ROUTER_USERNAME = config.get('configuration', 'user')
ROUTER_PASSWORD = config.get('configuration', 'password')
ROUTER_URL = config.get('configuration', 'router_url')


class Router:
    """Motorola Router"""

    FORWARDING_URL = '{}/goform/RgForwarding'
    TABLE_HEADER = 'tr[bgcolor="#4E97B9"]'
    TABLE_ROWS = 'tr[bgcolor="#E7DAAC"]'
    HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;'
                  'q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
    }

    def __init__(self, user: str, password: str, url: str):
        self.session: HTMLSession = HTMLSession()
        self.user_name: str = user
        self.password: str = password
        self.url: str = url
        self.ip_address: str = self.url.replace('http://', '')
        self.params = {'loginUsername': user, 'loginPassword': password}

    def __enter__(self):
        """Login to router admin site."""
        self.session.get(url=ROUTER_URL)
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Logout of router admin site."""
        self.logout()

    @property
    def login_url(self) -> str:
        """Return url for login page."""
        return f'{self.url}/goform/login'

    @property
    def logout_url(self) -> str:
        """Return url for logout page."""
        return f'{self.url}/logout.asp'

    @property
    def reboot_url(self) -> str:
        """Return url for reboot url."""
        return f'{self.url}/goform/RgConfiguration'

    def login(self):
        """Login in to router admin"""
        LOG.info('LOGGING IN...')
        self.session.post(
            url=self.login_url, headers=self.HEADERS, data=self.params
        )
        LOG.info('LOGGED IN...')

    @retry(wait_fixed=500, stop_max_attempt_number=5)
    def logout(self):
        """Logout in to router admin"""
        LOG.info('LOGGING OUT...')
        self.session.get(url=self.logout_url)
        LOG.info('LOGGED OUT...')

    def reboot(self):
        """Send command to reboot router"""
        LOG.info('Rebooting....')
        self.session.post(url=self.reboot_url, timeout=5)
        LOG.info('Reboot command completed.')

    def disable_wifi(self):
        """Disable WiFi"""
        LOG.info('DISABLING WIFI...')
        wireless_url = f'{self.url}/wlanRadio.asp'
        wireless_form = f'{self.url}/goform/wlanRadio'
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
        wireless_url = f'{self.url}/wlanRadio.asp'
        wireless_form = f'{self.url}/goform/wlanRadio'
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
        """List devices & statuses of the internal DHCP server for the LAN"""
        LOG.info('Getting list of devices on network.')
        rhdcp_url: str = f'{self.url}/RgDhcp.asp'
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
    command_line_args = parse_args()

    with Router(
            user=ROUTER_USERNAME,
            password=ROUTER_PASSWORD,
            url=ROUTER_URL
    ) as r:
        if command_line_args.reboot_switch:
            LOG.info('REBOOTING.....')
            # r.reboot()
            # r.disable_wifi()
        else:
            LOG.info('GETTING LIST OF DEVICES')
            r.list_devices()
