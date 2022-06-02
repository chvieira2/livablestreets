from livablestreets.utils import get_file, save_file, min_max_scaler
import pandas as pd
import numpy as np

def livability_score(df, weights = [1,1,1,1], columns_interest = ['activities_mean', 'comfort_mean', 'mobility_mean', 'social_mean']):
    """ Calculates the livability score in each grid by taking the weighted sum of all field_mean values"""

    df['livability'] = df[columns_interest].mul(weights).sum(axis=1)
    df = min_max_scaler(df, columns = ['livability'])
    return df


if __name__ == '__main__':
    df_grid = get_file(file_name='FeatCounts_Berlin_grid_1000m.csv')
    df_grid = livability_score(df_grid)
    save_file(df_grid, file_name='Livability_Berlin_grid_1000m.csv')
