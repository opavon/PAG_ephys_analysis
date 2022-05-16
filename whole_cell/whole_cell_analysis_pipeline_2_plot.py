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
# ### 1.2 | Plot sample traces for each conditions

# %%
# Once we have loaded the data, we can plot the average traces across conditions and export them for making figures.


# %%
# Load data
channels_df, time, dt, folder_name, file_name = importFile(curated_channel = 'Sweeps_Analysis')
print("file imported")

InputR_df, InputR_avg_df = getCellInputResistance(file_name, channels_df)
InputR_avg_df

# %%
## Potential vgat_ctrl sample traces
# dmpag_vgat_170222_c3_OP_IC_tau_inputresistance_2_1 (no)
# dmpag_vgat_201217_c3_WDIBM_OP_IC_tau_inputresistance_3_2 (no)
# dmpag_vgat_201217_c5_WDIBO_OP_IC_tau_inputresistance_3_1 (yes)

## Potential vgat_kynac_ptx sample traces
# dmpag_vgat_180507_c6_WDIAF_OP_IC_tau_inputresistance_1_1_kyn_ptx (no)
# dmpag_vgat_201218_c5_WDIBT_OP_IC_tau_inputresistance_3_2_kyn_ptx (yes)
# dmpag_vgat_181210_c6_WDIAL_OP_IC_tau_inputresistance_2_1_kyn_ptx (no)

## Potential vglut2_ctrl sample traces 
# dlpag_vglut2_200722_c3_WEAL_OP_IC_tau_inputresistance_2_1 (yes)
# dmpag_vglut2_200722_c7_WDEAT_OP_IC_tau_inputresistance_4_1
# dmpag_vglut2_200711_c2_WEAF_OP_IC_tau_inputresistance_3_2


## Potential vglut2_kynac_ptx sample traces 
# dmpag_vglut2_180504_c2_WDEAF_OP_IC_tau_inputresistance_1_1_kyn_ptx (no)
# dlpag_vglut2_180504_c4_WDEAH_OP_IC_tau_inputresistance_1_1_kyn_ptx (maybe)
# dmpag_vglut2_180503_c2_WDEAB_OP_IC_tau_inputresistance_1_1_kyn_ptx (yes)


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
vgat_ctrl_sample_cell = 'dlpag_vglut2_180504_c4_WDEAH_OP_IC_tau_inputresistance_1_1_kyn_ptx.hdf5'

test_pulse_membrane_baselined, test_pulse_command_baselined, avg_test_pulse_membrane_baselined, avg_test_pulse_command_baselined, time, dt = getSampleTracesIR(folder_sample_traces_IR, vgat_ctrl_sample_cell, curated_channel)

# channels_dataframe, time, dt = openFile(os.path.join(folder_sample_traces_IR, 'dlpag_vglut2_180504_c4_WDEAH_OP_IC_tau_inputresistance_1_1_kyn_ptx.hdf5'), curated_channel = 'Sweeps_Analysis') # extract channels from current file

# test_pulse_command_baselined = []
# test_pulse_membrane_baselined = []

# # Calculate the input resistance on a sweep-by-sweep basis:
# for sweep in channels_dataframe.columns:
#     ## Load sweep data: Channel A (voltage recording in current-clamp), Channel B (injected current) and Output B (command)
#     sweep_IA = np.array(channels_dataframe.at['Channel A', sweep]) # voltage
#     sweep_OA = np.array(channels_dataframe.at['Output A', sweep]) # command

#     ## Get the indices corresponding to the test_pulse using the Output Channel
#     test_pulse = np.where(sweep_OA < 0)
#     test_pulse_OA_indices = test_pulse[0]

#     sweep_OA_baseline = np.mean(sweep_OA[:(test_pulse_OA_indices[0]-1)]) # -1 to stop baseline before command starts
#     sweep_IA_baseline = np.mean(sweep_IA[:(test_pulse_OA_indices[0])])

#     ## Baseline sweeps
#     baselined_sweep_OA = sweep_OA - sweep_OA_baseline
#     baselined_sweep_IA = sweep_IA - sweep_IA_baseline
#     # Append results
#     test_pulse_command_baselined.append(baselined_sweep_OA)
#     test_pulse_membrane_baselined.append(baselined_sweep_IA)

# # Compute average trace from all baselined sweeps
# avg_test_pulse_command_baselined = np.array(np.mean(test_pulse_command_baselined, 0))
# avg_test_pulse_membrane_baselined = np.array(np.mean(test_pulse_membrane_baselined, 0))

# Plot
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)
# Plot protocol and cell's voltage response
for sweep in range(len(test_pulse_membrane_baselined)):
    axs['A'].plot(time[0], test_pulse_membrane_baselined[sweep], color = colour_vgat_ctrl)
axs['A'].plot(time[0], avg_test_pulse_membrane_baselined, color = 'k')
axs['A'].set_title('dlpag_vglut2_180504_c4_WDEAH', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]', fontsize = 10)
axs['A'].set_xlim([0, (len(avg_test_pulse_membrane_baselined)*dt)])
axs['B'].plot(time[0][0:len(avg_test_pulse_command_baselined)], avg_test_pulse_command_baselined, color = 'k')
axs['B'].set_title('Command', fontsize = 12)
axs['B'].set_ylabel('current [pA]', fontsize = 10)
axs['B'].set_xlim([0, (len(avg_test_pulse_membrane_baselined)*dt)])


# %%


vgat_control_IR
vgat_kyn_ptx_IR
vglut2_control_IR
vglut2_kyn_ptx_IR
vgat_control_IR['membrane_avg_trace_mV']
#vgat_ctrl_average_IR

# %%
# Plot vgat_ctrl example cell
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
for s in range(len(vgat_control_IR['membrane_avg_trace_mV'])):
    plt.plot(vgat_control_IR['membrane_avg_trace_mV'][s], colour_vgat_ctrl)
# plt.plot(vgat_ctrl_average_IR, color = 'k')
plt.title('VGAT control', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
# plt.xlim(120, 195) # 25 samples = 1 ms
# plt.ylim(-200, 125) # pA
fig.canvas.manager.window.move(0, 0)
plt.show()
# plt.savefig(os.path.join(folder_sample_traces_IR, 'vgat_ctrl_input_resistance.eps'), format = 'eps') # save figure as .eps

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
