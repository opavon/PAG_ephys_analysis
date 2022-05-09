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
# ## 1.0 | Input resistance

# Set path to input resistance results
folder_results_IR = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_results\IC_tau_inputresistance"

# Load .json files for vgat conditions
vgat_control_IR = pd.read_json(os.path.join(folder_results_IR, 'vgat_control_pooled_input_resistance.json'))
vgat_kyn_ptx_IR = pd.read_json(os.path.join(folder_results_IR, 'vgat_kynurenic_picrotoxin_pooled_input_resistance.json'))
vgat_ttx_IR = pd.read_json(os.path.join(folder_results_IR, 'vgat_ttx_pooled_input_resistance.json'))
vgat_dopamine_IR = pd.read_json(os.path.join(folder_results_IR, 'vgat_dopamine_pooled_input_resistance.json'))
vgat_agatoxin_IR = pd.read_json(os.path.join(folder_results_IR, 'vgat_agatoxin_pooled_input_resistance.json'))

# Load .json files for vglut2 conditions
vglut2_control_IR = pd.read_json(os.path.join(folder_results_IR, 'vglut2_control_pooled_input_resistance.json'))
vglut2_kyn_ptx_IR = pd.read_json(os.path.join(folder_results_IR, 'vglut2_kynurenic_picrotoxin_pooled_input_resistance.json'))
vglut2_ptx_IR = pd.read_json(os.path.join(folder_results_IR, 'vglut2_picrotoxin_pooled_input_resistance.json'))
vglut2_ptx_leucine_IR = pd.read_json(os.path.join(folder_results_IR, 'vglut2_picrotoxin_leucine_pooled_input_resistance.json'))
vglut2_ttx_IR = pd.read_json(os.path.join(folder_results_IR, 'vglut2_ttx_pooled_input_resistance.json'))
vglut2_dopamine_IR = pd.read_json(os.path.join(folder_results_IR, 'vglut2_dopamine_pooled_input_resistance.json'))

# Print average input resistance across conditions
print('----- Input Resistance -----')
print(f'The vgat_control input resistance is        {np.round(np.mean(vgat_control_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vgat_control_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vgat_kyn_ptx input resistance is        {np.round(np.mean(vgat_kyn_ptx_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vgat_kyn_ptx_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vgat_ttx input resistance is            {np.round(np.mean(vgat_ttx_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vgat_ttx_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vgat_dopamine input resistance is       {np.round(np.mean(vgat_dopamine_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vgat_dopamine_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vgat_agatoxin input resistance is       {np.round(np.mean(vgat_agatoxin_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vgat_agatoxin_IR[["IR_MOhm"]])[0], 2)} MOhm')

print(f'The vglut2_control input resistance is      {np.round(np.mean(vglut2_control_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vglut2_control_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vglut2_kyn_ptx input resistance is      {np.round(np.mean(vglut2_kyn_ptx_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vglut2_kyn_ptx_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vglut2_ptx input resistance is          {np.round(np.mean(vglut2_ptx_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vglut2_ptx_leucine input resistance is  {np.round(np.mean(vglut2_ptx_leucine_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx_leucine_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vglut2_ttx input resistance is          {np.round(np.mean(vglut2_ttx_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vglut2_ttx_IR[["IR_MOhm"]])[0], 2)} MOhm')
print(f'The vglut2_dopamine input resistance is     {np.round(np.mean(vglut2_dopamine_IR[["IR_MOhm"]])[0], 2)} +/- {np.round(np.std(vglut2_dopamine_IR[["IR_MOhm"]])[0], 2)} MOhm')

# %%
# ## 2.0 | Single Action Potential characterisation

# Set path to single Action Potential results
folder_results_single_AP = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_results\IC_single_AP"

# Load .json files for vgat conditions
vgat_control_single_AP = pd.read_json(os.path.join(folder_results_single_AP, 'vgat_control_pooled_single_AP_parameters.json'))
vgat_kyn_ptx_single_AP = pd.read_json(os.path.join(folder_results_single_AP, 'vgat_kynurenic_picrotoxin_pooled_single_AP_parameters.json'))
vgat_dopamine_single_AP = pd.read_json(os.path.join(folder_results_single_AP, 'vgat_dopamine_pooled_single_AP_parameters.json'))
vgat_agatoxin_single_AP = pd.read_json(os.path.join(folder_results_single_AP, 'vgat_agatoxin_pooled_single_AP_parameters.json'))

# Load .json files for vglut2 conditions
vglut2_control_single_AP = pd.read_json(os.path.join(folder_results_single_AP, 'vglut2_control_pooled_single_AP_parameters.json'))
vglut2_kyn_ptx_single_AP = pd.read_json(os.path.join(folder_results_single_AP, 'vglut2_kynurenic_picrotoxin_pooled_single_AP_parameters.json'))
vglut2_ptx_single_AP = pd.read_json(os.path.join(folder_results_single_AP, 'vglut2_picrotoxin_pooled_single_AP_parameters.json'))
vglut2_ptx_leucine_single_AP = pd.read_json(os.path.join(folder_results_single_AP, 'vglut2_picrotoxin_leucine_pooled_single_AP_parameters.json'))
vglut2_dopamine_single_AP = pd.read_json(os.path.join(folder_results_single_AP, 'vglut2_dopamine_pooled_single_AP_parameters.json'))

# Print average spike threshold and half-width across conditions
print('----- Spike Threshold -----')
print(f'The vgat_control spike threshold is         {np.round(np.mean(vgat_control_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vgat_control_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vgat_kyn_ptx spike threshold is         {np.round(np.mean(vgat_kyn_ptx_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vgat_kyn_ptx_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vgat_dopamine spike threshold is        {np.round(np.mean(vgat_dopamine_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vgat_dopamine_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vgat_agatoxin spike threshold is        {np.round(np.mean(vgat_agatoxin_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vgat_agatoxin_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')

print(f'The vglut2_control spike threshold is       {np.round(np.mean(vglut2_control_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_control_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vglut2_kyn_ptx spike threshold is       {np.round(np.mean(vglut2_kyn_ptx_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_kyn_ptx_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vglut2_ptx spike threshold is           {np.round(np.mean(vglut2_ptx_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vglut2_ptx_leucine spike threshold is   {np.round(np.mean(vglut2_ptx_leucine_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx_leucine_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vglut2_dopamine spike threshold is      {np.round(np.mean(vglut2_dopamine_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_dopamine_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')


print('\n----- Spike Half-width -----')
print(f'The vgat_control half-width is              {np.round(np.mean(vgat_control_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vgat_control_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vgat_kyn_ptx half-width is              {np.round(np.mean(vgat_kyn_ptx_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vgat_kyn_ptx_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vgat_dopamine half-width is             {np.round(np.mean(vgat_dopamine_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vgat_dopamine_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vgat_agatoxin half-width is             {np.round(np.mean(vgat_agatoxin_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vgat_agatoxin_single_AP[["half_width_ms"]])[0], 2)} ms')

print(f'The vglut2_control half-width is            {np.round(np.mean(vglut2_control_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_control_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vglut2_kyn_ptx half-width is            {np.round(np.mean(vglut2_kyn_ptx_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_kyn_ptx_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vglut2_ptx half-width is                {np.round(np.mean(vglut2_ptx_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vglut2_ptx_leucine half-width is        {np.round(np.mean(vglut2_ptx_leucine_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx_leucine_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vglut2_dopamine half-width is           {np.round(np.mean(vglut2_dopamine_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_dopamine_single_AP[["half_width_ms"]])[0], 2)} ms')

# %%
# Check the type of data you have in the dataframe
print(vglut2_ptx_single_AP.columns) # column names
print(vglut2_ptx_single_AP.index) # row names


# %%
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (6, 6))
# sns.lineplot(data = vgat_control_single_AP['holding_mV'], label = "VGAT control")
#sns.barplot(x = vgat_control_single_AP.index, y = vgat_control_single_AP['holding_mV'])
#sns.heatmap(data = vgat_control_single_AP[["holding_mV", "peaks_magnitude_mV", "avg_spike_threshold_mV"]], annot = True)
sns.scatterplot(x = vglut2_control_IR['IR_MOhm'], 
                y = vglut2_control_IR['injected_pA'])
#sns.regplot(x = vgat_control_single_AP['avg_spike_trough_mV'], y = vgat_control_single_AP['avg_spike_threshold_mV'])
#sns.lmplot(x ='avg_spike_trough_mV', y = 'avg_spike_threshold_mV', data = vgat_control_single_AP)

plt.title("A title")
#plt.xlabel("X axis")
#plt.ylabel("Y axis")
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner

# %%
pd.read_csv

# %%
