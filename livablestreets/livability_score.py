from livablestreets.utils import get_file, save_file, min_max_scaler
import pandas as pd
import numpy as np


def feature_field_mean_score(df):
    """ Receives a dataframe and looks for columns containing the field indicator (activities, comfort, mobility, social)
        Calculate the row-wise mean of columns in that field and add it to a new column called field_mean"""

    for field in ('activities', 'comfort', 'mobility', 'social'):
        columns_interest = [column for column in df.columns if f"{field}_" in column]
        df[f"{field}_mean"] = df[columns_interest].mean(axis=1)

    return df

def livability_score(df, weights = [1,1,1,1], columns_interest = ['activities_mean', 'comfort_mean', 'mobility_mean', 'social_mean']):
    """ Calculates the livability score in each grid by taking the weighted sum of all field_mean values"""

    df['livability'] = df[columns_interest].mul(weights).sum(axis=1)
    df = min_max_scaler(df, columns = ['livability'])
    return df


if __name__ == '__main__':
    df_grid = get_file(file_name='FeatCounts_Berlin_grid_1000m.csv')
    df_grid = min_max_scaler(df_grid)
    df_grid = feature_field_mean_score(df_grid)
    df_grid = livability_score(df_grid)
    save_file(df_grid, file_name='Livability_Berlin_grid_1000m.csv')
