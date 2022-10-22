from esy.osmfilter import run_filter
from esy.osmfilter import Node, Way, Relation

''' This filter function is used only when using PBF files as input. pbf files are much faster to load than osm files.
pbf files are also much smaller than osm files. The downside is that pbf files are not human readable. '''

def data_from_pbf(index, stri, pbf, json):
    '''index, string, pbf, json'''
    name = index
    string = stri
    PBF_inputfile = pbf
    JSON_outputfile = json
    prefilter = {Node: string, Way: string, Relation: {}}
    blackfilter = [("",""),]
    whitefilter = [(('',''),('','')),]

    [Data, E] = run_filter(name,
                            PBF_inputfile,
                            JSON_outputfile,
                            prefilter,
                            whitefilter,
                            blackfilter,
                            NewPreFilterData=True,
                            CreateElements=False,
                            LoadElements=False,
                            verbose=True)
    return Data


# if __name__ == '__main__':

#     return Data
