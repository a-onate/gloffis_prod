# -----------------------------------------------------------
# 
# Complementary functions to support the XML files creation
# 
# -----------------------------------------------------------

import pandas as pd
import xml.etree.cElementTree as ET
import os
import pyodbc

#Elements used for schema declaration in root in XML files 
_ns = {'xmlns': 'http://www.wldelft.nl/fews',
       'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
_schema_url = 'http://fews.wldelft.nl/schemas/version1.0/'

#Helper function to create xml root
def create_xml_root(schema_name, extra_attributes = {}):
    """ This function will return the root of the XML file to be created
    -Arguments: 
            schema_name: Name to be given to the root. String.
            extra_attributes: any additional attributes for the root, aside from the 
            elements used for schema declaration. When extra_attributes = {'version':False}
            the root does include information about the version. Dictionary.
            
    -Returns: Root of the XML file. XML Element. """
    
    attributes = {'xmlns': _ns['xmlns'],
            'xmlns:xsi': _ns['xmlns:xsi'],
                  'xsi:schemaLocation': '{} {}{}.xsd'.format(
                      _ns['xmlns'], _schema_url, schema_name),
                  'version':'1.0'}
    attributes.update(extra_attributes)
    if attributes['version'] is False:
        attributes.pop('version')

    ET.register_namespace('', attributes['xmlns'])
    ET.register_namespace('xsi', attributes['xmlns:xsi'])
    root = ET.Element('{{{}}}{}'.format(attributes.pop('xmlns'), schema_name), attributes)
    return root

#Implement the actual tabulation to the xml files
def indent(elem, level=0): 
    """ This function will arrage all lines of the generated XML text 
    into the correct tabulation 
    -Arguments: 
        elem: Root of the XML file. XML element """    
    
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
            
#save the xml files in the needed directory
def serialize_xml(root, directory, file_name): 
    """ This function exports the generated XML file 
    -Arguments: 
        root: Root of the XML file. XML element.
        directory: Location where the file will be saved. String.
        file_name: Name of the XML file. String.""" 
    
    indent(root)
    ET.ElementTree(root).write(os.path.join(directory, file_name),
                               encoding = 'UTF-8', xml_declaration = True, method='xml')

#Create a xml child element with text     
def add_child_with_text(parent, child, text):
    """ This function creates an XML child with only text and no attributes 
    -Arguments: 
        parent: Parent of the element to be created. XML element.
        child: Name of the element to be created. String.
        text: Text of the element. String.""" 
    child = ET.SubElement(parent, child)
    child.text = text

#Find a parameter associated to a certain ID in a different table/dataframe
def IdDfFinder (ID, df, colID, colInterest):
    """ This function returns a parameter associated to an ID in a dataframe
    -Arguments: 
        ID: id of parameter 1 e.g. wflow_model_ID = 3. Integer or string. 
        df: dataframe where ID will be searched e.g. "wflow_models". Dataframe.
        colID: column in dataframe where the ID is specified e.g. "wflow_models_ID". String.
        colInterest: Column where parameter 2 (the one to be returned) is e.g. temporal_resolution. String.
    -Return: Parameter of interest associated to the ID. Integer or string.""" 
    
    indexDF = df[df[colID]==ID].index[0]
    parameter = df.loc[indexDF,colInterest] 
    return parameter

#Read the Microsoft Access Database
def readDataBase (table, databasePath):
    """ This function returns a dataframe with the information associated to the table specified 
    in the arguments. 
    -Arguments: 
        table: Name of the table inside the database that wants to be retrieved. String.
        databasePath: Path where the database is located. String.
    -Return: Dataframe with the information of the table specified""" 
    
    tableSelection = 'select * from ' + table
    dbqPath = '{}{}{}'.format("DBQ=",databasePath,";")
    dbqDriver = '{}{}'.format("Driver={Microsoft Access Driver (*.mdb, *.accdb)};",dbqPath)
    conn = pyodbc.connect(dbqDriver)
    SQL_Query = pd.DataFrame(pd.read_sql_query(tableSelection,conn))
    
    return SQL_Query


#Create an array with all dates in a range considering a timestep delta 
def timeVector (start, end, delta):
    """ This function returns an array containing all dates within a range with a timestep specified. 
    -Arguments: 
        start: starting date of the array. Date and time object.
        end: ending date of the array. Date and time object
        delta: timestep for each array entry. Date object.
    -Return: Array with all dates in the range""" 
    
    timeVect = []
    current = start 
    while current <= end: 
        timeVect.append(current)
        current += delta
    return timeVect