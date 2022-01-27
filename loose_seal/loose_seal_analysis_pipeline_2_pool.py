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
from utilities import * # includes functions combineJSONresults, getAvgRsealResults, getSpikeHalfWidth, combineISIresults
print("done!")

# %% [markdown]
# ## 1 | Pool results across cells: seal resistance and firing rate

# Once we have run the previous steps for each recording and we have extracted our results, we can proceed to pool them across cell_type and condition.

# %%
# ## 1.0 | Set paths to subfolders where extracted results files are stored
vgat_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
vgat_kynac_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_kynurenic_picrotoxin"
vglut2_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_control"
vglut2_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_picrotoxin"
print("done!")

# %%
# ## 1.1 | Get average seal resistance for each cell and combine the results in one data frame for each cell type and condition

# Choose folders
folders_to_check = [vgat_ctrl_save_path, 
                    vgat_kynac_ptx_save_path, 
                    vglut2_ctrl_save_path, 
                    vglut2_ptx_save_path]

# Choose type of results and suffix for saved file
results_type_Rseal = '_df_Rseal'
save_type_Rseal = '_Rseal'

# Run function
vgat_ctrl_Rseal_df, vgat_kynac_ptx_Rseal_df, vglut2_ctrl_Rseal_df, vglut2_ptx_Rseal_df = getAvgRsealResults(folders_to_check, results_type_Rseal, save_type_Rseal)

# Print results number of cells in each group and inspect one of the resulting data frames
print(len(vgat_ctrl_Rseal_df))
print(len(vgat_kynac_ptx_Rseal_df))
print(len(vglut2_ctrl_Rseal_df))
print(len(vglut2_ptx_Rseal_df))
vgat_ctrl_Rseal_df

# %%
# ## 1.2 | Pool the data frames containing the firing frequency for each cell type and condition

# Choose folders
folders_to_check = [vgat_ctrl_save_path, 
                    vgat_kynac_ptx_save_path, 
                    vglut2_ctrl_save_path, 
                    vglut2_ptx_save_path]

# Choose type of results and suffix for saved file
results_type_ff = '_df_firing_frequency'
save_type_ff = '_firing_frequency'

# Run function
vgat_ctrl_firing_frequency_df, vgat_kynac_ptx_firing_frequency_df, vglut2_ctrl_firing_frequency_df, vglut2_ptx_firing_frequency_df = combineJSONresults(folders_to_check, results_type_ff, save_type_ff)

# Print results
print(len(vgat_ctrl_firing_frequency_df))
print(len(vgat_kynac_ptx_firing_frequency_df))
print(len(vglut2_ctrl_firing_frequency_df))
print(len(vglut2_ptx_firing_frequency_df))
vgat_ctrl_firing_frequency_df

# %%
# ## 1.3 | Load the average spike, calculate the half-width, append to the results data frame, and then pool the data frames for each cell type and condition

# Choose folders
folders_to_check = [vgat_ctrl_save_path, 
                    vgat_kynac_ptx_save_path, 
                    vglut2_ctrl_save_path, 
                    vglut2_ptx_save_path]

# Choose type of results and suffix for saved file
results_type_avg_spike = '_df_parameters_avg_spike'
save_type_avg_spike = '_avg_spike'

# Run function
vgat_ctrl_avg_spike_df, vgat_kynac_ptx_avg_spike_df, vglut2_ctrl_avg_spike_df, vglut2_ptx_avg_spike_df = getSpikeHalfWidth(folders_to_check, results_type_avg_spike, save_type_avg_spike)

# Print results number of cells in each group and inspect one of the resulting data frames
print(len(vgat_ctrl_avg_spike_df))
print(len(vgat_kynac_ptx_avg_spike_df))
print(len(vglut2_ctrl_avg_spike_df))
print(len(vglut2_ptx_avg_spike_df))
vgat_ctrl_avg_spike_df

# %%
# ## 1.4 | Pool the data frames containing the interspike intervals for each cell type and condition

# Choose folders
folders_to_check = [vgat_ctrl_save_path, 
                    vgat_kynac_ptx_save_path, 
                    vglut2_ctrl_save_path, 
                    vglut2_ptx_save_path]

# Choose type of results and suffix for saved file
results_type_isi = '_df_interspike_interval'
save_type_isi = '_interspike_interval'

# Run function
vgat_ctrl_isi_df, vgat_kynac_ptx_isi_df, vglut2_ctrl_isi_df, vglut2_ptx_isi_df = combineISIresults(folders_to_check, results_type_isi, save_type_isi)

# Print results number of cells in each group and inspect one of the resulting data frames
print(len(vgat_ctrl_isi_df))
print(len(vgat_kynac_ptx_isi_df))
print(len(vglut2_ctrl_isi_df))
print(len(vglut2_ptx_isi_df))
vgat_ctrl_isi_df