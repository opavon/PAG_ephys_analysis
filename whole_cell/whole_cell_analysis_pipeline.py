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
from whole_cell_utilities import * # includes functions importFile, openFile, openHDF5file, getInputResistance
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
last_folder_results_df = getInputResistance(folders_to_check_IR, folder_to_save_IR, results_type_IR, save_type_IR, curated_channel_IR)

# Inspect the output, corresponding to the dataframe from the last folder in the list
last_folder_results_df