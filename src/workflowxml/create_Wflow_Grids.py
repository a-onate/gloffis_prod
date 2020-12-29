"""
This module contains a function to create the Wflow Grids XML file to
describe the grids of the wflow models incorporated to the system

"""
#Load modules
import xml.etree.cElementTree as ET
import xmlfunct.xmlfunct as XMLF

def WflowGrids(pathDB,pathFEWS):
    """
    Arguments: 
        
        pathDB: [String] Path to the external database holding the information on the 
        characteristics of the system.
        pathFEWS: [String] Path to the Config Folder of scripted FEWS.
    
    Returns: 
        Tree with the XML document of the Grid information wflow models, indented 
        and exported as XML file (Wflow_Grids_import.xml) (RegionConfigFiles)
     
    """

    sub = ET.SubElement
    subText = XMLF.add_child_with_text
    
    #Read tables from Microsoft Access database
    wflow_model_grids = XMLF.readDataBase("tbl_Scripting_Wflow_GRID_Info",pathDB)

    #Creation of root of the Grids_wflow XML file
    root = XMLF.create_xml_root("grids",{'version':False})

    #Creation of XML Child Elements
    def add_grids(root, row):
        """This function creates the XML child elements of the current XML file
        Arguments: 
            root: [String] Root of the Grids_wflow XML file. 
            row: [String] Current row of the dataframe. Argument later used to loop through pandas rows
        
        Returns: 
            Tree with elements correspondent to each wflow model
        
        """
        #Children elements needed for the grid definition
        child0 = sub(root, "regular", {"locationId":row["Wflow_ModelID"]})
        subText(child0,"rows", str(row["rows"]))
        subText(child0,"columns", str(row["columns"]))
        subText(child0,"geoDatum", row["geoDatum"])
        child0_4 = sub(child0, "firstCellCenter")
        subText(child0_4,"x", str(row["firstCellCenter_x"]))
        subText(child0_4,"y", str(row["firstCellCenter_y"]))
        subText(child0,"xCellSize", str(row["xCellSize"]))
        subText(child0,"yCellSize", str(row["yCellSize"]))

    #Loop through rows of wflow_model_grids dataframe    
    [add_grids(root, row) for index, row in wflow_model_grids.iterrows()]

    #Creation of Grids_wflow XML indentation and file export
    XMLF.indent(root)  
    pathFile = '{}{}'.format(pathFEWS,'/Config/RegionConfigFiles/')
    XMLF.serialize_xml(root,pathFile,"Grids_wflow.xml") 

