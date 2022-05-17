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

# ### 1.1 | Load and summarise data

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

# Select vgat_ctrl sample cell
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

# Select vgat_ctrl sample cell
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
# ## 2.0 | Single Action Potential characterisation

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
