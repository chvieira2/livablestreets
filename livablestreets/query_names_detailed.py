
# 4 categories with key, values list for openstreetmap feature extraction
# dictionaries determinating geometry type (node or ways)
# dictionaries for determinig influece distance, for computing sigma (blurring)
# final master dictionary with all the information 'master_query'


'''-------------------------mobility------------------------------'''

#Queries for mobility

# Nodes
public_transport_bus = {'amenity':['bus_station'],
                    'bus_bay':'',
                   'highway':['bus_stop']}

public_transport_rail = { 'public_transport':['stop_position','station','stop_area'],
                   'railway':['station','tram_stop', 'subway_entrance']}

bike_infraestructure =  {'amenity':['bicycle_parking', 'bicycle_repair_station', 'bicycle_rental']}

# Ways
cycle_paths = {'bicycle':['designated'],
              'highway':['cycleway'],
              'cycleway':['lane','opposite','opposite_lane','track','opposite_track','share_busway']}

pedestrian = {'highway':['pedestrian','footway','living_street','corridor'],
                'foot':['designated']}

# Distance and sigma

mobility = {
            'node' : [ public_transport_bus , public_transport_rail, bike_infraestructure ],
            'way' : [ pedestrian, cycle_paths ]
            }

mobility_distance = {
                    'public_transport_bus' : 200 ,
                    'public_transport_rail' : 500 ,
                    'bike_infraestructure' : 50 ,
                    'pedestrian' : 100 ,
                    'cycle_paths' : 100
                    }

'''-------------------------social life---------------------------'''

#Queries for social life

# Nodes
eating = {'amenity':['cafe','restaurant', 'food_court', 'ice_cream']}

night_life = { 'amenity':['bar','pub','biergarten', 'nightclub', 'swingerclub', 'casino']}

culture = {'amenity':['social_centre','theatre','public_bookcase',
                      'events_venue', 'community_centre', 'cinema',
                      'arts_centre', 'conference_centre']}

community = {'office': ['association','charity', 'coworking',
                        'educational_institution', 'employment_agency', 'foundation',
                        'ngo', 'political_party', 'research']}

# Distance and sigma

social_life = {
            'node' : [ eating, night_life, culture, community ],
            'way' : []
            }

social_life_distance = {
                    'eating' : 200 ,
                    'night_life' : 300 ,
                    'culture' : 500 ,
                    'community' : 400 ,
                    }

'''------------------------activities-------------------------------'''


#Queries for acitvities

#Nodes
health_regional = {'amenity':['hospital', 'clinic','nursing_home', 'social_facility']}

health_local = {'amenity':['baby_hatch','dentist', 'doctors', 'pharmacy', 'veterinary']}

goverment = { 'amenity': ['townhall', 'courthouse']}

public_service = {'amenity':[ 'fire_station','police' ]}

post = {'amenity':[ 'post_box', 'post_office' ]}

education = {'amenity':['college', 'music_school', 'school', 'university']}

educational = { 'amenity' : ['kindergarten','language_school', 'library',]}

economic = {'amenity':['atm', 'bank', 'bureau_de_change']}

# Distance and sigma
activities = {
            'node' : [ health_regional, health_local, goverment, public_service, post, education, educational, economic],
            'way' : []
            }

activities_distance = {
                    'health_regional' : 1000 ,
                    'health_local' : 300 ,
                    'goverment' : 500 ,
                    'public_service' : 400 ,
                    'post' : 100,
                    'education' : 500,
                    'educational' : 200,
                    'economic' : 100
                    }

'''-----------------------------comfort--------------------------'''


#Queries for comfort

# Nodes
comfort_spots = {'amenity':['bbq','bench','dog_toilet',
                      '	drinking_water', 'give_box', 'shelter', 'shower',
                      'toilets', 'water_point', 'watering_place', 'fountain']}

leisure_spots = {'leisure':['bird_hide','dog_park', 'firepit', 'pitch', 'picnic_table'],
                 'historic': ['']}

leisure_mass = {'leisure':['bandstand', 'swimming_pool', 'stadium', 'sports_centre', 'fitness_centre']}

# Ways

green = {'landuse':['grass','forest','orchard','allotments','cementery','flowerbed', 'meadow','greenfield', 'recreation_ground','village_green'],
         'leisure':['park','playground','garden','swimming_area','playground', 'nature_reserve', 'marina'],
         'natural':['heath','shrubbery','wood','grassland']}

water = {'natural':['water','beach'],
         'amenity':['fountain']}

# Distance and sigma
comfort = {
            'node' : [ comfort_spots, leisure_spots, leisure_mass],
            'way' : [ green, water ]
            }

comfort_distance = {
                    'comfort_spots' : 100 ,
                    'leisure_spots' : 200 ,
                    'leisure_mass' : 500 ,
                    'green' : 500 ,
                    'water' : 500
                    }


'''--------------------------master query--------------------------'''


master_query = {
                mobility : mobility_distance ,
                social_life : social_life_distance,
                activities : activities_distance,
                comfort : comfort_distance
                }
