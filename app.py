import streamlit as st
import folium
import streamlit_folium as stf
from folium.plugins import HeatMap
import numpy as np
import pandas as pd
from livablestreets.display_map import show_map
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
mapObj = folium.Map(location=[52.5200, 13.4050], zoom_start=10)
# st.markdown(
#             f'''
#             <style>
#                 .css-18e3th9 {{
#                     padding-top: 10px;
#                 }}
#                 .css-1oe6wy4 {{
#                     padding-top: 35px;
#                 }}
#                 iframe {{
#                 width: 100%;
#                 height: 500px;
#                 }}
#             </style>
#             ''', unsafe_allow_html=True)


# st.markdown("""<h1 style='text-align: center; color: white;'>
#             Get livability scores in Berlin
#             </h1>""",
#             unsafe_allow_html=True)


# #------------------Creating a map-------------------------------
# mapObj = show_map()

# #-----------------------sidebar---------------------------------
# st.sidebar.markdown(f"""
#     ## Choose a map to display
#     """)
# if st.sidebar.checkbox('Berlin borders'):
#     print('Hello')
#     #geo_Berlin.add_to(mapObj)

# if st.sidebar.checkbox('Berlin districts'):
#     print('Hello')
#     #geo_livingArea.add_to(mapObj)

# if st.sidebar.checkbox('Bars'):
#     print('Hello')
#     # heatmap = HeatMap(coords_bars,
#     #                   min_opacity=0.2,
#     #                   radius=15,
#     #                   #name='bars in Berlin',
#     #                   show=True)
#     # mapObj.add_child(heatmap)

stf.folium_static(mapObj)
