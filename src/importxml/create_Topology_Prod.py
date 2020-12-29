"""
This module contains a function to write the topology XML file of the navigation
panel for the data products processing

"""
#Load modules
import xml.etree.cElementTree as ET
import xmlfunct.xmlfunct as XMLF

def TopologyProd (pathDB,pathFEWS):
    """
    Arguments: 
        
        pathDB: [String] Path to the external database holding the information on the 
        characteristics of the system.
        pathFEWS: [String] Path to the Config Folder of scripted FEWS.
    
    Returns: 
        Tree with the XML documents, indented and exported as XML files for: 
            
            -Topology of the navigation panel for the data products (RegionConfigFiles)
    """
    
    sub = ET.SubElement
    subText = XMLF.add_child_with_text
    
    #Read tables from Microsoft Access database
    workflows = XMLF.readDataBase("qry_Wflow_Workflows",pathDB)
    
    #Creation of root of Topology XML file
    root = XMLF.create_xml_root("topology",{'version':False})
    subText(root,"enableAutoRun", "false")
    
    def topologyChildren(prod, dataType, provider): 
        """
    Arguments: 
        
        prod: [String] data product name
        dataType: [String] data product type (e.g., NWP)
        provider: [String] data product provider
    
    Returns: 
        Tree with children of first element "nodes" 
    """
        #child element "nodes" with name of data product
        child1 = sub(child0, "nodes", {"id": prod, "name": prod})
        subText(child1,"showModifiers", "false")
        
        #Addition of children for data import
        child1_1 = sub(child1, "node", {"id": "import_"+ prod, "name": "Import " + prod})
        subText(child1_1,"workflowId", "import_"+ dataType +"_" + provider + "_" + prod)
        subText(child1_1,"localRun", "false")
        
        #Addition of children for postprocessing of import
        child1_2 = sub(child1, "node", {"id": "post-process_import_"+ prod, "name": "Post-process import " + prod})
        subText(child1_2,"workflowId", "postprocess_import_"+ dataType +"_" + provider + "_" + prod)
        subText(child1_2,"localRun", "false")
    
    
    #Creation of Topology for import and post-process of import of NWP
    child0 = sub(root, "nodes", {"id": "import_nwp", "name": "Import and post-process nwp forecast"})
    
    forecastProducts = [] # save forecast products in list, to later compare that list to products used as "observation" (for online reanalysis) and avoid repetition
    info_per_forecast_groups = workflows.groupby('DataProductID_Forecast') #Grouping of data products used for forecast by name
   
    #Topology for NWP data used for forecast (import and post-process)
    for forecast_group in info_per_forecast_groups:
        prod = forecast_group[0]
        infoWorkflow = forecast_group[1]
        forecastProducts.append(prod)
        
        dataType = "nwp"
        provider = infoWorkflow['DataProduct_Frcst_Provider'].iloc[0]
    
        topologyChildren(prod, dataType, provider)#Execution of topologyChildren for NWP used for forecast
    
    #Topology for NWP data used for online reanalysis (import and post-process)
    info_per_obs_groups = workflows.groupby('DataProductID_Observation') #Grouping of data products used for online reanalysis by name
    for obs_group in info_per_obs_groups:
        prod = obs_group[0]
        infoWorkflow = obs_group[1]
    
         #Add any NWP product that was imported but only used for online reanalysis creation for the update scenario and not for forecast 
        if prod not in forecastProducts: 
            
            forecastProducts.append(prod) #Add NWP to list
            
            dataType = "nwp"
            provider = infoWorkflow['DataProduct_Obs_Provider'].iloc[0]
            
            topologyChildren(prod, dataType, provider)#Execution of topologyChildren for NWP used for online reanalysis
    
    #Creation of Topology for import and post-process of reanalysis data products    
    child0 = sub(root, "nodes", {"id": "import_reanalysis", "name": "Import and post-process reanalysis products"})
    
    info_per_reanalysis_groups = workflows.groupby('DataProductID_Reanalysis')
    for reanalysis_group in info_per_reanalysis_groups:
        prod = reanalysis_group[0]
        infoWorkflow = reanalysis_group[1]
        
        dataType = "reanalysis"
        provider = infoWorkflow['DataProduct_Rean_Provider'].iloc[0]
    
        topologyChildren(prod, dataType, provider) #Execution of topologyChildren for NWP used for reanalysis data
        
    
    #Creation of Topology for creation of online reanalysis
    child1 = sub(root, "nodes", {"id": "create_reanalysis", "name": "Create online reanalysis"})
    subText(child1,"showModifiers", "false")
    
    for obs_group in info_per_obs_groups:
        prod = obs_group[0]
        infoWorkflow = obs_group[1]
        
        provider = infoWorkflow['DataProduct_Obs_Provider'].iloc[0]
        
        #Addition of children
        child1_1 = sub(child1, "node", {"id": "reanalysis_"+ prod, "name": "Create " + prod + " based reanalysis"})
        subText(child1_1,"workflowId", "create_reanalysis_" + provider + "_" + prod)
        subText(child1_1,"localRun", "false")
        subText(child1_1,"showRunApprovedForecastButton", "true")
    
    #Addition of element to later append the topology group for wflow models
    child2 = sub(root, "nodes", {"id": "wflow_models", "name": "wflow update, forecast runs"})
    subText(child2,"groupId", "wflow")
    
    
    #Creation of Topology XML indentation and file export
    XMLF.indent(root)  
    pathFile = '{}{}'.format(pathFEWS,'/Config/RegionConfigFiles/')
    XMLF.serialize_xml(root,pathFile,"Topology.xml") 
    
