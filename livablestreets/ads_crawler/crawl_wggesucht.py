import re
import time
import requests
import json
# import logging
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import pandas as pd
import numpy as np

from livablestreets.ads_crawler.abstract_crawler import Crawler
from livablestreets.string_utils import remove_prefix, standardize_characters, capitalize_city_name, german_characters
from livablestreets.utils import save_file, get_file
from livablestreets.params import dict_city_number_wggesucht
from livablestreets.ads_crawler.geocoding_addresses import geocoding_df

from config.config import ROOT_DIR



class CrawlWgGesucht(Crawler):
    """Implementation of Crawler interface for WgGesucht"""

    # __log__ = logging.getLogger('housing_crawler')

    def __init__(self):
        self.base_url = 'https://www.wg-gesucht.de/'

        # logging.getLogger("requests").setLevel(logging.WARNING)
        self.existing_findings = []

        # The number after the name of the city is specific to the city
        self.dict_city_number_wggesucht = dict_city_number_wggesucht

    def url_builder(self, location_name, page_number,
                    filters):
        # Make sure that the city name is correct
        location_name_for_url = capitalize_city_name(standardize_characters(location_name, separator=' ')).replace(' ', '-')

        filter_code = []

        if "wg-zimmer" in filters:
            filter_code.append('0')
        if "1-zimmer-wohnungen" in filters:
            filter_code.append('1')
        if "wohnungen" in filters:
            filter_code.append('2')
        if "haeuser" in filters:
            filter_code.append('3')

        filter_code = '+'.join(filter_code)
        filter_code = ''.join(['.']+[filter_code]+['.1.'])

        return self.base_url +\
            "-und-".join(filters) +\
                '-in-'+ location_name_for_url + '.' + self.dict_city_number_wggesucht.get(location_name) +\
                    filter_code + str(page_number) + '.html'

    def get_soup_from_url(self, url, sess, sleep_times = (1,2)):
        """
        Creates a Soup object from the HTML at the provided URL

        Overwrites the method inherited from abstract_crawler. This is
        necessary as we need to reload the page once for all filters to
        be applied correctly on wg-gesucht.
        """

        # Sleeping for random seconds to avoid overload of requests
        sleeptime = np.random.uniform(sleep_times[0], sleep_times[1])
        print(f"Waiting {round(sleeptime,2)} seconds to try connecting to:\n{url}")
        time.sleep(sleeptime)

        # Setup an agent
        print('Rotating agent')
        self.rotate_user_agent()

        # Second page load
        print(f"Connecting to page...")
        resp = sess.get(url, headers=self.HEADERS)
        print(f"Got response code {resp.status_code}")

        # Return soup object
        return BeautifulSoup(resp.content, 'html.parser')

    def get_soup_from_url_urllib(self, url, sleep_times = (1,2)):
        """
        Creates a Soup object from the HTML at the provided URL using urllib library.
        Implemented as an alternative for requesting with requests' library Session. It doesn't seem to have worked however....
        """

        # Sleeping for random seconds to avoid overload of requests
        sleeptime = np.random.uniform(sleep_times[0], sleep_times[1])
        print(f"Waiting {round(sleeptime,2)} seconds to try connecting with urllib to:\n{url}")
        time.sleep(sleeptime)

        # Setup an agent
        self.rotate_user_agent()

        req = Request(url , headers=self.HEADERS)
        webpage = urlopen(req).read()

        # Return soup object
        return BeautifulSoup(webpage, 'html.parser')

    def extract_data(self, soup):
        """Extracts all exposes from a provided Soup object"""

        # Find ads
        findings = soup.find_all(lambda e: e.has_attr('id') and e['id'].startswith('liste-'))
        findings_list = [
        e for e in findings if e.has_attr('class') and not 'display-none' in e['class']
        ]
        print(f"Extracted {len(findings_list)} entries")
        return findings_list

    def request_soup(self,url, sess):
        '''
        Extract findings with requests library
        '''
        soup = self.get_soup_from_url(url, sess=sess)
        return self.extract_data(soup)

    def parse_urls(self, location_name, number_pages, filters, sleep_time = 1800):
        """Parse through all exposes in self.existing_findings to return a formated dataframe.
        """
        # Process city name to match url
        location_name = capitalize_city_name(location_name)

        print(f'Processed location name. Searching for: {location_name}')


        # Create list with all urls for crawling
        list_urls = [self.url_builder(location_name = location_name, page_number = page,
                    filters = filters) for page in range(number_pages)]

        print(f'Created {len(list_urls)} urls for crawling')

        print('Opening session')
        sess = requests.session()
        # First page load to set filters; response is discarded
        print('Making first call to set filters (this is ignored)')
        sess.get(list_urls[0], headers=self.HEADERS)


        # Crawling each page and adding findings to self.new_findings list
        for url in list_urls:
            if sleep_time>0:
                # Loop until reCAPTCH is gone
                success = False
                while not success:
                    new_findings = self.request_soup(url, sess=sess)
                    if len(new_findings) == 0:
                        print(f'Sleeping for {sleep_time} to wait for reCAPTCH to disappear....')
                        time.sleep(sleep_time)
                        sleep_time += sleep_time
                    else:
                        success = True
            else:
                new_findings = self.request_soup(url)

                # # Try again with urllib library
                # if len(new_findings) == 0:
                #     soup = self.get_soup_from_url_urllib(url)
                #     new_findings = self.extract_data(soup)
            if len(new_findings) == 0:
                print('====== Stopped retrieving pages. Probably stuck at Recaptcha ======')
                break

            self.existing_findings = self.existing_findings + (new_findings)

    def save_df(self, df, location_name):
        ## First obtain older ads for updating table
        try:
            old_df = get_file(file_name=f'{location_name}_ads.csv',
                            local_file_path=f'livablestreets/data/{location_name}/Ads')
            print('Obtained older ads')
        except:
            old_df = pd.DataFrame(columns = df.columns)
            print('No older ads found')

        # Exclude weird ads without an id number
        df = df[df['id'] != 0]

        # Add new ads to older list and discard copies
        df = pd.concat([df,old_df]).drop_duplicates().reset_index(drop=True)
        print(f'''{len(df)-len(old_df)} new ads were added to the list.\n
                    There are now {len(df)} ads in {location_name}_ads.csv.''')

        # Save updated list
        save_file(df = df, file_name=f'{location_name}_ads.csv',
                  local_file_path=f'livablestreets/data/{location_name}/Ads')

    def crawl_all_pages(self, location_name, number_pages=3,
                    filters = ["wg-zimmer","1-zimmer-wohnungen","wohnungen","haeuser"],
                    path_save = None):
        if path_save is None:
            path_save = f'livablestreets/data/{standardize_characters(location_name)}/Ads'

        # Obtaining pages
        self.parse_urls(location_name = location_name, number_pages = number_pages,
                    filters = filters)

        # Extracting info of interest from pages
        print(f"Crawling {len(self.existing_findings)} ads")


        try:
            old_df = get_file(file_name=f'{location_name}_ads.csv',
                            local_file_path=f'livablestreets/data/{location_name}/Ads')
        except FileNotFoundError:
            old_df=pd.DataFrame({'url':[]})

        entries = []
        for row in self.existing_findings:

            ### Exclude commercial offers from companies with several rooms in same building
            try:
                test_text = row.find("div", {"class": "col-xs-9"})\
            .find("span", {"class": "label_verified ml5"}).text
                landlord_type = test_text
            except AttributeError:
                landlord_type = 'Private'

            # Ad title and url
            title_row = row.find('h3', {"class": "truncate_title"})
            title = title_row.text.strip()
            ad_url = self.base_url + remove_prefix(title_row.find('a')['href'], "/")

            # Save time by not parsing old ads
            # To check if add is old, check if the url already exist in the table
            if ad_url in old_df['url']:
                    pass

            ## Room details and address
            detail_string = row.find("div", {"class": "col-xs-11"}).text.strip().split("|")
            details_array = list(map(lambda s: re.sub(' +', ' ',
                                                    re.sub(r'\W', ' ', s.strip())),
                                    detail_string))

            # Offer type
            type_offer = details_array[0]

            # Number of rooms
            rooms_tmp = re.findall(r"^\d*[., ]?\d*", details_array[0])[0] # Finds int or dec in beginning of word. Needed to deal with '2.5', '2,5' or '2 5' sized flats
            rooms_tmp = float(rooms_tmp.replace(',','.').replace(' ','.'))
            if 'WG' in type_offer:
                type_offer = 'WG'
                rooms = 1
            else:
                rooms = rooms_tmp if rooms_tmp>0 else 0

            # Address
            address = details_array[2] + ', ' + details_array[1]

            # Flatmates
            try:
                flatmates = row.find("div", {"class": "col-xs-11"}).find("span", {"class": "noprint"})['title']
                flatmates_list = [int(n) for n in re.findall('[0-9]+', flatmates)]
            except TypeError:
                flatmates_list = [0,0,0,0]

            ### Price, size and date
            numbers_row = row.find("div", {"class": "middle"})

            # Price
            price = numbers_row.find("div", {"class": "col-xs-3"}).text.strip().split(' ')[0]

            # Offer availability dates
            availability_dates = re.findall(r'\d{2}.\d{2}.\d{4}',
                            numbers_row.find("div", {"class": "text-center"}).text)

            # Size
            size = re.findall(r'\d{1,4}\sm²',
                            numbers_row.find("div", {"class": "text-right"}).text)
            if len(size) == 0:
                size = ['0']

            size = re.findall('^\d+', size[0])[0]

            ## Publication date
            # Minutes and hours are in color green (#218700), while days are in color grey (#898989)
            try:
                published_time = row.find("div", {"class": "col-xs-9"})\
            .find("span", {"style": "color: #218700;"}).text
            except:
                published_time = row.find("div", {"class": "col-xs-9"})\
            .find("span", {"style": "color: #898989;"}).text

            # Format it for the date ignoring time
            if 'Minut' in published_time or 'Stund' in published_time or 'Sekund' in published_time:
                published_time = time.strftime("%d.%m.%Y", time.localtime())
            elif 'Tag' in published_time:
                day_diff = int(re.findall('[0-9]+', published_time)[0])
                past_day = int(time.strftime("%d", time.localtime())) - day_diff
                published_time = f"{str(past_day)}."+time.strftime(f"%m.%Y", time.localtime())
            else:
                published_time = published_time.split(' ')[1]





            ### Create dataframe with info
            details = {
                'id': int(ad_url.split('.')[-2]),
                'url': str(ad_url),
                'type_offer': str(type_offer),
                'landlord_type': str(landlord_type),
                'title': str(title),
                'price_euros': int(price),
                'size_sqm': int(size),
                'available_rooms': float(rooms),
                'WG_size': int(flatmates_list[0]),
                'available_spots_wg': int(flatmates_list[0]-flatmates_list[1]-flatmates_list[2]-flatmates_list[3]),
                'male_flatmates': int(flatmates_list[1]),
                'female_flatmates': int(flatmates_list[2]),
                'diverse_flatmates': int(flatmates_list[3]),
                'published_on': published_time,
                'address': str(address),
                'city': str(german_characters(location_name)),
                'crawler': 'WG-Gesucht'
            }
            if len(availability_dates) == 2:
                details['available from'] = str(availability_dates[0])
                details['available to'] = str(availability_dates[1])
            elif len(availability_dates) == 1:
                details['available from'] = str(availability_dates[0])
                details['available to'] = np.nan

            entries.append(details)

            # self.__log__.debug('extracted: %s', entries)

        # Reset existing_findings
        self.existing_findings = []

        df = pd.DataFrame(entries)

        if len(df)>0:
            # Geocode coordinates of ad
            df = geocoding_df(df=df, column='address')

            # Save info as df in csv format
            self.save_df(df=df, location_name=standardize_characters(location_name))
        else:
            print('===== Something went wrong. No entries were found. =====')
        return df

    def long_search(self):
        '''
        This method runs the search for ads constantly and saves results in .csv file until a defined date.
        '''
        today = time.strftime(f"%d.%m.%Y", time.localtime())
        day_stop_search = '31.07.2022'
        while today != day_stop_search:
            today = time.strftime(f"%d.%m.%Y", time.localtime())

            # Check if between 00 and 8am, and sleep in case it is
            hour_of_search = int(time.strftime(f"%H", time.localtime()))
            while hour_of_search >= 0 and hour_of_search <= 8:
                hour_of_search = int(time.strftime(f"%H", time.localtime()))
                print(f'It is now {hour_of_search}am. Program sleeping between 00 and 08am.')
                time.sleep(3600)

            for city in list(dict_city_number_wggesucht.keys())[0:]:
                self.crawl_all_pages(location_name = city, number_pages = 10,
                            filters = ["wg-zimmer","1-zimmer-wohnungen","wohnungen","haeuser"])



if __name__ == "__main__":
    test = CrawlWgGesucht()

    # test.crawl_all_pages(location_name = 'Aachen', number_pages = 1,
    #                 filters = ["wg-zimmer","1-zimmer-wohnungen","wohnungen","haeuser"])


    today = time.strftime(f"%d.%m.%Y", time.localtime())
    day_stop_search = '31.07.2022'
    while today != day_stop_search:
        today = time.strftime(f"%d.%m.%Y", time.localtime())

        # Check if between 00 and 8am, and sleep in case it is
        hour_of_search = int(time.strftime(f"%H", time.localtime()))
        while hour_of_search >= 0 and hour_of_search <= 8:
            hour_of_search = int(time.strftime(f"%H", time.localtime()))
            print(f'It is now {hour_of_search}am. Program sleeping between 00 and 08am.')
            time.sleep(3600)

        for city in list(dict_city_number_wggesucht.keys())[0:]:
            test.crawl_all_pages(location_name = city, page_number = 10,
                        filters = ["wg-zimmer","1-zimmer-wohnungen","wohnungen","haeuser"])
