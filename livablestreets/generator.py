from livablestreets.create_grid import create_geofence
from livablestreets.add_features_to_grid import integrate_all_features_counts3
from livablestreets.livability_score import livability_score
from livablestreets.utils import simple_time_tracker, get_file

class LivabilityMap(object):
    def __init__(self,stepsize = 3000):
        """ This class puts together all processes to generate and plot the map with livability heatmap
            """
        self.df_grid = None
        self.df_grid_FeatCount = None
        self.df_grid_Livability = None
        self.location = None
        self.stepsize = stepsize
        self.weights = None

    def location_input(self):
        """ Function that asks the user for their input.
        for now it automatically returns Berlin"""
        self.location = 'Berlin'

    def stepsize_input(self):
        """ Function that asks the user for their input.
        for now it automatically returns 3000"""
        self.stepsize = 3000

    def weights_input(self):
        """ Function that asks the user for their input.
        for now it automatically returns (1,1,1,1)"""
        self.weights = (1,1,1,1)

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

        return self.df_grid


    @simple_time_tracker
    def add_FeatCount_grid(self):
        """ Add features to grid """

        ## Makes sure that df_grid exists
        if self.df_grid is None:
            self.generate_grid()

        ## Get features for a given location
    # def get_feat_loc(self.location):
    #     pass
        # Needs fixing as it isn't working stand alone. Needs to collect from API (OSM) and save features as csv

        ## Integrates features count to grid
        if self.df_grid_FeatCount is None:
            try :
                self.df_grid_FeatCount = get_file(f'FeatCount_{self.location}_grid_{self.stepsize}m.csv', local_file_path=f'data/{self.location}/WorkingTables', gcp_file_path = f'data/{self.location}/WorkingTables', save_local=True)
            except FileNotFoundError:
                self.df_grid_FeatCount = integrate_all_features_counts3(df_grid = self.df_grid, stepsize=self.stepsize, location=self.location)
        else:
            print('add_FeatCount_grid has already been called before')

        ## Integrate other forms of features
        # For the future....

        return self.df_grid_FeatCount


    @simple_time_tracker
    def calc_livability(self):
        """ Calculate the livability score given the weights"""

        # Get weights
        if self.weights is None:
            self.weights_input()

        ## Makes sure that features have been added
        if self.df_grid_FeatCount is None:
            self.add_FeatCount_grid()

        ## Calculate livability
        if self.df_grid_Livability is None:
            try :
                self.df_grid_Livability = get_file(f'Livability_{self.location}_grid_{self.stepsize}m.csv', local_file_path=f'data/{self.location}/WorkingTables', gcp_file_path = f'data/{self.location}/WorkingTables', save_local=True)
            except FileNotFoundError:
                self.df_grid_Livability = livability_score(self.df_grid_FeatCount, weights = self.weights,
                                    columns_interest = ['activities_mean', 'comfort_mean', 'mobility_mean', 'social_mean'],
                                    stepsize = self.stepsize, location = self.location,
                                    save_local=True, save_gcp=True)
        else:
            print('calc_livability has already been called before')

        return self.df_grid_Livability

    def visualize(self):
        """ This method should plot the interactive map of location with the features and the livability shown in heatmap"""
        pass




if __name__ == '__main__':
    Berlin = LivabilityMap(stepsize = 3000).calc_livability()
    print(Berlin.describe())
