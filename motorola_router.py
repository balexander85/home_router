
import configparser
import requests
from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read("config.txt")

user = config.get("configuration", "user")
password = config.get("configuration", "password")
router_url = config.get("configuration", "router_url")

forwarding_url = f"{router_url}/goform/RgForwarding"


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

    def reboot(self):
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


class Forwarding:
    """
        NEED TO IMPLEMENT Add port forwarding

        PortForwardingCreateRemove    0
        PortForwardingLocalIp    XXX.XXX.XXX.XXX
        PortForwardingLocalStartPort    21
        PortForwardingLocalEndPort    21
        PortForwardingExtIp    0.0.0.0
        PortForwardingExtStartPort    21
        PortForwardingExtEndPort    21
        PortForwardingProtocol    4
        PortForwardingDesc    FTP+Cloud
        PortForwardingEnabled    0
        PortForwardingApply    2
        PortForwardingTable    0

    """
    NotImplementedError("Need to implement")


if __name__ == '__main__':

    with Router() as r:
        r.list_devices()
