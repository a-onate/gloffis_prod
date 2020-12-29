"""
This module contains a function to write XML files related to the import of 
data products for four Delft-FEWS directories: ModuleConfigFiles, IdMapFiles, 
RegionConfigFiles and WorkflowFiles

"""
#Load modules
import xml.etree.cElementTree as ET
import xmlfunct.xmlfunct as XMLF
import xmlfunct.fewshelpers as fewshelp
import os
import re

def ImportModule(pathDB,pathFEWS):
    """
    Arguments: 
        
        pathDB: [String] Path to the external database holding the information on the 
        characteristics of the system.
        pathFEWS: [String] Path to the Config Folder of scripted FEWS.
    
    Returns: 
        Tree with the XML documents, indented and exported as XML files for: 
            
            -Import module (ModuleConfigFiles)
            -ID of imported variables (IdMapFiles)
            -Worflow file for import (WorkflowFiles)
            -Workflow descriptors for import (RegionConfigFiles)
            -Module descriptors for import (RegionConfigFiles)
    """
    
    sub = ET.SubElement
    subText = XMLF.add_child_with_text

    #Read tables from Microsoft Access database
    import_info = XMLF.readDataBase("tbl_Scripting_DataProducts_IMPORT_Info",pathDB)
    
    ##############################################################
                #Creation of Import Module XML file
    ##############################################################

    info_per_product_groups = import_info.groupby('DataProduct_ID') #Grouping of data products by name 
    
    for product_group in info_per_product_groups:
        dataProduct = product_group[0]
        info_per_filetype_groups = product_group[1].groupby('FileType') #Grouping of data products by file type (e.g., GRIB2)
        
        for filetype_group in info_per_filetype_groups:
            import_filetype = filetype_group[0]
            parameter_info = filetype_group[1]
            
            #Creation of root of the Import Modules XML files for each data product
            root = XMLF.create_xml_root("timeSeriesImportRun",{'version':False})
            
            #Creation of the child elements of the Import Modules XML
            
            #General child elements 
            child1_import = sub(root,"import")
            child1_1_general = sub(child1_import,"general",{})
            subText(child1_1_general,"importType",import_filetype)
            subText(child1_1_general,"folder",r"$IMPORT_FOLDER$/{}/".format(dataProduct))
            
            if import_filetype == "GRIB2": 
                subText(child1_1_general,"fileNameParameterIdPattern",r".*_\d{3}_(.*).grib2*")
            
            subText(child1_1_general,"deleteImportedFiles","true")
            
            if re.match("icon", dataProduct): #All Icon products use the same IdMapFile as the names of variables are consistent within the data family
                subText(child1_1_general,"idMapId",'{}_{}_{}_{}'.format("IdImport", parameter_info['DataProduct_Type'].iloc[0], parameter_info['ProviderID'].iloc[0], "icon"))
            
            else: 
                subText(child1_1_general,"idMapId",'{}_{}_{}_{}'.format("IdImport", parameter_info['DataProduct_Type'].iloc[0], parameter_info['ProviderID'].iloc[0], dataProduct))
            
            subText(child1_1_general,"unitConversionsId","ImportUnitConversions")
            child1_1_1 = sub(child1_1_general,"importTimeZone",{})
            subText(child1_1_1,"timeZoneOffset","+00:00")
            subText(child1_1_general,"dataFeedId",dataProduct)
            subText(child1_1_general,"actionLogEventTypeId",'{}_{}_{}_{}{}'.format("import", parameter_info['DataProduct_Type'].iloc[0], parameter_info['ProviderID'].iloc[0], dataProduct,'.New'))
            
            #Timeseriesets child elements for each variable imported
            for row in parameter_info.itertuples():
                
                child_timeseriesset = sub(child1_import,"timeSeriesSet",{})
                subText(child_timeseriesset,"moduleInstanceId",'{}_{}_{}_{}'.format("import",row.DataProduct_Type,row.ProviderID,dataProduct))
                subText(child_timeseriesset,"valueType","grid")
                subText(child_timeseriesset,"parameterId",row.FEWS_VariablesID)
                subText(child_timeseriesset,"locationId",dataProduct)
                subText(child_timeseriesset,"timeSeriesType",row.Import_DataType)
                sub(child_timeseriesset,"timeStep",{"unit":"hour","multiplier":"{}".format(row.TimeStep)})
                subText(child_timeseriesset,"readWriteMode","add originals")
                sub(child_timeseriesset,"expiryTime",{"unit":"hour","multiplier":"{}".format(row.ExpiryTime)})
                
                if row.DataProduct_Type == "nwp": #All NWP are treated as if they were ensembles. If the product is deterministic, the ensemble is 1. 
                    subText(child_timeseriesset,"ensembleId", dataProduct)
                        
            #externUnit child elements for variables that are cumulative or need interpolation
            for row in parameter_info.itertuples(): 
                if row.CumulativeType == 'cumulativeSum':
                    sub(child1_import,"externUnit",dict(parameterId=row.FEWS_VariablesID), unit=row.DataProduct_VariableUnit, cumulativeSum='true')
                elif row.CumulativeType == 'cumulativeMean':
                    sub(child1_import,"externUnit",dict(parameterId=row.FEWS_VariablesID), unit=row.DataProduct_VariableUnit, cumulativeMean='true')
                else:
                    sub(child1_import,"externUnit",dict(parameterId=row.FEWS_VariablesID), unit=row.DataProduct_VariableUnit)
            
            if re.match("icon", dataProduct): #Icon products' variables are interpolated
                for row in parameter_info.itertuples():
                    sub(child1_import,"interpolateSerie",dict(parameterId=row.FEWS_VariablesID), interpolate='true')
            
            # import XML indentation and file export
            XMLF.indent(root)
                
            fileName = '{}_{}_{}_{}{}'.format("import",row.DataProduct_Type,parameter_info['ProviderID'].iloc[0],dataProduct,".xml")
            
            #Definition of path where the XML will be saved
            pathSave = os.path.join(pathFEWS,'Config/ModuleConfigFiles/imports/')
            fewshelp.makedir_ifnotexist(pathSave)
            
            #Import Module XML indentation and file export
            XMLF.serialize_xml(root,pathSave,fileName)
            
    ####################################################################################
    #Creation of IdMapFiles XML files for all imported parameters for each data product
    ####################################################################################
  
        #Creation of root of IdMapFile XML
        root = XMLF.create_xml_root("idMap",{'version':'1.1'})
        
        parameter_groups = product_group[1].groupby('DataProduct_VariableName') #Grouping of data products' variables by its external name 
        
        #Child elements of XML file
        for parameter_group in parameter_groups:
            parameter_name = parameter_group[0]
            parameter_fews_name = parameter_group[1]['FEWS_VariablesID'].iloc[0]
            
            sub(root,'parameter',dict(external=parameter_name,internal=parameter_fews_name))
            
            #IdMapFiles XML indentation
            XMLF.indent(root)
            pathSave= os.path.join(pathFEWS,'Config/IdMapFiles')#path where the file will be saved
            
            #Definition of XML file name for IdMapFiles
            if re.match("icon", dataProduct): #For all Icon products there is only one IdMapFile created as the names of variables are consistent within the data family
                idMapName = '{}_{}_{}_{}'.format("IdImport", parameter_info['DataProduct_Type'].iloc[0], parameter_info['ProviderID'].iloc[0], "icon") #All ICON family uses the same IDMapFile
                sub(root,'parameter',dict(external=parameter_name.lower(),internal=parameter_fews_name))
            else: 
                idMapName = '{}_{}_{}_{}'.format("IdImport", parameter_info['DataProduct_Type'].iloc[0], parameter_info['ProviderID'].iloc[0], dataProduct)#For the other products
                
            #IdMapFiles XML export    
            XMLF.serialize_xml(root,pathSave,'{}{}'.format(idMapName, ".xml"))
 
    #############################################################################################
    #Creation of Import Workflows XML files for each data product and thus each module instance
    #############################################################################################
    
    for product_group in info_per_product_groups:
        dataProduct = product_group[0]
        productInfo = product_group[1]
        moduleInstanceName = '{}_{}_{}_{}'.format("import",productInfo['DataProduct_Type'].iloc[0],productInfo['ProviderID'].iloc[0],dataProduct)
        
        #Creation of root of Workflow File
        root = XMLF.create_xml_root("workflow")
        
        #Child elements of XML
        child1_activity = sub(root,"activity")
        subText(child1_activity,"runIndependent","true")
        subText(child1_activity,"moduleInstanceId",moduleInstanceName)
        subText(child1_activity,"moduleConfigFileName",moduleInstanceName)

        #Workflow XML indentation 
        XMLF.indent(root)
        
        #Definition of XML name for export
        fileName = '{}_{}_{}_{}{}'.format('import',productInfo['DataProduct_Type'].iloc[0],productInfo['ProviderID'].iloc[0], dataProduct,".xml")
        
        #Definition of path where the file will be saved
        pathSave= os.path.join(pathFEWS,'Config/WorkflowFiles/import/')
        fewshelp.makedir_ifnotexist(pathSave)
        
        #Workflow files XML export
        XMLF.serialize_xml(root,pathSave,fileName)
        
    ##############################################################
     #Creation of Workflow descriptors XML for each workflow file
    ##############################################################       
    
    #Creation of root of Workflow Descriptors File
    root = XMLF.create_xml_root("workflowDescriptors")
    
    for product_group in info_per_product_groups:
        
        dataProduct = product_group[0]
        product_info = product_group[1]
        
        #Child elements of XML
        sub(root,"workflowDescriptor",dict(id='{}_{}_{}_{}'.format('import',product_info['DataProduct_Type'].iloc[0],product_info['ProviderID'].iloc[0], dataProduct),name='import '+ dataProduct,visible='true'))
        
        #Workflow descriptors XML indentation and file export
        XMLF.indent(root)
        pathSave = os.path.join(pathFEWS,'Config/RegionConfigFiles')#path where the file will be saved
        XMLF.serialize_xml(root,pathSave,'WorkflowDescriptors_import.xml')
    
        
    ##########################################################################################################
    #Creation of XML containing Module Instance Descriptors for each moduleconfig file (nwp product imported)
    ##########################################################################################################
    
    #Creation of root of Module Instance Descriptors File
    root = XMLF.create_xml_root("moduleInstanceDescriptors")
    
    #Child element of XML
    sub(root,"moduleInstanceDescriptor",dict(id='import_nwp'))
    
    for product_group in info_per_product_groups:
        product_info = product_group[1]       
        
        #Definition of name for instance descriptor
        instanceDescriptor = '{}_{}_{}_{}'.format('import',product_info['DataProduct_Type'].iloc[0],product_info['ProviderID'].iloc[0],product_group[0])
        
        #Child elements of XML
        sub(root,"moduleInstanceDescriptor",dict(id= instanceDescriptor))
        
        #Module Instance Descriptors XML indentation and file export
        XMLF.indent(root)
        pathSave = os.path.join(pathFEWS,'Config/RegionConfigFiles') #path where the file will be saved
        XMLF.serialize_xml(root,pathSave,'ModuleInstanceDescriptors_import.xml')

              