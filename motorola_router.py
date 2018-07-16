"""Accessing home router via local control because
   for some reason the WiFi drops unexpectedly and
   and I would like to restart router programatically.
"""
import argparse
import logging
import sys

import configparser
import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Send command to router.')
args = parser.parse_args()

config = configparser.ConfigParser()
config.read('config.txt')

user = config.get('configuration', 'user')
password = config.get('configuration', 'password')
router_url = config.get('configuration', 'router_url')
local_ip = router_url.replace('http://', '')
forwarding_url = f'{router_url}/goform/RgForwarding'


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
        self.session = requests.Session()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;i'
                      'q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate'
        }
        self.params = dict(loginUsername=user, loginPassword=password)

    def __enter__(self):
        """Login in to router admin"""
        self.login()
        return self

    def __exit__(self, *args):
        """Logout in to router admin"""
        self.logout()

    def login(self) -> requests.Response:
        """Login in to router admin"""
        login_request_url = f'{router_url}/goform/login'
        return self.session.post(
            login_request_url, headers=self.headers, params=self.params
        )

    def logout(self) -> requests.Response:
        """Logout in to router admin"""
        logout_request_url = f'{router_url}/logout.asp'
        return self.session.get(logout_request_url, headers=self.headers)

    def restart_wifi(self):
        """Send command to restart Wifi"""
        restart_wifi_url = f'{router_url}/wlanRadio.asp'
        base_params = {
            'WirelessMacAddress': 0,
            'WirelessEnable': 0,
            'OutputPower': 100,
            'Band': 2,
            'NMode': 1,
            'NSupReq': 0,
            'NBandwidth': 20,
            'ChannelNumber': 4,
            'STBCTx': 0,
            'restoreWirelessDefaults': 0,
            'commitwlanRadio': 1,
            'scanActions': 0,
            'loginUsername': user,
            'loginPassword': password
        }
        # disable WIFI
        self.session.post(
            restart_wifi_url, headers=self.headers, params=base_params
        )
        # now re-enable WIFI
        base_params.update({'WirelessEnable': 1})
        self.session.post(
            restart_wifi_url, headers=self.headers, params=base_params
        )

    def _reboot(self):
        """Send command to reboot router"""
        reboot_url = f'{router_url}/goform/RgConfiguration'
        self.session.post(
            reboot_url, headers=self.headers, params={'SaveChanges': 'Reboot'}
        )
        exit('Rebooting.....')

    def list_devices(self):
        """List all the devices and statuses of the internal
           DHCP server for the LAN
        """
        rhdcp_url = f'{router_url}/RgDhcp.asp'
        table_header_bgcolor = '#4E97B9'
        table_row_bgcolor = '#E7DAAC'
        response = self.session.get(
            rhdcp_url, headers=self.headers, params=self.params
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        table_header_map = {
            str(i): x.text for i, x in enumerate(
                soup.find('tr', attrs={'bgcolor': table_header_bgcolor})('td')
        )
        }
        rows = soup.findAll('tr', attrs={'bgcolor': table_row_bgcolor})
        print('    '.join(table_header_map.values()))
        for row in rows:
            print('    '.join([x.text for x in row('td')]))


class Forwarding(Router):
    """Setup port forwarding on the router to allow outbound connections

       Example Usage:
           with Forwarding() as f:
               f.get_forwarded_ips()
               f.update(
                   ip='192.168.0.21',
                   port='80',
                   desc='Dad Gum Dashboard',
                   enabled=1
               )
               f.get_forwarded_ips()
    """

    def __init__(self):
        super(Forwarding, self).__init__()
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Length': '332',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': local_ip,
            'Origin': router_url,
            'Referer': f'{router_url}/RgForwarding.asp',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/63.0.3239.132 Safari/537.36'
        }

    @staticmethod
    def form_data(ip: str, port: str, desc: str, enabled: int):
        return dict(
            PortForwardingCreateRemove='0',
            PortForwardingLocalIp=ip,
            PortForwardingLocalStartPort=port,
            PortForwardingLocalEndPort=port,
            PortForwardingExtIp='0.0.0.0',
            PortForwardingExtStartPort=port,
            PortForwardingExtEndPort=port,
            PortForwardingProtocol='4',
            PortForwardingDesc=desc,
            PortForwardingEnabled=enabled,
            PortForwardingApply='2',
            PortForwardingTable='0',
        )

    def get_forwarded_ips(self):
        """List all the devices and statuses of the internal DHCP servers for
           the given LAN
        """
        forwarding_url = f'{router_url}/RgForwarding.asp'
        response = self.session.get(
            forwarding_url, headers=self.headers, params=self.params
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        table_header = [row.text for row in soup.select(
            '.table_data12 table tr th'
        )][2:11]
        rows = [row for row in soup.select('.table_data12 table tr')][2:]
        print('    '.join(table_header))
        for row in rows:
            print('    '.join([x.text for x in row('td')]))

    def update(self, url: str, ip: str, port: str, desc: str, enabled: int):
        """Update existing IP Forwarding settings"""
        form_data = self.form_data(
            ip=ip, port=port, desc=desc, enabled=enabled
        )
        return self.session.post(url=url, headers=self.headers, data=form_data)


if __name__ == '__main__':

    with Router() as r:
        r.list_devices()
