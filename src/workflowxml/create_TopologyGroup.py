"""
This module contains a function to create the Topology Group XML file for Wflow
model execution from the navigation panel 

"""
#Load modules
import xml.etree.cElementTree as ET
import xmlfunct.xmlfunct as XMLF

def TopologyGroup(pathDB,pathFEWS): 
    """
    Arguments: 
        
        pathDB: [String] Path to the external database holding the information on the 
        characteristics of the system.
        pathFEWS: [String] Path to the Config Folder of scripted FEWS.
    
    Returns: 
        Tree with the XML document of the Grid information of data products, indented 
        and exported as XML file for the:
        -Topology of the navigation panel for the wflow model execution (RegionConfigFiles)
     
    """
    
    sub = ET.SubElement
    subText = XMLF.add_child_with_text

    #Read tables from Microsoft Access database
    workflows= XMLF.readDataBase("qry_Wflow_Workflows", pathDB)
    
    #Creation of root of the Topology Group XML file"""
    root = XMLF.create_xml_root("topologyGroup",{'version':False})
    
    #Creation of XML Child Elements
    child0 = sub(root, "group", {"id":"wflow"})
    child1 = sub(child0, "nodes", {"id":"wflow_group","name":"wflow update, forecast runs"})
    
    
    info_per_model_groups = workflows.groupby('Wflow_ModelID') #Grouping of workflows by wflow model 
    for model_group in info_per_model_groups:
        wflowModel = model_group[0]
        wflowModelInfo = model_group[1]
        
        child1_1 = sub(child1, "nodes", {"id":wflowModel,"name":wflowModel})
        
        #Addition of Workflow names to topology for update (online reanalysis) and forecast scenarios for each wflow model using NWP data 
        for index, row in wflowModelInfo.iterrows(): 
            myWfId = row["Wflow_WorkflowName"]
            child1_1_1 = sub(child1_1, "node", {"id":myWfId, "name":myWfId})
            subText(child1_1_1, "workflowId", myWfId)
        
        #Addition of Workflow names to topology for update for each wflow model using reanalysis
        info_per_reanalysis_groups = model_group[1].groupby('DataProductID_Reanalysis') #Grouping of wflow models by reanalysis product used for its update
        for reanalysis_group in info_per_reanalysis_groups:
            reanalysisProduct = reanalysis_group[0]
            
            myWfId = wflowModel + "_update_" + reanalysisProduct
            child1_1_1 = sub(child1_1, "node", {"id":myWfId, "name":myWfId})
            subText(child1_1_1, "workflowId", myWfId)
    
    
    #Creation of Topology Group XML indentation and file export
    XMLF.indent(root)  
    pathFile = '{}{}'.format(pathFEWS,'/Config/RegionConfigFiles/')
    XMLF.serialize_xml(root,pathFile,"TopologyGroup_wflow.xml") 
    
