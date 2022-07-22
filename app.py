# -*- coding: utf-8 -*-

"""Livablestreets - visualize life quality at street level for cities around the world"""

__author__ = "Carlos Henrique Vieira e Vieira, Laia Grobe, Nicolas Quiroga and Ieva Bidermane"
__version__ = "1.0"
__maintainer__ = "chvieira2"
__email__ = "carloshvieira2@gmail.com"
__status__ = "Production"


import streamlit as st
from PIL import Image
import folium
from folium import GeoJson
import streamlit_folium as stf
from folium.plugins import HeatMap
import numpy as np
import pandas as pd
from config.config import ROOT_DIR
from livablestreets.livability_map.display_map import plot
from livablestreets.livability_map.generator import LivabilityMap
from livablestreets.params import preloaded_cities, dict_city_number_wggesucht
from livablestreets.ads_crawler.crawl_wggesucht import CrawlWgGesucht


def launch_flat_search(location_name = 'berlin', page_number = 3,
                    filters = ["wg-zimmer"], path_save = None):
    """Starts the crawler"""

    crawler = CrawlWgGesucht()
    crawler.crawl_all_pages(location_name = location_name, page_number = page_number,
                    filters = filters, path_save = path_save)


#-----------------------page configuration-------------------------
st.set_page_config(
    page_title="Livablestreets",
    page_icon=':house:', # gives a random emoji //to be addressed for final ver
    layout="wide",
    initial_sidebar_state="auto")

#-------------------styling for layouts--------------------------
#.css-18e3th9 change top padding main container
# .css-1oe6wy4 changed top paging sidebar
# iframe changed the size of the map's iframe
st.markdown(
            f'''
            <style>
                .css-18e3th9 {{
                    padding-top: 15px;
                    padding-right: 15px;
                    padding-bottom: 15px;
                    padding-left: 15px;
                }}
                .css-1oe6wy4 {{
                    padding-top: 15px;
                }}
                .css-192cp98{{
                    padding-top: 15px;
                }}

                iframe {{
                width: 100%;
                height: 500px;
                }}
                .css-1inwz65{{
                    font-family:inherit
                }}
                .css-16huue1{{
                    font-size:18px;
                    color: rgb(139, 145, 153);
                    justify-content: center;
                }}
                .st-bt {{
                    background-color: inherit;
                }}
            </style>
            ''', unsafe_allow_html=True)


#----Simple placeholder for the world map with arbitrary city coordenates------
placeholder_map = st.empty()
placeholderMap = folium.Map(location=[37.6000, 10.0154],
                            #tiles="Stamen Terrain",
                            zoom_start=2)
placeholder_cities = {'Berlin' : [52.5200, 13.4050],
                      'London' : [51.5072,0.1276],
                      'New York' : [40.7128, -73.9352],
                      'Tokyo' : [35.6762,139.6503],
                      'Sao Paulo': [-23.5558, -46.6396],
                      'Qatar': [25.3548,51.1839],
                      'Marrakesh': [31.6295,7.9811]
                      }
for city,coords in placeholder_cities.items():
    folium.Marker(coords,
                  popup=city,
                  icon=folium.Icon(color='green',
                                   icon='home')).add_to(placeholderMap)

with placeholder_map.container():

    # Hacky way to center image: create three columns and place image in center
    col1, col2 = st.columns([1,1.8])

    with col1:
        image = Image.open('livablestreets_logo.png')
        st.image(image=image, width=300)
    with col2:
        st.write('\n')
        st.markdown("""
                # Welcome to <span style="color:tomato">Livablestreets</span>!
                ## Explore life quality (livability) of streets in cities around the world.
                For more information, please check our [GitHub page](https://github.com/chvieira2/livablestreets)
                """, unsafe_allow_html=True)
    st.markdown("""
            ### Let's start:
            - On the tab on your left (click the arrow on the top left if you can not see it), select the city of interest;
            - Use the sliding bars to indicate how much each feature (activities and services/comfort/mobility/social life) are relevant for you;
            - Press "Calculate Livability", and wait a few seconds for your result.
            """)
    # stf.folium_static(placeholderMap)


#------------------------user inputs-----------------------------------
#inputs for weights for users
weight_dict={"Don't care much":0.25,
             "Somewhat important":0.5,
             'Average':1,
             'Quite important':2,
             'Very important':4}

with st.sidebar:
    form = st.form("calc_weights")

    # City selection
    form.selectbox(label = 'Select a city of interest', key='input_city', options = preloaded_cities, index=preloaded_cities.index('Berlin'))
    # form.text_input(label='Type city name', key='input_city', type="default", on_change=None, placeholder='p.ex. Berlin')

    # Weights selection
    form.select_slider(label='Activities and services:', options=list(weight_dict.keys()), value='Average', key='weight_activity', help=None, on_change=None)
    form.select_slider(label='Comfort:', options=list(weight_dict.keys()), value='Average', key='weight_comfort', help=None, on_change=None)
    form.select_slider(label='Mobility:', options=list(weight_dict.keys()), value='Average', key='weight_mobility', help=None, on_change=None)
    form.select_slider(label='Social life:', options=list(weight_dict.keys()), value='Average', key='weight_social', help=None, on_change=None)


    #Form submit button to generate the inputs from the user
    submitted = form.form_submit_button('Calculate Livability', on_click=None)

if submitted:
    placeholder_map.empty()
    weights_inputs = (st.session_state.weight_activity,
               st.session_state.weight_comfort,
               st.session_state.weight_mobility,
               st.session_state.weight_social,
               'Average')
    weights=[weight_dict[i] for i in weights_inputs]
    #check weights
    print(f'Weights entered by user: {weights}')

    city = LivabilityMap(location=st.session_state.input_city, weights=weights)
    city.calc_livability()
    df = city.df_grid_Livability
    #city center position lat,lon
    city_coords = [np.mean(df['lat_center']),np.mean(df['lng_center'])]
    print(f"""============ {city.location} coordinates: {city_coords} =============""")

    #for filling the polygon
    style_function = {'fillColor': 'transparent',
                 'lineColor': '#00FFFFFF'}
    # city borders map
    geojson_path=f'{ROOT_DIR}/livablestreets/data/{city.location_name}/{city.location_name}_boundaries.geojson'
    file = open(geojson_path, encoding="utf8").read()
    city_borders = GeoJson(file,
                          name=city.location,
                          show=True,
                          style_function=lambda x:style_function,
                          zoom_on_click=True)
    mapObj = plot(df, city_coords, city_borders)
    #Used to fill the placeholder of the world map with according one of the selected city
    with placeholder_map.container():
        col1,col2,col3=st.columns(3)
        col2.header(f'Livability score in: {city.location}')
        stf.folium_static(mapObj)
