"""
This module contains a function to write a XML file and a csv file used to
describe the grids of the data products imported to the system 

"""
#Load modules
import xml.etree.cElementTree as ET
import xmlfunct.xmlfunct as XMLF


def GridsImport(pathDB,pathFEWS):
    
    """
    Arguments: 
        
        pathDB: [String] Path to the external database holding the information on the 
        characteristics of the system.
        pathFEWS: [String] Path to the Config Folder of scripted FEWS.
    
    Returns: 
        -Tree with the XML document of the Grid information of data products, indented 
        and exported as XML file (Grids_import.xml) (RegionConfigFiles)
        -.csv file with names of data products being imported (for locations - MapLayerFiles)
    
    """
    
    sub = ET.SubElement
    subText = XMLF.add_child_with_text
    
    #Read tables from Microsoft Access database
    gridIDs = XMLF.readDataBase("tbl_Scripting_DataProducts_GRID_Info",pathDB)
    
    ##############################################################
                # Create Grids Import XML File
    ##############################################################
    
    #Creation of root of the Grids_import XML file
    root = XMLF.create_xml_root("grids",{'version':False})
    
    #Creation of the child elements of the XML
    for index, row in gridIDs.iterrows(): 
    
        child0 = sub(root, "regular", {"locationId":row["DataProduct_ID"]})
        subText(child0,"rows", str(row["rows"]))
        subText(child0,"columns", str(row["columns"]))
        subText(child0,"geoDatum", row["geoDatum"])
        
        
        if row['firstCellCenter_x'] != None and "0": #If grid is defined using first cell centers.
            child0_4 = ET.SubElement(child0, "firstCellCenter")
            subText(child0_4,"x", str(row["firstCellCenter_x"]))
            subText(child0_4,"y", str(row["firstCellCenter_y"]))
            subText(child0,"xCellSize", str(row["xCellSize"]))
            subText(child0,"yCellSize", str(row["yCellSize"]))
        else: 
            child0_4 = ET.SubElement(child0, "gridCorners") #If grid is defined using grid corners.
            child0_4_1 = ET.SubElement(child0_4, "upperLeft")
            subText(child0_4_1,"x", str(row["cornerUpLeft_x"]))
            subText(child0_4_1,"y", str(row["cornerUpLeft_y"]))
            child0_4_2 = ET.SubElement(child0_4, "lowerRight")
            subText(child0_4_2,"x", str(row["cornerLowRight_x"]))
            subText(child0_4_2,"y", str(row["cornerLowRight_y"]))

    #Grids XML indentation and file export
    XMLF.indent(root)  
    pathFileGrid = '{}{}'.format(pathFEWS,'/Config/RegionConfigFiles/') #path where the file will be saved
    XMLF.serialize_xml(root,pathFileGrid,"Grids_import.xml")
    
    
    ##############################################################
            #Creation of csv file with names of data products
    ##############################################################
    
    info_per_productType_groups = gridIDs.groupby('DataProduct_Type') #grouping of products depending on their type, to create a .csv for each type (e.g., nwp, reanalysis)
    
    for productType_group in info_per_productType_groups:
        
        dataProductType = productType_group[0]
        dataProductInfo = productType_group[1]
        pathFileCSV = '{}{}{}_{}_{}'.format(pathFEWS,'/Config/MapLayerFiles/csv/','import',dataProductType, 'grids.csv')
        headerCSV = '{}{}{}'.format('import_',dataProductType,'_grids')
        
        dataProductInfo.DataProduct_ID.to_csv(pathFileCSV,index=False, header=[headerCSV])



