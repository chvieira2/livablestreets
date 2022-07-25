# -*- coding: utf-8 -*-

"""Livablestreets - visualize life quality at street level for cities around the world"""

__author__ = "Carlos Henrique Vieira e Vieira, Laia Grobe, Nicolas Quiroga and Ieva Bidermane"
__version__ = "1.0"
__maintainer__ = "chvieira2"
__email__ = "carloshvieira2@gmail.com"
__status__ = "Production"


# from sqlalchemy import null
import streamlit as st
from PIL import Image
import folium
from folium import GeoJson
import streamlit_folium as stf
from folium.plugins import HeatMap, MarkerCluster
import numpy as np
import pandas as pd
from config.config import ROOT_DIR
from livablestreets.livability_map.display_map import plot_map
from livablestreets.livability_map.generator import LivabilityMap
from livablestreets.params import preloaded_cities, dict_city_number_wggesucht
from livablestreets.ads_crawler.crawl_wggesucht import CrawlWgGesucht
from livablestreets.string_utils import standardize_characters, capitalize_city_name, german_characters

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
# placeholder_cities = {'Berlin' : [52.5200, 13.4050],
#                       'London' : [51.5072,0.1276],
#                       'New York' : [40.7128, -73.9352],
#                       'Tokyo' : [35.6762,139.6503],
#                       'Sao Paulo': [-23.5558, -46.6396],
#                       'Qatar': [25.3548,51.1839],
#                       'Marrakesh': [31.6295,7.9811]
#                       }
# for city,coords in placeholder_cities.items():
#     folium.Marker(coords,
#                   popup=city,
#                   icon=folium.Icon(color='green',
#                                    icon='home')).add_to(placeholderMap)

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
            ### Let's start:<br>
            - Select your city of interest in the left side tab (click the arrow on the top left if you can not see the side tab);<br>
            - Check the box to explore housing ads in your city of interest (only available for cities in Germany);<br>
            - Use the sliding bars to indicate how much each feature is relevant to you:<br>
            <span style="color:tomato">Activities and Services</span>: health care, education, public services, and banks<br>
            <span style="color:tomato">Comfort</span>: parks, green spaces, water points, leisure areas, and sports<br>
            <span style="color:tomato">Mobility</span>: public transport and biking infrastructure<br>
            <span style="color:tomato">Social life</span>: eating out, night life, culture, and community spaces<br>
            - Press "Display livability map" on the bottom, and explore the result.
            """, unsafe_allow_html=True)
    # stf.folium_static(placeholderMap)


#------------------------user inputs-----------------------------------
#inputs for weights for users
weight_dict={"Don't care much":-9,
             "Somewhat important":-3,
             'Average':1,
             'Quite important':3,
             'Very important':9}

user_number_pages_dict={"few":1,
             "some":3,
             'many':5}

with st.sidebar:
    form = st.form("calc_weights")

    # City selection
    form.selectbox(label = 'Select a city of interest', key='input_city', options = preloaded_cities, index=preloaded_cities.index('Berlin'))
    # form.text_input(label='Type city name', key='input_city', type="default", on_change=None, placeholder='p.ex. Berlin')



    # Weights selection
    form.select_slider(label='Activities and Services:', options=list(weight_dict.keys()), value='Average', key='weight_activity', help=None, on_change=None)
    form.select_slider(label='Comfort:', options=list(weight_dict.keys()), value='Average', key='weight_comfort', help=None, on_change=None)
    form.select_slider(label='Mobility:', options=list(weight_dict.keys()), value='Average', key='weight_mobility', help=None, on_change=None)
    form.select_slider(label='Social life:', options=list(weight_dict.keys()), value='Average', key='weight_social', help=None, on_change=None)

    ## Checkbox for wg-gesuch ads
    # TO DO make clicking the box open more options: filters for search, number of pages, etc
    cbox_wggesucht = form.checkbox('Show housing offers (Germany only)?')
    user_filters = form.multiselect(
                'Search filters',
                ["wg-zimmer","1-zimmer-wohnungen","wohnungen","haeuser"],
                ["wg-zimmer"])

    # form.selectbox(label = 'Number of offers (affects loading time significantly)', key='user_number_pages', options = user_number_pages_dict.keys(), index='some')

    user_number_pages = form.radio('Number of housing offers to display', user_number_pages_dict.keys())

    user_number_pages = user_number_pages_dict.get(user_number_pages)

    #Form submit button to generate the inputs from the user
    submitted = form.form_submit_button('Display livability map', on_click=None)


## Page after submission
if submitted:
    placeholder_map.empty()
    weights_inputs = (st.session_state.weight_activity,
               st.session_state.weight_comfort,
               st.session_state.weight_mobility,
               st.session_state.weight_social,
               'Average') # Last weight 'average refers to negative features
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
    mapObj = plot_map(df, city_coords, city_borders)
    #Used to fill the placeholder of the world map with according one of the selected city
    with placeholder_map.container():
        st.markdown(f"""
                # Here's the livability map for <span style="color:tomato">{city.location}</span>
                """, unsafe_allow_html=True)

        ## Add wg-gesucht ads
        if city.location in list(dict_city_number_wggesucht.keys()) and cbox_wggesucht:
            st.markdown("""
                    Searching for flatshare offers...<br>
                    If this is taking longer than 2-3 minutes, please try again later.
                    """, unsafe_allow_html=True)

            # Obtain recent ads
            ## TO DO include a filter for type of add
            ## TO DO find way to display text and map hide text when done. Use that to break apart 'crawl_all_pages function and display text of ongoing process while user waits for ads to load.
            CrawlWgGesucht().crawl_all_pages(location_name = city.location,
                                             number_pages = user_number_pages,
                                             filters = user_filters)

            df = pd.read_csv(f"{ROOT_DIR}/livablestreets/data/{standardize_characters(city.location)}/Ads/{standardize_characters(city.location)}_ads.csv")
            print(f'===> Loaded ads')

            ## Filter ads table
            # Remove ads without latitude and longitude
            df = df.dropna(subset=['latitude'])

            ## Add ads to map
            for index,row in df.iterrows():
                folium.Marker(location=[row.loc['latitude'], row.loc['longitude']],
                              tooltip=f"""
                              {row.loc['title']}<br>
                              Price: {row.loc['price_euros']} €<br>
                              Room size: {row.loc['size_sqm']} sqm<br>
                              Address: {row.loc['address']}<br>
                              Published on: {row.loc['published_on'] if np.isnan(row.loc['published_at']) else str(row.loc['published_on'])+' around '+str(int(row.loc['published_at']))+'h'}
                              """,
                              popup=f"""
                              <a href="{row.loc['url']}">{row.loc['url']}</a>

                              """,
                                icon=folium.Icon(color='purple', icon='home'))\
                    .add_to(mapObj)

        ## Display map
        stf.folium_static(mapObj)

        st.markdown("""
                    Showing recently posted flatshare offers in your city. Be aware that the displayed locations are approximated.<br> This list is not comprehensive and more offers are available at [wg-gesucht.de](wg-gesucht.de).
                    """, unsafe_allow_html=True)
