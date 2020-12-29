"""
This module contains a function to write workflow XML files related to the postprocess 
of import of data products as well as to append the workflow descriptors and module 
instance descriptors of the postprocess to their respective XML files previously
created for the import.

"""
#Load modules
import xml.etree.cElementTree as ET
import xmlfunct.xmlfunct as XMLF
import xmlfunct.fewshelpers as fewshelp
import os

def PostprocessImport(pathDB,pathFEWS):
    """
    Arguments: 
        
        pathDB: [String] Path to the external database holding the information on the 
        characteristics of the system.
        pathFEWS: [String] Path to the Config Folder of scripted FEWS.
    
    Returns: 
        Tree with the XML documents, indented and exported as XML files for: 
            
            -Worflow file for postprocess of import (WorkflowFiles)
            -Workflow descriptors for postprocess of import (RegionConfigFiles)
            -Module descriptors for postprocess of import (RegionConfigFiles)
    """
    
    sub = ET.SubElement
    subText = XMLF.add_child_with_text
    
    ##############################################################
        #Creation of Workflow files for postprocess of import
    ##############################################################
    
    #Read tables from Microsoft Access database
    import_info = XMLF.readDataBase("tbl_Scripting_DataProducts_IMPORT_Info",pathDB)
    
    info_per_product_groups = import_info.groupby('DataProduct_ID')#Grouping of data products by name 
    for product_group in info_per_product_groups:
        dataProduct = product_group[0]
        productInfo = product_group[1]
        
        moduleInstanceImport_ID = '{}_{}_{}_{}'.format("import",productInfo['DataProduct_Type'].iloc[0],productInfo['ProviderID'].iloc[0],dataProduct) #Name of module instance for import
        
        #Creation of root of the Postprocess Import XML files for each data product
        root = XMLF.create_xml_root("workflow")
        
        #Creation of the child elements of the XML for Postprocess of Import - "Properties"
        child1_properties = sub(root,"properties")
              
        if productInfo['DataProduct_Type'].iloc[0] == "nwp": #Sort data products depending on its type (e.g., NWP, Reanalysis) 
            
            sub(child1_properties, "string", {"key": "_NWP_MODULE_INSTANCE", "value": moduleInstanceImport_ID})
            sub(child1_properties, "string", {"key": "_NWP", "value": dataProduct})
            sub(child1_properties, "string", {"key": "_NWP_PRODUCT_TEMPORAL_RESOLUTION", "value": str(productInfo['TimeStep'].iloc[0])})
            sub(child1_properties, "string", {"key": "_EXPIRY_TIME", "value": str(productInfo['ExpiryTime'].iloc[0])})
            
            if "ssrd" not in productInfo['FEWS_VariablesID'].tolist(): #Calculate the SSRD if the variable is not directly imported
                
                child1_activity = sub(root,"activity")
                subText(child1_activity,"runIndependent","true")
                subText(child1_activity,"moduleInstanceId","calculate_ssrd")
                subText(child1_activity,"moduleConfigFileName","calculate_ssrd_template_nwp")
        
        elif productInfo['DataProduct_Type'].iloc[0] == "reanalysis": # Child elements in case the data products are a reanalysis
            
            sub(child1_properties, "string", {"key": "_REANALYSIS_MODULE_INSTANCE", "value": moduleInstanceImport_ID})
            sub(child1_properties, "string", {"key": "_REANALYSIS_PROD", "value": dataProduct})
            sub(child1_properties, "string", {"key": "_REANALYSIS_TEMPORAL_RESOLUTION", "value": str(productInfo['TimeStep'].iloc[0])})
            sub(child1_properties, "string", {"key": "_REL_VIEW_PERIOD_START", "value": str(productInfo['RelViewPeriod_Start'].iloc[0])})
            sub(child1_properties, "string", {"key": "_REL_VIEW_PERIOD_END", "value": str(productInfo['RelViewPeriod_End'].iloc[0])})
            sub(child1_properties, "string", {"key": "_EXPIRY_TIME", "value": str(productInfo['ExpiryTime'].iloc[0])})
        
        #Creation of the child elements of the XML for Postprocess of Import - "Activity"
        
        #Specification of module used to calculate PET 
        moduleConfigFileName = '{}_{}'.format("calculate_pet_makkink_template", productInfo['DataProduct_Type'].iloc[0])
        #Specification of name of module instance of postprocess
        moduleInstancePostprocess_ID = 'postprocess_' + moduleInstanceImport_ID
        
        child2_activity = sub(root,"activity") #Append of elements to activity
        subText(child2_activity,"runIndependent","true")
        subText(child2_activity,"moduleInstanceId", "calculate_pet_makkink")
        subText(child2_activity,"moduleConfigFileName", moduleConfigFileName)
        
        
        #Postprocess workflow XML indentation and file export
        XMLF.indent(root)
        
        fileName = moduleInstancePostprocess_ID + '.xml' #Name of file to be exported
        pathSave= os.path.join(pathFEWS,'Config/WorkflowFiles/import_postprocessing/')#path where the file will be saved
        fewshelp.makedir_ifnotexist(pathSave)
        
        XMLF.serialize_xml(root,pathSave,fileName)
    
    ###########################################################################################################
    #Append of module instance descriptors related to the postprocess of import to the correspondent XML file
    ###########################################################################################################
        
        #Retrival of Module Instance Descriptors XML file's root created with create_MCF_Import.py
        moduleInstanceFile= os.path.join(pathFEWS,'Config/RegionConfigFiles/ModuleInstanceDescriptors_import.xml')
        tree = ET.parse(moduleInstanceFile) #Parsing of module instance descriptors file
        root = tree.getroot() 
        
        #Append of module instance descriptors related to postprocess of import
        sub(root,"moduleInstanceDescriptor",{"id": moduleInstancePostprocess_ID}) 
    
        #Modified Module Instance Descriptors XML indentation and file export
        XMLF.indent(root)
        pathSave = os.path.join(pathFEWS,'Config/RegionConfigFiles') #path where the file will be saved
        XMLF.serialize_xml(root,pathSave,'ModuleInstanceDescriptors_import.xml')
        
    ###########################################################################################################
    #Append of workflow descriptors related to the postprocess of import to the correspondent XML file
    ###########################################################################################################
         
        #Retrival of Workflow Descriptors XML file's root created with create_MCF_Import.py
        WorkflowFile= os.path.join(pathFEWS,'Config/RegionConfigFiles/WorkflowDescriptors_import.xml')
        tree = ET.parse(WorkflowFile)#Parsing of workflow descriptors file
        root = tree.getroot()
        
        #Append of workflow descriptors related to postprocess of import
        sub(root,"workflowDescriptor",{"id": moduleInstancePostprocess_ID, "name":'postprocess import '+ dataProduct,"visible": 'true'})
    
        #Modified Workflow Descriptors XML indentation and file export
        XMLF.indent(root)
        pathSave = os.path.join(pathFEWS,'Config/RegionConfigFiles') #path where the file will be saved
        XMLF.serialize_xml(root,pathSave,'WorkflowDescriptors_import.xml')
        




    
            
    
    
                
                
                
            
            
