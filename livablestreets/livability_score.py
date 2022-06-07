from livablestreets.utils import save_file, min_max_scaler, get_file
import pandas as pd
import numpy as np

def livability_score(df, weights = [1,1,1,1],
                     columns_interest = ['activities_mean', 'comfort_mean', 'mobility_mean', 'social_mean'],
                     stepsize = 100, location = 'berlin',
                     save_local=True, save_gcp=True):
    """ Calculates the livability score in each grid by taking the weighted sum of all category_mean values.
        Category_mean values Have been already MinMax scaled
        """
    new_cols = [col + '_weighted' for col in columns_interest]
    df_foo = df.copy()
    df_foo[new_cols] = df_foo[columns_interest].mul(weights)
    df['livability'] = df_foo[new_cols].sum(axis=1)
    df = min_max_scaler(df, columns = ['livability'])

    save_file(df, file_name=f'Livability_{location}_grid_{stepsize}m.csv', local_file_path=f'data/{location}/WorkingTables', gcp_file_path = f'data/{location}/WorkingTables', save_local=save_local, save_gcp=save_gcp)

    return df

if __name__ == '__main__':
    df_grid = get_file(file_name='data_berlin_WorkingTables_Livability_berlin_grid_3000m.csv', local_file_path='data/berlin/WorkingTables', gcp_file_path = 'data/berlin/WorkingTables')
    print(livability_score(df_grid, stepsize = 100))
    print('')
