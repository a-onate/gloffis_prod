"""
This module contains a function to write a csv file with the wflow model names
for the Map Layer Configuration

"""
#Load modules
import xmlfunct.xmlfunct as XMLF
import xmlfunct.fewshelpers as fewshelp
import os

def MapLayerFiles (pathDB,pathFEWS):
    """
    Arguments: 
        pathDB: Path where the database is. String.
        pathFEWS: Path where the FEWS Folder is. String.
    
    Returns: 
        .csv file with names of wflow models active in database for system
    """

    #Read tables from Microsoft Access database
    wflow_models = XMLF.readDataBase("tbl_Scripting_Wflow_GRID_Info",pathDB)

    #Path where the .csv wflow model list will be saved
    path = os.path.join(pathFEWS,'Config/MapLayerFiles/csv/')
    fewshelp.makedir_ifnotexist(path)
    
    #Export the .csv wflow model list
    wflow_models.Wflow_ModelID.to_csv('{}{}'.format(path,'wflow_models.csv'), index=False, header =["wflow_models"])




