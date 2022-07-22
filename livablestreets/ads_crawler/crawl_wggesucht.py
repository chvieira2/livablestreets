# from cmath import isnan
import re
import time
import requests
# import json
# import logging
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

from livablestreets.ads_crawler.abstract_crawler import Crawler
from livablestreets.string_utils import remove_prefix, simplify_address, standardize_characters, capitalize_city_name, german_characters
from livablestreets.utils import save_file, get_file
from livablestreets.params import dict_city_number_wggesucht
from livablestreets.ads_crawler.geocoding_addresses import geocoding_address

from config.config import ROOT_DIR



class CrawlWgGesucht(Crawler):
    """Implementation of Crawler interface for WgGesucht"""

    # __log__ = logging.getLogger('livablestreets')

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
        if resp.status_code != 200:
            return None
        return BeautifulSoup(resp.content, 'html.parser')

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
        if soup is None:
            return None
        return self.extract_data(soup)

    def parse_urls(self, location_name, page_number, filters, sess, sleep_time = 1800):
        """Parse through all exposes in self.existing_findings to return a formated dataframe.
        """
        # Process city name to match url
        location_name = capitalize_city_name(location_name)

        print(f'Processed location name. Searching for: {location_name}')

        # Create list with all urls for crawling
        list_urls = [self.url_builder(location_name = location_name, page_number = page_number,
                    filters = filters)]

        print(f'Created url for crawling')

        # Crawling each page and adding findings to self.new_findings list
        for url in list_urls:
            if sleep_time>0:
                # Loop until CAPTCH is gone
                success = False
                while not success:
                    new_findings = self.request_soup(url, sess=sess)
                    if new_findings is None:
                        pass
                    elif len(new_findings) == 0:
                        time_now = time.mktime(time.localtime())
                        print(f'Sleeping until {time.strftime("%H:%M", time.localtime(time_now + sleep_time))} to wait for CAPTCH to disappear....')
                        time.sleep(sleep_time)
                        sleep_time += sleep_time
                    else:
                        success = True
            else:
                new_findings = self.request_soup(url)

            if len(new_findings) == 0:
                print('====== Stopped retrieving pages. Probably stuck at CAPTCH ======')
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

        # Make sure new df and old df have same columns
        for new_column in old_df.columns:
            if new_column not in df.columns:
                df[new_column] = np.nan

        # Add new ads to older list and discard copies. Keep = first is important because wg-gesucht keeps on refreshing the post date of some ads (private paid ads?). With keep = first I keep the first entry
        df = pd.concat([df,old_df]).drop_duplicates(subset='id', keep="last").reset_index(drop=True)
        print(f'''{len(df)-len(old_df)} new ads were added to the list.\n
                    There are now {len(df)} ads in {location_name}_ads.csv.''')

        # Save updated list
        save_file(df = df, file_name=f'{location_name}_ads.csv',
                  local_file_path=f'livablestreets/data/{location_name}/Ads')
        return len(df)-len(old_df)

    def crawl_all_pages(self, location_name, number_pages,
                    filters = ["wg-zimmer","1-zimmer-wohnungen","wohnungen","haeuser"],
                    path_save = None):
        '''
        Main crawling function. Function will first connect to all pages and save findings (ads) using the parse_url method. Next, it obtain older ads table to which newer ads will be added.
        '''
        if path_save is None:
            path_save = f'livablestreets/data/{standardize_characters(location_name)}/Ads'

        print('Opening session')
        sess = requests.session()
        # First page load to set filters; response is discarded
        print('Making first call to set filters')
        url_set_filters = self.url_builder(location_name = location_name, page_number = 1,
                    filters = filters)
        sess.get(url_set_filters, headers=self.HEADERS)

        zero_new_ads_in_a_row = 0
        total_added_findings = 0
        for page_number in range(number_pages):
            # Obtaining pages
            self.parse_urls(location_name = location_name, page_number= page_number,
                        filters = filters, sess=sess)


            # Obtain older ads, or create empty table if there are no older ads
            try:
                old_df = get_file(file_name=f'{location_name}_ads.csv',
                                local_file_path=f'livablestreets/data/{location_name}/Ads')
            except FileNotFoundError:
                old_df=pd.DataFrame({'url':[]})


            # Extracting info of interest from pages
            print(f"Crawling {len(self.existing_findings)} ads")
            entries = []
            total_findings = len(self.existing_findings)
            for index in range(total_findings):
                # Print count down
                print(f'=====> Geocoded {index+1}/{total_findings}', end='\r')
                row = self.existing_findings[index]

                ### Commercial offers from companies, often with several rooms in same building
                try:
                    test_text = row.find("div", {"class": "col-xs-9"})\
                .find("span", {"class": "label_verified ml5"}).text
                    landlord_type = test_text.replace(' ','').replace('"','').replace('\n','').replace('\t','').replace(';','')
                except AttributeError:
                    landlord_type = 'Private'

                # Ad title and url
                title_row = row.find('h3', {"class": "truncate_title"})
                title = title_row.text.strip().replace('"','').replace('\n',' ').replace('\t',' ')\
                    .replace(';','')
                ad_url = self.base_url + remove_prefix(title_row.find('a')['href'], "/")

                # Save time by not parsing old ads
                # To check if add is old, check if the url already exist in the table
                if ad_url in old_df['url']:
                    pass
                else:
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
                    address = details_array[2].replace('"','').replace('\n',' ').replace('\t',' ').replace(';','')\
                        + ', ' + details_array[1].replace('"','').replace('\n',' ').replace('\t',' ').replace(';','')

                    address = simplify_address(address)


                    # Latitude and longitude
                    lat, lon = geocoding_address(address)
                    time.sleep(0.5)
                    # Try again with shorter address if first search failed
                    if pd.isnull(lat) or pd.isnull(lon):
                        # Test if there's a mispelling of lack of space in between street and house number
                        try:
                            match = re.match(r"(\D+)(\d+)(\D+)", address, re.I)
                            if match:
                                items = match.groups()
                                address = ' '.join(items).replace(' ,', ',')
                        except UnboundLocalError:
                            pass

                        try:
                            street_number = address.split(',')[0].strip().replace('  ', ' ')
                            city_name = address.split(',')[2].strip().replace('  ', ' ')
                            address_without_neigh = ', '.join([street_number, city_name]).strip().replace('  ', ' ')
                            print(f'Search did not work with "{address}". Trying with "{address_without_neigh}"')
                            time.sleep(0.5)
                            lat,lon = geocoding_address(address=address_without_neigh)
                        except IndexError:
                            print(f'Weird address format: "{address}"')
                            pass
                        # If still haven't found anything
                        if pd.isnull(lat) or pd.isnull(lon) or lat == 0 or lon == 0:
                            print('Could not find latitude and longitude.')
                            lat,lon = np.nan,np.nan
                        else:
                            print(f'Found latitude = {lat} and longitude = {lon}')


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
                    # Prevent n.a. entries in price
                    try:
                        int(price)
                    except ValueError:
                        price = 0

                    # Offer availability dates
                    availability_dates = re.findall(r'\d{2}.\d{2}.\d{4}',
                                    numbers_row.find("div", {"class": "text-center"}).text)

                    # Size
                    size = re.findall(r'\d{1,4}\sm²',
                                    numbers_row.find("div", {"class": "text-right"}).text)
                    if len(size) == 0:
                        size = ['0']

                    size = re.findall('^\d+', size[0])[0]


                    ## Publication date and time
                    # Seconds, minutes and hours are in color green (#218700), while days are in color grey (#898989)
                    try:
                        published_date = row.find("div", {"class": "col-xs-9"})\
                    .find("span", {"style": "color: #218700;"}).text
                    except:
                        published_date = row.find("div", {"class": "col-xs-9"})\
                    .find("span", {"style": "color: #898989;"}).text

                    # For ads published mins or secs ago, publication time is the time of the search
                    hour_of_search = int(time.strftime(f"%H", time.localtime()))
                    if 'Minut' in published_date or 'Sekund' in published_date:
                        published_date = time.strftime("%d.%m.%Y", time.localtime())
                        published_time = hour_of_search

                    # For ads published hours ago, publication time is the time of search minus the hours difference. That might lead to negative time of the day and that's corrected below. That could also lead to publication date of 00, and that's also corrected below.
                    elif 'Stund' in published_date:
                        hour_diff = int(re.findall('[0-9]+', published_date)[0])
                        published_time = hour_of_search - hour_diff
                        if published_time < 0:
                            # Fix publication hour
                            published_time = 24 + published_time
                            # Fix publication date to the day before the day of the search
                            published_date = time.strftime("%d.%m.%Y", time.localtime(time.mktime(time.localtime())-24*60*60))

                        else:
                            published_date = time.strftime("%d.%m.%Y", time.localtime())

                    # For ads published days ago, publication time is NaN
                    elif 'Tag' in published_date:
                        day_diff = int(re.findall('[0-9]+', published_date)[0])
                        published_date = time.strftime("%d.%m.%Y", time.localtime(time.mktime(time.localtime())-day_diff*24*60*60))
                        published_time = np.nan

                    # For ads published at specified date (ads older than 5 days), publication time is NaN
                    else:
                        published_date = published_date.split(' ')[1]
                        published_time = np.nan



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
                        'published_on': str(published_date),
                        'published_at': np.nan if pd.isnull(published_time) else int(published_time),
                        'address': str(address),
                        'city': str(german_characters(location_name)),
                        'crawler': 'WG-Gesucht',
                        'latitude': np.nan if pd.isnull(lat) else float(lat),
                        'longitude': np.nan if pd.isnull(lon) else float(lon)
                    }
                    if len(availability_dates) == 2:
                        details['available from'] = str(availability_dates[0])
                        details['available to'] = str(availability_dates[1])
                    elif len(availability_dates) == 1:
                        details['available from'] = str(availability_dates[0])
                        details['available to'] = np.nan

                    entries.append(details)

            # Reset existing_findings
            self.existing_findings = []

            # Create the dataframe
            df = pd.DataFrame(entries)

            if len(df)>0:
                # Save info as df in csv format
                ads_added = self.save_df(df=df, location_name=standardize_characters(location_name))
                total_added_findings = total_added_findings + ads_added
                if int(ads_added) == 0:
                    zero_new_ads_in_a_row += 1
                    print(f'{zero_new_ads_in_a_row} pages with no new ads added in a series')
                else:
                    zero_new_ads_in_a_row = 0
            else:
                print('===== Something went wrong. No entries were found. =====')

            if zero_new_ads_in_a_row >=3:
                break

        print(f'========= {total_added_findings} ads in total were added to {location_name}_ads.csv =========')


if __name__ == "__main__":
    CrawlWgGesucht().crawl_all_pages('Berlin', 5)

    # df = get_file(file_name=f'berlin_ads.csv',
    #                         local_file_path=f'livablestreets/data/berlin/Ads')

    # CrawlWgGesucht().save_df(df, 'berlin')
