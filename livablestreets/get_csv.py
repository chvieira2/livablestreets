import pandas as pd
from pathlib import Path
import pandas as pd
import requests
import json
import csv
from livablestreets.query_names import public_transport, bike_infraestructure, eating, night_life, culture, community, health_care, public_service, education, economic, comfort_sports, leisure_sports
from osm_query import query_params_osm

from livablestreets.utils import simple_time_tracker
from google.cloud import storage
from livablestreets.params import BUCKET_NAME
from livablestreets.osm_query import query_params_osm

def get_public_transp(public_transport):
    for querie in public_transport:
        new_querie = query_params_osm(querie, 'nodes')

    df_public_transport = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
    df_public_transport['coor'] = list(zip(df_public_transport.lat, df_public_transport.lon))
    df_public_transport.to_csv('../livablestreets/data/df_public_transport.csv', index=False)
    return df_public_transport

def get_bike_infraestructure(bike_infraestructure):
    new_querie = query_params_osm(bike_infraestructure, 'nodes')
    df_bike_infraestructure = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
    df_bike_infraestructure['coor'] = list(zip(df_bike_infraestructure.lat, df_bike_infraestructure.lon))
    df_bike_infraestructure.to_csv('../livablestreets/data/df_bike_infraestructure.csv', index=False)
    return df_bike_infraestructure

def get_eating(eating):
    new_querie = query_params_osm(eating, 'nodes')
    df_eating = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
    df_eating['coor'] = list(zip(df_eating.lat, df_eating.lon))
    df_eating.to_csv('../livablestreets/data/df_eating.csv', index=False)
    return df_eating

def get_night_life(night_life):
    new_querie = query_params_osm(night_life, 'nodes')
    df_night_life = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
    df_night_life['coor'] = list(zip(df_night_life.lat, df_night_life.lon))
    df_night_life.to_csv('../livablestreets/data/df_night_life.csv', index=False)
    return df_night_life

def get_culture(culture):
    new_querie = query_params_osm(culture, 'nodes')
    df_culture = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
    df_culture['coor'] = list(zip(df_culture.lat, df_culture.lon))
    df_culture.to_csv('../livablestreets/data/df_culture.csv', index=False)
    return df_culture

def get_community(community):
    new_querie = query_params_osm(community, 'nodes')
    df_community = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
    df_community['coor'] = list(zip(df_community.lat, df_community.lon))
    df_community.to_csv('../livablestreets/data/df_community.csv', index=False)
    return df_community

def get_health_care(health_care):
    new_querie = query_params_osm(health_care, 'nodes')
    df_health_care = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
    df_health_care['coor'] = list(zip(df_health_care.lat, df_health_care.lon))
    df_health_care.to_csv('../livablestreets/data/df_health_care.csv', index=False)
    return df_health_care

def get_public_service(public_service):
    new_querie = query_params_osm(public_service, 'nodes')
    df_public_service = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
    df_public_service['coor'] = list(zip(df_public_service.lat, df_public_service.lon))
    df_public_service.to_csv('../livablestreets/data/df_public_service.csv', index=False)
    return df_public_service

def get_education(education):
    new_querie = query_params_osm(education, 'nodes')
    df_education = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
    df_education['coor'] = list(zip(df_education.lat, df_education.lon))
    df_education.to_csv('../livablestreets/data/df_education.csv', index=False)
    return df_education

def get_economic(economic):
    new_querie = query_params_osm(economic, 'nodes')
    df_economic = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
    df_economic['coor'] = list(zip(df_economic.lat, df_economic.lon))
    df_economic.to_csv('../livablestreets/data/df_economic.csv', index=False)
    return df_economic

def get_comfort_sports(comfort_sports):
    new_querie = query_params_osm(comfort_sports, 'nodes')
    df_comfort_sports = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
    df_comfort_sports['coor'] = list(zip(df_comfort_sports.lat, df_comfort_sports.lon))
    df_comfort_sports.to_csv('../livablestreets/data/df_comfort_spots.csv', index=False)
    return df_comfort_sports

def get_leisure_sports(leisure_sports):
    new_querie = query_params_osm(leisure_sports, 'nodes')
    df_leisure_sports = pd.DataFrame(new_querie['elements'])[['lat', 'lon']]
    df_leisure_sports['coor'] = list(zip(df_leisure_sports.lat, df_leisure_sports.lon))
    df_leisure_sports.to_csv('../livablestreets/data/df_leisure_sports.csv', index=False)
    return df_leisure_sports




if __name__ == "__main__":
    print(get_eating(eating))
    df_eating.to_csv('../livablestreets/data/df_eating.csv', index=False)
