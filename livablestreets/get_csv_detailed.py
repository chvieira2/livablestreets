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


import os



def get_csv(city):
    query_df = master_query()
    # query_df = df.iloc[2:]
    for index, row in query_df.iterrows():
        filter_name = index
        string = row['query_string']
        category = row['category']

        new_querie = query_params_osm(location = city.capitalize(), keys = string, features = 'nodes')
        print(f'------------------------> {new_querie}')

        df_new_querie = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
        df_new_querie['coor'] = list(zip(df_new_querie.lat, df_new_querie.lon))

        cwd = os.getcwd()
        df_new_querie.to_csv(f'{cwd}/data/{city.lower()}/Features/{category}_{filter_name}.csv', index=False)


if __name__ == "__main__":

    # print(get_eating(eating))
    # df_eating.to_csv('../livablestreets/data/df_eating.csv', index=False)
    # get_all(location = 'Berlin')
    # get_leisure_sports(location = 'berlin', leisure_sports= leisure_sports)
    print(get_csv('Dresden'))
