import json
from bs4 import BeautifulSoup

from bijou.exceptions import ParserException


def get_bs4_parser(response, html_parser='lxml', parse_only=None):
    return BeautifulSoup(response, html_parser, parse_only=parse_only)


def get_json_parser(response):
    try:
        return json.loads(response)
    except ValueError:
        raise ParserException('Couldn\'t load json response')
