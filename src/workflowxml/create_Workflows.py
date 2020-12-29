"""
This module contains a function to write XML files related to the execution of 
wflow models in update and forecast mode for two Delft-FEWS directories: 
RegionConfigFiles and WorkflowFiles

"""
#Load modules
import xml.etree.cElementTree as ET
import xmlfunct.xmlfunct as XMLF
import xmlfunct.fewshelpers as fewshelp
import os


def Workflows(pathDB,pathFEWS):
    """
    Arguments: 
        
        pathDB: [String] Path to the external database holding the information on the 
        characteristics of the system.
        pathFEWS: [String] Path to the Config Folder of scripted FEWS.
    
    Returns: 
        -Tree with the XML document of the Workflows XML files for model execution,
        indented and exported as XML file (WorkflowFiles).
        -Module instance descritors for model execution (RegionConfigFiles)
        -Workflows descritors for model execution (RegionConfigFiles)
    """
    
    sub = ET.SubElement
    subText = XMLF.add_child_with_text
    
    #Read tables from Microsoft Access database 
    import_info = XMLF.readDataBase("qry_Wflow_Workflows",pathDB)
    
    #Creation of roots for moduleInstanceDescriptors and WorkflowDescriptors XML files
    rootModuleInstance = XMLF.create_xml_root("moduleInstanceDescriptors")  
    rootWorkflow = XMLF.create_xml_root("workflowDescriptors")
    
    ################################################################################################
        #Creation of Workflows for Execution of Models in Update Mode using Reanalysis Data
    ################################################################################################
    
    info_per_model_groups = import_info.groupby('Wflow_ModelID') #Grouping of information by name of wflow model 
    for model_group in info_per_model_groups:
        wflowModel = model_group[0]
        modelInfo = model_group[1]
        
        #Addition of children to modelInstanceDescriptors XML 
        sub(rootModuleInstance, "moduleInstanceDescriptor", {"id": wflowModel}) #id = name of wflow model
        
        #In case wflow model is global (w3ra), add also moduleInstanceDescriptor for routing
        if modelInfo['Wflow_ModelTypeID'].iloc[0] == "w3ra": 
            sub(rootModuleInstance, "moduleInstanceDescriptor", {"id": wflowModel + "_routing"}) 
        
        info_per_reanalysis_groups = model_group[1].groupby('DataProductID_Reanalysis')#Grouping of wflow models by name of reanalysis products used to run them 
        for reanalysis_group in info_per_reanalysis_groups:
            reanalysisProduct = reanalysis_group[0]
            reanalysis_info = reanalysis_group[1]
            
            #Creation of root of workflows XMLs
            root = XMLF.create_xml_root("workflow")
            
            #Creation of element "properties"
            child1_properties = sub(root,"properties") 
            
            #Addition of children elements to "properties"
            moduleInstanceImport_ID = '{}_{}_{}_{}'.format("import",reanalysis_info['DataProduct_Rean_Type'].iloc[0],reanalysis_info['DataProduct_Rean_Provider'].iloc[0],reanalysisProduct)
            sub(child1_properties, "string", {"key": "_DATA_PROD_MODULE_INSTANCE", "value": moduleInstanceImport_ID})
            sub(child1_properties, "string", {"key": "_DATA_PROD", "value": reanalysisProduct})
            sub(child1_properties, "string", {"key": "_DATA_PROD_TEMPORAL_RES", "value": str(reanalysis_info['DataProduct_Rean_TimeStep'].iloc[0])})
            sub(child1_properties, "string", {"key": "_REL_VIEW_PERIOD_START", "value": str(int(reanalysis_info['Rean_RelViewPeriod_Start'].iloc[0])+1)})
            sub(child1_properties, "string", {"key": "_REL_VIEW_PERIOD_END", "value": str(reanalysis_info['Rean_RelViewPeriod_End'].iloc[0])})
            sub(child1_properties, "string", {"key": "_WARM_STATE_START", "value": str(reanalysis_info['Rean_RelViewPeriod_Start'].iloc[0])})
            sub(child1_properties, "string", {"key": "_WARM_STATE_MODULE_INSTANCE", "value": '{}_update_{}'.format(wflowModel, reanalysisProduct)})
            sub(child1_properties, "string", {"key": "_WFLOW_MODEL", "value": wflowModel})
            sub(child1_properties, "string", {"key": "_WFLOW_MODEL_TEMPORAL_RES", "value": str(reanalysis_info['Wflow_TimeStep'].iloc[0])})
            sub(child1_properties, "string", {"key": "_WFLOW_BUNDLE", "value": str(reanalysis_info['Wflow_BinariesID'].iloc[0])})
            sub(child1_properties, "string", {"key": "_EXPIRY_TIME", "value": str(reanalysis_info['ExpiryTime'].iloc[0])})
            
            #Addition of element "Activity" (1) (Preprocess of reanalysis data)
            child2_activity = sub(root,"activity") 
            
            subText(child2_activity,"runIndependent","true")
            
            #Definition of module instance name for preprocess of reanalysis data to run the model
            moduleInstancePreprocess_Rean = 'preprocess_{}_update_{}'.format(wflowModel,reanalysisProduct)
            
            #Comparison of time steps of models and reanalysis product to select the template used for preprocess
            if reanalysis_info['Wflow_TimeStep'].iloc[0] == reanalysis_info['DataProduct_Rean_TimeStep'].iloc[0]: 
                FileName_Preprocess = "spatial_processing_observation"
            else: 
                FileName_Preprocess = "temporal_spatial_processing_observation"
            
            #Addition of children to "Activity" (1) element 
            subText(child2_activity,"moduleInstanceId", moduleInstancePreprocess_Rean)
            subText(child2_activity,"moduleConfigFileName", FileName_Preprocess)
            
            #Addition of element "Activity" (2) (Execution of wflow model using reanalysis data in update mode)
            child3_activity = sub(root,"activity") #activity 2
            
            subText(child3_activity,"runIndependent","true")
            
            #Definition of module instance name for model execution using reanalysis data 
            moduleInstanceGA_Rean = '{}_update_{}'.format(wflowModel, reanalysisProduct)
            
            #Addition of children to "Activity" (2) element 
            subText(child3_activity,"moduleInstanceId", moduleInstanceGA_Rean)
            subText(child3_activity,"moduleConfigFileName", "wflow_"+ reanalysis_info['Wflow_ModelTypeID'].iloc[0] + "_update_template")

            #Addition of additional element "Activity" (3) to execute routing of global wflow model (w3ra)
            if reanalysis_info['Wflow_ModelTypeID'].iloc[0] == "w3ra": 
                
                #Creation of element "Activity" (3)
                child4_activity = sub(root,"activity") 
                
                subText(child4_activity,"runIndependent","true")
                
                 #Definition of module instance name for global model routing
                moduleInstanceGA_Rean_Rout = '{}_update_{}_{}'.format(wflowModel, reanalysisProduct,"routing")
                
                #Addition of children to "Activity" (3) element 
                subText(child4_activity,"moduleInstanceId", moduleInstanceGA_Rean_Rout)
                subText(child4_activity,"moduleConfigFileName", "wflow_routing_update_template")
                
                #Addition of children to modelInstanceDescriptors XML for wflow global model routing
                sub(rootModuleInstance, "moduleInstanceDescriptor", {"id": moduleInstanceGA_Rean_Rout}) 
            
            #Addition of all module instances defined previously as children to modelInstanceDescriptors XML 
            sub(rootModuleInstance, "moduleInstanceDescriptor", {"id": moduleInstancePreprocess_Rean}) #Addition of module instance descriptor for reanalysis
            sub(rootModuleInstance, "moduleInstanceDescriptor", {"id": moduleInstanceGA_Rean}) 
            sub(rootWorkflow, "workflowDescriptor", {"id": moduleInstanceGA_Rean, "name": "run "+ moduleInstanceGA_Rean,"visible":"true","forecast":"true","autoApprove": "true"}) #Addition of workflow descriptor for reanalysis
            
            #Creation of Workflow file XML used for model execution in update mode (reanalysis) indentation and file export
            XMLF.indent(root)
            
            fileName = moduleInstanceGA_Rean + '.xml'
            pathSave= os.path.join(pathFEWS,'Config/WorkflowFiles/wflow/')
            fewshelp.makedir_ifnotexist(pathSave)
            
            XMLF.serialize_xml(root,pathSave,fileName)
        
        
    ###################################################################################################################
        #Creation of Workflows for Execution of Models in Update Mode (Online reanalysis) and Forecast Mode using NWP
    ###################################################################################################################
    
    
    for index, row in import_info.iterrows():
        
        #Creation of root of workflows XMLs
        root = XMLF.create_xml_root("workflow")
        
        #Creation of element "properties"
        child1_properties = sub(root,"properties")
        
        #Addition of children to "properties" element for the model execution using online reanalysis for update
        if row['WorkflowTypeID'] == "update":
            
            moduleInstanceImport_ID = 'create_reanalysis_{}_{}'.format(row['DataProduct_Obs_Provider'],row['DataProductID_Observation'])
            sub(child1_properties, "string", {"key": "_DATA_PROD_MODULE_INSTANCE", "value": moduleInstanceImport_ID})
            sub(child1_properties, "string", {"key": "_DATA_PROD", "value": row['DataProductID_Observation']})
            sub(child1_properties, "string", {"key": "_DATA_PROD_TEMPORAL_RES", "value": str(row['DataProduct_Obs_TimeStep'])})
            sub(child1_properties, "string", {"key": "_REL_VIEW_PERIOD_START", "value": str(row['Rean_RelViewPeriod_End'])})
            sub(child1_properties, "string", {"key": "_REL_VIEW_PERIOD_END", "value": str(0)})
            sub(child1_properties, "string", {"key": "_WARM_STATE_START", "value": str(int(row['Rean_RelViewPeriod_Start'])+2)})
            sub(child1_properties, "string", {"key": "_WARM_STATE_MODULE_INSTANCE", "value": '{}_update_{}'.format(row['Wflow_ModelID'], row['DataProductID_Reanalysis'])})
            
            #Comparison of time steps of models and reanalysis product to select the template used for preprocess
            if row['Wflow_TimeStep'] == row['DataProduct_Obs_TimeStep']: 
                moduleConfigFileName_Preprocess = "spatial_processing_observation"
            else: 
                moduleConfigFileName_Preprocess = "temporal_spatial_processing_observation"
            
            #Definition of name of template of general adapter for model run (update)
            moduleConfigFileName_GA = "wflow_" + row['Wflow_ModelTypeID'] + "_update_template"
        
        #Addition of children to "properties" element for the model execution using NWP for forecast
        else: 
            
            moduleInstanceImport_ID = 'import_nwp_{}_{}'.format(row['DataProduct_Frcst_Provider'],row['DataProductID_Forecast'])
            sub(child1_properties, "string", {"key": "_FCST_PROD_MODULE_INSTANCE", "value": moduleInstanceImport_ID})
            sub(child1_properties, "string", {"key": "_FCST_PROD", "value": row['DataProductID_Forecast']})
            sub(child1_properties, "string", {"key": "_OBS_PROD", "value": row['DataProductID_Observation']})
            sub(child1_properties, "string", {"key": "_PROVIDER", "value": row['DataProduct_Frcst_Provider']})
            sub(child1_properties, "string", {"key": "_FCST_PROD_TEMPORAL_RES", "value": str(row['DataProduct_Frcst_TimeStep'])})
            sub(child1_properties, "string", {"key": "_ENSEMBLE", "value": row['DataProductID_Forecast']})
            sub(child1_properties, "string", {"key": "_WARM_STATE_MODULE_INSTANCE", "value": '{}_update_{}'.format(row['Wflow_ModelID'], row['DataProductID_Observation'])})
            
            #Comparison of time steps of models and reanalysis product to select the template used for preprocess
            if row['Wflow_TimeStep'] == row['DataProduct_Frcst_TimeStep']: 
                moduleConfigFileName_Preprocess = "spatial_processing_nwp_forecast"
            else: 
                moduleConfigFileName_Preprocess = "temporal_spatial_processing_nwp_forecast"
            
            #Definition of name of template of general adapter for model run (forecast)
            moduleConfigFileName_GA = "wflow_" + row['Wflow_ModelTypeID'] + "_forecast_template"
            
        #Additional children of "properties" element that are shared by update and forecast mode with NWP    
        sub(child1_properties, "string", {"key": "_WFLOW_MODEL", "value": str(row['Wflow_ModelID'])})
        sub(child1_properties, "string", {"key": "_WFLOW_MODEL_TEMPORAL_RES", "value": str(row['Wflow_TimeStep'])})
        sub(child1_properties, "string", {"key": "_WFLOW_BUNDLE", "value": str(row['Wflow_BinariesID'])})
        sub(child1_properties, "string", {"key": "_EXPIRY_TIME", "value": str(row['ExpiryTime'])})
        
        #Definition of module instance name for preprocess of NWP for model run 
        moduleInstancePreprocess_NWP = 'preprocess_{}'.format(row['Wflow_WorkflowName'])
        
        #Addition of "Activity" (1) element for preprocess of NWP data
        child3_activity = sub(root,"activity") 
        
        #Addition of children to "Activity" (1) element 
        subText(child3_activity,"runIndependent","true")
        subText(child3_activity,"moduleInstanceId", moduleInstancePreprocess_NWP)
        subText(child3_activity,"moduleConfigFileName", moduleConfigFileName_Preprocess)
        
        #Addition of element "Activity" (2) (creation of forecast scenario)
        if row['WorkflowTypeID'] == "forecast":       
            child2_activity = sub(root,"activity") 
            
            #Addition of children to "Activity" (2) element 
            subText(child2_activity,"runIndependent","true")
            subText(child2_activity,"moduleInstanceId", row['Wflow_WorkflowName'])
            subText(child2_activity,"moduleConfigFileName", "create_forecast_scenario_wflow")
        
        #Addition of element "Activity" (3) (model execution in forecast mode)
        child4_activity = sub(root,"activity") #activity 3 
        
        #Addition of children to "Activity" (3) element
        subText(child4_activity,"runIndependent","true")
        subText(child4_activity,"moduleInstanceId", row['Wflow_WorkflowName'])
        subText(child4_activity,"moduleConfigFileName", moduleConfigFileName_GA)
        
        #Addition of extra children "ensemble" to Activity (3): To treat all NWP as ensemble
        if row['WorkflowTypeID'] == "forecast":
            child4_1 = sub(child4_activity, "ensemble") 
            
            subText(child4_1,"ensembleId",row['DataProductID_Forecast'])
            subText(child4_1,"runInLoop", "true")
        
        #Addition of additional element "Activity" (4) to execute routing of global wflow model (w3ra)    
        if row['Wflow_ModelTypeID'] == "w3ra": #additional activity for routing
            child5_activity = sub(root,"activity") 
            
            #Addition of children to "Activity" (4) element
            subText(child5_activity,"runIndependent","true")
            subText(child5_activity,"moduleInstanceId", row['Wflow_WorkflowName'])
            subText(child5_activity,"moduleConfigFileName", "wflow_routing_" + row['WorkflowTypeID'] + "_template")
            
            #Addition of extra children "ensemble" to Activity (4)
            if row['WorkflowTypeID'] == "forecast":
                child5_1 = sub(child5_activity, "ensemble") #treating all nwp as ensemble
                
                #Addition of extra children to "Activity" (4) element
                subText(child5_1,"ensembleId",row['DataProductID_Forecast'])
                subText(child5_1,"runInLoop", "true")
            
            #Addition of module instance defined for routing to modelInstanceDescriptors XML
            sub(rootModuleInstance, "moduleInstanceDescriptor", {"id": row['Wflow_WorkflowName'] + "_routing"}) #Addition of module instance descriptor for reanalysis - wflow models for routing

        #Creation of Workflow file XML used for model execution in forecast mode indentation and file export
        XMLF.indent(root)
        
        fileName = row['Wflow_WorkflowName'] + '.xml'
        pathSave= os.path.join(pathFEWS,'Config/WorkflowFiles/wflow/')
        fewshelp.makedir_ifnotexist(pathSave)
        
        XMLF.serialize_xml(root,pathSave,fileName)
        
        ##############################################################################################
                    #Creation of Module Instance Descriptors XML File for wflow model execution
        ##############################################################################################
        
        #Addition of module instances not incorporated previously      
        sub(rootModuleInstance, "moduleInstanceDescriptor", {"id": moduleInstancePreprocess_NWP})
        sub(rootModuleInstance, "moduleInstanceDescriptor", {"id": row['Wflow_WorkflowName']})
        
        #ModuleInstanceDescriptors XML file for wflow model execution
        XMLF.indent(rootModuleInstance)
        
        pathSave = os.path.join(pathFEWS,'Config/RegionConfigFiles/wflow/')
        fewshelp.makedir_ifnotexist(pathSave)
        
        XMLF.serialize_xml(rootModuleInstance,pathSave,'ModuleInstanceDescriptors_wflow.xml')
        
        #############################################################################
                    #Workflow Descriptors XML File for wflow model execution
        #############################################################################
        
        sub(rootWorkflow, "workflowDescriptor", {"id": row['Wflow_WorkflowName'],"name": "run "+ row['Wflow_WorkflowName'],"visible":"true","forecast":"true","autoApprove": "true"})
        
        #WorkflowDescriptors XML file for wflow model execution
        XMLF.indent(rootWorkflow)
        
        pathSave = os.path.join(pathFEWS,'Config/RegionConfigFiles/wflow/')
        fewshelp.makedir_ifnotexist(pathSave)
        
        XMLF.serialize_xml(rootWorkflow,pathSave,'WorkflowDescriptors_wflow.xml')

