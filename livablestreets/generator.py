from livablestreets.create_grid import create_geofence, get_shape_of_location
from livablestreets.add_features_to_grid import integrate_all_features_counts
from livablestreets.livability_score import livability_score
from livablestreets.utils import simple_time_tracker, get_file, create_dir
from livablestreets.get_csv import get_all
from livablestreets.osm_query import query_params_osm

from livablestreets.query_names_detailed import master_query, master_query_complex, master_query_negative
from livablestreets.query_geojson import run_filter

from memoized_property import memoized_property
import pandas as pd


class LivabilityMap(object):
    def __init__(self, location = 'berlin' , location_country = 'germany', stepsize = 1000, weights = (1,1,1,1)):
        """ This class puts together all processes to generate and plot the map with livability heatmap
            """
        self.df_grid = None
        self.df_grid_FeatCount = None
        self.df_grid_Livability = None
        self.location = location.lower()
        self.location_country = location_country.lower()
        self.stepsize = stepsize
        self.weights = weights
        self.sigmas = [0,0,0,0,8,0,0,9,0,0,0,0,0,0]

        # Create folder for location if it doesn't exist
        create_dir(path = f'livablestreets/data/{self.location}')
        create_dir(path = f'livablestreets/data/{self.location}/Features')
        create_dir(path = f'livablestreets/data/{self.location}/WorkingTables')

    @simple_time_tracker
    def generate_grid(self):
        """ Function that puts together everything"""

        ## Gets input from user
        if self.location is None:
            self.location_input()

        if self.stepsize is None:
            self.stepsize_input()


        ## Creates the Geofance for the inputed location
        if self.df_grid is None:
            try :
                self.df_grid = get_file(f'{self.location}_grid_{self.stepsize}m.csv', local_file_path=f'data/{self.location}/WorkingTables', gcp_file_path = f'data/{self.location}/WorkingTables', save_local=True)
            except FileNotFoundError:
                self.df_grid = create_geofence(stepsize = self.stepsize, location = self.location, save_local=True, save_gcp=True)
        else:
            print('generate_grid has already been called before')

        ## Create the location center as class variable and the path to the corresponding GeoJson file
        # get location shape
        gdf_shape_location = get_shape_of_location(self.location)

        # Obtain shape's centroid
        centroid = gdf_shape_location.centroid
        centroid = list(centroid[0].coords)[0]
        self.location_centroid = centroid

        self.path_location_geojson = f'livablestreets/data/{self.location}/{self.location}_boundaries.geojson'

        return self.df_grid

    @memoized_property
    def get_features(self):
        # get_all(location=self.location)

        # get csv of cities of the world
        df_cities = pd.read_csv('data/world-cities.csv')
        city = self.location
        # assigns country name to variable
        country = df_cities.loc[df_cities['name'] == city.capitalize()].country.values.flatten()[0]

        #launchs queries of gejson and csv files from local PBF
        df = master_query()
        run_filter(df, country.lower(), city)

    @simple_time_tracker
    def add_FeatCount_grid(self):
        """ Add features to grid """
        ## Makes sure that df_grid exists
        if self.df_grid is None:
            self.generate_grid()

        ## Get features for a given location
        try:
            get_file('activities_economic.csv', local_file_path='data/{self.location}/WorkingTables', gcp_file_path = 'data/{self.location}/WorkingTables', save_local=True)
        except FileNotFoundError:
            self.get_features()

        ## Integrates features count to grid
        if self.df_grid_FeatCount is None:
            try :
                self.df_grid_FeatCount = get_file(f'FeatCount_{self.location}_grid_{self.stepsize}m.csv', local_file_path=f'data/{self.location}/WorkingTables', gcp_file_path = f'data/{self.location}/WorkingTables', save_local=True)
            except FileNotFoundError:
                self.df_grid_FeatCount = integrate_all_features_counts(df_grid = self.df_grid, stepsize=self.stepsize, location=self.location)
        else:
            print('add_FeatCount_grid has already been called before')

        ## Integrate other forms of features
        # For the future....

        return self.df_grid_FeatCount

    @simple_time_tracker
    def calc_livability(self, imputed_weights = None):
        """ Calculate the livability score given the weights"""

        # Get weights
        if imputed_weights is None:
            if self.weights is None:
                self.weights_input()
        else:
            self.weights = imputed_weights

        ## Calculate livability
        if self.df_grid_Livability is None:
            try :
                self.df_grid_Livability = get_file(f'Livability_{self.location}_grid_{self.stepsize}m.csv', local_file_path=f'data/{self.location}/WorkingTables', gcp_file_path = f'data/{self.location}/WorkingTables', save_local=True)

            except FileNotFoundError:
                self.df_grid_Livability = livability_score(self.add_FeatCount_grid(), weights = self.weights,
                                    columns_interest = ['activities_mean',
                                                        'comfort_mean',
                                                        'mobility_mean',
                                                        'social_mean'],
                                    stepsize = self.stepsize, location = self.location,
                                    save_local=True, save_gcp=True)
        else:
            print('livability_score has already been called before')

        if imputed_weights is not None:
            self.df_grid_Livability = livability_score(self.df_grid_Livability,
                                                        weights = self.weights,
                            columns_interest = ['activities_mean',
                                                'comfort_mean',
                                                'mobility_mean',
                                                'social_mean'],
                            stepsize = self.stepsize, location = self.location,
                            save_local=True, save_gcp=True)
            print(f'Livability has been updated with weights {self.weights}')

        return self.df_grid_Livability





if __name__ == '__main__':
    # city = LivabilityMap(location = 'berlin')
    # city.calc_livability()
    # print(city.df_grid_Livability.describe())
    city = LivabilityMap(location = 'berlin', stepsize= 2000)
    city.calc_livability()
    print(city.df_grid_Livability.describe())
