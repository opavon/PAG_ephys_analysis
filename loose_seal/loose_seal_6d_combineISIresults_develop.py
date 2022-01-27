# %% [markdown]
# ## 0 | Import packages and load data

# %%
# Import packages
import os
import tkinter
from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
import h5py
from collections import defaultdict
from nptdms import TdmsFile
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from IPython import get_ipython
from utilities import * # includes functions importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes, plotSpikesQC, spikesQC, cleanSpikes, averageSpikes, getSpikeParameters, getFiringRate, getInterspikeInterval, saveLooseSealResults, combineJSONresults
print("done!")

# Paths to results
vgat_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
vgat_kynac_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_kynurenic_picrotoxin"
vglut2_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_control"
vglut2_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_picrotoxin"

# %%
# To retrieve the data from a .json file into a dataframe do:
    # df_name = pd.read_json(os.path.join(save_path, file_name))

# Let's retrieve one dataframe containing the interspike interval results for one cell from a .json file 
vgat_ctrl_ISI_df = pd.read_json(os.path.join(vgat_ctrl_save_path, "vlpag_vgat_190124_c2_LICJ_OP_VC_clear_nointerval_1_df_interspike_interval.json"))
vgat_ctrl_ISI_df

# %%
# Now we want to combine all the ISI and related values into a single vector, assign each vector to a new column, and assign the cell id to the row name. And we want to do this for all the files in a subfolder.

# Choose a subfolder
folders_to_check = [vgat_ctrl_save_path]

# Choose type of results
results_type = '_df_interspike_interval'

for folder in folders_to_check:
    vgat_ctrl_temp_list = [] # an empty list to store the data frames
    vgat_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]
    for file in vgat_ctrl_results_files:
        # Get the cell ID
        file_id = [file.split('.')[0]]
        cell_id = ['_'.join((file_id[0].split('_'))[0:-3])]
        print(cell_id)

        temp_1 = pd.read_json(os.path.join(folder, file)) # read data frame from json file

        # We need to check wheter the cell we are looking at had any spikes. If number of spikes is zero, then we don't need to calculate anything.
        if isinstance(temp_1.loc['interspike_interval_ms'][0], float):
            temp_1_isi_ms = temp_1.loc['interspike_interval_ms'].values
            temp_1_isi_pA_avg = temp_1.loc['holding_isi_pA_avg'].values
            temp_1_isi_std = temp_1.loc['holding_isi_std'].values
            
            temp_df = pd.DataFrame([[temp_1_isi_ms, temp_1_isi_pA_avg, temp_1_isi_std]], index = cell_id, columns = ['interspike_interval_ms', 'holding_isi_pA_avg', 'holding_isi_std'])

        # If, on the other hand, we didn't detect any spikes for this cell, we will have "NA" in the "spike_magnitude_pA" field. In that case, we just append "NA" to the new columns to keep the shape of the dataframe.
        if isinstance(temp_1.loc['interspike_interval_ms'][0], str):            
            temp_df = pd.DataFrame([['NA', 'NA', 'NA']], index = cell_id, columns = ['interspike_interval_ms', 'holding_isi_pA_avg', 'holding_isi_std'])
        
        vgat_ctrl_temp_list.append(temp_df)
    
    vgat_ctrl_df = pd.concat(vgat_ctrl_temp_list) # concatenate all the data frames in the list

vgat_ctrl_df

# %%
# Now that we were able to do this for one of the folders, let's make a function to do it for all of them at once.

def combineISIresults(
    folders_to_check,
    results_type = "_df_interspike_interval",
    save_type = "_interspike_interval"
    ):
    """
    `combineISIresults` finds the .json files that match the criteria in each celltype_condition folder, loads the results they contain, combines all the values of a each row into a single vector and puts the vector in the corresponding column of a new dataframe, and saves the final dataframe as a new .json file. It returns one separate dataframe for the pooled results of each folder. For example, if we set `results_type = '_df_interspike_interval'` it will load the results from all the JSON files in a folder containing that type of data and will combine them into a single dataframe that can be used for statistical analysis and plotting.
    
    :folders_to_check: a list containing the paths to the four folders to check.
    :results_type: a string containing the type of result (without its .json extension) to load and combine.
    :save_type: a string containing the type of result you are saving. For example, if `results_type = "_df_interspike_interval"`, setting `save_type = "_interspike_interval"` will avoid errors if we re-run the function.
    """   

    # Check conditions
    if not len(folders_to_check) == 4:
        print(f"Please provide the path to the four folders corresponding to: vgat_control, vgat_kynurenic_picrotoxin, vglut2_control, vglut2_picrotoxin")
        return None, None, None, None

    for folder in folders_to_check:
        if 'vgat_control' in folder:
            vgat_ctrl_temp_list = [] # an empty list to store the data frames
            vgat_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]  # get the files that contain the type of results you want
            for file in vgat_ctrl_results_files:
                # Get the cell ID
                temp_1_file_id = [file.split('.')[0]]
                temp_1_cell_id = ['_'.join((temp_1_file_id[0].split('_'))[0:-3])]

                temp_1_isi_results = pd.read_json(os.path.join(folder, file)) # read data frame from json file

                # We need to check wheter the cell we are looking at had any spikes. If number of spikes is zero, then we don't need to calculate anything.
                if isinstance(temp_1_isi_results.loc['interspike_interval_ms'][0], float):
                    temp_1_isi_ms = temp_1_isi_results.loc['interspike_interval_ms'].values
                    temp_1_isi_pA_avg = temp_1_isi_results.loc['holding_isi_pA_avg'].values
                    temp_1_isi_std = temp_1_isi_results.loc['holding_isi_std'].values
                    
                    temp_1_df = pd.DataFrame([[temp_1_isi_ms, temp_1_isi_pA_avg, temp_1_isi_std]], index = temp_1_cell_id, columns = ['interspike_interval_ms', 'holding_isi_pA_avg', 'holding_isi_std'])

                # If, on the other hand, we didn't detect any spikes for this cell, we will have "NA" in the "interspike_interval_ms" field. In that case, we just append "NA" to the new columns to keep the shape of the dataframe.
                if isinstance(temp_1_isi_results.loc['interspike_interval_ms'][0], str):            
                    temp_1_df = pd.DataFrame([['NA', 'NA', 'NA']], index = temp_1_cell_id, columns = ['interspike_interval_ms', 'holding_isi_pA_avg', 'holding_isi_std'])
                
                vgat_ctrl_temp_list.append(temp_1_df)
        
            vgat_ctrl_df = pd.concat(vgat_ctrl_temp_list) # concatenate all the data frames in the list
            vgat_ctrl_df.to_json(os.path.join(folder, 'vgat_control_pooled' + save_type + '.json')) # save combined results as new .json file

        if 'vgat_kynurenic_picrotoxin' in folder:
            vgat_kynac_ptx_temp_list = [] # an empty list to store the data frames
            vgat_kynac_ptx_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]  # get the files that contain the type of results you want
            for file in vgat_kynac_ptx_results_files:
                # Get the cell ID
                temp_2_file_id = [file.split('.')[0]]
                temp_2_cell_id = ['_'.join((temp_2_file_id[0].split('_'))[0:-3])]

                temp_2_isi_results = pd.read_json(os.path.join(folder, file)) # read data frame from json file

                # We need to check wheter the cell we are looking at had any spikes. If number of spikes is zero, then we don't need to calculate anything.
                if isinstance(temp_2_isi_results.loc['interspike_interval_ms'][0], float):
                    temp_2_isi_ms = temp_2_isi_results.loc['interspike_interval_ms'].values
                    temp_2_isi_pA_avg = temp_2_isi_results.loc['holding_isi_pA_avg'].values
                    temp_2_isi_std = temp_2_isi_results.loc['holding_isi_std'].values
                    
                    temp_2_df = pd.DataFrame([[temp_2_isi_ms, temp_2_isi_pA_avg, temp_2_isi_std]], index = temp_2_cell_id, columns = ['interspike_interval_ms', 'holding_isi_pA_avg', 'holding_isi_std'])

                # If, on the other hand, we didn't detect any spikes for this cell, we will have "NA" in the "interspike_interval_ms" field. In that case, we just append "NA" to the new columns to keep the shape of the dataframe.
                if isinstance(temp_2_isi_results.loc['interspike_interval_ms'][0], str):            
                    temp_2_df = pd.DataFrame([['NA', 'NA', 'NA']], index = temp_2_cell_id, columns = ['interspike_interval_ms', 'holding_isi_pA_avg', 'holding_isi_std'])
                
                vgat_kynac_ptx_temp_list.append(temp_2_df)
        
            vgat_kynac_ptx_df = pd.concat(vgat_kynac_ptx_temp_list) # concatenate all the data frames in the list
            vgat_kynac_ptx_df.to_json(os.path.join(folder, 'vgat_kynurenic_picrotoxin_pooled' + save_type + '.json')) # save combined results as new .json file

        if 'vglut2_control' in folder:
            vglut2_ctrl_temp_list = [] # an empty list to store the data frames
            vglut2_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]  # get the files that contain the type of results you want
            for file in vglut2_ctrl_results_files:
                # Get the cell ID
                temp_3_file_id = [file.split('.')[0]]
                temp_3_cell_id = ['_'.join((temp_3_file_id[0].split('_'))[0:-3])]

                temp_3_isi_results = pd.read_json(os.path.join(folder, file)) # read data frame from json file

                # We need to check wheter the cell we are looking at had any spikes. If number of spikes is zero, then we don't need to calculate anything.
                if isinstance(temp_3_isi_results.loc['interspike_interval_ms'][0], float):
                    temp_3_isi_ms = temp_3_isi_results.loc['interspike_interval_ms'].values
                    temp_3_isi_pA_avg = temp_3_isi_results.loc['holding_isi_pA_avg'].values
                    temp_3_isi_std = temp_3_isi_results.loc['holding_isi_std'].values
                    
                    temp_3_df = pd.DataFrame([[temp_3_isi_ms, temp_3_isi_pA_avg, temp_3_isi_std]], index = temp_3_cell_id, columns = ['interspike_interval_ms', 'holding_isi_pA_avg', 'holding_isi_std'])

                # If, on the other hand, we didn't detect any spikes for this cell, we will have "NA" in the "interspike_interval_ms" field. In that case, we just append "NA" to the new columns to keep the shape of the dataframe.
                if isinstance(temp_3_isi_results.loc['interspike_interval_ms'][0], str):            
                    temp_3_df = pd.DataFrame([['NA', 'NA', 'NA']], index = temp_3_cell_id, columns = ['interspike_interval_ms', 'holding_isi_pA_avg', 'holding_isi_std'])
                
                vglut2_ctrl_temp_list.append(temp_3_df)
        
            vglut2_ctrl_df = pd.concat(vglut2_ctrl_temp_list) # concatenate all the data frames in the list
            vglut2_ctrl_df.to_json(os.path.join(folder, 'vglut2_control_pooled' + save_type + '.json')) # save combined results as new .json file

        if 'vglut2_picrotoxin' in folder:
            vglut2_ptx_temp_list = [] # an empty list to store the data frames
            vglut2_ptx_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]  # get the files that contain the type of results you want
            for file in vglut2_ptx_results_files:
                # Get the cell ID
                temp_4_file_id = [file.split('.')[0]]
                temp_4_cell_id = ['_'.join((temp_4_file_id[0].split('_'))[0:-3])]

                temp_4_isi_results = pd.read_json(os.path.join(folder, file)) # read data frame from json file

                # We need to check wheter the cell we are looking at had any spikes. If number of spikes is zero, then we don't need to calculate anything.
                if isinstance(temp_4_isi_results.loc['interspike_interval_ms'][0], float):
                    temp_4_isi_ms = temp_4_isi_results.loc['interspike_interval_ms'].values
                    temp_4_isi_pA_avg = temp_4_isi_results.loc['holding_isi_pA_avg'].values
                    temp_4_isi_std = temp_4_isi_results.loc['holding_isi_std'].values
                    
                    temp_4_df = pd.DataFrame([[temp_4_isi_ms, temp_4_isi_pA_avg, temp_4_isi_std]], index = temp_4_cell_id, columns = ['interspike_interval_ms', 'holding_isi_pA_avg', 'holding_isi_std'])

                # If, on the other hand, we didn't detect any spikes for this cell, we will have "NA" in the "interspike_interval_ms" field. In that case, we just append "NA" to the new columns to keep the shape of the dataframe.
                if isinstance(temp_4_isi_results.loc['interspike_interval_ms'][0], str):            
                    temp_4_df = pd.DataFrame([['NA', 'NA', 'NA']], index = temp_4_cell_id, columns = ['interspike_interval_ms', 'holding_isi_pA_avg', 'holding_isi_std'])
                
                vglut2_ptx_temp_list.append(temp_4_df)
        
            vglut2_ptx_df = pd.concat(vglut2_ptx_temp_list) # concatenate all the data frames in the list
            vglut2_ptx_df.to_json(os.path.join(folder, 'vglut2_picrotoxin_pooled' + save_type + '.json')) # save combined results as new .json file
    
    print('results saved')

    return vgat_ctrl_df, vgat_kynac_ptx_df, vglut2_ctrl_df, vglut2_ptx_df # pandas dataframes


# %%
# Test function

# Set paths to subfolders
vgat_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
vgat_kynac_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_kynurenic_picrotoxin"
vglut2_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_control"
vglut2_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_picrotoxin"

# Choose folders
folders_to_check = [vgat_ctrl_save_path, vgat_kynac_ptx_save_path, vglut2_ctrl_save_path, vglut2_ptx_save_path]

# Choose type of results
results_type = '_df_interspike_interval'
save_type = '_interspike_interval'

# Run function
vgat_ctrl_df, vgat_kynac_ptx_df, vglut2_ctrl_df, vglut2_ptx_df = combineISIresults(folders_to_check, results_type, save_type)

# Print results
print(len(vgat_ctrl_df))
print(len(vgat_kynac_ptx_df))
print(len(vglut2_ctrl_df))
print(len(vglut2_ptx_df))
# %%
