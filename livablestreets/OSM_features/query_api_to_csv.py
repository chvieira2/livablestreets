import pandas as pd
# from google.cloud import storage
# from livablestreets.params import BUCKET_NAME
from livablestreets.OSM_features.query_api_osm import query_params_osm
from livablestreets.OSM_features.query_api_categories import master_query

import os, sys, time
# import time
from config.config import ROOT_DIR



# url api status
url = 'http://overpass-api.de/api/status'



def get_csv(location, location_name, query_df):

    for _, row in query_df.iterrows():
        filter_name = row['name']
        geomtype = row['geomtype']
        outdir = f'{ROOT_DIR}/livablestreets/data/{location_name}/Features'

        # for some unknown reason, 'query_string from Node features are saved as dict and from Ways are saved as string of dictionary and need to be eval to become a dict.
        if isinstance(row['query_string'], str):
            string = eval(row['query_string'])
        else:
            string = row['query_string']


        if not os.path.exists(path = f'{outdir}/{filter_name}.csv'):

            if geomtype != 'Node':
                print(f'getting {filter_name} as ways')
                # new_querie = query_params_osm(location = location, keys = string, features = 'ways')
                #print(new_querie['elements'])

                retries = 1
                success = False
                while not success:
                    try:
                        new_querie = query_params_osm(location = location, keys = string, features = 'ways')
                        success = True
                    except Exception as e:
                        wait = retries * 5
                        print (f'''Overpass API busy. Check API status: http://overpass-api.de/api/status\n
                               Waiting {wait} secs and re-trying...\n''')
                        sys.stdout.flush()
                        time.sleep(wait)
                        retries += 1

                if new_querie['elements']:
                    df_new_querie = pd.DataFrame(new_querie['elements'])
                    print(f'--------------------------------')

                    ne = df_new_querie[df_new_querie['geometry'].notna()]
                    xss = ne['geometry']
                    flat_list = [x for xs in xss for x in xs]
                    df_new_querie = pd.DataFrame(flat_list)[['lat', 'lon']]
                    df_new_querie['coor'] = list(zip(df_new_querie.lat, df_new_querie.lon))


                    print(f'\n ---- saving {filter_name}.csv --- ')
                    df_new_querie.to_csv(f'{outdir}/{filter_name}.csv', index=False)


                else:
                    print(f'\n ----- saving EMPTY {filter_name}.csv ---')
                    empty_df=pd.DataFrame({'lat':[],'lon':[],'coor':[]})
                    empty_df.to_csv(f'{outdir}/{filter_name}.csv', index=False)


            if geomtype == 'Node':
                print(f'getting {filter_name} as nodes')
                # new_querie = query_params_osm(location = location, keys = string, features = 'nodes')

                retries = 1
                success = False
                while not success:
                    try:
                        new_querie = query_params_osm(location = location, keys = string, features = 'nodes')
                        success = True
                    except Exception as e:
                        wait = retries * 5
                        print (f'''Overpass API busy. Check API status: http://overpass-api.de/api/status\n
                               Waiting {wait} and re-trying...\n''')
                        sys.stdout.flush()
                        time.sleep(wait)
                        retries += 1

                if new_querie['elements']:
                    print(f'--------------------------------')

                    df_new_querie = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
                    df_new_querie['coor'] = list(zip(df_new_querie.lat, df_new_querie.lon))


                    print(f'\n ---- saving {filter_name}.csv --- ')
                    df_new_querie.to_csv(f'{outdir}/{filter_name}.csv', index=False)


                else:
                    print(f'\n ----- saving EMPTY {filter_name}.csv ---')
                    empty_df=pd.DataFrame({'lat':[],'lon':[],'coor':[]})
                    empty_df.to_csv(f'{outdir}/{filter_name}.csv', index=False)

    print(f'''--- csv file for {location} is finished---\n ''')


if __name__ == "__main__":

    # print(get_eating(eating))
    # df_eating.to_csv('../livablestreets/data/df_eating.csv', index=False)
    # get_all(location = 'Berlin')
    # get_leisure_sports(location = 'berlin', leisure_sports= leisure_sports)

    query_df = master_query()
    get_csv(location='stockholm', location_name='stockholm', query_df=query_df)
