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
from livablestreets.utils import get_liv_from_coord, min_max_scaler

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

with placeholder_map.container():

    # Hacky way to center image: create three columns and place image in center
    col1, col2 = st.columns([1,1.8])

    with col1:
        image = Image.open('livablestreets_logo.png')
        st.image(image=image, width=275)
    with col2:
        st.write('\n')
        st.markdown("""
                # Welcome to <span style="color:tomato">Livablestreets</span>!
                ## Explore life quality (livability) of streets in cities around the world.
                For more information, please check our [GitHub page](https://github.com/chvieira2/livablestreets)
                """, unsafe_allow_html=True)
    st.markdown("""
            ### Let's start:<br>
            - Select a city of interest in the left sidetab (click the arrow on the top left if you can not see the sidetab);<br>
            - Set the relevance of each features category by using the sliding bars:<br>
            <span style="color:tomato">Activities and Services</span>: health care, education, public services, and banks<br>
            <span style="color:tomato">Comfort</span>: parks, green spaces, water points, leisure areas, and sports<br>
            <span style="color:tomato">Mobility</span>: public transport and biking infrastructure<br>
            <span style="color:tomato">Social life</span>: eating out, night life, culture, and community spaces<br>
            - If you are searching for housing (only available for cities in Germany) then open the indicated menu, check the box and set the search parameters;<br>
            - Press "Display livability map" on the bottom, and explore the result. Use the toggle between layers icon on the top right corner of the map for more details on how each feature category affects the livability.

            """, unsafe_allow_html=True)
    # stf.folium_static(placeholderMap)


#------------------------user inputs-----------------------------------
#inputs for weights for users
weight_dict={"Don't care much":1/10,
             "Somewhat important":1/3,
             'Average':1,
             'Quite important':3,
             'Very important':10}

user_number_pages_dict={"few":1,
             "some":3,
             'many':5}

with st.sidebar:
    form = st.form("calc_weights")

    # City selection
    form.selectbox(label = 'Select a city of interest', key='input_city', options = preloaded_cities, index=preloaded_cities.index('Berlin'))
    # form.text_input(label='Type city name', key='input_city', type="default", on_change=None, placeholder='p.ex. Berlin')


    expander_weights = form.expander("Options")

    # Weights selection
    expander_weights.select_slider(label='Activities and Services:', options=list(weight_dict.keys()), value='Average', key='weight_activity', help=None, on_change=None)
    expander_weights.select_slider(label='Comfort:', options=list(weight_dict.keys()), value='Average', key='weight_comfort', help=None, on_change=None)
    expander_weights.select_slider(label='Mobility:', options=list(weight_dict.keys()), value='Average', key='weight_mobility', help=None, on_change=None)
    expander_weights.select_slider(label='Social life:', options=list(weight_dict.keys()), value='Average', key='weight_social', help=None, on_change=None)



    ## Checkbox for wg-gesuch ads
    expander = form.expander("Housing offers (German cities only)")

    cbox_wggesucht = expander.checkbox('Display housing offers?')

    # Search filter criterium
    user_filters = expander.multiselect(
                'Search filters',
                ["Room in flatshare","Single room flat","Flat","House"],
                ["Room in flatshare"])

    dict_filters = {"Room in flatshare":"wg-zimmer",
                    "Single room flat":"1-zimmer-wohnungen",
                    "Flat":"wohnungen",
                    "House":"haeuser"}
    user_filters = [dict_filters.get(filter) for filter in user_filters]

    # Number of search pages
    user_number_pages = expander.radio('Number of housing offers to display', user_number_pages_dict.keys())

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
            #    'Average' # Last weight 'average' refers to negative features
               )
    weights=[weight_dict[i] for i in weights_inputs]
    #check weights
    print(f'Weights entered by user: {weights}')

    city = LivabilityMap(location=st.session_state.input_city, weights=weights)
    city.calc_livability()
    df_liv = city.df_grid_Livability

    # MinMax scale all columns for display
    categories_interest = ['activities_mean', 'comfort_mean', 'mobility_mean', 'social_mean']
    df_liv = min_max_scaler(df_liv, columns = categories_interest)
    #city center position lat,lon
    # city_coords = [np.mean(df_liv['lat_center']),np.mean(df_liv['lng_center'])]
    row_max_liv = df_liv[df_liv['livability'] == max(df_liv['livability'])].head(1)
    city_coords = [float(row_max_liv['lat_center']),float(row_max_liv['lng_center'])]

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
    mapObj = plot_map(df_liv, city_coords, city_borders)
    #Used to fill the placeholder of the world map with according one of the selected city
    with placeholder_map.container():
        st.markdown(f"""
                # Here's the livability map for <span style="color:tomato">{city.location}</span><br>
                """, unsafe_allow_html=True)

        displayed_map = st.empty()
        with displayed_map:
            stf.folium_static(mapObj, width=700, height=500)

        ## Add wg-gesucht ads
        if city.location in list(dict_city_number_wggesucht.keys()) and cbox_wggesucht:
            start_placeholder = st.empty()
            start_placeholder.markdown("""
                    Searching for housing offers...<br>
                    If this is taking longer than 2-3 minutes, please try again later.
                    """, unsafe_allow_html=True)

            # Obtain recent ads
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
                if 'WG' in row.loc['type_offer']:
                    tooltip = f"""
                              {row.loc['title']}<br>
                              Address: {row.loc['address']}<br>
                              Rent (month): {row.loc['price_euros']} €<br>
                              Room size: {row.loc['size_sqm']} sqm<br>
                              Capacity: {row.loc['WG_size']} people<br>
                              Published on: {row.loc['published_on']}<br>
                              Available from: {row.loc['available_from']}<br>
                              Available until: {'open end' if pd.isnull(row.loc['available_to']) else row.loc['available_to']}<br>
                              Location livability score: {int(get_liv_from_coord(row.loc['latitude'],
                              row.loc['longitude'],liv_df = df_liv))}%
                              """
                elif '1 Zimmer Wohnung' in row.loc['type_offer']:
                    tooltip = f"""
                              {row.loc['title']}<br>
                              Address: {row.loc['address']}<br>
                              Rent (month): {row.loc['price_euros']} €<br>
                              Property size: {row.loc['size_sqm']} sqm<br>
                              Published on: {row.loc['published_on']}<br>
                              Available from: {row.loc['available_from']}<br>
                              Available until: {'open end' if pd.isnull(row.loc['available_to']) else row.loc['available_to']}<br>
                              Location livability score: {int(get_liv_from_coord(row.loc['latitude'],
                              row.loc['longitude'],liv_df = df_liv))}%
                              """
                else:
                    tooltip = f"""
                              {row.loc['title']}<br>
                              Address: {row.loc['address']}<br>
                              Rent (month): {row.loc['price_euros']} €<br>
                              Property size: {row.loc['size_sqm']} sqm<br>
                              Rooms: {row.loc['available_rooms']} rooms<br>
                              Published on: {row.loc['published_on']}<br>
                              Available from: {row.loc['available_from']}<br>
                              Available until: {'open end' if pd.isnull(row.loc['available_to']) else row.loc['available_to']}<br>
                              Location livability score: {int(get_liv_from_coord(row.loc['latitude'],
                              row.loc['longitude'],liv_df = df_liv))}%
                              """


                folium.Marker(location=[row.loc['latitude'], row.loc['longitude']],
                              tooltip=tooltip,
                              popup=f"""
                              <a href="{row.loc['url']}">{row.loc['url']}</a>
                              """,
                                icon=folium.Icon(color='purple', icon='home'))\
                    .add_to(mapObj)

            ## Display map
            start_placeholder.markdown("""
                    Showing recently posted housing offers in your city. Be aware that the displayed locations are approximated.<br> This list is not comprehensive and more offers are available at [wg-gesucht.de](wg-gesucht.de).
                    """, unsafe_allow_html=True)

        with displayed_map:
            stf.folium_static(mapObj, width=500, height=500)
