
import logging
import sys

import configparser
import requests
from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read("config.txt")

user = config.get("configuration", "user")
password = config.get("configuration", "password")
router_url = config.get("configuration", "router_url")
local_ip = router_url.replace("http://", "")
forwarding_url = f"{router_url}/goform/RgForwarding"


logging.basicConfig(
    level=logging.ERROR,
    format="%(levelname)7s: %(message)s",
    stream=sys.stdout,
)

LOG = logging.getLogger("")


class Router:
    """Motorola Router"""

    def __init__(self):
        super(Router, self).__init__()
        self.session = requests.Session()
        self.headers = {
            "Accept":
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,*/*;q=0.8",
            "Accept-Encoding":
                "gzip, deflate"
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
        login_request_url = f"{router_url}/goform/login"
        return self.session.post(
            login_request_url, headers=self.headers, params=self.params
        )

    def logout(self) -> requests.Response:
        """Logout in to router admin"""
        logout_request_url = f"{router_url}/logout.asp"
        return self.session.get(logout_request_url, headers=self.headers)

    def restart_wifi(self):
        """Send command to restart Wifi"""
        pass

    def _reboot(self):
        """Send command to reboot router"""
        reboot_url = f"{router_url}/goform/RgConfiguration"
        return self.session.post(
            reboot_url, headers=self.headers, params={"SaveChanges": "Reboot"}
        )

    def list_devices(self):
        """
            List all the devices and status of
            the internal DHCP server for the LAN
        """
        rhdcp_url = f"{router_url}/RgDhcp.asp"
        table_header_bgcolor = "#4E97B9"
        table_row_bgcolor = "#E7DAAC"
        response = self.session.get(
            rhdcp_url, headers=self.headers, params=self.params
        )
        soup = BeautifulSoup(response.content, "html.parser")
        table_header_map = {
            str(i): x.text for i, x in enumerate(
                soup.find("tr", attrs={'bgcolor': table_header_bgcolor})('td')
        )
        }
        rows = soup.findAll("tr", attrs={'bgcolor': table_row_bgcolor})
        print("    ".join(table_header_map.values()))
        for row in rows:
            print("    ".join([x.text for x in row('td')]))


class Forwarding(Router):
    """
        Setup port forwarding on the router to allow outbound connections
    """

    def __init__(self):
        super(Forwarding, self).__init__()
        self.forward_headers = {
            "Accept":
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding":
                "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Content-Length": "332",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": f"{local_ip}",
            "Origin": f"{router_url}",
            "Referer": f"{router_url}/RgForwarding.asp",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/63.0.3239.132 Safari/537.36"
        }

    @staticmethod
    def form_data(ip: str, port: str, desc: str, enabled: int):
        return dict(
            PortForwardingCreateRemove="0",
            PortForwardingLocalIp=ip,
            PortForwardingLocalStartPort=port,
            PortForwardingLocalEndPort=port,
            PortForwardingExtIp="0.0.0.0",
            PortForwardingExtStartPort=port,
            PortForwardingExtEndPort=port,
            PortForwardingProtocol="4",
            PortForwardingDesc=desc,
            PortForwardingEnabled=enabled,
            PortForwardingApply="2",
            PortForwardingTable="0",
        )

    def get_forwarded_ips(self):
        """
            List all the devices and status of
            the internal DHCP server for the LAN
        """
        forwarding_url = f"{router_url}/RgForwarding.asp"
        response = self.session.get(
            forwarding_url, headers=self.headers, params=self.params
        )
        soup = BeautifulSoup(response.content, "html.parser")
        table_header = [row.text for row in soup.select(
            ".table_data12 table tr th"
        )][2:11]
        rows = [row for row in soup.select(".table_data12 table tr")][2:]
        print("    ".join(table_header))
        for row in rows:
            print("    ".join([x.text for x in row('td')]))

    def update(self, ip: str, port: str, desc: str, enabled: int):
        """
            Update existing IP Forwarding settings
        """
        form_data = self.form_data(
            ip=ip, port=port, desc=desc, enabled=enabled
        )
        return self.session.post(
            forwarding_url, headers=self.forward_headers, data=form_data
        )


if __name__ == '__main__':

    with Router() as r:
        r.list_devices()

    # with Forwarding() as f:
    #     f.get_forwarded_ips()
    #     f.update(ip="192.168.0.7", port="21", desc="FTP Cloud No", enabled=0)
    #     f.get_forwarded_ips()
