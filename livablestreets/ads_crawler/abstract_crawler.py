"""Interface for webcrawlers. Crawler implementations should subclass this. Based on https://github.com/flathunters/flathunter
"""
import re
# import logging
from time import sleep
import requests
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import HardwareType, Popularity

class Crawler:
    """Defines the Crawler interface. Based on https://github.com/flathunters/flathunter"""

    # __log__ = logging.getLogger('housing_crawler')

    def __init__(self):
        self.base_url  = None

    user_agent_rotator = UserAgent(popularity=[Popularity.COMMON.value],
                                   hardware_types=[HardwareType.COMPUTER.value])

    HEADERS = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent_rotator.get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;'
                  'q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Language': 'en-US,en;q=0.9',
        'referer':'https://www.google.com/'
    }

    def rotate_user_agent(self):
        """Choose a new random user agent"""
        self.HEADERS['User-Agent'] = self.user_agent_rotator.get_random_user_agent()

    def get_soup_from_url(self, url):
        """Creates a Soup object from the HTML at the provided URL"""

        # Rotate the agent to avoid getting stuck
        self.rotate_user_agent()

        # Execute request and obtain soup object
        resp = requests.get(url, headers=self.HEADERS)
        print(f"Got response code {resp.status_code}")

        return BeautifulSoup(resp.content, 'html.parser')

    def extract_data(self, soup):
        """Should be implemented in subclass"""
        raise NotImplementedError

    def parse_urls(self, location_name, page_number, filters):
        """Should be implemented in subclass"""
        raise NotImplementedError

    def crawl_all_pages(self, location_name):
        """Should be implemented in subclass"""
        raise NotImplementedError
