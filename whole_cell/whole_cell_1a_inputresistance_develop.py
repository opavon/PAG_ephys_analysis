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
from whole_cell_utilities import * # includes functions importFile, openFile, openHDF5file
print("done!")

# %%
# Load data
channels_df, time, dt, folder_name, file_name = importFile(curated_channel = None)
print("file imported")

# %%
# Extract data and plot
sweep_IA = np.array(channels_df.loc['Channel A', :])
sweep_OA = np.array(channels_df.loc['Output A', :])

# Get color palette and generate one color for each sweep
import matplotlib.cm as cm
sweep_colors = cm.viridis(np.linspace(0, 1, len(sweep_IA)))

get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (10, 5), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)

for sweep in range(len(sweep_IA)):
        axs['A'].plot(sweep_IA[sweep], color = sweep_colors[sweep])
axs['A'].set_title('Channel A', fontsize = 12)
axs['A'].set_ylabel('current [pA]')

for sweep in range(len(sweep_OA)):
        axs['B'].plot(sweep_OA[sweep], color = sweep_colors[sweep])
axs['B'].set_title('Output A', fontsize = 12)
axs['B'].set_ylabel('Voltage [mV]')

fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
plt.show()

# %%
# Initialize variables to build results dataframe:
test_pulse_command = []
test_pulse_membrane = []
input_resistance = []
holding_mV = []
trial_keys = []

for sweep in channels_df.columns:
    ## Load data: Output B (command) and Channel A (recording in Current Clamp)
    sweep_IA = np.array(channels_df.at['Channel A', sweep])
    # sweep_IB = np.array(channels_df.at['Channel B', sweep]) # Not needed as we record in Current Clamp
    sweep_OA = np.array(channels_df.at['Output A', sweep])

    ## Get the indices corresponding to the test_pulse using the Output Channel
    test_pulse = np.where(sweep_OA < 0)
    test_pulse_OA_indices = test_pulse[0]

    ## Get test_pulse magnitude
    # Use the indices of the test_pulse command (Output B) to define baseline period and test period
    sweep_OA_baseline = np.mean(sweep_OA[:(test_pulse_OA_indices[0]-1)]) # -1 to stop baseline before command starts
    sweep_OA_pulse = np.mean(sweep_OA[test_pulse_OA_indices])
    tp_command = sweep_OA_pulse - sweep_OA_baseline # pA

    ## Get cell response to test_pulse:
    # Use the test_pulse indices to get the baseline and cell response to calculate the input resistance
    # To be exact and account for the delays between digital command and output from the amplifier, you could add +1 to the first index to calculate the baseline.
    sweep_IA_baseline = np.mean(sweep_IA[:(test_pulse_OA_indices[0])])
    # To ensure we evaluate the epoch where the cell response has reached steady state, we average the values corresponding to the second half of the pulse.
    sweep_IA_pulse = np.mean(sweep_IA[(round(len(test_pulse_OA_indices)/2)):(test_pulse_OA_indices[-1])])
    tp_membrane = sweep_IA_pulse - sweep_IA_baseline # mV


    ## Get input resistance = mV/pA
    InputR = (tp_membrane / tp_command) * 1000 # to get MOhm
    # Append results
    test_pulse_command.append(tp_command)
    test_pulse_membrane.append(tp_membrane)
    holding_mV.append(sweep_IA_baseline)
    input_resistance.append(InputR)

    ## Get trial name for results dataframe
    trial_keys.append(sweep)

# %%
# Create dataframe of data:
InputR_dataframe = pd.DataFrame([test_pulse_command, test_pulse_membrane, holding_mV, input_resistance], index = ['test_pulse_command_pA', 'test_pulse_membrane_mV', 'holding_mV', 'input_resistance_MOhm'], columns = trial_keys)
InputR_dataframe

# %%
# Plot InputR across sweeps
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
plt.plot(InputR_dataframe.loc['input_resistance_MOhm'], 'k')
plt.title('Input Resistance across sweeps', fontsize = 14)
plt.xlabel('sweep number', fontsize = 12)
plt.ylabel('Input Resistance [MOhm]', fontsize = 12)
plt.axis([-1, len(InputR_dataframe.loc['input_resistance_MOhm']), 0, round(np.mean(InputR_dataframe.loc['input_resistance_MOhm'])*2)])
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
plt.show()
# %%
