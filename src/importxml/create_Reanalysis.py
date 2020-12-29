"""
This module contains a function to write workflow XML files related to the creation
of the online reanalysis using NWP data as well as to append the workflow descriptors 
and module instance descriptors of the created reanalysis to their respective XML files 
previously created for the import.

"""
#Load modules
import xml.etree.cElementTree as ET
import xmlfunct.xmlfunct as XMLF
import xmlfunct.fewshelpers as fewshelp
import os


def CreateReanalysis(pathDB,pathFEWS):
    """
    Arguments: 
        
        pathDB: [String] Path to the external database holding the information on the 
        characteristics of the system.
        pathFEWS: [String] Path to the Config Folder of scripted FEWS.
    
    Returns: 
        Tree with the XML documents, indented and exported as XML files for: 
            
            -Worflow file for the creation of online reanalysis (WorkflowFiles)
            -Workflow descriptors for postprocess of import (RegionConfigFiles)
            -Module descriptors for postprocess of import (RegionConfigFiles)
    """

    sub = ET.SubElement
    subText = XMLF.add_child_with_text
    
    #open database
    import_info = XMLF.readDataBase("qry_Wflow_Workflows",pathDB)
    
    ################################################################################
        #Creation of Workflow files for creation of Online Reanalysis using NWP data
    ################################################################################
        
    info_per_product_groups = import_info.groupby('DataProductID_Observation') #Selection of NWP products destined to create the online reanalysis
    for product_group in info_per_product_groups:
        dataProduct = product_group[0]
        workflowInfo = product_group[1]
        
        #Creation of root of the Creation of Reanalysis XML files for each data product assigned for this task
        root = XMLF.create_xml_root("workflow")
        
        #Creation of the child elements of the XML for Creation of Reanalysis - "Properties"
        child1_properties = sub(root,"properties")
        
        sub(child1_properties, "string", {"key": "_NWP_PROD", "value": dataProduct})
        sub(child1_properties, "string", {"key": "_PROVIDER", "value": str(workflowInfo['DataProduct_Obs_Provider'].iloc[0])})
        sub(child1_properties, "string", {"key": "_NWP_TEMPORAL_RES", "value": str(workflowInfo['DataProduct_Obs_TimeStep'].iloc[0])})
        sub(child1_properties, "string", {"key": "_EXPIRY_TIME", "value": str(workflowInfo['ExpiryTime'].iloc[0])})
        
        
        #Creation of the child elements of the XML for Creation of Reanalysis - "Activity"
        instanceID = 'create_reanalysis_{}_{}'.format(workflowInfo['DataProduct_Obs_Provider'].iloc[0],dataProduct)#Name of module instance for creation of reanalysis
        
        child2_activity = sub(root,"activity") 
        subText(child2_activity,"runIndependent","true")                 
        subText(child2_activity,"moduleInstanceId", instanceID)
        subText(child2_activity,"moduleConfigFileName", "create_reanalysis_template")
    
        #Creation of online reanalysis workflow XML indentation and file export
        XMLF.indent(root)
        
        fileName = instanceID + '.xml' #Name of file to be exported
        pathSave= os.path.join(pathFEWS,'Config/WorkflowFiles/import_postprocessing/')#path where the file will be saved
        fewshelp.makedir_ifnotexist(pathSave)
        
        XMLF.serialize_xml(root,pathSave,fileName)
        
        ###########################################################################################################
        #Append of module instance descriptors related to the creation of reanalysis to the correspondent XML file
        ###########################################################################################################
            
        #Retrival of Module Instance Descriptors XML file's root created with create_MCF_Import.py
        moduleInstanceFile= os.path.join(pathFEWS,'Config/RegionConfigFiles/ModuleInstanceDescriptors_import.xml')
        tree = ET.parse(moduleInstanceFile) #Parsing of module instance descriptors file
        root = tree.getroot()

        #Append of module instance descriptors related to the creation of reanalysis
        sub(root,"moduleInstanceDescriptor",{"id": instanceID})
        
        #Modified Module Instance Descriptors XML indentation and file export
        XMLF.indent(root)
        pathSave = os.path.join(pathFEWS,'Config/RegionConfigFiles') #path where the file will be saved
        XMLF.serialize_xml(root,pathSave,'ModuleInstanceDescriptors_import.xml')
        
        ###########################################################################################################
        #Append of workflow descriptors related to the creation of reanalysis to the correspondent XML file
        ###########################################################################################################        
            
        #Retrival of Module Instance Descriptors XML file's root created with create_MCF_Import.py    
        WorkflowFile= os.path.join(pathFEWS,'Config/RegionConfigFiles/WorkflowDescriptors_import.xml')
        tree = ET.parse(WorkflowFile) #Parsing of module instance descriptors file
        root = tree.getroot()
        
        #Append of workflow descriptors related to the creation of reanalysis
        sub(root,"workflowDescriptor",{"id": instanceID, "name":'create reanalysis '+ dataProduct,"visible": 'true'})
        
        #Modified Module Instance Descriptors XML indentation and file export
        XMLF.indent(root)
        pathSave = os.path.join(pathFEWS,'Config/RegionConfigFiles') #path where the file will be saved
        XMLF.serialize_xml(root,pathSave,'WorkflowDescriptors_import.xml')
