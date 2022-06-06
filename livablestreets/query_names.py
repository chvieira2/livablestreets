'''-------------------------mobility------------------------------'''

#Queries for mobility
# Nodes
public_transport = {'amenity':['bus_station'],
                    'bus_bay':'',
                   'highway':['bus_stop','platform'],
                   'public_transport':['stop_position','platform','station','stop_area'],
                   'railway':['station','tram_stop', 'subway_entrance']}

bike_infraestructure =  {'amenity':['bicycle_parking', 'bicycle_repair_station', 'bicycle_rental']}

# Ways
cycle_paths = {'bicycle':['designated'],
              'highway':['cycleway'],
              'cycleway':['lane','opposite','opposite_lane','track','opposite_track','share_busway']}

pedestrian = {'highway':['pedestrian','footway','living_street','corridor'],
                'foot':['designated']}

'''-------------------------social life---------------------------'''

#Queries for social life

# Nodes
eating = {'amenity':['cafe','restaurant', 'food_court', 'ice_cream']}

night_life = { 'amenity':['bar','pub','biergarten', 'nightclub', 'swingerclub', 'casino']}

culture = {'amenity':['social_centre','theatre','public_bookcase',
                      'fountain', 'events_venue', 'community_centre', 'cinema',
                      'arts_centre', 'conference_centre']}

community = {'office': ['association','charity', 'coworking',
                        'educational_institution', 'employment_agency', 'foundation',
                        'ngo', 'political_party', 'research']}



'''------------------------activities-------------------------------'''


#Queries for acitvities

#Nodes
health_care = {'amenity':['baby_hatch','clinic','dentist',
                      'doctors', 'hospital', 'nursing_home', 'pharmacy',
                      'social_facility', 'veterinary']}

public_service = {'amenity':['courthouse','fire_station','police',
                      'post_box', 'post_office', 'townhall']}

education = {'amenity':['college','kindergarten','language_school',
                      'library', 'music_school', 'school', 'university']}

economic = {'amenity':['atm', 'bank', 'bureau_de_change']}



'''-----------------------------comfort--------------------------'''


#Queries for comfort

# Nodes
comfort_spots = {'amenity':['bbq','bench','dog_toilet',
                      '	drinking_water', 'give_box', 'shelter', 'shower',
                      'toilets', 'water_point', 'watering_place']}

leisure_spots = {'leisure':['bandstand','bird_hide','dog_park',
                      'firepit', 'swimming_pool', 'stadium', 'sports_centre',
                      'pitch', 'picnic_table', 'fitness_centre'],
                 'historic':''}

# Ways

green = {'landuse':['grass','forest','orchard','allotments','cementery','flowerbed', 'meadow','greenfield', 'recreation_ground','village_green'],
         'leisure':['park','playground','garden','swimming_area','playground', 'nature_reserve', 'marina'],
         'natural':['heath','shrubbery','wood','grassland']}

water = {'natural':['water','beach'],
         'amenity':['fountain']}
