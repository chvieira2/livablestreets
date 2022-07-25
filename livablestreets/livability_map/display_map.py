import folium
from folium.plugins import HeatMap, Fullscreen
import branca.colormap
from collections import defaultdict
import pandas as pd
import numpy as np
from livablestreets.utils import get_file


def plot_map(df, city_coords:tuple, city_borders):
    '''Plots the map of the city with overlayers for each category as well as
    livability score
    Inputs: obtained from LivabilityMap class instance generated from user
    inputs
    Output: map object
    '''
    #----------------------take only data from inside city coundaries--------
    df = df[df['grid_in_location']==True]
    # -------------- get all categories from df ----------------------------
    columns = df.columns
    columns_categories = [col for col in columns if col.split('_')[-1]=='mean']
    if 'livability' in columns:
        columns_categories.append('livability')
    #---------- create data arrays for each category + livability ---------
    categories={}
    for cat in columns_categories:
        categories[cat] = np.array(df[['lat_center','lng_center', cat]])




    # ---------- create map with color legend -----------
    mapObj = folium.Map(location=city_coords, zoom_start=10, max_zoom = 15)

    steps = 1000

    ## For selecting colors https://carto.com/carto-colors/ or https://colorbrewer2.org/#type=sequential&scheme=PuBu&n=9
    # colors = ['White','Blue','cyan','lime','yellow','Orange','red']
    # colors = ['#d3f2a3','#97e196','#6cc08b','#4c9b82','#217a79','#105965','#074050'] # Emrld
    # colors = ['#fde0c5','#facba6','#f8b58b','#f59e72','#f2855d','#ef6a4c','#eb4a40'] # Peach
    # colors = ['#d1eeea','#a8dbd9','#85c4c9','#68abb8','#4f90a6','#3b738f','#2a5674'] # Teal
    # colors = ['#fbe6c5','#f5ba98','#ee8a82','#dc7176','#c8586c','#9c3f5d','#70284a'] #BurgYl
    # colors = ['#f3e79b','#fac484','#f8a07e','#eb7f86','#ce6693','#a059a0','#5c53a5'] # Sunset
    # colors = ['#009392','#39b185','#9ccb86','#e9e29c','#eeb479','#e88471','#cf597e'] # Temps
    # colors = ['#008080','#70a494','#b4c8a8','#f6edbd','#edbb8a','#de8a5a','#ca562c'] # Geyser
    # colors = ['#3d5941','#778868','#b5b991','#f6edbd','#edbb8a','#de8a5a','#ca562c'] # Fall
    # colors = ['#ffffb2','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#b10026'] # YlOrRd
    # colors = ['#ffffd9', '#edf8b1', '#c7e9b4', '#7fcdbb', '#41b6c4', '#1d91c0', '#225ea8', '#0c2c84'] # YlGrBl
    # colors = ['#dadaeb', '#bcbddc', '#9e9ac8', '#807dba', '#6a51a3', '#54278f', '#3f007d'] # 7-classes purple
    # colors = ['#762a83', '#9970ab', '#c2a5cf', #'#e7d4e8', '#d9f0d3',
    #           '#a6dba0', '#5aae61', '#1b7837']# PRGn
    # colors = ['#e66101','#fdb863', '#b2abd2', '#5e3c99'] # PuOr
    # colors = ['#a6611a', '#dfc27d', '#80cdc1', '#018571'] # BrBG
    colors = ['#d0d1e6', '#a6bddb', '#74a9cf', '#3690c0', '#0570b0', '#045a8d'] # PuBu
    colormap = branca.colormap.LinearColormap(colors=colors, index= np.arange(0, 1, 1/len(colors)), vmin=0.0, vmax=1.0, caption='Livability score').to_step(steps)
    colormap.add_to(mapObj)

    # Prepare gradient dictionary with step separation

    gradient_dict=defaultdict(dict)
    for i in range(steps):
        gradient_dict[1/steps*i] = colormap.rgb_hex_str(1/steps*i) # Convert to hex in case it is rgb or color name string ('blue', 'red', etc)

    #---------- create heatmaps for each category ---------------------
    heatmaps={}
    for category in categories.keys():
        if category=='livability':
            heatmaps[category]=HeatMap(categories[category],
                            min_opacity=0,
                            max_opacity=0,
                            gradient=gradient_dict,
                            radius=15,
                            name=category,
                            show=True)
        else:
            heatmaps[category]=HeatMap(categories[category],
                            min_opacity=0,
                            max_opacity=0,
                            gradient=gradient_dict,
                            radius=15,
                            name=category.split('_')[0],
                            show=False)
    #--------- add heatmap overlayers ---------------------
    for hm in heatmaps.values():
        mapObj.add_child(hm)
    #---------- add city borderer as extra layer ----------------------
    city_borders.add_to(mapObj)
    folium.LayerControl().add_to(mapObj)
    Fullscreen(position='topleft',
               title='Full Screen',
               title_cancel='Exit Full Screen',
               force_separate_button=False).add_to(mapObj)

    return mapObj


#--------------help functions--------------------
##----Get all categories that end with _mean and if present 'livability'
def get_category_names(df):
        columns = df.columns
        columns_categories = [col for col in columns if col.split('_')[-1]=='mean']
        if 'livability' in columns:
            columns_categories.append('livability')
        return columns_categories
##----Create df for each category returned as a dictionary with {cat_name: df}
def create_category_array(df):
    column_category_mean = get_category_names(df)
    categories={}
    for cat in column_category_mean:
        categories[cat] = np.array(df[['lat_center','lng_center', cat]])
    return categories
##----Create heatmaps for each feature
def create_heatmap(data:dict):
    heatmaps={}
    for category in data.keys():
        heatmaps[category]=HeatMap(data[category],
                          min_opacity=0.2,
                          gradient={0:'Navy', 0.25:'Blue',0.5:'Green', 0.75:'Yellow',1: 'Red'},
                          radius=20,
                          name=category,
                          show=False)
    return heatmaps
##-----plot heatmaps
def plot_heatmaps(heatmaps):
    mapObj = folium.Map(location=[52.5200, 13.4050], zoom_start=10) #hardcoded for Berlin
    for hm in heatmaps.values():
        mapObj.add_child(hm)
    folium.LayerControl().add_to(mapObj)
    return mapObj


def show_map(cityname='Berlin'):
    df = get_file('Livability_berlin_grid_100m.csv', local_file_path='data/berlin/WorkingTables',
                  gcp_file_path = 'data/berlin/WorkingTables',
                  save_local=True)
    #----select only the data for inside the grid--------
    df = df[df['grid_in_location']==True]
    ##----Get all categories that end with _mean and if present 'livability'
    column_categories = get_category_names(df)
    ##----Create df for each category returned as a dictionary with {cat_name: df}
    categories = create_category_array(df)
    ##----Create heatmaps for each feature
    heatmaps = create_heatmap(categories)
    ##-----plot heatmaps
    mapObj = plot_heatmaps(heatmaps)
    pass
    #return mapObj,heatmaps

if __name__ == '__main__':

    gradient_dict = {}
