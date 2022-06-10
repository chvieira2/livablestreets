import folium
from folium.plugins import HeatMap, Fullscreen
import pandas as pd
import numpy as np
from livablestreets.utils import get_file


def plot(df, city_coords:tuple, city_borders):
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
    #---------- create heatmaps for each category ---------------------
    heatmaps={}
    for category in categories.keys():
        if category=='livability':
            heatmaps[category]=HeatMap(categories[category],
                            min_opacity=0,
                            max_opacity=0,
                            gradient={
                                      0:'White',
                                      0.33:'Blue',
                                      0.66:'Green',
                                      1: 'Orange'
                                      },
                            radius=15,
                            name=category,
                            show=True)
        else:
            heatmaps[category]=HeatMap(categories[category],
                            min_opacity=0,
                            max_opacity=0,
                            gradient={
                                      0:'White',
                                      0.33:'Blue',
                                      0.66:'Green',
                                      1: 'Orange'
                                      },
                            radius=15,
                            name=category.split('_')[0],
                            show=False)
    #--------- create map with heatmap overlayers ---------------------
    mapObj = folium.Map(location=city_coords, zoom_start=10, max_zoom = 14)
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
    print('Loading map...')
    show_map(cityname='Berlin')
