# ------------------------------------------------------
# 
# Master Script for file batch creation
# 
# ------------------------------------------------------

import xmlfunct.fewshelpers as fewshelp
import workflowxml.create_ModuleDataSets_ColdStateFiles as MDCS
import workflowxml.create_Wflow_Grids as wflowGrids
import workflowxml.create_MapLayerFiles as MLF
import workflowxml.create_SpatialDisplay_Wflow as SDW
import workflowxml.create_TopologyGroup as TG
import workflowxml.create_Workflows as WGA


import importxml.create_Import_Grids as ImpGrids
import importxml.create_MCF_Import as MCFI
import importxml.create_Postprocess_Import as postImp
import importxml.create_Reanalysis as Rean
import importxml.create_SpatialDisplay_Prod as SDD
import importxml.create_Topology_Prod as TopoProd


"""**************Information Entry*****************"""

#Information to read database 
pathDB = r"c:/FEWS_19_02/gloffis_prod/scripts/gloffis/externals/Database_gloffis_prod.accdb" # Path to Database
pathFEWS = r"c:/FEWS_19_02/gloffis_prod/scripts/gloffis/fews_scripted/" #Path to Config Folder of scripted FEWS
pathDefaults = r"c:/FEWS_19_02/gloffis_prod/scripts/gloffis/fews_defaults/" #Path to Config Folder of defaults FEWS
pathFinalConfig = r"c:/FEWS_19_02/gloffis_prod/fews/" #Path to Config Folder with merged scripted and defaults configuration

#Information for generation of ColdStateFiles and ModuleDataSets
pathModuleFiles = r"c:/FEWS_19_02/gloffis_prod/scripts/gloffis/externals/wflow_modules/" #location of files needed for cold states and module datasets

#Information for basic Spatial Display 
pathTemplates = r"c:/FEWS_19_02/gloffis_prod/scripts/gloffis/externals/xml_templates/" #Path of default spatial display xml

#Information to create empty directory structure in fews_scripts directory
directory_list = ['CoefficientSetsFiles',
    'ColdStateFiles',
    'DisplayConfigFiles',
    'IconFiles',
    'IdMapFiles',
    'MapLayerFiles',
    'ModuleConfigFiles',
    'ModuleDataSetFiles',
    'RegionConfigFiles',
    'ReportImageFiles',
    'ReportTemplateFiles',
    'RootConfigFiles',
    'SystemConfigFiles',
    'UnitConversionsFiles',
    'WorkflowFiles',
    '../Macros']
#fewshelp.create_fews_folder_structure(pathFEWS,directory_list)

"""**************Execution of Scripts*****************"""


#%% Run scripts related to Import

#Create module config file for import of data products
MCFI.ImportModule(pathDB,pathFEWS)

#Create workflow for postprocess of import of data products
postImp.PostprocessImport(pathDB,pathFEWS)

#Create Grid XML File for data products
ImpGrids.GridsImport(pathDB,pathFEWS)

#Create Spatial Display XML File for Data Products
SDD.SpatialDisplayProd(pathDB,pathFEWS,pathTemplates)

#Create workflow for online reanalysis creation
Rean.CreateReanalysis(pathDB,pathFEWS)

#Create topology for data products
TopoProd.TopologyProd(pathDB,pathFEWS)

#%% Run scripts for generating configuration xml for wflow model runs

#Create Cold State Files for Update Workflows
MDCS.ModuleData_ColdStates(pathDB, pathFEWS, pathModuleFiles)

#Create Grid XMF File for Wflow models
wflowGrids.WflowGrids(pathDB, pathFEWS)

#Create Map Layer File for Wflow models
MLF.MapLayerFiles(pathDB,pathFEWS)

#Create Spatial Display XML File for Wflow models
SDW.SpatialDisplayWflow(pathDB,pathFEWS)

#Create Topology Group XML File for Wflow models
TG.TopologyGroup(pathDB,pathFEWS)

#Create wflow uptdate and forecast XML Files for Wflow models
WGA.Workflows(pathDB,pathFEWS)

#%% Finalize config: Merge scripted and default FEWS config

fewshelp.mergefews_scripted_default(pathFEWS,pathDefaults, pathFinalConfig)