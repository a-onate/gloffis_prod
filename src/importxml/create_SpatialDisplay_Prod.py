"""
This module contains a function to write the spatial display XML file for the 
data products imported

"""
#Load modules
import xml.etree.cElementTree as ET
import xmlfunct.xmlfunct as XMLF
import xmlfunct.fewshelpers as fewshelp
import os

def SpatialDisplayProd(pathDB, pathFEWS,pathDefault):
    """
    Arguments: 
        
        pathDB: [String] Path to the external database holding the information on the 
        characteristics of the system.
        pathFEWS: [String] Path to the Config Folder of scripted FEWS.
    
    Returns: 
        Tree with the XML documents, indented and exported as XML files for: 
            
            -Spatial display for the data products imported (DisplayConfigFiles)
    """

    sub = ET.SubElement
    subText = XMLF.add_child_with_text
    
    #Read tables from Microsoft Access database    
    workflows = XMLF.readDataBase("qry_Wflow_Workflows",pathDB)
    
    #Definition of variables imported to be shown in the spatial data display  
    parameters = {"tp": "Precipitation [mm]", "2t":"Temperature (2m) [oC]", "E.ref.mak": "PET (Makkink) [mm]"} #parameters displayed
    
    #Read and parse the default spatial display config file
    sdDefault= os.path.join(pathDefault,'SpatialDisplay_defaults.xml') 
    tree = ET.parse(sdDefault) 
    root = tree.getroot() 
    
    #Creation of the child elements of the XML of Spatial Display
    
    #NWP Products used for forecast 
    forecastProducts = [] # save forecast products in list, to later compare that list to products used as "observation" (for online reanalysis) and avoid repetition
    info_per_forecast_groups = workflows.groupby('DataProductID_Forecast') #Grouping of data products used for forecast by name
    for forecast_group in info_per_forecast_groups:
        forecastProd = forecast_group[0]
        infoWorkflow = forecast_group[1]
        forecastProducts.append(forecastProd) #Adding forecast product names to list
        
        #GridPlotGroup element and children for Ensembles of NWP products
        if forecastProd.endswith('eps'): 
            
            child1 = sub(root, "gridPlotGroup", {"id":forecastProd, "name":forecastProd})
            
            for par, namePar in parameters.items(): #display of all variables listed in dictionary 'parameters'
                
                for n in range (1, 41): #Ensembles of 41 elements
                    
                    #Children of gridPlotGroup element
                    child1_1 = sub(child1, "gridPlot", {"id": '{}_{}_{}_{}_{}'.format("nwp", infoWorkflow['DataProduct_Frcst_Provider'].iloc[0], forecastProd, par, str(n)), "name": namePar + "Member " + str(n)}) 
                    child1_1_1 = sub(child1_1, "timeSeriesSet")
                    
                    #TimeSeriesSet children elements
                    subText(child1_1_1, "moduleInstanceId", '{}_{}_{}'.format("import_nwp", infoWorkflow['DataProduct_Frcst_Provider'].iloc[0], forecastProd))
                    subText(child1_1_1,"valueType", "grid")
                    subText(child1_1_1,"parameterId", par) 
                    subText(child1_1_1,"locationId", forecastProd) 
                    subText(child1_1_1,"timeSeriesType", "external forecasting") 
                    sub(child1_1_1, "timeStep", {"unit":"hour", "multiplier": str(infoWorkflow['DataProduct_Frcst_TimeStep'].iloc[0])})
                    subText(child1_1_1,"readWriteMode", "read complete forecast")
                    subText(child1_1_1,"ensembleId", forecastProd)
                    subText(child1_1_1,"ensembleMemberIndex", str(n))
        
        #GridPlotGroup element and children for Deterministic NWP products            
        else: 
    
            child1 = sub(root, "gridPlotGroup", {"id":forecastProd, "name":forecastProd})
            
            for par, namePar in parameters.items(): #display of all variables listed in dictionary 'parameters'
                
                #Children of gridPlotGroup element
                child1_1 = sub(child1, "gridPlot", {"id": '{}_{}_{}_{}'.format("nwp", infoWorkflow['DataProduct_Frcst_Provider'].iloc[0], forecastProd, par), "name": namePar}) 
                child1_1_1 = sub(child1_1, "timeSeriesSet")
                
                #TimeSeriesSet children elements
                subText(child1_1_1, "moduleInstanceId", '{}_{}_{}'.format("import_nwp", infoWorkflow['DataProduct_Frcst_Provider'].iloc[0], forecastProd))
                subText(child1_1_1,"valueType", "grid")
                subText(child1_1_1,"parameterId", par) 
                subText(child1_1_1,"locationId", forecastProd) 
                subText(child1_1_1,"timeSeriesType", "external forecasting") 
                sub(child1_1_1, "timeStep", {"unit":"hour", "multiplier": str(infoWorkflow['DataProduct_Frcst_TimeStep'].iloc[0])})
                subText(child1_1_1,"readWriteMode", "read complete forecast")
                subText(child1_1_1,"ensembleId", forecastProd)
    
    #NWP used for creation of Online Reanalysis               
    info_per_obs_groups = workflows.groupby('DataProductID_Observation') #Grouping of data products used for "observation" (Online Reanalysis) by name
    for obs_group in info_per_obs_groups:
        obsProd = obs_group[0]
        infoWorkflow = obs_group[1]
        
        #Add online reanalysis to the grid display        
        child1 = sub(root, "gridPlotGroup", {"id":"create_reanalysis_" + obsProd, "name": "create_reanalysis_" + obsProd})
            
        for par, namePar in parameters.items(): #display all variables listed in dictionary 'parameters'
            
            #Children of GridPlotGroup element
            child1_1 = sub(child1, "gridPlot", {"id": '{}_{}_{}_{}'.format("create_reanalysis", infoWorkflow['DataProduct_Obs_Provider'].iloc[0], obsProd, par), "name": namePar}) 
            child1_1_1 = sub(child1_1, "timeSeriesSet")
            
            #TimeSeriesSet children elements
            subText(child1_1_1, "moduleInstanceId", '{}_{}_{}'.format("create_reanalysis", infoWorkflow['DataProduct_Obs_Provider'].iloc[0], obsProd))
            subText(child1_1_1,"valueType", "grid")
            subText(child1_1_1,"parameterId", par) 
            subText(child1_1_1,"locationId", obsProd) 
            subText(child1_1_1,"timeSeriesType", "external historical") 
            sub(child1_1_1, "timeStep", {"unit":"hour", "multiplier": str(infoWorkflow['DataProduct_Obs_TimeStep'].iloc[0])})
            sub(child1_1_1, "relativeViewPeriod", {"unit":"day", "start":"0","end":"5"})
            subText(child1_1_1,"readWriteMode", "read only")
        
        #Add any NWP product that was imported but only used for online reanalysis creation for the update scenario and not for forecast 
        if obsProd not in forecastProducts: 
            
            #GridPlotGroup element
            child1 = sub(root, "gridPlotGroup", {"id":obsProd, "name":obsProd})
            
            for par, namePar in parameters.items(): #display all variables listed in dictionary 'parameters'
                
                    #Children of GridPlotGroup element
                    child1_1 = sub(child1, "gridPlot", {"id": '{}_{}_{}_{}'.format("nwp", infoWorkflow['DataProduct_Obs_Provider'].iloc[0], obsProd, par), "name": namePar}) 
                    child1_1_1 = sub(child1_1, "timeSeriesSet")
                    
                    #TimeSeriesSet children elements
                    subText(child1_1_1, "moduleInstanceId", '{}_{}_{}'.format("import_nwp", infoWorkflow['DataProduct_Obs_Provider'].iloc[0], obsProd))
                    subText(child1_1_1,"valueType", "grid")
                    subText(child1_1_1,"parameterId", par) 
                    subText(child1_1_1,"locationId", obsProd) 
                    subText(child1_1_1,"timeSeriesType", "external forecasting") 
                    sub(child1_1_1, "timeStep", {"unit":"hour", "multiplier": str(infoWorkflow['DataProduct_Obs_TimeStep'].iloc[0])})
                    subText(child1_1_1,"readWriteMode", "read complete forecast")
                    subText(child1_1_1,"ensembleId", obsProd)
    
    #Reanalysis data used for update scenario  
    info_per_rean_groups = workflows.groupby('DataProductID_Reanalysis') #Grouping of data products used for update by name
    for rean_group in info_per_rean_groups:
        reanProd = rean_group[0]
        infoWorkflow = rean_group[1]
            
        child1 = sub(root, "gridPlotGroup", {"id":reanProd, "name":reanProd})
        
        for par, namePar in parameters.items(): #display all parameters listed in dictionary 'parameters'
                
                #Children of GridPlotGroup element
                child1_1 = sub(child1, "gridPlot", {"id": '{}_{}_{}_{}'.format("reanalysis", infoWorkflow['DataProduct_Rean_Provider'].iloc[0], reanProd, par), "name": namePar}) 
                child1_1_1 = sub(child1_1, "timeSeriesSet")
                
                #TimeSeriesSet children elements
                subText(child1_1_1, "moduleInstanceId", '{}_{}_{}'.format("import_reanalysis", infoWorkflow['DataProduct_Rean_Provider'].iloc[0], reanProd))
                subText(child1_1_1,"valueType", "grid")
                subText(child1_1_1,"parameterId", par) 
                subText(child1_1_1,"locationId", reanProd) 
                subText(child1_1_1,"timeSeriesType", "external historical") 
                sub(child1_1_1, "timeStep", {"unit":"hour", "multiplier": str(infoWorkflow['DataProduct_Rean_TimeStep'].iloc[0])})
                sub(child1_1_1, "relativeViewPeriod", {"unit":"day", "start":str(infoWorkflow['Rean_RelViewPeriod_Start'].iloc[0]),"end":str(infoWorkflow['Rean_RelViewPeriod_End'].iloc[0])})
                subText(child1_1_1,"readWriteMode", "read only")
                 
    #Modified Spatial display XML indentation and file export
    XMLF.indent(root)
    
    pathSave = os.path.join(pathFEWS,'Config/DisplayConfigFiles/') #path where the file will be saved
    fewshelp.makedir_ifnotexist(pathSave)
    
    XMLF.serialize_xml(root,pathSave,'GridDisplay.xml')