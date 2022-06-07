from esy.osmfilter import run_filter
from esy.osmfilter import Node, Way, Relation

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
                            CreateElements=True,
                            LoadElements=False,
                            verbose=True)
    return Data


# if __name__ == '__main__':

#     return Data
