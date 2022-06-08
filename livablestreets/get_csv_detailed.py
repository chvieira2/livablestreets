import pandas as pd
# from pathlib import Path
# import requests
# import json
# import csv
# from livablestreets.query_names import public_transport, bike_infraestructure, eating, night_life, culture, community, health_care, public_service, education, economic, comfort_sports, leisure_sports


# from google.cloud import storage
# from livablestreets.params import BUCKET_NAME
from livablestreets.utils import simple_time_tracker
from livablestreets.osm_query import query_params_osm
from livablestreets.query_names_detailed import master_query, master_query_complex, master_query_negative
from livablestreets.utils import create_dir

import os, sys, time
# import time
from config.config import ROOT_DIR



# url api status
url = 'http://overpass-api.de/api/status'



def get_csv(city, query_df):

    for index, row in query_df.iterrows():
        filter_name = index
        string = row['query_string']
        category = row['category']
        geomtype = row['geomtype']

        outdir = f'{ROOT_DIR}/livablestreets/data/{city.lower()}/Features'
        # create_dir(path = f'{ROOT_DIR}/livablestreets/data/{city.lower()}')
        # create_dir(path = f'{ROOT_DIR}/livablestreets/data/{city.lower()}/Features')

        if not os.path.exists(path = f'{ROOT_DIR}/livablestreets/data/{city.lower()}/Features/{category}_{filter_name}.csv'):

            if geomtype != 'Node':
                print(f'getting {filter_name} as ways')
                # new_querie = query_params_osm(location = city.capitalize(), keys = string, features = 'ways')
                #print(new_querie['elements'])

                retries = 1
                success = False
                while not success:
                    try:
                        new_querie = query_params_osm(location = city.capitalize(), keys = string, features = 'ways')
                        success = True
                    except Exception as e:
                        wait = retries * 30
                        print ('Error! Waiting %s secs and re-trying...' % wait)
                        sys.stdout.flush()
                        time.sleep(wait)
                        retries += 1

                if new_querie['elements']:
                    df_new_querie = pd.DataFrame(new_querie['elements'])
                    print(f'------------------------------------------------------------>')

                    ne = df_new_querie[df_new_querie['geometry'].notna()]
                    xss = ne['geometry']
                    flat_list = [x for xs in xss for x in xs]
                    df_new_querie = pd.DataFrame(flat_list)[['lat', 'lon']]
                    df_new_querie['coor'] = list(zip(df_new_querie.lat, df_new_querie.lon))


                    print(f'\n --------------- ʕᵔᴥᵔʔ saving csv ---------------------- ')
                    df_new_querie.to_csv(f'{outdir}/{category}_{filter_name}.csv', index=False)

                    print(f'''\nServer cooldown ┬─┬⃰͡ (ᵔᵕᵔ͜ ) please wait 30 seconds \n------------------------------------------------------------/''')

                    # time.sleep(30)


            if geomtype == 'Node':
                print(f'getting {filter_name} as nodes')
                # new_querie = query_params_osm(location = city.capitalize(), keys = string, features = 'nodes')

                retries = 1
                success = False
                while not success:
                    try:
                        new_querie = query_params_osm(location = city.capitalize(), keys = string, features = 'nodes')
                        success = True
                    except Exception as e:
                        wait = retries * 30
                        print ('Error! Waiting %s secs and re-trying...' % wait)
                        sys.stdout.flush()
                        time.sleep(wait)
                        retries += 1

                if new_querie['elements']:
                    print(f'----------------------------------------------------------->')

                    df_new_querie = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
                    df_new_querie['coor'] = list(zip(df_new_querie.lat, df_new_querie.lon))


                    print(f'\n --------------- ʕᵔᴥᵔʔ saving csv ---------------------- ')
                    df_new_querie.to_csv(f'{outdir}/{category}_{filter_name}.csv', index=False)

                    print(f'''\nServer cooldown ┬─┬⃰͡ (ᵔᵕᵔ͜ ) please wait 5 seconds\n------------------------------------------------------------/''')

                    # time.sleep(5)

    print(f'''Finally done ⊂(◉‿◉)つ sorry for the wait'
              ------------------------------------------------------------/''')


if __name__ == "__main__":

    # print(get_eating(eating))
    # df_eating.to_csv('../livablestreets/data/df_eating.csv', index=False)
    # get_all(location = 'Berlin')
    # get_leisure_sports(location = 'berlin', leisure_sports= leisure_sports)
    query_df = master_query_complex()
    print(get_csv('Berlin', query_df))
