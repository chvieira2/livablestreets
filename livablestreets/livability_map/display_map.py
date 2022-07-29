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
    ##----Create df for each category returned as a dictionary with {cat_name: df}
    categories = create_category_array(df)

    # ---------- create color legend -----------
    mapObj = folium.Map(location=city_coords, zoom_start=11.5, max_zoom = 15, width='75%', height='100%')

    steps = 1000

    ## For selecting colors see https://carto.com/carto-colors/ or https://colorbrewer2.org/#type=sequential&scheme=PuBu&n=9
    colors = ['white','blue','lime','yellow','red','magenta','purple']
    # colors = ['white','blue','lime','yellow', 'orange','red', 'brown']

    colormap = branca.colormap.LinearColormap(colors=colors, index= np.arange(0, 100, 100/len(colors)), vmin=0, vmax=100, caption='Livability score (%)').to_step(steps)
    colormap.add_to(mapObj)

    # Prepare gradient dictionary with step separation
    gradient_dict=defaultdict(dict)
    for i in range(steps):
        gradient_dict[1/steps*i] = colormap.rgb_hex_str(100/steps*i) # Convert to hex in case it is rgb or color name string ('blue', 'red', etc)

    #---------- create heatmaps for each category ---------------------
    heatmaps={}
    for category in categories.keys():
        if category=='livability':
            heatmaps[category]=HeatMap(categories[category],
                            min_opacity=0,
                            max_opacity=0,
                            gradient=gradient_dict,
                            radius=10,
                            name='Livability score',
                            show=True)
        elif category=='absolute_livability':
            heatmaps[category]=HeatMap(categories[category],
                            min_opacity=0,
                            max_opacity=0,
                            gradient=gradient_dict,
                            radius=10,
                            name='Livability score (Absolute)',
                            show=False)
        else:
            heatmaps[category]=HeatMap(categories[category],
                            min_opacity=0,
                            max_opacity=0,
                            gradient=gradient_dict,
                            radius=10,
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
def get_category_names(df):
    '''
    Get all categories that end with _mean and if present 'livability

    '''
    columns = df.columns
    columns_categories = [col for col in columns if col.split('_')[-1]=='mean']
    if 'livability' in columns:
        columns_categories.append('livability')
    if 'absolute_livability' in columns:
        columns_categories.append('absolute_livability')
    return columns_categories

def create_category_array(df):
    '''
    Create df for each category returned as a dictionary with {cat_name: df}
    '''
    column_category_mean = get_category_names(df)
    categories={}
    for cat in column_category_mean:
        categories[cat] = np.array(df[['lat_center','lng_center', cat]])
    return categories

if __name__ == '__main__':

    gradient_dict = {}
