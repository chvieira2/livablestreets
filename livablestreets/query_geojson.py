import os

from esy.osmfilter import run_filter
from esy.osmfilter import export_geojson

import urllib.request
import geopandas as gpd

import shapely.geometry as geometry
from shapely.ops import linemerge, unary_union, polygonize

from shapely.geometry import mapping
from geojson import dump


from livablestreets.query_names_detailed import master_query
from livablestreets.query_names_detailed import master_query_complex
from livablestreets.query_osmfilter import data_from_pbf


def get_pbf_json(country= 'germany',city = 'berlin'):
    #Download PBF file from geofabrik
    #example url: https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf
    #Returns the file paths for use at Run_filter

    city_name = f'{city}-latest'

    if not os.path.exists(f'livablestreets/data/{city}/Features/{city_name}.osm.pbf'):
        filename, headers = urllib.request.urlretrieve(
            f'https://download.geofabrik.de/europe/{country}/{city_name}.osm.pbf',
            filename=f'livablestreets/data/{city}/Features/{city_name}.osm.pbf')
        PBF_inputfile = filename

    #gets the path for PBF
    PBF_inputfile = os.path.join(os.getcwd(), f'livablestreets/data/{city}/Features/{city_name}.osm.pbf')
    JSON_outputfile = os.path.join(os.getcwd(), f'livablestreets/data/{city}/Features/{city_name}.json')


    return PBF_inputfile, JSON_outputfile



def shapely_format(lis,shapelytype):
    # Returns the shapely format for the layer for use at Run_filter

    if shapelytype == 'Point':
        # converting to multi points
        shapely_geom = geometry.MultiPoint(lis)

    if shapelytype == 'lineString':
    # converting to multi lines
        merged = linemerge([*lis])  # merge LineStrings
        borders = unary_union(merged)  # linestrings to a MultiLineString
        shapely_geom = geometry.MultiLineString(lis)

    if shapelytype == 'multiPolygon':
    #converting to multipolygon
        merged = linemerge([*lis])  # merge LineStrings
        borders = unary_union(merged)  # linestrings to a MultiLineString
        polygons = list(polygonize(borders))
        shapely_geom = geometry.MultiPolygon(lis)

    return shapely_geom





def run_filter(query_df, country= 'germany' , city_name= 'berlin'):
    # run filter from PBF file
    # get file paths
    PBF_inputfile, JSON_outputfile = get_pbf_json(country,city_name)

    # loops over dataframe of queries from query_names_detailed
    for index, row in query_df.iterrows():
        filter_name = index
        string = row['query_string']
        geometry = row['geomtype']

        jsontype = row['jsontype']
        category = row['category']
        shapelytype = row['shapelytype']

        if not os.path.exists(f'livablestreets/data/{city_name}/Features/df-{category}-{filter_name}.geojson'):
            # initilize filter
            print(f'Filtering fetures: {filter_name} - {category}')

            # calls filter from query_osmfilter.py
            Data = data_from_pbf(filter_name, string, PBF_inputfile, JSON_outputfile)
            export_geojson(Data[geometry],Data,filename=f'livablestreets/data/{city_name}/Features/df-{category}-{filter_name}.geojson',jsontype=jsontype)

        if not os.path.exists(f'livablestreets/data/{city_name}/Features/shapes-{category}-{filter_name}.geojson'):
            print(f'Exporting shapes of: {filter_name} - {category} as: {geometry}')
            elements = gpd.read_file(f'livablestreets/data/{city_name}/Features/df-{category}-{filter_name}.geojson')

            # create list of features
            lis = []
            for l in elements['geometry']:
                lis.append(l)

            shapely_geo = shapely_format(lis,shapelytype)

            gjson = mapping(shapely_geo)
            with open(f'livablestreets/data/{city_name}/Features/shapes-{category}-{filter_name}.geojson', 'w') as f:
                dump(gjson, f)



if __name__ == "__main__":

    # set up dataframe:
    # uncomment the desired one:

    # df = master_query()
    df = master_query_complex()
    # df = master_query_advanced()

    # uncomment to create slice:
    # new = df.iloc[14:22]

    run_filter(df,'germany', 'berlin')
