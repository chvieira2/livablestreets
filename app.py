import streamlit as st
import folium
import streamlit_folium as stf
from folium.plugins import HeatMap
import numpy as np
import pandas as pd
from livablestreets.display_map import plot
from livablestreets.generator import LivabilityMap
#-----------------------page configuration-------------------------
st.set_page_config(
    page_title="Livable Streets",
    page_icon='random', # gives a random emoji //to be addressed for final ver
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
                }}
                .css-1oe6wy4 {{
                    padding-top: 35px;
                }}
                iframe {{
                width: 100%;
                height: 500px;
                }}
            </style>
            ''', unsafe_allow_html=True)


st.markdown("""<h1 style='text-align: center; color: white;'>
            Explore livability scores in city of your choice
            </h1>""",
            unsafe_allow_html=True)


#-------------------user inputs---------------------------
#city
st.markdown('#### Select city:')
form = st.form("calc_weights")
form.text_input(label='City', max_chars=20, key='input_city', type="default", on_change=None, placeholder='p.ex. Berlin')

form.slider(label='activity', key='weight_activity',min_value=0.0, max_value=1., step=0.1, value=1., format='%.1f')
form.slider(label='comfort', key='weight_comfort',min_value=0.0, max_value=1., step=0.1, value=1., format='%.1f')
form.slider(label='mobility',key='weight_mobility', min_value=0.0, max_value=1., step=0.1, value=1., format='%.1f')
form.slider(label='social',key='weight_social', min_value=0.0, max_value=1., step=0.1, value=1., format='%.1f')

#Livability button
submitted = form.form_submit_button('Calculate Livability', on_click=None)

if submitted:
    st.write(st.session_state)
    weights = [st.session_state.weight_activity,
               st.session_state.weight_comfort,
               st.session_state.weight_mobility,
               st.session_state.weight_social]
    city = LivabilityMap(weights=weights)
    df = city.calc_livability()
    mapObj = plot(df)
    stf.folium_static(mapObj)
