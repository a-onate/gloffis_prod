"""
This module contains a function to write a XML file and a csv file used to
describe the grids of the data products imported to the system 

"""
#Load modules
import xmlfunct.xmlfunct as XMLF
import xmlfunct.fewshelpers as fewshelp
import shutil


def ModuleData_ColdStates(pathDB,pathFEWS,pathFiles):
    """
    Arguments: 
        
        pathDB: [String] Path to the external database holding the information on the 
        characteristics of the system.
        pathFEWS: [String] Path to the Config Folder of scripted FEWS.
        pathFiles: [String] Location of files needed for cold states and module datasets definition
    
    Returns: 
        -Zips containing ColdStateFiles of wflow models (initial conditions)
        -Zips containing ModuleDataSets (external wflow models to be run in the system)
    
    """

    #Read tables from Microsoft Access database
    import_info = XMLF.readDataBase("qry_Wflow_Workflows",pathDB)
    
    #Retrival of all wflow model names incorporated in the system
    info_per_model_groups = import_info.groupby('Wflow_ModelID') #grouping of wflow model names regardless of the scenario they are executed for
    for model_group in info_per_model_groups:
        wflowModel = model_group[0]
        
        
        ##############################################################
                    #Zipping of Module Data Set Files
        ##############################################################
        
        pathZip = '{}{}'.format(pathFEWS,'/Config/ModuleDataSetFiles/wflow/') #path where the file will be saved
        pathModuleDataFiles = '{}/{}{}'.format(pathFiles,wflowModel,'/ModuleDataSetFiles/') #path where the external wflow model is located
        fewshelp.makedir_ifnotexist(pathZip)
        
        zipName = '{}{}'.format(pathZip,wflowModel) #Name of Zip
        
        ModuleDataSet_zip = shutil.make_archive(zipName, "zip", pathModuleDataFiles)
        
        
        ##############################################################
                #Cold State Files Zipping For Reanalysis 
        ##############################################################
        
        info_per_reanalysis_groups = model_group[1].groupby('DataProductID_Reanalysis') #for each wflow model, grouping of reanalysis data products used for update 
        for reanalysis_group in info_per_reanalysis_groups:
            reanalysisProduct = reanalysis_group[0]
            reanalysis_info = reanalysis_group[1]
            
            pathZip = '{}{}'.format(pathFEWS,'/Config/ColdStateFiles/') #path to ColdStateFiles folder
            pathColdFiles = '{}/{}{}'.format(pathFiles,reanalysis_info["Wflow_ModelID"].iloc[0],'/ColdStateFiles/') #path where the file will be saved
            fewshelp.makedir_ifnotexist(pathZip)
            zipName = '{}{}_update_{}'.format(pathZip,reanalysis_info["Wflow_ModelID"].iloc[0],reanalysisProduct)  #Name of Zip
            
            ColdFiles_zip = shutil.make_archive(zipName + " Default", "zip", pathColdFiles)
            
            #When using the global model w3ra (a routing model is also needed and thus the ColdStateFiles for this model)
            if reanalysis_info['Wflow_ModelTypeID'].iloc[0] == "w3ra":
                routingModelName = '{}{}_{}'.format(pathZip,wflowModel,"routing")
                shutil.make_archive(routingModelName, "zip", pathColdFiles)
                shutil.move(routingModelName + ".zip", zipName + "_routing Default.zip")
                                    

    ##############################################################
            #Cold State Files Zipping For NWP
    ##############################################################
    
    for index, row in import_info.iterrows(): 
        
        pathZip = '{}{}'.format(pathFEWS,'/Config/ColdStateFiles/') #path to ColdStateFiles folder
        pathColdFiles = '{}/{}{}'.format(pathFiles,row["Wflow_ModelID"],'/ColdStateFiles/') #path where the file will be saved
        fewshelp.makedir_ifnotexist(pathZip)
        zipName = '{}{}'.format(pathZip,row["Wflow_WorkflowName"]) #Name of Zip
        
        ColdFiles_zip = shutil.make_archive(zipName + " Default", "zip", pathColdFiles)
        
        #When using the global model w3ra (a routing model is also needed and thus the ColdStateFiles for this model)
        if row['Wflow_ModelTypeID'] == "w3ra":
                routingModelName = '{}{}_{}'.format(pathZip,wflowModel,"routing")
                shutil.make_archive(routingModelName, "zip", pathColdFiles)
                shutil.move(routingModelName + ".zip", zipName + "_routing Default.zip")
