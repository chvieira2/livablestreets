import pandas as pd
from livablestreets.utils import save_file

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


# Distance and sigma


mobility = {
            'public_transport_bus' : [public_transport_bus, 'mobility_public_transport_bus', 200 , 'Node', 'Point', 'Point' , 'mobility' ] ,
            'public_transport_rail' : [public_transport_rail, 'mobility_public_transport_rail', 500 , 'Node', 'Point', 'Point' , 'mobility' ] ,
            'bike_infraestructure' : [bike_infraestructure, 'mobility_bike_infraestructure' , 50 , 'Node', 'Point', 'Point' , 'mobility' ]
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
                'eating' : [eating, 'social_life_eating', 200 , 'Node', 'Point', 'Point' , 'social_life' ] ,
                'night_life' : [night_life,'social_life_night_life' , 300 , 'Node', 'Point', 'Point' , 'social_life' ] ,
                'culture' : [culture,'social_life_culture' ,  500 , 'Node', 'Point', 'Point' , 'social_life' ] ,
                'community' : [community,'social_life_community', 400 , 'Node', 'Point', 'Point' , 'social_life' ]
                }

'''------------------------activities-------------------------------'''


#Queries for activities

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
            'health_regional' : [health_regional, 'activities_health_regional', 1000 , 'Node','Point','Point', 'activities'] ,
            'health_local' : [health_local, 'activities_health_local', 300 , 'Node','Point','Point', 'activities'] ,
            'goverment' : [goverment,'activities_goverment', 500  , 'Node','Point','Point', 'activities'] ,
            'public_service' : [public_service, 'activities_public_service', 400 , 'Node','Point','Point', 'activities'] ,
            'post' : [post, 'activities_post', 100, 'Node','Point','Point', 'activities'] ,
            'education' : [education, 'activities_education', 500, 'Node','Point','Point', 'activities'] ,
            'educational' : [educational, 'activities_educational', 200, 'Node','Point','Point', 'activities'] ,
            'economic' : [economic, 'activities_economic', 100 , 'Node','Point','Point', 'activities']
            }

'''-----------------------------comfort--------------------------'''


#Queries for comfort

# Nodes
comfort_spots = {'amenity':['bbq','bench','dog_toilet',
                      '	drinking_water', 'give_box', 'shelter', 'shower',
                      'toilets', 'water_point', 'watering_place', 'fountain']}

leisure_spots = {'leisure':['bird_hide','dog_park', 'firepit', 'pitch', 'picnic_table'],
                 'historic': [True]}

leisure_mass = {'leisure':['bandstand', 'swimming_pool', 'stadium', 'sports_centre', 'fitness_centre']}


# Distance and sigma

comfort = {
            'comfort_spots' : [ comfort_spots, 'comfort_comfort_spots', 100 , 'Node' , 'Point', 'Point', 'comfort' ] ,
            'leisure_spots' : [ leisure_spots, 'comfort_leisure_spots', 200 , 'Node' , 'Point', 'Point', 'comfort' ] ,
            'leisure_mass' : [ leisure_mass, 'comfort_leisure_mass', 500 , 'Node' , 'Point', 'Point', 'comfort' ] }



'''--------------------------complex query--------------------------'''
# Ways

green_forests = {'landuse':['wood','forest','orchard']}
green_space = {'landuse':['allotments','cementery','flowerbed', 'meadow','greenfield', 'recreation_ground','village_green']}
green_parks = {'leisure':['park','playground','garden','swimming_area','playground', 'nature_reserve', 'marina']}
green_natural = {'natural':['heath','shrubbery','grass','grassland']}


lakes = {'natural':['water','beach']}
rivers = {'waterway':['river']}

# Ways
pedestrian = {'highway':['pedestrian']}
pedestrian1 = {'highway': ['footway']}
pedestrian2 = {'highway':['living_street','corridor']}
pedestrian3 = {'foot':['designated']}

cycle_paths = {'bicycle':['designated']}
cycle_paths1 = {'highway':['cycleway'], 'cycleway':['lane','opposite','opposite_lane']}
cycle_paths2 = {'cycleway':['track','opposite_track','share_busway']}




complex = {
            # 'pedestrian' : [pedestrian,'pedestrian' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            # 'pedestrian1' : [pedestrian1,'pedestrian1' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            # 'pedestrian2' : [pedestrian2,'pedestrian2' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            # 'pedestrian3' : [pedestrian3,'pedestrian3' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            # 'cycle_paths' : [cycle_paths,'cyclpath' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            # 'cycle_paths1' : [cycle_paths1,'cyclpath1' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            # 'cycle_paths2' : [cycle_paths2,'cyclpath2' , 100 , 'Way', 'Line', 'lineString' , 'mobility' ] ,
            'green_forests' : [ green_forests,'comfort_green_forests', 800 , 'Way' ,'Line','multiPolygon', 'comfort' ] ,
            'green_space' : [ green_space,'comfort_green_space', 300 , 'Way' ,'Line','multiPolygon', 'comfort' ] ,
            'green_parks' : [ green_parks,'comfort_green_parks', 500 , 'Way' ,'Line','multiPolygon', 'comfort' ] ,
            'green_natural' : [ green_natural,'comfort_green_natural', 200 , 'Way' ,'Line','multiPolygon', 'comfort' ] ,
            'lakes' : [ lakes,'comfort_lakes', 200 , 'Way' ,'Line','multiPolygon', 'comfort' ],
            'rivers' : [ rivers,'comfort_rivers', 300 , 'Way' ,'Line','multiPolygon', 'comfort' ]
            }

'''--------------------------negative query--------------------------'''


street_motorway = {'highway':['motorway']}
street_primary = {'highway':['primary']}
street_secondary = {'highway':['secondary']}
# street_terteary = {'highway':['terteary']}

railway = {'railway':['light_rail'],
            'bridge':['viaduct']}
# street_terteary_wf = [(('',''),('','')),]
# street_terteary_bf = [('',''),]

industrial = {'building' : ['industrial']}
retail = {'building' : ['retail']}
supermarket = {'building' : ['supermarket']}
warehouse = {'building' : ['warehouse']}


negative = {
            'street_motorway' : [street_motorway,'negative_street_motorway', 500 , 'Way', 'Line', 'lineString' , 'negative'], #, street_motorway_wf, street_motorway_bf ] ,
             'street_primary' : [street_primary,'negative_street_primary', 250 , 'Way', 'Line', 'lineString' , 'negative'],#, street_primary_wf, street_primary_bf ] ,
             'street_secondary' : [street_secondary,'negative_street_secondary', 100 , 'Way', 'Line', 'lineString' , 'negative'],#, street_secondary_wf, street_secondary_bf ] ,
            #  'street_terteary' : [street_terteary,'street_terteary',50 , 'Way', 'Line', 'lineString' , 'negative'], #, street_terteary_wf, street_terteary_bf ] ,
             'railway' : [railway,'negative_railway' ,500 , 'Way', 'Line', 'lineString' , 'negative'], #, railway_wf, railway_bf ] ,
             'industrial' : [industrial,'negative_industrial', 300 , 'Way' ,'Line','lineString', 'negative' ],
             'retail' : [retail,'negative_retail', 200 , 'Way' ,'Line','lineString', 'negative' ],
             'supermarket' : [supermarket,'negative_supermarket', 200 , 'Way' ,'Line','lineString', 'negative' ],
             'warehouse' : [warehouse,'negative_warehouse', 200 , 'Way' ,'Line','lineString', 'negative' ],
}




'''--------------------------  definitions  --------------------------'''

columns = ['query_string','name','distance','geomtype','jsontype','shapelytype','category']
columns_wb = ['query_string', 'name','distance','geomtype','jsontype','shapelytype','category','whitefilter','blackfilter']

def master_query(location_name = None, save_local=True, save_gcp=False):

        master_q = {}
        master_q.update(mobility)
        master_q.update(social_life)
        master_q.update(activities)
        master_q.update(comfort)
        master_q.update(complex)
        master_q.update(negative)

        query_df = pd.DataFrame.from_dict(master_q, orient='index', columns = columns)

        if location_name is not None:
            save_file(query_df, file_name=f'master_query_{location_name}.csv', local_file_path=f'livablestreets/data/{location_name}/WorkingTables', gcp_file_path = f'data/{location_name}/WorkingTables', save_local=save_local, save_gcp=save_gcp)

        return query_df


if __name__ == "__main__":
    print(master_query())
