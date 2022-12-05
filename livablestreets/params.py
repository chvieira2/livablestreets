import pandas as pd

### GCP configuration - - - - - - - - - - - - - - - - - - -

# /!\ you should fill these according to your account

### GCP Project - - - - - - - - - - - - - - - - - - - - - -

# not required here

### GCP Storage - - - - - - - - - - - - - - - - - - - - - -

BUCKET_NAME = 'wagon-data-871-vieira-livablestreets'

##### Data  - - - - - - - - - - - - - - - - - - - - - - - -

# train data file location
# /!\ here you need to decide if you are going to train using the provided and uploaded data/train_1k.csv sample file
# or if you want to use the full dataset (you need need to upload it first of course)
BUCKET_TRAIN_DATA_PATH = 'data/Berlin_grid_1000m.csv'

##### Training  - - - - - - - - - - - - - - - - - - - - - -

# not required here

##### Model - - - - - - - - - - - - - - - - - - - - - - - -

# model folder name (will contain the folders for all trained model versions)
MODEL_NAME = 'livablestreets'

# model version folder name (where the trained model.joblib file will be stored)
MODEL_VERSION = 'v1'

### GCP AI Platform - - - - - - - - - - - - - - - - - - - -

# not required here

### - - - - - - - - - - - - - - - - - - - - - - - - - - - -



#### Preloaded cities of choice ####
dict_city_number_wggesucht = {
            'Berlin': '8',
            'München': '90',
            'Stuttgart': '124',
            'Köln': '73',
            'Hamburg': '55',
            'Düsseldorf': '30',
            'Bremen':'17',
            'Leipzig':'77',
            'Kiel':'71',
            'Heidelberg':'59',
            'Karlsruhe':'68',
            'Hannover':'57',
            'Dresden':'27',
            'Aachen':'1',
            'Bonn':'13',
            'Darmstadt': '23',
            'Frankfurt am Main':'41',
            'Göttingen':'49',
            'Münster':'91',
            'Mainz':'84',
            'Mannheim':'85',
            'Nürnberg':'96',
            'Regensburg':'111',
            'Tübingen':'127',
            'Würzburg':'141'
        }


#### test nominatim, 'city' , 'country ISO code'
failed_cities = {'Stockholm': 'SE',
                 'Belfast': 'GB',
                 'Brussels': 'BE',
                 'Copenhagen': 'DK',
                 'Moscow': 'RU',
                 'Quebec': 'CA'}


preloaded_cities = sorted(set([
            'Amsterdam',
            'Barcelona',
            # 'Belfast', # Wrong location in US
            'Boston',
            'Bratislava',
            # 'Bruxelles', # no features
            'Budapest',
            'Buenos Aires',
            # 'Copenhagen', # wrong location in US
            'Dublin',
            'Lisboa',
            'London',
            'Los Angeles',
            'Madrid',
            'Marseille',
            'Miami',
            'Milano',
            'Montpellier',
            'Montréal',
            # 'Moscow', # no features
            'New York',
            'Oslo',
            'Palo Alto',
            'Paris',
            'Porto Alegre',
            # 'Québec', # This gives me the whole province
            'Rio de Janeiro',
            'Roma',
            'Salt Lake City',
            'San Francisco',
            'San Jose',
            'São Paulo',
            'Stockholm', # no features
            'Tallinn',
            'Vancouver',
            'Warszawa',
            'Wien',
            'Zagreb',
            'Zürich'
                    ] + list(dict_city_number_wggesucht.keys())))



##### Conversion values for OSM features
indiv_factors_mapping = {'activities_economic':2,
                        'activities_education':4,
                        'activities_educational':2,
                        'activities_goverment':1,
                        'activities_health_local':4,
                        'activities_health_regional':2,
                        'activities_post':1,
                        'activities_public_service':2,
                        'activities_retail':4,
                        'activities_supermarket':2,

                        'comfort_comfort_spots':2,
                        'comfort_green_forests':4,
                        'comfort_green_natural':2,
                        'comfort_green_parks':2,
                        'comfort_green_space':2,
                        'comfort_lakes':4,
                        'comfort_leisure_mass':2,
                        'comfort_leisure_spots':1,
                        'comfort_rivers':4,
                        'comfort_railway':4,
                        'comfort_street_motorway':4, # Highways
                        'comfort_industrial':4,
                        'comfort_warehouse':1,

                        'mobility_bike_infraestructure':4,
                        'mobility_public_transport_bus':4,
                        'mobility_public_transport_rail':2,
                        'mobility_street_primary':2, # Main roads in the city?
                        'mobility_street_secondary':2, # Other type of main roads?

                        'social_life_community':1,
                        'social_life_culture':2,
                        'social_life_eating':4,
                        'social_life_night_life':4}



conversion_formulas_OSM_features = pd.DataFrame(
                [['activities_economic',[0, 1, 2, 3, 4, 5], [-0.5, 4, 1, 0, -1, -1], 4],
                 ['activities_education',[0, 1, 2, 3, 4, 5], [-0.5, 4, 1, 0, -1, -1], 4],
                 ['activities_educational',[0, 1, 2, 3, 4, 5], [0, 4, 1, 0, -1, -1], 4],
                 ['activities_goverment',[0, 1, 2, 3, 4, 5], [0, 4, 2, 0, 0, -1], 4],
                 ['activities_health_local',[0, 1, 2, 3, 4, 5], [-1, 2, 4, 2, 0, -1], 3],
                 ['activities_health_regional',[0, 1, 2, 3, 4, 5], [-0.5, 4, 0, 0, -1, -1], 4],
                 ['activities_post',[0, 1, 2, 3, 4, 5], [0, 4, 2, 0, 0, -1], 4],
                 ['activities_public_service',[0, 1, 2, 3, 4, 5], [-0.5, 4, 2, 0, 0, -1], 4],
                 ['activities_retail',[0, 1, 2, 4, 5], [-4, 0, 4, -4, -4], 4],
                 ['activities_supermarket',[0, 1, 2, 3, 4, 5], [-1, 2, 4, 2, 0, -1], 3],

                 ['comfort_comfort_spots',[0, 1, 2, 3, 4, 5], [-0.5, 4, 2, 1, 0, -1], 3],
                 ['comfort_green_forests',[0, 1, 2, 3, 4, 5], [0, 3, 4, 3, 2, 2], 4],
                 ['comfort_green_natural',[0, 3, 6, 9, 12, 15], [0, 3, 4, 3, 2, 1], 4],
                 ['comfort_green_parks',[0, 3, 6, 9, 12, 15], [-0.5, 3, 4, 2, 1, 0], 4],
                 ['comfort_green_space',[0, 2, 4, 6, 8, 10], [-0.5, 3, 4, 2, 1, 0], 4],
                 ['comfort_lakes',[0, 1, 2, 3], [0, 4, 4, 4], 3],
                 ['comfort_leisure_mass',[0, 1, 2, 3, 4, 5], [0, 4, 1, 0, -1, -1], 4],
                 ['comfort_leisure_spots',[0, 2, 4, 6, 8], [0, 4, 2, 0, 0], 3],
                 ['comfort_rivers',[0, 1, 2, 3], [0, 4, 4, 4], 3],
                 ['comfort_railway',[0, 1, 2, 3, 4], [0, -3, -4, -4, -4], 2],
                 ['comfort_street_motorway',[0, 1, 2, 3, 4], [0, -3, -4, -4, -4], 2],
                 ['comfort_industrial',[0, 1, 2, 3, 4], [0, -2, -3, -4, -4], 2],
                 ['comfort_warehouse',[0, 1, 2, 3, 4], [0, -2, -2, -4, -4], 2],

            ['mobility_bike_infraestructure',[0, 1, 2, 3, 4, 5], [-0.5, 4, 2, 1, 0, -1], 4],
            ['mobility_public_transport_bus',[0, 1, 2, 3, 4, 5], [-0.5, 4, 4, 1, 0, -1], 4],
            ['mobility_public_transport_rail',[0, 1, 2, 3, 4, 5], [-0.5, 4, 2, 1, 0, -1], 4],
                 ['mobility_street_primary',[0, 1, 2, 3, 4], [-1, 4, 2, -1, -2], 4],
                 ['mobility_street_secondary',[0, 1, 2, 3, 4], [-1, 4, 2, -1, -2], 4],


                 ['social_life_community',[0, 1, 2, 3, 4, 5], [-0.5, 4, 1, 0, -1, -1], 4],
                 ['social_life_culture',[0, 1, 2, 3, 4, 5], [-0.5, 4, 1, 0, -1, -1], 4],
                 ['social_life_eating',[0,1,2,3,4,5,6,7,8], [-1,2,4,4,2,1,0,0,-1], 5],
                 ['social_life_night_life',[0,1,2,3,4,5,6], [-0.5, 2, 4, 1, 0, -1, -1], 4],
                 ],
                columns = ['feature', 'x', 'y', 'poly_degree'])

mins = []
maxs = []
for _, row in conversion_formulas_OSM_features.iterrows():
    mapping_factor = indiv_factors_mapping[row['feature']]
    min_val_row = min(row['y'])
    max_val_row = max(row['y'])
    mins.append(min_val_row * mapping_factor)
    maxs.append(max_val_row * mapping_factor)

conversion_formulas_OSM_features['min_val'] = mins
conversion_formulas_OSM_features['max_val'] = maxs
