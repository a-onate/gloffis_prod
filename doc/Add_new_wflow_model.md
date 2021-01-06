# Adding a new wflow hydrological model to GLOFFIS.

The production system gloffis_prod generates Delft-FEWS configuration files relying on the information stored in a MS Access Database and the series of scripts presented in this repository, to contribute to the automatization of the system’s set-up. The external database holds the information related to the system’s characteristics (according to the specific design adopted) mainly associated to the data products considered and wflow models incorporated. The scripts retrieve that information and produce XML configuration files belonging to the directories mentioned in the readme file.
In order to illustrate how the system can be edited using the production system to include a new wflow hydrological model for its execution, this document proposes a series of steps applied to incorporate the wflow model for the Moselle catchment in France as an example.

## Step 1: 

Arrange the proposed directory structure as the one shown in Fig. 1. The FEWS bin and configuration folder (fews) should be unzipped and correctly placed in the chosen working directory, as well as the unzipped wflow bundle for model execution *(C:\FEWS_19_02\gloffis_prod\fews\Modules\wflow\wflow-2020.1.1-bundle)*.

<p align="center">
<img width="200" height="150" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/add_wflow_model_fig1.png">
</p>

**Please note that:** If the folder structure adopted is different to the one proposed, then the paths descriptions should be changed according to your preferred structure in the master.py script for: 
- The MS Access database 
- The scripted and defaults Delft-FEWS configuration folder, and 
- The final merged Delft-FEWS configuration folder.

## Step 2: 
Create the conda environment and make sure the MS ACE drivers are installed in your computer, as stated in the readme file. 

## Step 3: 

Unzip the *Example_Moselle.zip* file and place the folder *“wflow_moselle_20200720”* (containing ColdStateFiles and ModuleDataSetFiles for the example model) in the following directory: *C:\FEWS_19_02\gloffis_prod\scripts\gloffis\externals\wflow_modules*. 

## Step 4:

Add the information related to the wflow model to the database *(the database <Database_gloffis_prod> is located in: C:\FEWS_19_02\gloffis_prod\scripts\gloffis\externals)*. The required information refers to the model characteristics: grid definition, temporal resolution, workflow set-up to run the model in update and forecasting mode, and wflow bundle used, which is shown in the table below: 

<p align="center">
<img width="500" height="250" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/add_wflow_model_table1.png">
</p>

Two workflows for model execution will be set: for update using ERA5 and an ICON-EU online reanalysis, and for forecasting using ICON-EU NWP. 

There are two ways of adding the required information to the database: by direct edition of the tables, or by using the forms created in the database. 
The tables where the information will be saved are: 

- tbl_FEWS_GridDetails 
- tbl_Wflow_Models
- tbl_Wflow_Workflows

To use the Access Database forms, click on *frm_MasterForm_DataMgmt*. 

<p align="center">
<img width="280" height="120" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/add_wflow_model_fig2.png">
</p>

In this form, the section *“Manage wflow models’ information”* (Fig. 3) will be of interest to add the new model. 

<p align="center">
<img width="320" height="280" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/add_wflow_model_fig3.png">
</p>

First the wflow model grid is added by clicking *“add new model grid”*, and the information from Table 1 will be entered in the emerging window, as shown in Fig. 4. The same goes for *Wflow Model Information (Fig. 5)* and *Wflow Model Workflow* (Fig. 6).

<p align="center">
<img width="500" height="290" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/add_wflow_model_fig4_5.png">
</p>

The update and forecast workflows are both entered by clicking on “add new model workflow”[^1].

<p align="center">
<img width="500" height="210" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/add_wflow_model_fig6.png">
</p>

## Step 5:

Once the information has been entered and saved, the queries must be run, to retrieve the latest changes done to the tables. To run the queries in batch mode, open the *frm_Run_mtbl_Scripting_queries* form and click on *“Run Queries”*

<p align="center">
<img width="280" height="100" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/add_wflow_model_fig7.png">
</p>

<p align="center">
<img width="330" height="100" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/add_wflow_model_fig8.png">
</p>

## Step 6:

Close the MS Access Database, and using your preferred python IDE execute the master script *(C:\FEWS_19_02\gloffis_prod\scripts\gloffis\master.py)*, making sure the paths are correct. 

## Step 7:

Finally, open the Delft-FEWS GUI and the workflows for the wflow model for the Moselle catchment will successfully be added. 

<p align="center">
<img width="320" height="260" src="https://github.com/a-onate/gloffis_prod/blob/main/doc/images/add_wflow_model_fig9.png">
</p>


[^1]: Note: Although the update workflow should only include information about the data products used as observation and online reanalysis, it is also advised to fill the *"NWP used for forecast"* field, with the same NWP used for online reanalysis, to avoid problems with the database.  This will not affect the forecast workflow.
