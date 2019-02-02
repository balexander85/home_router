"""Util.py"""

from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from pathlib import Path

from requests_html import HTML


def get_page_selected_selects_as_dict(html: HTML) -> dict:
    """Finds all of the selects on page and parses the select name as key
    and the selected option as the value"""
    return {
        e.attrs['name']: e.find(
            'option[selected="selected"]', first=True).text
        for e in html.find('select')
    }


def load_config() -> ConfigParser:
    """Loading configuration file into ConfigParser object"""
    file_path = Path(__file__).parent
    config_file_path = file_path / 'config.txt'
    config_parser = ConfigParser()
    config_parser.read(config_file_path)
    return config_parser


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


def save_page(html: HTML, file_name: str = "test.html"):
    """Helper function to save page as an html file."""
    with open(file_name, "w") as f:
        f.write(html.html)
