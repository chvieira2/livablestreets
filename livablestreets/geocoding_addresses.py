
import pandas as pd
import numpy as np
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

def fix_addresses(df, column = 'address'):
    ## Add here any other type of weird naming on addresses
    weird_patterns = ['Am S Bahnhof ']

    for weird in weird_patterns:
        df[column] = df[column].apply(lambda row: row.replace(weird, ''))

    df[column] = df[column].apply(lambda row: row.replace('kungerstrasse', 'kunger strasse'))

    return df

def geocoding_df(df, column = 'address'):

    print("Geocoding addresses")
    df = fix_addresses(df=df, column = column)

    locator = Nominatim(user_agent='myGeocoder')
    # 1 - conveneint function to delay between geocoding calls
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
    # 2- - create location column
    df['location'] = df[column].apply(geocode)
    # 3 - create longitude, laatitude and altitude from location column (returns tuple)
    df['location'] = df['location'].apply(lambda loc: tuple(loc.point) if loc else None).tolist()
    # 4 - Remove entries without detectable location
    # df = df.dropna(subset=['location'])
    # 5 - split point column into latitude, longitude and altitude columns
    try:
        df[['latitude', 'longitude', 'altitude']] = pd.DataFrame(df['location'].tolist(), index=df.index)
    except ValueError:
        df[['latitude', 'longitude', 'altitude']] = [np.nan,np.nan,np.nan]
    # 6 - Remove unnecessary columns
    return df.drop(columns=['location', 'altitude'])

if __name__ == "__main__":
     df = pd.DataFrame({'address':["Am S Bahnhof Sundgauer Str , Berlin Zehlendorf",
                             "Müggelstraße 9, Berlin Friedrichshain",
                             "Brachvogelstraße 8, Berlin Kreuzberg"]})

     print(geocoding_df(df=df))
