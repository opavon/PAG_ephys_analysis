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

# %% [markdown]
# ## 1 | Input resistance
# Below follow some lines of code to summarise the input resistance data and plot the average traces across conditions.

# ### 1.1 | Load and summarise results

# %%
# Set path to input resistance results
folder_results_IR = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_results\IC_tau_inputresistance"

# Load data from .json files for vgat conditions
vgat_control_IR = pd.read_json(os.path.join(folder_results_IR, 'vgat_control_pooled_input_resistance.json'))
vgat_kyn_ptx_IR = pd.read_json(os.path.join(folder_results_IR, 'vgat_kynurenic_picrotoxin_pooled_input_resistance.json'))
vgat_ttx_IR = pd.read_json(os.path.join(folder_results_IR, 'vgat_ttx_pooled_input_resistance.json'))
vgat_dopamine_IR = pd.read_json(os.path.join(folder_results_IR, 'vgat_dopamine_pooled_input_resistance.json'))
vgat_agatoxin_IR = pd.read_json(os.path.join(folder_results_IR, 'vgat_agatoxin_pooled_input_resistance.json'))

# Load data from .json files for vglut2 conditions
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

# %% [markdown]
# ### 1.2 | Plot Input Resistance sample traces for each condition

# %%
# Once we have loaded the data, we can plot the average traces across conditions and export them for making figures.

# %%
# Set colours
colour_vgat_ctrl = '#FF8080'
colour_vgat_kynac_ptx = '#FFCCCC'
colour_vglut2_ctrl = '#0F99B2'
colour_vglut2_kynac_ptx = '#9FD6E0'
print('colours set!')

# Set path to save folder
folder_sample_traces_IR = r"D:\Dropbox (UCL - SWC)\Project_paginhibition\analysis\whole_cell\whole_cell_plots\IC_tau_inputresistance\sample_traces"
curated_channel = 'Sweeps_Analysis'
print('path to results loaded!')

# %%
## Potential vgat_ctrl sample traces
# dmpag_vgat_170222_c3_OP_IC_tau_inputresistance_2_1 (no)
# dmpag_vgat_201217_c3_WDIBM_OP_IC_tau_inputresistance_3_2 (no)
# dmpag_vgat_201217_c5_WDIBO_OP_IC_tau_inputresistance_3_1 (yes)

# Select vgat_ctrl sample cell
vgat_ctrl_sample_cell = 'dmpag_vgat_201217_c5_WDIBO_OP_IC_tau_inputresistance_3_1.hdf5'

test_pulse_membrane_baselined, test_pulse_command_baselined, avg_test_pulse_membrane_baselined, avg_test_pulse_command_baselined, time, dt = getSampleTracesIR(folder_sample_traces_IR, vgat_ctrl_sample_cell, curated_channel)

# Plot protocol and cell's voltage response
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)
# Plot individual baselined sweeps
for sweep in range(len(test_pulse_membrane_baselined)):
    axs['A'].plot(time[0], test_pulse_membrane_baselined[sweep], color = colour_vgat_ctrl)
# Plot average sweep
axs['A'].plot(time[0], avg_test_pulse_membrane_baselined, color = 'k')
axs['A'].set_title("Cell's membrane response", fontsize = 12)
axs['A'].set_xlabel('time [ms]', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([0, (len(avg_test_pulse_membrane_baselined)*dt)])
axs['A'].set_ylim([-20, 5])
# Plot command
axs['B'].plot(time[0][0:len(avg_test_pulse_command_baselined)], avg_test_pulse_command_baselined, color = 'k')
axs['B'].set_title('Command', fontsize = 12)
axs['B'].set_xlabel('time [ms]', fontsize = 12)
axs['B'].set_ylabel('current [pA]', fontsize = 12)
axs['B'].set_xlim([0, (len(avg_test_pulse_membrane_baselined)*dt)])
axs['B'].set_ylim([-25, 5])
plt.suptitle('\nVGAT control: dmpag_vgat_201217_c5_WDIBO\n', fontsize = 14)
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_IR, 'vgat_ctrl_input_resistance_WDIBO.eps'), format = 'eps') # save figure as .eps

# %%
## Potential vgat_kynac_ptx sample traces
# dmpag_vgat_180507_c6_WDIAF_OP_IC_tau_inputresistance_1_1_kyn_ptx (no)
# dmpag_vgat_201218_c5_WDIBT_OP_IC_tau_inputresistance_3_2_kyn_ptx (yes)
# dmpag_vgat_181210_c6_WDIAL_OP_IC_tau_inputresistance_2_1_kyn_ptx (no)

# Select vgat_kynac_ptx sample cell
vgat_kynac_ptx_sample_cell = 'dmpag_vgat_201218_c5_WDIBT_OP_IC_tau_inputresistance_3_2_kyn_ptx.hdf5'

test_pulse_membrane_baselined, test_pulse_command_baselined, avg_test_pulse_membrane_baselined, avg_test_pulse_command_baselined, time, dt = getSampleTracesIR(folder_sample_traces_IR, vgat_kynac_ptx_sample_cell, curated_channel)

# Plot protocol and cell's voltage response
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)
# Plot individual baselined sweeps
for sweep in range(len(test_pulse_membrane_baselined)):
    axs['A'].plot(time[0], test_pulse_membrane_baselined[sweep], color = colour_vgat_kynac_ptx)
# Plot average sweep
axs['A'].plot(time[0], avg_test_pulse_membrane_baselined, color = 'k')
axs['A'].set_title("Cell's membrane response", fontsize = 12)
axs['A'].set_xlabel('time [ms]', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([0, (len(avg_test_pulse_membrane_baselined)*dt)])
axs['A'].set_ylim([-20, 5])
# Plot command
axs['B'].plot(time[0][0:len(avg_test_pulse_command_baselined)], avg_test_pulse_command_baselined, color = 'k')
axs['B'].set_title('Command', fontsize = 12)
axs['B'].set_xlabel('time [ms]', fontsize = 12)
axs['B'].set_ylabel('current [pA]', fontsize = 12)
axs['B'].set_xlim([0, (len(avg_test_pulse_membrane_baselined)*dt)])
axs['B'].set_ylim([-25, 5])
plt.suptitle('\nVGAT in kynac_ptx: dmpag_vgat_201218_c5_WDIBT\n', fontsize = 14)
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_IR, 'vgat_kynac_ptx_input_resistance_WDIBT.eps'), format = 'eps') # save figure as .eps

# %%
## Potential vglut2_ctrl sample traces 
# dlpag_vglut2_200722_c3_WEAL_OP_IC_tau_inputresistance_2_1 (yes)
# dmpag_vglut2_200722_c7_WDEAT_OP_IC_tau_inputresistance_4_1 (maybe)
# dmpag_vglut2_200711_c2_WEAF_OP_IC_tau_inputresistance_3_2 (no)

# Select vglut2_ctrl sample cell
vglut2_ctrl_sample_cell = 'dlpag_vglut2_200722_c3_WEAL_OP_IC_tau_inputresistance_2_1.hdf5'

test_pulse_membrane_baselined, test_pulse_command_baselined, avg_test_pulse_membrane_baselined, avg_test_pulse_command_baselined, time, dt = getSampleTracesIR(folder_sample_traces_IR, vglut2_ctrl_sample_cell, curated_channel)

# Plot protocol and cell's voltage response
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)
# Plot individual baselined sweeps
for sweep in range(len(test_pulse_membrane_baselined)):
    axs['A'].plot(time[0], test_pulse_membrane_baselined[sweep], color = colour_vglut2_ctrl)
# Plot average sweep
axs['A'].plot(time[0], avg_test_pulse_membrane_baselined, color = 'k')
axs['A'].set_title("Cell's membrane response", fontsize = 12)
axs['A'].set_xlabel('time [ms]', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([0, (len(avg_test_pulse_membrane_baselined)*dt)])
axs['A'].set_ylim([-20, 5])
# Plot command
axs['B'].plot(time[0][0:len(avg_test_pulse_command_baselined)], avg_test_pulse_command_baselined, color = 'k')
axs['B'].set_title('Command', fontsize = 12)
axs['B'].set_xlabel('time [ms]', fontsize = 12)
axs['B'].set_ylabel('current [pA]', fontsize = 12)
axs['B'].set_xlim([0, (len(avg_test_pulse_membrane_baselined)*dt)])
axs['B'].set_ylim([-25, 5])
plt.suptitle('\nVGluT2 control: dlpag_vglut2_200722_c3_WEAL\n', fontsize = 14)
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_IR, 'vglut2_ctrl_input_resistance_WEAL.eps'), format = 'eps') # save figure as .eps

# %%
## Potential vglut2_kynac_ptx sample traces 
# dmpag_vglut2_180504_c2_WDEAF_OP_IC_tau_inputresistance_1_1_kyn_ptx (no)
# dlpag_vglut2_180504_c4_WDEAH_OP_IC_tau_inputresistance_1_1_kyn_ptx (no)
# dmpag_vglut2_180503_c2_WDEAB_OP_IC_tau_inputresistance_1_1_kyn_ptx (yes)

# Select vglut2_kynac_ptx sample cell
vglut2_kynac_ptx_sample_cell = 'dmpag_vglut2_180503_c2_WDEAB_OP_IC_tau_inputresistance_1_1_kyn_ptx.hdf5'

test_pulse_membrane_baselined, test_pulse_command_baselined, avg_test_pulse_membrane_baselined, avg_test_pulse_command_baselined, time, dt = getSampleTracesIR(folder_sample_traces_IR, vglut2_kynac_ptx_sample_cell, curated_channel)

# Plot protocol and cell's voltage response
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)
# Plot individual baselined sweeps
for sweep in range(len(test_pulse_membrane_baselined)):
    axs['A'].plot(time[0], test_pulse_membrane_baselined[sweep], color = colour_vglut2_kynac_ptx)
# Plot average sweep
axs['A'].plot(time[0], avg_test_pulse_membrane_baselined, color = 'k')
axs['A'].set_title("Cell's membrane response", fontsize = 12)
axs['A'].set_xlabel('time [ms]', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([0, (len(avg_test_pulse_membrane_baselined)*dt)])
axs['A'].set_ylim([-20, 5])
# Plot command
axs['B'].plot(time[0][0:len(avg_test_pulse_command_baselined)], avg_test_pulse_command_baselined, color = 'k')
axs['B'].set_title('Command', fontsize = 12)
axs['B'].set_xlabel('time [ms]', fontsize = 12)
axs['B'].set_ylabel('current [pA]', fontsize = 12)
axs['B'].set_xlim([0, (len(avg_test_pulse_membrane_baselined)*dt)])
axs['B'].set_ylim([-25, 5])
plt.suptitle('\nVGluT2 in kynac_ptx: dmpag_vglut2_180503_c2_WDEAB\n', fontsize = 14)
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_IR, 'vglut2_kynac_ptx_input_resistance_WDEAB.eps'), format = 'eps') # save figure as .eps

# %% [markdown]
# ## 2 | Single Action Potential characterisation

# ### 2.1 | Load and summarise results

# %%
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
# VGAT
print(f'The vgat_control spike threshold is         {np.round(np.mean(vgat_control_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vgat_control_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vgat_kyn_ptx spike threshold is         {np.round(np.mean(vgat_kyn_ptx_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vgat_kyn_ptx_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vgat_dopamine spike threshold is        {np.round(np.mean(vgat_dopamine_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vgat_dopamine_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vgat_agatoxin spike threshold is        {np.round(np.mean(vgat_agatoxin_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vgat_agatoxin_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
# VGluT2
print(f'The vglut2_control spike threshold is       {np.round(np.mean(vglut2_control_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_control_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vglut2_kyn_ptx spike threshold is       {np.round(np.mean(vglut2_kyn_ptx_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_kyn_ptx_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vglut2_ptx spike threshold is           {np.round(np.mean(vglut2_ptx_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vglut2_ptx_leucine spike threshold is   {np.round(np.mean(vglut2_ptx_leucine_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx_leucine_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')
print(f'The vglut2_dopamine spike threshold is      {np.round(np.mean(vglut2_dopamine_single_AP[["avg_spike_threshold_mV"]])[0], 2)} +/- {np.round(np.std(vglut2_dopamine_single_AP[["avg_spike_threshold_mV"]])[0], 2)} mV')


print('\n----- Spike Half-width -----')
# VGAT
print(f'The vgat_control half-width is              {np.round(np.mean(vgat_control_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vgat_control_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vgat_kyn_ptx half-width is              {np.round(np.mean(vgat_kyn_ptx_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vgat_kyn_ptx_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vgat_dopamine half-width is             {np.round(np.mean(vgat_dopamine_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vgat_dopamine_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vgat_agatoxin half-width is             {np.round(np.mean(vgat_agatoxin_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vgat_agatoxin_single_AP[["half_width_ms"]])[0], 2)} ms')
# VGluT2
print(f'The vglut2_control half-width is            {np.round(np.mean(vglut2_control_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_control_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vglut2_kyn_ptx half-width is            {np.round(np.mean(vglut2_kyn_ptx_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_kyn_ptx_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vglut2_ptx half-width is                {np.round(np.mean(vglut2_ptx_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vglut2_ptx_leucine half-width is        {np.round(np.mean(vglut2_ptx_leucine_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_ptx_leucine_single_AP[["half_width_ms"]])[0], 2)} ms')
print(f'The vglut2_dopamine half-width is           {np.round(np.mean(vglut2_dopamine_single_AP[["half_width_ms"]])[0], 2)} +/- {np.round(np.std(vglut2_dopamine_single_AP[["half_width_ms"]])[0], 2)} ms')

# %% [markdown]
# ### 2.2 | Plot single Action Potential sample traces for each condition
# Example figures to illustrate the AP threshold and phase plots

# %%
# We can check the type of data in a given dataframe as follows
# print(vgat_control_single_AP.columns) # column names
# print(vglut2_ptx_single_AP.index) # row names

# Set colours
colour_vgat_ctrl = '#FF8080'
colour_vgat_kynac_ptx = '#FFCCCC'
colour_vglut2_ctrl = '#0F99B2'
colour_vglut2_kynac_ptx = '#9FD6E0'
print('colours set!')

# Set path to save folder
folder_sample_traces_singleAP = r"D:\Dropbox (UCL - SWC)\Project_paginhibition\analysis\whole_cell\whole_cell_plots\IC_single_AP\sample_traces"
print('path to results loaded!')

# %%
## Potential vgat_ctrl sample traces
# dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5

# Select vgat_ctrl sample cell
vgat_ctrl_sample_cell_avg_spike = np.array(vgat_control_single_AP.avg_spike_trace_mV.loc['dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5'])
vgat_ctrl_sample_cell_spikes = np.array(vgat_control_single_AP.cut_spikes_traces_mV.loc['dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5'])
vgat_ctrl_sample_cell_threshold_index = vgat_control_single_AP.avg_spike_threshold_index.loc['dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5']
vgat_ctrl_sample_cell_threshold_mV = np.round(vgat_control_single_AP.avg_spike_threshold_mV.loc['dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5'], 2)
vgat_ctrl_sample_cell_dvdt = np.array(vgat_control_single_AP.dvdt_trace.loc['dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5'])

# Plot protocol and cell's voltage response
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)
# Plot individual baselined sweeps
for sweep in range(len(vgat_ctrl_sample_cell_spikes)):
    axs['A'].plot(vgat_ctrl_sample_cell_spikes[sweep], color = colour_vgat_ctrl)
# Plot average sweep
axs['A'].plot(vgat_ctrl_sample_cell_avg_spike, color = 'k')
# Plot average spike threshold
axs['A'].plot(vgat_ctrl_sample_cell_threshold_index, vgat_ctrl_sample_cell_avg_spike[vgat_ctrl_sample_cell_threshold_index], "or")
axs['A'].set_title('VGAT control: dlpag_vgat_200922_c1_WIAT', fontsize = 14)
axs['A'].text(2325, 20, f'AP threshold: {vgat_ctrl_sample_cell_threshold_mV} mV', fontsize = 11)
axs['A'].set_xlabel('samples', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([2200, 2400])
axs['A'].set_ylim([-80, 40])
# Phase plot
axs['B'].plot(vgat_ctrl_sample_cell_avg_spike[1:], vgat_ctrl_sample_cell_dvdt, color = colour_vgat_ctrl)
axs['B'].set_title('Phase plot', fontsize = 14)
axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
axs['B'].set_xlim([-100, 100])
axs['B'].set_ylim([-500, 600])
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_singleAP, 'vgat_ctrl_single_AP_WIAT.eps'), format = 'eps') # save figure as .eps

# %%
## Potential vgat_kynac_ptx sample traces
# dmpag_vgat_181211_c4_WDIAQ_OP_IC_single_AP_3_1_kyn_ptx

# Select vgat_kynac_ptx sample cell
vgat_kynac_ptx_sample_cell_avg_spike = np.array(vgat_kyn_ptx_single_AP.avg_spike_trace_mV.loc['dmpag_vgat_181211_c4_WDIAQ_OP_IC_single_AP_3_1_kyn_ptx'])
vgat_kynac_ptx_sample_cell_spikes = np.array(vgat_kyn_ptx_single_AP.cut_spikes_traces_mV.loc['dmpag_vgat_181211_c4_WDIAQ_OP_IC_single_AP_3_1_kyn_ptx'])
vgat_kynac_ptx_sample_cell_threshold_index = vgat_kyn_ptx_single_AP.avg_spike_threshold_index.loc['dmpag_vgat_181211_c4_WDIAQ_OP_IC_single_AP_3_1_kyn_ptx']
vgat_kynac_ptx_sample_cell_threshold_mV = np.round(vgat_kyn_ptx_single_AP.avg_spike_threshold_mV.loc['dmpag_vgat_181211_c4_WDIAQ_OP_IC_single_AP_3_1_kyn_ptx'], 2)
vgat_kynac_ptx_sample_cell_dvdt = np.array(vgat_kyn_ptx_single_AP.dvdt_trace.loc['dmpag_vgat_181211_c4_WDIAQ_OP_IC_single_AP_3_1_kyn_ptx'])

# Plot protocol and cell's voltage response
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)
# Plot individual baselined sweeps
for sweep in range(len(vgat_kynac_ptx_sample_cell_spikes)):
    axs['A'].plot(vgat_kynac_ptx_sample_cell_spikes[sweep], color = colour_vgat_kynac_ptx)
# Plot average sweep
axs['A'].plot(vgat_kynac_ptx_sample_cell_avg_spike, color = 'k')
# Plot average spike threshold
axs['A'].plot(vgat_kynac_ptx_sample_cell_threshold_index, vgat_kynac_ptx_sample_cell_avg_spike[vgat_kynac_ptx_sample_cell_threshold_index], "or")
axs['A'].set_title('VGAT in kynac_ptx: dmpag_vgat_181211_c4_WDIAQ', fontsize = 14)
axs['A'].text(2325, 20, f'AP threshold: {vgat_kynac_ptx_sample_cell_threshold_mV} mV', fontsize = 11)
axs['A'].set_xlabel('samples', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([2200, 2400])
axs['A'].set_ylim([-80, 40])
# Phase plot
axs['B'].plot(vgat_kynac_ptx_sample_cell_avg_spike[1:], vgat_kynac_ptx_sample_cell_dvdt, color = colour_vgat_kynac_ptx)
axs['B'].set_title('Phase plot', fontsize = 14)
axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
axs['B'].set_xlim([-100, 100])
axs['B'].set_ylim([-500, 600])
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_singleAP, 'vgat_kynac_ptx_single_AP_WDIAQ.eps'), format = 'eps') # save figure as .eps

# %%
## Potential vglut2_ctrl sample traces 
# dlpag_vglut2_200722_c3_WEAL_OP_IC_single_AP_4_4

# Select vglut2_ctrl sample cell
vglut2_ctrl_sample_cell_avg_spike = np.array(vglut2_control_single_AP.avg_spike_trace_mV.loc['dlpag_vglut2_200722_c3_WEAL_OP_IC_single_AP_4_4'])
vglut2_ctrl_sample_cell_spikes = np.array(vglut2_control_single_AP.cut_spikes_traces_mV.loc['dlpag_vglut2_200722_c3_WEAL_OP_IC_single_AP_4_4'])
vglut2_ctrl_sample_cell_threshold_index = vglut2_control_single_AP.avg_spike_threshold_index.loc['dlpag_vglut2_200722_c3_WEAL_OP_IC_single_AP_4_4']
vglut2_ctrl_sample_cell_threshold_mV = np.round(vglut2_control_single_AP.avg_spike_threshold_mV.loc['dlpag_vglut2_200722_c3_WEAL_OP_IC_single_AP_4_4'], 2)
vglut2_ctrl_sample_cell_dvdt = np.array(vglut2_control_single_AP.dvdt_trace.loc['dlpag_vglut2_200722_c3_WEAL_OP_IC_single_AP_4_4'])

# Plot protocol and cell's voltage response
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)
# Plot individual baselined sweeps
for sweep in range(len(vglut2_ctrl_sample_cell_spikes)):
    axs['A'].plot(vglut2_ctrl_sample_cell_spikes[sweep], color = colour_vglut2_ctrl)
# Plot average sweep
axs['A'].plot(vglut2_ctrl_sample_cell_avg_spike, color = 'k')
# Plot average spike threshold
axs['A'].plot(vglut2_ctrl_sample_cell_threshold_index, vglut2_ctrl_sample_cell_avg_spike[vglut2_ctrl_sample_cell_threshold_index], "or")
axs['A'].set_title('VGluT2 control: dlpag_vglut2_200722_c3_WEAL', fontsize = 14)
axs['A'].text(2325, 20, f'AP threshold: {vglut2_ctrl_sample_cell_threshold_mV} mV', fontsize = 11)
axs['A'].set_xlabel('samples', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([2200, 2400])
axs['A'].set_ylim([-80, 40])
# Phase plot
axs['B'].plot(vglut2_ctrl_sample_cell_avg_spike[1:], vglut2_ctrl_sample_cell_dvdt, color = colour_vglut2_ctrl)
axs['B'].set_title('Phase plot', fontsize = 14)
axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
axs['B'].set_xlim([-100, 100])
axs['B'].set_ylim([-500, 600])
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_singleAP, 'vglut2_ctrl_single_AP_WEAL.eps'), format = 'eps') # save figure as .eps

# %%
## Potential vglut2_kynac_ptx sample traces 
# dmpag_vglut2_180504_c3_WDEAG_OP_IC_single_AP_1_1_kyn_ptx

# Select vglut2_kynac_ptx sample cell
vglut2_kynac_ptx_sample_cell_avg_spike = np.array(vglut2_kyn_ptx_single_AP.avg_spike_trace_mV.loc['dmpag_vglut2_180504_c3_WDEAG_OP_IC_single_AP_1_1_kyn_ptx'])
vglut2_kynac_ptx_sample_cell_spikes = np.array(vglut2_kyn_ptx_single_AP.cut_spikes_traces_mV.loc['dmpag_vglut2_180504_c3_WDEAG_OP_IC_single_AP_1_1_kyn_ptx'])
vglut2_kynac_ptx_sample_cell_threshold_index = vglut2_kyn_ptx_single_AP.avg_spike_threshold_index.loc['dmpag_vglut2_180504_c3_WDEAG_OP_IC_single_AP_1_1_kyn_ptx']
vglut2_kynac_ptx_sample_cell_threshold_mV = np.round(vglut2_kyn_ptx_single_AP.avg_spike_threshold_mV.loc['dmpag_vglut2_180504_c3_WDEAG_OP_IC_single_AP_1_1_kyn_ptx'], 2)
vglut2_kynac_ptx_sample_cell_dvdt = np.array(vglut2_kyn_ptx_single_AP.dvdt_trace.loc['dmpag_vglut2_180504_c3_WDEAG_OP_IC_single_AP_1_1_kyn_ptx'])

# Plot protocol and cell's voltage response
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)
# Plot individual baselined sweeps
for sweep in range(len(vglut2_kynac_ptx_sample_cell_spikes)):
    axs['A'].plot(vglut2_kynac_ptx_sample_cell_spikes[sweep], color = colour_vglut2_kynac_ptx)
# Plot average sweep
axs['A'].plot(vglut2_kynac_ptx_sample_cell_avg_spike, color = 'k')
# Plot average spike threshold
axs['A'].plot(vglut2_kynac_ptx_sample_cell_threshold_index, vglut2_kynac_ptx_sample_cell_avg_spike[vglut2_kynac_ptx_sample_cell_threshold_index], "or")
axs['A'].set_title('VGluT2 in kynac_ptx: dmpag_vglut2_180504_c3_WDEAG', fontsize = 14)
axs['A'].text(2325, 20, f'AP threshold: {vglut2_kynac_ptx_sample_cell_threshold_mV} mV', fontsize = 11)
axs['A'].set_xlabel('samples', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([2200, 2400])
axs['A'].set_ylim([-80, 40])
# Phase plot
axs['B'].plot(vglut2_kynac_ptx_sample_cell_avg_spike[1:], vglut2_kynac_ptx_sample_cell_dvdt, color = colour_vglut2_kynac_ptx)
axs['B'].set_title('Phase plot', fontsize = 14)
axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
axs['B'].set_xlim([-100, 100])
axs['B'].set_ylim([-500, 600])
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_singleAP, 'vglut2_kynac_ptx_single_AP_WDEAG.eps'), format = 'eps') # save figure as .eps

# %%
# Plot all the sample traces together
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)
# Plot individual baselined sweeps
for sweep in range(len(vgat_ctrl_sample_cell_spikes)):
    axs['A'].plot(vgat_ctrl_sample_cell_spikes[sweep], color = colour_vgat_ctrl)
# Plot average sweep
axs['A'].plot(vgat_ctrl_sample_cell_avg_spike, color = 'k')
# Plot average spike threshold
axs['A'].plot(vgat_ctrl_sample_cell_threshold_index, vgat_ctrl_sample_cell_avg_spike[vgat_ctrl_sample_cell_threshold_index], "or")
# Plot individual baselined sweeps
for sweep in range(len(vgat_kynac_ptx_sample_cell_spikes)):
    axs['A'].plot(vgat_kynac_ptx_sample_cell_spikes[sweep], color = colour_vgat_kynac_ptx)
# Plot average sweep
axs['A'].plot(vgat_kynac_ptx_sample_cell_avg_spike, color = 'k')
# Plot average spike threshold
axs['A'].plot(vgat_kynac_ptx_sample_cell_threshold_index, vgat_kynac_ptx_sample_cell_avg_spike[vgat_kynac_ptx_sample_cell_threshold_index], "or")
# Plot individual baselined sweeps
for sweep in range(len(vglut2_ctrl_sample_cell_spikes)):
    axs['A'].plot(vglut2_ctrl_sample_cell_spikes[sweep], color = colour_vglut2_ctrl)
# Plot average sweep
axs['A'].plot(vglut2_ctrl_sample_cell_avg_spike, color = 'k')
# Plot average spike threshold
axs['A'].plot(vglut2_ctrl_sample_cell_threshold_index, vglut2_ctrl_sample_cell_avg_spike[vglut2_ctrl_sample_cell_threshold_index], "or")
# Plot individual baselined sweeps
for sweep in range(len(vglut2_kynac_ptx_sample_cell_spikes)):
    axs['A'].plot(vglut2_kynac_ptx_sample_cell_spikes[sweep], color = colour_vglut2_kynac_ptx)
# Plot average sweep
axs['A'].plot(vglut2_kynac_ptx_sample_cell_avg_spike, color = 'k')
# Plot average spike threshold
axs['A'].plot(vglut2_kynac_ptx_sample_cell_threshold_index, vglut2_kynac_ptx_sample_cell_avg_spike[vglut2_kynac_ptx_sample_cell_threshold_index], "or")
axs['A'].set_title('Action potential trace', fontsize = 14)
axs['A'].set_xlabel('samples', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([2200, 2300])
axs['A'].set_ylim([-80, 40])
# Phase plot
axs['B'].plot(vgat_ctrl_sample_cell_avg_spike[1:], vgat_ctrl_sample_cell_dvdt, color = colour_vgat_ctrl)
axs['B'].plot(vglut2_ctrl_sample_cell_avg_spike[1:], vglut2_ctrl_sample_cell_dvdt, color = colour_vglut2_ctrl)
axs['B'].plot(vgat_kynac_ptx_sample_cell_avg_spike[1:], vgat_kynac_ptx_sample_cell_dvdt, color = colour_vgat_kynac_ptx)
axs['B'].plot(vglut2_kynac_ptx_sample_cell_avg_spike[1:], vglut2_kynac_ptx_sample_cell_dvdt, color = colour_vglut2_kynac_ptx)
axs['B'].set_title('Phase plot', fontsize = 14)
axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
axs['B'].set_xlim([-100, 100])
axs['B'].set_ylim([-500, 600])
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_singleAP, 'all_cells_single_AP.eps'), format = 'eps') # save figure as .eps


# %% [markdown]
# ### 2.3 | Plot all average Action Potential sample traces for each condition

# # %%
# # Select vgat_ctrl recordings
# vgat_ctrl_all_cells_avg_spike = vgat_control_single_AP.avg_spike_trace_mV
# vgat_ctrl_all_cells_dvdt = vgat_control_single_AP.dvdt_trace

# # Plot protocol and cell's voltage response
# get_ipython().run_line_magic('matplotlib', 'qt')
# fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
# axs = fig.subplot_mosaic(
#     """
#     AA
#     BB
#     """
# )
# # Plot the average spike trace of each recorded cell
# for cell in range(len(vgat_ctrl_all_cells_avg_spike)):
#     axs['A'].plot(vgat_ctrl_all_cells_avg_spike[cell], color = colour_vgat_ctrl)
# axs['A'].set_title('VGAT control', fontsize = 14)
# axs['A'].set_xlabel('samples', fontsize = 12)
# axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
# axs['A'].set_xlim([2200, 4000])
# axs['A'].set_ylim([-90, 60])
# # Phase plot of each recorded cell
# for cell in range(len(vgat_ctrl_all_cells_avg_spike)):
#     axs['B'].plot(vgat_ctrl_all_cells_avg_spike[cell][1:], vgat_ctrl_all_cells_dvdt[cell], color = colour_vgat_ctrl)
# axs['B'].set_title('Phase plot', fontsize = 14)
# axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
# axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
# axs['B'].set_xlim([-100, 100])
# axs['B'].set_ylim([-700, 700])
# fig.canvas.manager.window.move(0, 0)
# plt.show()
# #plt.savefig(os.path.join(folder_sample_traces_singleAP, 'vgat_ctrl_slow_AHP.eps'), format = 'eps') # save figure as .eps

# # %%
# # Select vgat_kynac_ptx recordings
# vgat_kynac_ptx_all_cells_avg_spike = vgat_kyn_ptx_single_AP.avg_spike_trace_mV
# vgat_kynac_ptx_all_cells_dvdt = vgat_kyn_ptx_single_AP.dvdt_trace

# # Plot protocol and cell's voltage response
# get_ipython().run_line_magic('matplotlib', 'qt')
# fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
# axs = fig.subplot_mosaic(
#     """
#     AA
#     BB
#     """
# )
# # Plot the average spike trace of each recorded cell
# for cell in range(len(vgat_kynac_ptx_all_cells_avg_spike)):
#     axs['A'].plot(vgat_kynac_ptx_all_cells_avg_spike[cell], color = colour_vgat_kynac_ptx)
# axs['A'].set_title('VGAT in kynac_ptx', fontsize = 14)
# axs['A'].set_xlabel('samples', fontsize = 12)
# axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
# axs['A'].set_xlim([2200, 4000])
# axs['A'].set_ylim([-90, 60])
# # Phase plot of each recorded cell
# for cell in range(len(vgat_kynac_ptx_all_cells_avg_spike)):
#     axs['B'].plot(vgat_kynac_ptx_all_cells_avg_spike[cell][1:], vgat_kynac_ptx_all_cells_dvdt[cell], color = colour_vgat_kynac_ptx)
# axs['B'].set_title('Phase plot', fontsize = 14)
# axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
# axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
# axs['B'].set_xlim([-100, 100])
# axs['B'].set_ylim([-700, 700])
# fig.canvas.manager.window.move(0, 0)
# plt.show()
# #plt.savefig(os.path.join(folder_sample_traces_singleAP, 'vgat_kynac_ptx_slow_AHP.eps'), format = 'eps') # save figure as .eps

# # %%
# # Select vglut2_ctrl recordings
# vglut2_ctrl_all_cells_avg_spike = vglut2_control_single_AP.avg_spike_trace_mV
# vglut2_ctrl_all_cells_dvdt = vglut2_control_single_AP.dvdt_trace

# # Plot protocol and cell's voltage response
# get_ipython().run_line_magic('matplotlib', 'qt')
# fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
# axs = fig.subplot_mosaic(
#     """
#     AA
#     BB
#     """
# )
# # Plot the average spike trace of each recorded cell
# for cell in range(len(vglut2_ctrl_all_cells_avg_spike)):
#     axs['A'].plot(vglut2_ctrl_all_cells_avg_spike[cell], color = colour_vglut2_ctrl)
# axs['A'].set_title('\nVGluT2 control: dlpag_vglut2_200722_c3_WEAL\n', fontsize = 14)
# axs['A'].set_xlabel('samples', fontsize = 12)
# axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
# axs['A'].set_xlim([2200, 4000])
# axs['A'].set_ylim([-90, 60])
# # Phase plot of each recorded cell
# for cell in range(len(vglut2_ctrl_all_cells_avg_spike)):
#     axs['B'].plot(vglut2_ctrl_all_cells_avg_spike[cell][1:], vglut2_ctrl_all_cells_dvdt[cell], color = colour_vglut2_ctrl)
# axs['B'].set_title('Phase plot', fontsize = 14)
# axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
# axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
# axs['B'].set_xlim([-100, 100])
# axs['B'].set_ylim([-700, 700])
# fig.canvas.manager.window.move(0, 0)
# plt.show()
# #plt.savefig(os.path.join(folder_sample_traces_singleAP, 'vglut2_ctrl_slow_AHP.eps'), format = 'eps') # save figure as .eps

# # %%
# # Select vglut2_ctrl recordings
# vglut2_kynac_ptx_all_cells_avg_spike = vglut2_kyn_ptx_single_AP.avg_spike_trace_mV
# vglut2_kynac_ptx_all_cells_dvdt = vglut2_kyn_ptx_single_AP.dvdt_trace

# # Plot protocol and cell's voltage response
# get_ipython().run_line_magic('matplotlib', 'qt')
# fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
# axs = fig.subplot_mosaic(
#     """
#     AA
#     BB
#     """
# )
# # Plot the average spike trace of each recorded cell
# for cell in range(len(vglut2_kynac_ptx_all_cells_avg_spike)):
#     axs['A'].plot(vglut2_kynac_ptx_all_cells_avg_spike[cell], color = colour_vglut2_kynac_ptx)
# axs['A'].set_title('VGluT2 in kynac_ptx', fontsize = 14)
# axs['A'].set_xlabel('samples', fontsize = 12)
# axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
# axs['A'].set_xlim([2200, 4000])
# axs['A'].set_ylim([-90, 60])
# # Phase plot of each recorded cell
# for cell in range(len(vglut2_kynac_ptx_all_cells_avg_spike)):
#     axs['B'].plot(vglut2_kynac_ptx_all_cells_avg_spike[cell][1:], vglut2_kynac_ptx_all_cells_dvdt[cell], color = colour_vglut2_kynac_ptx)
# axs['B'].set_title('Phase plot', fontsize = 14)
# axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
# axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
# axs['B'].set_xlim([-100, 100])
# axs['B'].set_ylim([-700, 700])
# fig.canvas.manager.window.move(0, 0)
# plt.show()
# #plt.savefig(os.path.join(folder_sample_traces_singleAP, 'vglut2_kyn_ptx_slow_AHP.eps'), format = 'eps') # save figure as .eps

# %% [markdown]
# ### 2.4 | Plot example Action Potential sample traces with and without slow AHP

# %%
## Potential vgat_ctrl sample traces with slow AHP
# dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5 (-2.57 mV)

# Select vgat_ctrl sample cell
vgat_ctrl_sample_cell_avg_spike = np.array(vgat_control_single_AP.avg_spike_trace_mV.loc['dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5'])
vgat_ctrl_sample_cell_spikes = np.array(vgat_control_single_AP.cut_spikes_traces_mV.loc['dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5'])
vgat_ctrl_sample_cell_adp_index = vgat_control_single_AP.avg_spike_adp_index.loc['dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5']
vgat_ctrl_sample_cell_ahp_index = vgat_control_single_AP.avg_spike_ahp_index.loc['dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5']
vgat_ctrl_sample_cell_adp_to_ahp_mV = np.round(vgat_control_single_AP.adp_to_ahp_mV.loc['dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5'], 2)
vgat_ctrl_sample_cell_dvdt = np.array(vgat_control_single_AP.dvdt_trace.loc['dlpag_vgat_200922_c1_WIAT_OP_IC_single_AP_4_5'])

# Plot protocol and cell's voltage response
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)
# Plot individual baselined sweeps
for sweep in range(len(vgat_ctrl_sample_cell_spikes)):
    axs['A'].plot(vgat_ctrl_sample_cell_spikes[sweep], color = colour_vgat_ctrl)
# Plot average sweep
axs['A'].plot(vgat_ctrl_sample_cell_avg_spike, color = 'k')
# Plot average spike slow AHP
axs['A'].plot(vgat_ctrl_sample_cell_adp_index, vgat_ctrl_sample_cell_avg_spike[vgat_ctrl_sample_cell_adp_index], "or")
axs['A'].plot(vgat_ctrl_sample_cell_ahp_index, vgat_ctrl_sample_cell_avg_spike[vgat_ctrl_sample_cell_ahp_index], "or")
axs['A'].set_title('VGAT with slow AHP: dlpag_vgat_200922_c1_WIAT', fontsize = 14)
axs['A'].text(4000, -75, f'slow AHP: {vgat_ctrl_sample_cell_adp_to_ahp_mV} mV', fontsize = 11)
axs['A'].set_xlabel('samples', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([2200, 5000])
axs['A'].set_ylim([-80, -40])
# Repeat plot zooming in the Y axis
# Plot individual baselined sweeps
for sweep in range(len(vgat_ctrl_sample_cell_spikes)):
    axs['B'].plot(vgat_ctrl_sample_cell_spikes[sweep], color = colour_vgat_ctrl)
# Plot average sweep
axs['B'].plot(vgat_ctrl_sample_cell_avg_spike, color = 'k')
# Plot average spike slow AHP
axs['B'].plot(vgat_ctrl_sample_cell_adp_index, vgat_ctrl_sample_cell_avg_spike[vgat_ctrl_sample_cell_adp_index], "or")
axs['B'].plot(vgat_ctrl_sample_cell_ahp_index, vgat_ctrl_sample_cell_avg_spike[vgat_ctrl_sample_cell_ahp_index], "or")
axs['B'].set_title('VGAT with slow AHP: dlpag_vgat_200922_c1_WIAT', fontsize = 14)
axs['B'].text(4000, 30, f'slow AHP: {vgat_ctrl_sample_cell_adp_to_ahp_mV} mV', fontsize = 11)
axs['B'].set_xlabel('samples', fontsize = 12)
axs['B'].set_ylabel('voltage [mV]', fontsize = 12)
axs['B'].set_xlim([2200, 5000])
axs['B'].set_ylim([-80, 50])
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_singleAP, 'vgat_ctrl_with_slow_AHP_WIAT.eps'), format = 'eps') # save figure as .eps

# %%
## Potential vgat_ctrl sample traces without slow AHP
# dmpag_vgat_201217_c3_WDIBM_OP_IC_single_AP_5_4 (-0.12 mV)

# Select vgat_ctrl sample cell
vgat_ctrl_sample_cell_avg_spike = np.array(vgat_control_single_AP.avg_spike_trace_mV.loc['dmpag_vgat_201217_c3_WDIBM_OP_IC_single_AP_5_4'])
vgat_ctrl_sample_cell_spikes = np.array(vgat_control_single_AP.cut_spikes_traces_mV.loc['dmpag_vgat_201217_c3_WDIBM_OP_IC_single_AP_5_4'])
vgat_ctrl_sample_cell_adp_index = vgat_control_single_AP.avg_spike_adp_index.loc['dmpag_vgat_201217_c3_WDIBM_OP_IC_single_AP_5_4']
vgat_ctrl_sample_cell_ahp_index = vgat_control_single_AP.avg_spike_ahp_index.loc['dmpag_vgat_201217_c3_WDIBM_OP_IC_single_AP_5_4']
vgat_ctrl_sample_cell_adp_to_ahp_mV = np.round(vgat_control_single_AP.adp_to_ahp_mV.loc['dmpag_vgat_201217_c3_WDIBM_OP_IC_single_AP_5_4'], 2)
vgat_ctrl_sample_cell_dvdt = np.array(vgat_control_single_AP.dvdt_trace.loc['dmpag_vgat_201217_c3_WDIBM_OP_IC_single_AP_5_4'])

# Plot protocol and cell's voltage response
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)
# Plot individual baselined sweeps
for sweep in range(len(vgat_ctrl_sample_cell_spikes)):
    axs['A'].plot(vgat_ctrl_sample_cell_spikes[sweep], color = colour_vgat_ctrl)
# Plot average sweep
axs['A'].plot(vgat_ctrl_sample_cell_avg_spike, color = 'k')
# Plot average spike slow AHP
axs['A'].plot(vgat_ctrl_sample_cell_adp_index, vgat_ctrl_sample_cell_avg_spike[vgat_ctrl_sample_cell_adp_index], "or")
axs['A'].plot(vgat_ctrl_sample_cell_ahp_index, vgat_ctrl_sample_cell_avg_spike[vgat_ctrl_sample_cell_ahp_index], "or")
axs['A'].set_title('VGAT without slow AHP: dmpag_vgat_201217_c3_WDIBM', fontsize = 14)
axs['A'].text(4000, -75, f'slow AHP: {vgat_ctrl_sample_cell_adp_to_ahp_mV} mV', fontsize = 11)
axs['A'].set_xlabel('samples', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([2200, 5000])
axs['A'].set_ylim([-80, -40])
# Repeat plot zooming in the Y axis
# Plot individual baselined sweeps
for sweep in range(len(vgat_ctrl_sample_cell_spikes)):
    axs['B'].plot(vgat_ctrl_sample_cell_spikes[sweep], color = colour_vgat_ctrl)
# Plot average sweep
axs['B'].plot(vgat_ctrl_sample_cell_avg_spike, color = 'k')
# Plot average spike slow AHP
axs['B'].plot(vgat_ctrl_sample_cell_adp_index, vgat_ctrl_sample_cell_avg_spike[vgat_ctrl_sample_cell_adp_index], "or")
axs['B'].plot(vgat_ctrl_sample_cell_ahp_index, vgat_ctrl_sample_cell_avg_spike[vgat_ctrl_sample_cell_ahp_index], "or")
axs['B'].set_title('VGAT without slow AHP: dmpag_vgat_201217_c3_WDIBM', fontsize = 14)
axs['B'].text(4000, 30, f'slow AHP: {vgat_ctrl_sample_cell_adp_to_ahp_mV} mV', fontsize = 11)
axs['B'].set_xlabel('samples', fontsize = 12)
axs['B'].set_ylabel('voltage [mV]', fontsize = 12)
axs['B'].set_xlim([2200, 5000])
axs['B'].set_ylim([-80, 50])
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_singleAP, 'vgat_ctrl_without_slow_AHP_WDIBM.eps'), format = 'eps') # save figure as .eps

# %%
# Quickly visualise the relationship between AP threshold, half-width, and slow AHP
# vgat_control_single_AP.avg_spike_threshold_mV
# vgat_control_single_AP.half_width_ms
# vgat_control_single_AP.adp_to_ahp_mV

get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AB
    CD
    """
)
axs['A'].scatter(x = vgat_control_single_AP.half_width_ms,
                    y = vgat_control_single_AP.adp_to_ahp_mV)
axs['A'].set_title('VGAT control')
axs['A'].set_xlabel('half-width [ms]')
axs['A'].set_ylabel('slow AHP [mV]')
axs['B'].scatter(x = vgat_kyn_ptx_single_AP.half_width_ms,
                    y = vgat_kyn_ptx_single_AP.adp_to_ahp_mV)
axs['B'].set_title('VGAT in kynac_ptx')
axs['B'].set_xlabel('half-width [ms]')
axs['B'].set_ylabel('slow AHP [mV]')
axs['C'].scatter(x = vglut2_control_single_AP.half_width_ms,
                    y = vglut2_control_single_AP.adp_to_ahp_mV)
axs['C'].set_title('VGluT2 control')
axs['C'].set_xlabel('half-width [ms]')
axs['C'].set_ylabel('slow AHP [mV]')
axs['D'].scatter(x = vglut2_kyn_ptx_single_AP.half_width_ms,
                    y = vglut2_kyn_ptx_single_AP.adp_to_ahp_mV)
axs['D'].set_title('VGluT2 in kynac_ptx')
axs['D'].set_xlabel('half-width [ms]')
axs['D'].set_ylabel('slow AHP [mV]')
fig.canvas.manager.window.move(0, 0)
plt.show()

# %%
