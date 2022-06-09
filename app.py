import streamlit as st
import folium
from folium import GeoJson
import streamlit_folium as stf
from folium.plugins import HeatMap
import numpy as np
import pandas as pd
from config.config import ROOT_DIR
from livablestreets.display_map import plot
from livablestreets.generator import LivabilityMap
#-----------------------page configuration-------------------------
st.set_page_config(
    page_title="Livable Streets",
    page_icon=':house:', # gives a random emoji //to be addressed for final ver
    layout="wide",
    initial_sidebar_state="auto")

#-------------------styling for layouts--------------------------
#.css-18e3th9 change top padding main container
# .css-1oe6wy4 changed top paging sidebar
# iframe changed the size of the map's iframe
#mapObj = folium.Map(location=[52.5200, 13.4050], zoom_start=10)
st.markdown(
            f'''
            <style>
                .css-18e3th9 {{
                    padding-top: 10px;
                    padding-right: 10px;
                    padding-bottom: 10px;
                    padding-left: 10px;
                }}
                .css-1oe6wy4 {{
                    padding-top: 35px;
                }}
                .css-192cp98{{
                    padding-top: 35px;
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


# st.markdown("""<h1 style='text-align: center; color: white'>
#             Explore livability scores in city of your choice
#             </h1>""",
#             unsafe_allow_html=True)

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
    st.markdown("""<h2 style='text-align: center; color: white'>
            Explore livability scores in city of your choice
            </h2>""",
            unsafe_allow_html=True)
    stf.folium_static(placeholderMap)


#------------------------user inputs-----------------------------------
#inputs for weights for users
weight_dict={"Don't care":0,
             "Somewhat important":0.25,
             'Average':0.5,
             'Quite important':0.75,
             'Very important':1}
with st.sidebar:
    form = st.form("calc_weights")
    form.text_input(label='Type city name', key='input_city', type="default", on_change=None, placeholder='p.ex. Berlin')
    form.select_slider(label='Activity options', options=list(weight_dict.keys()), value='Average', key='weight_activity', help=None, on_change=None)
    form.select_slider(label='Comfort', options=list(weight_dict.keys()), value='Average', key='weight_comfort', help=None, on_change=None)
    form.select_slider(label='Mobility around the city', options=list(weight_dict.keys()), value='Average', key='weight_mobility', help=None, on_change=None)
    form.select_slider(label='Social aspects', options=list(weight_dict.keys()), value='Average', key='weight_social', help=None, on_change=None)


    #Form submit button to generate the inputs from the user
    submitted = form.form_submit_button('Calculate Livability', on_click=None)

if submitted:
    placeholder_map.empty()
    weights_inputs = (st.session_state.weight_activity,
               st.session_state.weight_comfort,
               st.session_state.weight_mobility,
               st.session_state.weight_social)
    weights=tuple([weight_dict[i] for i in weights_inputs])
    #check weights
    print(f'Weights entered by user: {weights}')

    city = LivabilityMap(location=st.session_state.input_city)
    city.calc_livability()
    city.update_livability(imputed_weights=weights)
    df = city.df_grid_Livability
    #city center position lat,lon
    city.generate_grid()
    city_coords = [city.location_centroid[1],city.location_centroid[0]]
    #for filling the polygon
    style_function = {'fillColor': 'transparent',
                 'lineColor': '#00FFFFFF'}
    # city borders map
    geojson_path=city.path_location_geojson
    file = open(geojson_path, encoding="utf8").read()
    city_borders = GeoJson(file,
                          name=city.location,
                          show=True,
                          style_function=lambda x:style_function,
                          zoom_on_click=True)
    print(city_borders)
    mapObj = plot(df, city_coords, city_borders)
    #Used to fill the placeholder of the world map with according one of the selected city
    with placeholder_map.container():
        col1,col2,col3=st.columns(3)
        col2.header(f'Livability score in: {city.location.capitalize()}')
        stf.folium_static(mapObj)
