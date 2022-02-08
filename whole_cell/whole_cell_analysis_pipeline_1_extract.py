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
from whole_cell_utilities import * # includes functions importFile, openFile, openHDF5file, getInputResistance, getSpikeParameters
print("done!")

# %%
# Manually load data for a single recording
#channels_df, time, dt, folder_name, file_name = importFile(curated_channel = None)
#print("file imported")

# %% [markdown]
# ## 1 | Get input resistance from all the curated cells in one or more folders

# %%
# ## 1.0 | Set paths to subfolders where curated .hdf5 files are stored
# Each file has already been inspected and moved to the subfolder corresponding to the celltype_condition of the experiment
vgat_agatoxin_IR_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vgat_agatoxin"
vgat_ctrl_IR_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vgat_control"
vgat_dopamine_IR_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vgat_dopamine"
vgat_kynac_ptx_IR_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vgat_kynurenic_picrotoxin"
vgat_ttx_IR_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vgat_ttx"
vglut2_ctrl_IR_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vglut2_control"
vglut2_dopamine_IR_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vglut2_dopamine"
vglut2_kynac_ptx_IR_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vglut2_kynurenic_picrotoxin"
vglut2_ptx_IR_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vglut2_picrotoxin"
vglut2_ptx_leucine_IR_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vglut2_picrotoxin_leucine"
vglut2_ttx_IR_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vglut2_ttx"
print("done!")

# %%
# ## 1.1 | Get the average input resistance for each cell and combine the results in one data frame for each cell type and condition

# Choose folders
folders_to_check_IR = [vgat_agatoxin_IR_save_path,
                    vgat_ctrl_IR_save_path,
                    vgat_dopamine_IR_save_path, 
                    vgat_kynac_ptx_IR_save_path,
                    vgat_ttx_IR_save_path,
                    vglut2_ctrl_IR_save_path,
                    vglut2_dopamine_IR_save_path,
                    vglut2_kynac_ptx_IR_save_path,
                    vglut2_ptx_IR_save_path,
                    vglut2_ptx_leucine_IR_save_path,
                    vglut2_ttx_IR_save_path]

# Specify the path to the folder where results will be saved. It should contain the same number of subfolders with the same names as the ones specified in `folders_to_check`
folder_to_save_IR = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_results\IC_tau_inputresistance"

# Choose type of results and suffix for saved file
results_type_IR = '_IC_tau_inputresistance'
save_type_IR = '_input_resistance'

# Set the name of the curated channel, if any:
curated_channel_IR = 'Sweeps_Analysis'

# Run function
last_folder_IR_results_df = getInputResistance(folders_to_check_IR, folder_to_save_IR, results_type_IR, save_type_IR, curated_channel_IR)

# Inspect the output, corresponding to the dataframe from the last folder in the list
last_folder_IR_results_df

# %%
# ## 1.2 | Quickly summarise input resistance results

# Set path to results
folder_to_save_IR = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_results\IC_tau_inputresistance"

# Load .json files
vgat_control_IR = pd.read_json(os.path.join(folder_to_save_IR, 'vgat_control_pooled_input_resistance.json'))
vgat_kyn_ptx_IR = pd.read_json(os.path.join(folder_to_save_IR, 'vgat_kynurenic_picrotoxin_pooled_input_resistance.json'))
vgat_ttx_IR = pd.read_json(os.path.join(folder_to_save_IR, 'vgat_ttx_pooled_input_resistance.json'))
vglut2_control_IR = pd.read_json(os.path.join(folder_to_save_IR, 'vglut2_control_pooled_input_resistance.json'))
vglut2_kyn_ptx_IR = pd.read_json(os.path.join(folder_to_save_IR, 'vglut2_kynurenic_picrotoxin_pooled_input_resistance.json'))
vglut2_ptx_IR = pd.read_json(os.path.join(folder_to_save_IR, 'vglut2_picrotoxin_pooled_input_resistance.json'))
vglut2_ttx_IR = pd.read_json(os.path.join(folder_to_save_IR, 'vglut2_ttx_pooled_input_resistance.json'))

# Print average input resistance across conditions
print('----- Input Resistance -----')
print(f'The vgat_control input resistance is    {np.round(np.mean(vgat_control_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vgat_control_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vgat_kyn_ptx input resistance is    {np.round(np.mean(vgat_kyn_ptx_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vgat_kyn_ptx_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vgat_ttx input resistance is        {np.round(np.mean(vgat_ttx_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vgat_ttx_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vglut2_control input resistance is  {np.round(np.mean(vglut2_control_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vglut2_control_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vglut2_kyn_ptx input resistance is  {np.round(np.mean(vglut2_kyn_ptx_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vglut2_kyn_ptx_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vglut2_ptx input resistance is      {np.round(np.mean(vglut2_ptx_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vglut2_ttx input resistance is      {np.round(np.mean(vglut2_ttx_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vglut2_ttx_IR[["IR_MOhm"]])[0], 2)} MOhm')

# %% [markdown]
# ## 2 | Get the action potential threshold and other parameters from all the curated cells in one or more folders

# %%
# ## 2.0 | Set paths to subfolders where curated .hdf5 files are stored
# Each file has already been inspected and moved to the subfolder corresponding to the celltype_condition of the experiment
vgat_agatoxin_single_AP_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_single_AP\vgat_agatoxin"
vgat_ctrl_single_AP_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_single_AP\vgat_control"
vgat_dopamine_single_AP_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_single_AP\vgat_dopamine"
vgat_kynac_ptx_single_AP_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_single_AP\vgat_kynurenic_picrotoxin"
vglut2_ctrl_single_AP_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_single_AP\vglut2_control"
vglut2_dopamine_single_AP_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_single_AP\vglut2_dopamine"
vglut2_kynac_ptx_single_AP_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_single_AP\vglut2_kynurenic_picrotoxin"
vglut2_ptx_single_AP_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_single_AP\vglut2_picrotoxin"
vglut2_ptx_leucine_single_AP_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_single_AP\vglut2_picrotoxin_leucine"
print("done!")

# %%
# ## 2.1 | Get the action potential threshold and other parameters from the single AP protocol for each cell and combine the results in one data frame for each cell type and condition

# Choose folders
folders_to_check_single_AP = [vgat_agatoxin_single_AP_save_path,
                            vgat_ctrl_single_AP_save_path,
                            vgat_dopamine_single_AP_save_path,
                            vgat_kynac_ptx_single_AP_save_path,
                            vglut2_ctrl_single_AP_save_path,
                            vglut2_dopamine_single_AP_save_path,
                            vglut2_kynac_ptx_single_AP_save_path,
                            vglut2_ptx_single_AP_save_path,
                            vglut2_ptx_leucine_single_AP_save_path]

# Specify the path to the folder where results will be saved. It should contain the same number of subfolders with the same names as the ones specified in `folders_to_check`
folder_to_save_single_AP = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_results\IC_single_AP"

# Choose type of results and suffix for saved file
results_type_single_AP = '_IC_single_AP'
save_type_single_AP = '_single_AP_parameters'

# Set the name of the curated channel, if any:
curated_channel_single_AP = 'Sweeps_Analysis'

# Run function
last_folder_single_AP_results_df = getSpikeParameters(folders_to_check_single_AP, folder_to_save_single_AP, results_type_single_AP, save_type_single_AP, curated_channel_single_AP)

# Inspect the output, corresponding to the dataframe from the last folder in the list
last_folder_single_AP_results_df

# %%
# ## 2.2 | Quickly summarise single AP results

# Set path to results
folder_to_save_single_AP = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_results\IC_single_AP"

# Load .json files
vgat_control = pd.read_json(os.path.join(folder_to_save_single_AP, 'vgat_control_pooled_single_AP_parameters.json'))
vgat_kyn_ptx = pd.read_json(os.path.join(folder_to_save_single_AP, 'vgat_kynurenic_picrotoxin_pooled_single_AP_parameters.json'))
vglut2_control = pd.read_json(os.path.join(folder_to_save_single_AP, 'vglut2_control_pooled_single_AP_parameters.json'))
vglut2_kyn_ptx = pd.read_json(os.path.join(folder_to_save_single_AP, 'vglut2_kynurenic_picrotoxin_pooled_single_AP_parameters.json'))
vglut2_ptx = pd.read_json(os.path.join(folder_to_save_single_AP, 'vglut2_picrotoxin_pooled_single_AP_parameters.json'))

# Print average spike threshold and half-width across conditions
print('----- Spike Threshold -----')
print(f'The vgat_control spike threshold is     {np.round(np.mean(vgat_control[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vgat_control[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vgat_kyn_ptx spike threshold is     {np.round(np.mean(vgat_kyn_ptx[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vgat_kyn_ptx[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vglut2_control spike threshold is   {np.round(np.mean(vglut2_control[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_control[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vglut2_kyn_ptx spike threshold is   {np.round(np.mean(vglut2_kyn_ptx[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_kyn_ptx[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vglut2_ptx spike threshold is       {np.round(np.mean(vglut2_ptx[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx[["avg_spike_threshold_mV"]])[0], 2)} mV')
print('\n----- Spike Half-width -----')
print(f'The vgat_control half-width is          {np.round(np.mean(vgat_control[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vgat_control[["half_width_ms"]])[0], 2)} ms')
print(f'The vgat_kyn_ptx half-width is          {np.round(np.mean(vgat_kyn_ptx[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vgat_kyn_ptx[["half_width_ms"]])[0], 2)} ms')
print(f'The vglut2_control half-width is        {np.round(np.mean(vglut2_control[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_control[["half_width_ms"]])[0], 2)} ms')
print(f'The vglut2_kyn_ptx half-width is        {np.round(np.mean(vglut2_kyn_ptx[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_kyn_ptx[["half_width_ms"]])[0], 2)} ms')
print(f'The vglut2_ptx half-width is            {np.round(np.mean(vglut2_ptx[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx[["half_width_ms"]])[0], 2)} ms')

# %%
