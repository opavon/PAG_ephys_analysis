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
from utilities import * # includes functions importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes, plotSpikesQC, spikesQC, cleanSpikes, averageSpikes, getSpikeParameters, getFiringRate, getInterspikeInterval, saveLooseSealResults
print("done!")

# %%
# Paths to results
vgat_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
vgat_kynac_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_kynurenic_picrotoxin"
vglut2_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_control"
vglut2_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_picrotoxin"

# %%
# To retrieve the data from a .json file into a dataframe do:
    # df_name = pd.read_json(os.path.join(save_path, file_name))

vgat_ctrl_firing_frequency = pd.read_json(os.path.join(vgat_ctrl_save_path, "dlpag_vgat_171113_c5_LIAI_OP_clear_VC_1_df_firing_frequency.json"))


# A possible way to automate this is by doing:
    # df_name = pd.read_json(os.path.join(save_path, file_id[0] + "_df_name.json"))

vgat_kynac_ptx_firing_frequency = pd.read_json(os.path.join(vgat_kynac_ptx_save_path, cell_id + "_df_firing_frequency.json"))
vglut2_ctrl_firing_frequency = pd.read_json(os.path.join(vglut2_ctrl_save_path, cell_id + "_df_firing_frequency.json"))
vglut2_ptx_firing_frequency = pd.read_json(os.path.join(vglut2_ptx_save_path, cell_id + "_df_firing_frequency.json"))

# %%
# To retrieve the data from a .npz file into a variable do:
    # results_data = np.load(os.path.join(save_path, file_id[0] + "_results.npz"))
    # print([key for key in results_data])
    # Then you can retrieve one specific variable
    # average_spike = results_data['average_spike']
results_data = np.load(os.path.join(vgat_ctrl_save_path, "dlpag_vgat_171113_c5_LIAI_OP_clear_VC_1_results.npz"))

print([key for key in results_data])

# %%
# We want a function that allows you to decide which type of results you want to retrieve and from which subfolders. For instance, something like the steps below:
    # Loop over .json files in a results folder
    # load only the file with "firing_frequency"
    # get the cell id from the file name
    # append to common data frame

# Let's try to obtain the names of all the results file that fulfill a criteria - for instance, those that contain the firing_frequency dataframe
# get the .json file names corresponding to one type of results for one condition
results_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
results_type = '_df_firing_frequency'
results_files = [results_file for results_file in os.listdir(results_path) if results_type in results_file]
results_files

# %%
# Now we want to load all .json files and combine the results into a single dataframe. For instance, let's get one single dataframe containing all the firing_frequency dataframes from vgat_control cells.
temp_list = [] # an empty list to store the data frames
for file in results_files:
    temp = pd.read_json(os.path.join(results_path, file)) # read data frame from json file
    temp_list.append(temp) # append the data frame to the list
temp_2df = pd.concat(temp_list) # concatenate all the data frames in the list
temp_2df

# %%
# Now we need to expand this and obtain one dataframe for all the files corresponding to each celltype_condition, saved in the following subfolders:
vgat_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
vgat_kynac_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_kynurenic_picrotoxin"
vglut2_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_control"
vglut2_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_picrotoxin"

folders_to_check = [vgat_ctrl_save_path, vgat_kynac_ptx_save_path, vglut2_ctrl_save_path, vglut2_ptx_save_path]

results_type = '_df_firing_frequency'

for folder in folders_to_check:
    if 'vgat_control' in folder:
        vgat_ctrl_temp_list = [] # an empty list to store the data frames
        vgat_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]
        for file in vgat_ctrl_results_files:
            temp = pd.read_json(os.path.join(folder, file)) # read data frame from json file
            vgat_ctrl_temp_list.append(temp) # append the data frame to the list
        vgat_ctrl_df = pd.concat(vgat_ctrl_temp_list) # concatenate all the data frames in the list
    if 'vgat_kynurenic_picrotoxin' in folder:
        vgat_kynac_ptx_temp_list = [] # an empty list to store the data frames
        vgat_kynac_ptx_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]
        for file in vgat_kynac_ptx_results_files:
            temp = pd.read_json(os.path.join(folder, file)) # read data frame from json file
            vgat_kynac_ptx_temp_list.append(temp) # append the data frame to the list
        vgat_kynac_ptx_df = pd.concat(vgat_kynac_ptx_temp_list) # concatenate all the data frames in the list
    if 'vglut2_control' in folder:
        vlut2_ctrl_temp_list = [] # an empty list to store the data frames
        vlut2_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]
        for file in vlut2_ctrl_results_files:
            temp = pd.read_json(os.path.join(folder, file)) # read data frame from json file
            vlut2_ctrl_temp_list.append(temp) # append the data frame to the list
        vlut2_ctrl_df = pd.concat(vlut2_ctrl_temp_list) # concatenate all the data frames in the list
    if 'vglut2_picrotoxin' in folder:
        vglut2_ptx_temp_list = [] # an empty list to store the data frames
        vglut2_ptx_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]
        for file in vglut2_ptx_results_files:
            temp = pd.read_json(os.path.join(folder, file)) # read data frame from json file
            vglut2_ptx_temp_list.append(temp) # append the data frame to the list
        vglut2_ptx_df = pd.concat(vglut2_ptx_temp_list) # concatenate all the data frames in the list

print(len(vgat_ctrl_df))
print(len(vgat_kynac_ptx_df))
print(len(vlut2_ctrl_df))
print(len(vglut2_ptx_df))

# %%
# Put it into a function
def combineJSONresults(
    folders_to_check,
    results_type
    ):
    """
    `combineJSONresults` finds the .json files of that match the criteria in each celltype_condition folder, loads the results they contain, combines them into a single dataframe, and saves them as a new .json file. It returns one separate dataframe for the pooled results of each folder. For example, if we set `results_type = '_df_firing_frequency'` it will load the results from all the JSON files in a folder containing that type of data and will combine them into a single dataframe that can be used for statistical analysis and plotting.
    
    :folders_to_check: a list containing the paths to the four folders to check.
    :results_type: a string containing the type of result (without its .json extension) to load and combine.
    """
    # Check conditions
    if not len(folders_to_check) == 4:
        print(f"Please provide the path to the four folders corresponding to: vgat_control, vgat_kynurenic_picrotoxin, vglut2_control, vglut2_picrotoxin")
        return None, None, None, None

    for folder in folders_to_check:
        if 'vgat_control' in folder:
            vgat_ctrl_temp_list = [] # an empty list to store the data frames
            vgat_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]
            for file in vgat_ctrl_results_files:
                temp_1 = pd.read_json(os.path.join(folder, file)) # read data frame from json file
                vgat_ctrl_temp_list.append(temp_1) # append the data frame to the list
            vgat_ctrl_df = pd.concat(vgat_ctrl_temp_list) # concatenate all the data frames in the list
            vgat_ctrl_df.to_json(os.path.join(folder, 'vgat_control_pooled' + results_type + '.json')) # save combined results as new .json file
        
        if 'vgat_kynurenic_picrotoxin' in folder:
            vgat_kynac_ptx_temp_list = [] # an empty list to store the data frames
            vgat_kynac_ptx_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]
            for file in vgat_kynac_ptx_results_files:
                temp_2 = pd.read_json(os.path.join(folder, file)) # read data frame from json file
                vgat_kynac_ptx_temp_list.append(temp_2) # append the data frame to the list
            vgat_kynac_ptx_df = pd.concat(vgat_kynac_ptx_temp_list) # concatenate all the data frames in the list
            vgat_kynac_ptx_df.to_json(os.path.join(folder, 'vgat_kynurenic_picrotoxin_pooled' + results_type + '.json')) # save combined results as new .json file

        
        if 'vglut2_control' in folder:
            vglut2_ctrl_temp_list = [] # an empty list to store the data frames
            vglut2_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]
            for file in vglut2_ctrl_results_files:
                temp_3 = pd.read_json(os.path.join(folder, file)) # read data frame from json file
                vglut2_ctrl_temp_list.append(temp_3) # append the data frame to the list
            vglut2_ctrl_df = pd.concat(vglut2_ctrl_temp_list) # concatenate all the data frames in the list
            vglut2_ctrl_df.to_json(os.path.join(folder, 'vglut2_control_pooled' + results_type + '.json')) # save combined results as new .json file
        
        if 'vglut2_picrotoxin' in folder:
            vglut2_ptx_temp_list = [] # an empty list to store the data frames
            vglut2_ptx_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]
            for file in vglut2_ptx_results_files:
                temp_4 = pd.read_json(os.path.join(folder, file)) # read data frame from json file
                vglut2_ptx_temp_list.append(temp_4) # append the data frame to the list
            vglut2_ptx_df = pd.concat(vglut2_ptx_temp_list) # concatenate all the data frames in the list
            vglut2_ptx_df.to_json(os.path.join(folder, 'vglut2_picrotoxin_pooled' + results_type + '.json')) # save combined results as new .json file
    
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
results_type = '_df_firing_frequency'

# Run function
vgat_ctrl_df, vgat_kynac_ptx_df, vlut2_ctrl_df, vglut2_ptx_df = combineJSONresults(folders_to_check, results_type)

# Print results
print(len(vgat_ctrl_df))
print(len(vgat_kynac_ptx_df))
print(len(vlut2_ctrl_df))
print(len(vglut2_ptx_df))

# %%
