"""
This module contains a function to append the Wflow update and forecast scenarios 
XML file containing to the spatial display of the system

"""
#Load modules
import xml.etree.cElementTree as ET
import xmlfunct.xmlfunct as XMLF
import xmlfunct.fewshelpers as fewshelp
import os
import numpy as np
import pandas as pd


def SpatialDisplayWflow(pathDB, pathFEWS):
    """
    Arguments: 
        
        pathDB: [String] Path to the external database holding the information on the 
        characteristics of the system.
        pathFEWS: [String] Path to the Config Folder of scripted FEWS.
    
    Returns: 
        Tree with the XML documents, indented and exported as XML files for: 
            
            -Spatial display for the wflow models' forecast and update scenarios (DisplayConfigFiles)
    """    
    sub = ET.SubElement
    subText = XMLF.add_child_with_text
    
    #Read tables from Microsoft Access database 
    import_info = XMLF.readDataBase("qry_Wflow_Workflows",pathDB)
    
    #Read and parse the spatial display config file containing the defaults and the data products
    tree = ET.parse(pathFEWS + "/Config/DisplayConfigFiles/GridDisplay.xml")#Read and parse the spatial display config file that contains the data products imported
    root = tree.getroot()
    
    #Definition of variables imported to be shown in the spatial data display
    parameters = {"tp": "Precipitation [mm]", "2t":"Temperature (2m) [oC]", "E.ref.mak": "PET (Makkink) [mm]","Q.simulated": "Discharge [m3/s]"} 
    
    #Forecast chain elements
    chainInformation = pd.DataFrame(np.array([['Reanalysis', 'historical'], ['Observation', 'historical'], ['Forecast', 'forecasting']]), columns= ['product', 'type']) 
    
    #Creation of the child elements of the XML of Spatial Display
    
    info_per_model_groups = import_info.groupby('Wflow_ModelID') #Grouping display by wflow model name
    for model_group in info_per_model_groups:
        wflowModel = model_group[0]
        infoWorkflow = model_group[1]
        
        #GridPlotGroup element and children for wflow models
        child0 = sub(root, "gridPlotGroup", {"id":wflowModel, "name":wflowModel}) 
        
        # for each model, select the workflows with type forecast (to display of whole forecast chain) associated to the workflow name
        for index0, row0 in infoWorkflow.iterrows():  
            
            if row0['WorkflowTypeID'] == 'update': 
                chainInfo = chainInformation.iloc[0:2] #Select only "historical" mode of the forecast chain
            else: 
                chainInfo = chainInformation
            
            #create display for each forecast scenario available for each wflow model.
            child1 = sub(child0, "gridPlotGroup", {"id":row0['Wflow_WorkflowName'], "name":row0['Wflow_WorkflowName']}) 
            
            
            def function (n):
                """
                Arguments: 
                    
                    n: [string] Ensemble number of the data product used for forecast ("single" if deterministic)
                
                Returns: 
                    Tree with all elements correspondent to the wflow models execution workflows
                        
                """  
                
                #Display all variables listed in dictionary 'parameters'
                for par, namePar in parameters.items(): 
                    
                    #Display of all forecast chain reanalysis - online reanalysis - forecast
                    for index, row in chainInfo.iterrows(): 
                        
                        #Definition of name of element "GridPlot" depending on the type of scenario (update, forecast)
                        if row["product"] == "Reanalysis":                    
                            gridPlotName = '{}_{}_{}_{}'.format('update', row0['DataProductID_Reanalysis'], par, n)
                        elif row["product"] == "Observation":                    
                            gridPlotName = '{}_{}_{}_{}'.format('update', row0['DataProductID_Observation'], par, n)
                        else:
                            gridPlotName = '{}_{}_{}_{}_{}'.format('forecast', row0['DataProductID_Observation'], row0['DataProductID_Observation'], par, n)
                            
                    child1_1 = sub(child1, "gridPlot", {"id": gridPlotName, "name": namePar + " " + n}) 
            
                    for index, row in chainInfo.iterrows(): #Display of all forecast chain reanalysis - online reanalysis - forecast
                      
                        # Creation of time series set element depending on type of scenario
                        child1_1_1 = sub(child1_1, "timeSeriesSet") 
                        
                        #Definition of moduleInstanceName used to plot the time series. 
                        #The display is for the preprocessed data (tot_prec, pet, t2m) and the simulated flow (Q)
                        if row["product"] == "Forecast": 
                            
                            moduleInstanceName = '{}_{}_{}_{}'.format(wflowModel, 'forecast', row0['DataProductID_Observation'], row0['DataProductID_Forecast'])
                            
                        else: 
                            
                            #Module instance name adopted in the general adapter for the simulated flow 
                            if par == "Q.simulated": 
                                moduleInstanceName = '{}_{}_{}'.format(wflowModel, 'update', row0['DataProductID_'+ row['product']])
                            #Module instance name of preprocessed variables
                            else: 
                                moduleInstanceName = '{}_{}_{}_{}'.format('preprocess', wflowModel, 'update', row0['DataProductID_' + row['product']])
                        
                        #Children of time series set element
                        subText(child1_1_1, "moduleInstanceId", moduleInstanceName)
                        subText(child1_1_1,"valueType", "grid")
                        subText(child1_1_1,"parameterId", par) 
                        subText(child1_1_1,"locationId", wflowModel) 
                        
                        #Definition of time series type for variables
                        if par == "Q.simulated":
                            tsTypeName = "simulated " + row['type']
                        else: 
                            tsTypeName = "external " + row['type']
                         
                        #More children of time series set element
                        subText(child1_1_1,"timeSeriesType", tsTypeName) 
                        sub(child1_1_1, "timeStep", {"unit":"hour", "multiplier": str(row0['Wflow_TimeStep'])})
                        
                        #Definition of relative view period and read write mode according to the type of data product
                        #Addition of more children to time series set element 
                        if row["product"] == "Reanalysis":
                            sub(child1_1_1, "relativeViewPeriod", {"unit":"day", "start":str(row0['Rean_RelViewPeriod_Start']),"end":str(row0['Rean_RelViewPeriod_End'])})
                            subText(child1_1_1,"readWriteMode", "read only")
                        elif row["product"] == "Observation":
                            sub(child1_1_1, "relativeViewPeriod", {"unit":"day", "start":str(row0['Rean_RelViewPeriod_End']),"end":"0"})
                            subText(child1_1_1,"readWriteMode", "read only")
                        else: 
                            subText(child1_1_1,"readWriteMode", "read complete forecast")
                            subText(child1_1_1,"ensembleId", row0['DataProductID_Forecast'])
                            if row0['DataProductID_Forecast'].endswith('eps'):
                                subText(child1_1_1,"ensembleMemberIndex", str(n)) #Consideration of ensembles
            
            #Determination of type of forecast product used in workflow  
            if row0['DataProductID_Forecast'].endswith('eps'):
                
                for n in range (1, 41): #Consideration of ensemble 
                    
                    function(str(n))   
            else: 
                
                function("single") #In case forecast product is deterministic
                        
        #Modified Spatial display XML indentation and file export
        XMLF.indent(root)
        pathSave = os.path.join(pathFEWS,'Config/DisplayConfigFiles/')
        fewshelp.makedir_ifnotexist(pathSave)
        XMLF.serialize_xml(root,pathSave,'GridDisplay.xml')
