"""Module to access Motorola Router with python request_html

Accessing my home router via local control because for some reason the WiFi
drops unexpectedly and I would like to restart router programmatically.
"""

__author__ = 'Brian Alexander'

from typing import Dict

from furl import furl
from requests_html import (
    HTMLResponse,
    HTMLSession,
)

from pages import DHCP, Login, Logout, Configuration
from util import (
    LOGGER,
    get_page_selected_selects_as_dict,
    load_config,
    parse_args,
    save_page
)


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
        self.url: furl = furl(url)
        self.ip_address: str = self.url.host
        self.params: Dict = {'loginUsername': user, 'loginPassword': password}

    def __enter__(self):
        """Login to router admin site."""
        login_page: Login = Login(base_url=self.url,
                                  session=self.session,
                                  payload=self.params)
        login_page.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Logout of router admin site."""
        logout_page: Logout = Logout(base_url=self.url,
                                     session=self.session)
        logout_page.logout()

    def reboot(self):
        """Send command to reboot router"""
        LOGGER.info('Rebooting....')
        config_page = Configuration(base_url=self.url, session=self.session)
        config_page.reboot()
        LOGGER.info('Reboot command completed.')

    def disable_wifi(self):
        """Disable WiFi"""
        LOGGER.info('DISABLING WIFI...')
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
        LOGGER.info('DISABLING WIFI...')
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
        dhcp = DHCP(base_url=self.url, session=self.session)
        dhcp.list_devices()


if __name__ == '__main__':
    command_line_args = parse_args()

    with Router(
            user=ROUTER_USERNAME,
            password=ROUTER_PASSWORD,
            url=ROUTER_URL
    ) as r:
        if command_line_args.reboot_switch:
            LOGGER.info('REBOOTING.....')
            r.reboot()
            # r.disable_wifi()
        else:
            r.list_devices()
