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

# Let's retrieve one dataframe containing the Rseal results for one cell from a .json file 
vgat_ctrl_Rseal_df = pd.read_json(os.path.join(vgat_ctrl_save_path, "lpag_vgat_190204_c2_LICU_OP_VC_clear_nointerval_3_df_Rseal.json"))
vgat_ctrl_Rseal_df

# %%
# We can quickly plot the evolution of the Rseal throughout that particular recording on a sweep by sweep basis
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
plt.plot(vgat_ctrl_Rseal_df.loc['seal_resistance_MOhm'], 'k')
plt.title('Seal Resistance across sweeps', fontsize = 14)
plt.xlabel('sweep number', fontsize = 12)
plt.ylabel('Seal Resistance [MOhm]', fontsize = 12)
plt.ylim([0, round(np.mean(vgat_ctrl_Rseal_df.loc['seal_resistance_MOhm'])*2)])
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
plt.show()

# %%
# Let's get an average of the seal resistance throughout the recording
np.mean(vgat_ctrl_Rseal_df.loc['seal_resistance_MOhm'])

# %%
# Let's get the standard deviation for the average seal resistance throughout the recording
np.std(vgat_ctrl_Rseal_df.loc['seal_resistance_MOhm'])

# %%
# Now we want to do this for all the Rseal dataframes we generated when extracting the data, and we want to put them in the same dataframe format that we used for the firing frequency.

# Choose a subfolder
folders_to_check = [vgat_ctrl_save_path]

# Choose type of results
results_type = '_df_Rseal'

for folder in folders_to_check:
    vgat_ctrl_temp_list = [] # an empty list to store the data frames
    vgat_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]
    for file in vgat_ctrl_results_files:
        # Get the cell ID and assign it to the row label
        file_id = [file.split('.')[0]]
        cell_id = ['_'.join((file_id[0].split('_'))[0:-2])]
        print(cell_id)

        temp_1 = pd.read_json(os.path.join(folder, file)) # read data frame from json file

        temp_avg_Rseal = np.mean(temp_1.loc['seal_resistance_MOhm'])

        temp_df = pd.DataFrame([temp_avg_Rseal], index = cell_id, columns = ['seal_resistance_MOhm'])

        vgat_ctrl_temp_list.append(temp_df)
    
    vgat_ctrl_df = pd.concat(vgat_ctrl_temp_list) # concatenate all the data frames in the list

vgat_ctrl_df

# %%
# Now that we were able to do this for one of the folders, let's make a function to do it for all of them at once.

def getAvgRsealResults(
    folders_to_check,
    results_type,
    save_type
    ):
    """
    `getAvgRsealResults` finds the .json files that match the criteria in each celltype_condition folder, loads the results they contain, computes the average of the RSeal, combines them into a single dataframe, and saves them as a new .json file. It returns one separate dataframe for the pooled results of each folder. For example, if we set `results_type = '_df_Rseal'` it will load the results from all the JSON files in a folder containing that type of data and will combine them into a single dataframe that can be used for statistical analysis and plotting.
    
    :folders_to_check: a list containing the paths to the four folders to check.
    :results_type: a string containing the type of result (without its .json extension) to load and combine.
    :save_type: a string containing the type of result you are saving. For example, if `results_type = "df_Rseal"`, setting `save_type = "Rseal"` will avoid errors if we re-run the function.
    """
    # Check conditions
    if not len(folders_to_check) == 4:
        print(f"Please provide the path to the four folders corresponding to: vgat_control, vgat_kynurenic_picrotoxin, vglut2_control, vglut2_picrotoxin")
        return None, None, None, None

    for folder in folders_to_check:
        if 'vgat_control' in folder:
            vgat_ctrl_temp_list = [] # an empty list to store the data frames
            vgat_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file] # get the files that contain the type of results you want
            for file in vgat_ctrl_results_files:
                # Get the cell ID and assign it to the row label
                temp_file_id = [file.split('.')[0]]
                temp_cell_id = ['_'.join((temp_file_id[0].split('_'))[0:-2])]

                temp_1 = pd.read_json(os.path.join(folder, file)) # read data frame from json file
                temp_1_avg_Rseal = np.mean(temp_1.loc['seal_resistance_MOhm']) # compute the average Rseal across sweeps
                temp_1_std_Rseal = np.std(temp_1.loc['seal_resistance_MOhm']) # compute the standard deviation of the Rseal average across sweeps
                temp_1_df = pd.DataFrame([[temp_1_avg_Rseal, temp_1_std_Rseal]], index = temp_cell_id, columns = ['Rseal_avg_MOhm', 'Rseal_avg_std']) # create a new dataframe with the average Rseal and the cell ID
                vgat_ctrl_temp_list.append(temp_1_df) # append the data frame to the list
            vgat_ctrl_df = pd.concat(vgat_ctrl_temp_list) # concatenate all the data frames in the list
            vgat_ctrl_df.to_json(os.path.join(folder, 'vgat_control_pooled' + save_type + '.json')) # save combined results as new .json file
        
        if 'vgat_kynurenic_picrotoxin' in folder:
            vgat_kynac_ptx_temp_list = [] # an empty list to store the data frames
            vgat_kynac_ptx_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file] # get the files that contain the type of results you want
            for file in vgat_kynac_ptx_results_files:
                # Get the cell ID and assign it to the row label
                temp_file_id = [file.split('.')[0]]
                temp_cell_id = ['_'.join((temp_file_id[0].split('_'))[0:-2])]

                temp_2 = pd.read_json(os.path.join(folder, file)) # read data frame from json file
                temp_2_avg_Rseal = np.mean(temp_2.loc['seal_resistance_MOhm']) # compute the average Rseal across sweeps
                temp_2_std_Rseal = np.std(temp_2.loc['seal_resistance_MOhm']) # compute the standard deviation of the Rseal average across sweeps
                temp_2_df = pd.DataFrame([[temp_2_avg_Rseal, temp_2_std_Rseal]], index = temp_cell_id, columns = ['Rseal_avg_MOhm', 'Rseal_avg_std']) # create a new dataframe with the average Rseal and the cell ID
                vgat_kynac_ptx_temp_list.append(temp_2_df) # append the data frame to the list
            vgat_kynac_ptx_df = pd.concat(vgat_kynac_ptx_temp_list) # concatenate all the data frames in the list
            vgat_kynac_ptx_df.to_json(os.path.join(folder, 'vgat_kynurenic_picrotoxin_pooled' + save_type + '.json')) # save combined results as new .json file

        if 'vglut2_control' in folder:
            vglut2_ctrl_temp_list = [] # an empty list to store the data frames
            vglut2_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file] # get the files that contain the type of results you want
            for file in vglut2_ctrl_results_files:
                # Get the cell ID and assign it to the row label
                temp_file_id = [file.split('.')[0]]
                temp_cell_id = ['_'.join((temp_file_id[0].split('_'))[0:-2])]

                temp_3 = pd.read_json(os.path.join(folder, file)) # read data frame from json file
                temp_3_avg_Rseal = np.mean(temp_3.loc['seal_resistance_MOhm']) # compute the average Rseal across sweeps
                temp_3_std_Rseal = np.std(temp_3.loc['seal_resistance_MOhm']) # compute the standard deviation of the Rseal average across sweeps
                temp_3_df = pd.DataFrame([[temp_3_avg_Rseal, temp_3_std_Rseal]], index = temp_cell_id, columns = ['Rseal_avg_MOhm', 'Rseal_avg_std']) # create a new dataframe with the average Rseal and the cell ID
                vglut2_ctrl_temp_list.append(temp_3_df) # append the data frame to the list
            vglut2_ctrl_df = pd.concat(vglut2_ctrl_temp_list) # concatenate all the data frames in the list
            vglut2_ctrl_df.to_json(os.path.join(folder, 'vglut2_control_pooled' + save_type + '.json')) # save combined results as new .json file
        
        if 'vglut2_picrotoxin' in folder:
            vglut2_ptx_temp_list = [] # an empty list to store the data frames
            vglut2_ptx_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file] # get the files that contain the type of results you want
            for file in vglut2_ptx_results_files:
                # Get the cell ID and assign it to the row label
                temp_file_id = [file.split('.')[0]]
                temp_cell_id = ['_'.join((temp_file_id[0].split('_'))[0:-2])]

                temp_4 = pd.read_json(os.path.join(folder, file)) # read data frame from json file
                temp_4_avg_Rseal = np.mean(temp_4.loc['seal_resistance_MOhm']) # compute the average Rseal across sweeps
                temp_4_std_Rseal = np.std(temp_4.loc['seal_resistance_MOhm']) # compute the standard deviation of the Rseal average across sweeps
                temp_4_df = pd.DataFrame([[temp_4_avg_Rseal, temp_4_std_Rseal]], index = temp_cell_id, columns = ['Rseal_avg_MOhm', 'Rseal_avg_std']) # create a new dataframe with the average Rseal and the cell ID
                vglut2_ptx_temp_list.append(temp_4_df) # append the data frame to the list
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
results_type = '_df_Rseal'
save_type = '_Rseal'

# Run function
vgat_ctrl_df, vgat_kynac_ptx_df, vglut2_ctrl_df, vglut2_ptx_df = getAvgRsealResults(folders_to_check, results_type, save_type)

# Print results
print(len(vgat_ctrl_df))
print(len(vgat_kynac_ptx_df))
print(len(vglut2_ctrl_df))
print(len(vglut2_ptx_df))