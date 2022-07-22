
import re
import time
import pandas as pd
import numpy as np
import requests
import urllib.parse

def fix_weird_address(address, weird_patterns = ['Am S Bahnhof', 'xxx', 'xx', 'Nahe', 'nahe', 'Nähe','nähe','Close To', 'Nearby','nearby']):
    ## Add here any other type of weird naming on addresses
    for weird in weird_patterns:
        address = address.replace(weird, '').strip().replace('  ', ' ')

    # Correcting mispelling input from users is a never ending job....
    return address.replace(' ,', ',')\
        .replace('srasse','strasse').replace('strs,','strasse,').replace('str,','strasse,').replace('Strs,','Strasse,').replace('Str,','Strasse,').replace('stasse,','strasse,').replace('Stasse,','Strasse,').replace('Strß,','Straße,').replace('strasze,','strasse,').replace('Strasze,','Strasse,')\
        .replace('Alle ', 'Allee ').replace('alle ', 'Allee ').replace('Alle,', 'Allee,').replace('alle,', 'Allee,').replace('feder','felder')\
        .replace('kungerstrasse', 'kunger strasse').replace('nummer zwei', '2')\
        .replace('Schonehauser', 'Schönhauser').replace('Warschschauer','Warschauer')\
        .replace('Dunkerstraße','Dunckerstraße').replace('Reinstraße','Rheinstraße')\
        .replace('Neltstraße', 'Neltestraße').replace('Camebridger', 'Cambridger')\
        .replace('Koperniskusstraße', 'Kopernikusstraße').replace('Düsseldoffer', 'Düsseldorfer')\
        .replace('Borndorfer','Bornsdorfer')

def geocoding_address(address, sleep_time = 900):
    '''
    Function takes on address and returns latitude and longitude
    '''
    ## Coorect weird entries in address
    address = fix_weird_address(address=address).strip().replace('  ', ' ').replace(' ,', ',')

    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36',
        'User-Agent': 'carloshvieira2@gmail.com',
    }

    # Loop until request is successfull
    success = False
    while not success:
        try:
            response = requests.get(url, headers=HEADERS)
        except requests.exceptions.ConnectionError:
            print(f'Got requests.exceptions.ConnectionError')
            time_now = time.mktime(time.localtime())
            print(f'Sleeping for {sleep_time/60} min until {time.strftime("%H:%M", time.localtime(time_now + sleep_time))} to wait for API to be available again.')
            time.sleep(sleep_time)
            sleep_time += sleep_time
            pass

        if response.status_code != 200:
            print(f'Got response code {response.status_code}')
            time_now = time.mktime(time.localtime())
            print(f'Sleeping for {sleep_time/60} min until {time.strftime("%H:%M", time.localtime(time_now + sleep_time))} to wait for API to be available again.')
            time.sleep(sleep_time)
            sleep_time += sleep_time
        else:
            success = True
    try:
        return (response.json()[0]["lat"], response.json()[0]["lon"])
    except IndexError:
        return (np.nan,np.nan)




if __name__ == "__main__":
    #  df = pd.DataFrame({'address':["Am S Bahnhof Sundgauer Str , Berlin Zehlendorf",
    #                          "Müggelstraße 9, Berlin Friedrichshain",
    #                          "Brachvogelstraße 8, Berlin Kreuzberg",
    #                          'Langhansstraße 21, Berlin Prenzlauer Berg']})

    print(fix_weird_address(address = "dsds Südendstraße54 , Schöneberg, Berlin"))
