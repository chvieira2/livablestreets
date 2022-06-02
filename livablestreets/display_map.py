import folium
from folium.plugins import HeatMap
import pandas as pd
import numpy as np
from livablestreets.utils import get_file, save_file, min_max_scaler
from livablestreets.livability_score import feature_field_mean_score,livability_score

#--------------display map--------------------
mapObj = folium.Map(location=[52.5200, 13.4050], zoom_start=11)

if __name__ == '__main__':

    df_grid = get_file(file_name='FeatCounts_Berlin_grid_1000m.csv', save_local=True)
    df_grid = min_max_scaler(df_grid)
    df_features = feature_field_mean_score(df_grid)
    df_livability = livability_score(df_features)
    save_file(df_features, file_name='Features_Berlin_grid_1000m.csv')
    save_file(df_livability, file_name='Livability_Berlin_grid_1000m.csv')
