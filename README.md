# gloffis_prod
 gloffis_prod is an open-source software tool written in python and intended to contribute to the automatization of XML configuration files production for Deltares' Global Hydrological Forecasting System set up. It provides a new approach for configuration of Delft-FEWS based systems, showing its potential related to system maintenance, expansion and replicability.
 
 <p align="center">
<img width="800" height="470" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/readme_ebro_fews.png">
</p>

### Description 

In certain cases when a forecasting system set-up based on Delft-FEWS could be useful and applicable to other study zones, or would likely need to expand the meteorological data sources used and the  hydrological models incorporated (e.g., to consider models with different spatial resolutions), the automatization of Delft-FEWS configuration could be useful, as these tasks would not be as fast forward if a traditional system set-up took place.
To address this prospect, the development of a production system that could replace the manual writing and editing of XML files was carried out, to automatically generate the configuration files. This production system is based on a series of scripts that take the necessary characteristics (according to the specific design adopted) for the system development (e.g., data considered, processing methods, models, etc.) from an external database. In this way, any changes made in the system for either its replication or expansion are directly done in the database, and by running the scripts they are propagated and reflected into the system.

The relational database compiles and organizes into tables with defined relationships the information mainly related to meteorological data products, its variables, and the external hydrological models coupled to the forecasting system. Later, the data is retrieved using multiple queries according to the required information for the scripts to produce the configuration.

Not all configuration files are generated automatically, as some configuration is not likely to change whereas the data products or models in the system are modified. Thus, then the system configuration relies on two groups:
1. The Delft-FEWS defaults, which is the basic configuration system, that do not directly depend on the information entered in the relational database (such as the processing module templates, internal parameters, unit conversion files, among others), and
2. The Delft-FEWS scripted files, which are fully dependant on the data held by the relational database and deeply inter-related to one another.

<p align="center">
<img width="500" height="250" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/readme_system_composition.png">
</p>

A more detailed description of the scripts composing the toolkit and the files generated by each of them can be found in the table below: 

<p align="center">
<img width="800" height="1200" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/readme_scripts-description.png">
</p>

### Installation 

Before starting, the proposed directory structure shown in the following figure could be followed: 

<p align="center">
<img width="180" height="160" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/readme_folder_structure.png">
</p>


To run the scripts, [Anaconda](https://www.anaconda.com/download/) will be needed. Once you have it installed on your PC, open the command prompt window and use the change directory command `cd` to go to the src folder of this repository, and create a Python environment using the environment.yml file.

```
conda activate
conda env create -f environment.yml
```
Once the environment is created, the packages need to be installed in the python environment. Thus, from the same directory as the environment.yml file: 

```
conda activate gloffis
pip install -e .
conda deactivate
```
Since information is retrieved from a Microsoft Access Database, be sure the Microsoft ACE drivers 'Microsoft Access Driver (*.mdb, *.accdb)'* are available.

To check if the drivers are installed, you could run from your python IDE: 

```
import pyodbc
print([x for x in pyodbc.drivers() if x.startswith('Microsoft Access Driver')])
```
If drivers are installed, the list will show the 'Microsoft Access Driver (*.mdb, *.accdb)'* driver. Otherwise, the list will return empty. 

**If the drivers are not installed, you can obtain them from** [here](https://www.microsoft.com/en-US/download/details.aspx?id=13255)

In case the Access Database Engine could not be installed because of discrepancies between versions of Office installed (32-64 bits), please install the Microsoft ACE drivers on pasive mode from the command line: 

*To install the Microsoft ACE 64-bit driver on a machine running Office 2010 32-bit:*
```
$> AccessDatabaseEngine_X64.exe /passive
```

*To install the Microsoft ACE 32-bit driver on a machine running Office 2010 64-bit:*

```
$> AccessDatabaseEngine.exe /passive
```

- To run all the scripts in batch mode and generate all configuration files at once, please run the "master.py" script (located in the folder: *gloffis\master.py*)

- To learn how to use the tool by adding a new wflow model to the database and thus to the hydrological forecasting system, please visit the [Add_new_wflow_model](https://github.com/a-onate/gloffis_prod/blob/main/doc/Add_new_wflow_model.md) file in the documentation. 

The scripts composing the system are available from 2020 at https://github.com/a-onate/gloffis_prod. Other software used in this project is Delft-FEWS (Werner et al., 2013) freely available for end-users at www.delft-fews.eu, and wflow (Imhoff et al., 2020), whose open-source code can be found at https://github.com/openstreams/wﬂow. Finally, the data used for this work includes the Numerical Weather Prediction products NWP ICON (ICOsahedral Nonhydrostatic model) made available free of charge by The Deutscher Wetterdienst (DWD) at http://opendata.dwd.de/ and the ERA5 reanalysis product distributed freely by the European Centre for Medium-Range Weather Forecasts (ECMWF) via https://cds.climate.copernicus.eu.


