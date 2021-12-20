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
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)

for sweep in range(len(sweep_IA)):
        axs['A'].plot(sweep_IA[sweep], color = sweep_colors[sweep])
axs['A'].set_title('Channel A', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]')
axs['A'].set_xlim([0, (len(sweep_IA[0]))])

for sweep in range(len(sweep_OA)):
        axs['B'].plot(sweep_OA[sweep], color = sweep_colors[sweep])
axs['B'].set_title('Output A', fontsize = 12)
axs['B'].set_ylabel('current [pA]')
axs['B'].set_xlim([0, (len(sweep_IA[0]))])

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
# Create dataframe of data across sweeps:
InputR_dataframe = pd.DataFrame([test_pulse_command, test_pulse_membrane, holding_mV, input_resistance], index = ['test_pulse_command_pA', 'test_pulse_membrane_mV', 'holding_mV', 'input_resistance_MOhm'], columns = trial_keys)
InputR_dataframe

# %%
# Create dataframe of average InputR and cell ID
file_id = [file_name.split('.')[0]] # Get the file name without the extension
cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

InputR_avg = pd.DataFrame([[np.round(np.mean(InputR_dataframe.loc['test_pulse_command_pA']), 2), np.round(np.mean(InputR_dataframe.loc['test_pulse_membrane_mV']), 2), np.round(np.mean(InputR_dataframe.loc['holding_mV']), 2), np.round(np.mean(InputR_dataframe.loc['input_resistance_MOhm']), 2)]], columns =  ['test_pulse_command_pA', 'test_pulse_membrane_mV', 'holding_mV', 'input_resistance_MOhm'], index = cell_id)

InputR_avg

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
# Put into function
def getInputResistance(
    file_name,
    channels_dataframe
    ):
    """
    `getInputResistance` takes the dataframe containing the extracted channel data from a current-clamp recording using the IC_tau_inputresistance protocol and calculates the input resistance (InputR) from the test pulse size and the cell's response to it.
    It returns a dataframe with the InputR value (MOhm) across sweeps for the time of recording (where the columns are sweeps) together with the magnitude of the test_pulse command (pA), the response of the cell (mV), and the holding potential (mV). It also plots the calculated InputR across sweeps and returns a second dataframe with the average values and cell ID.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :channels_dataframe: dataframe with extracted data from a whole-cell current-clamp recording (e.g. several repetitions of a sweep with a hyperpolarising pulse to record the cell's response).
    """

    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id

    # Initialize variables to build results dataframe:
    test_pulse_command = []
    test_pulse_membrane = []
    input_resistance = []
    holding_mV = []
    trial_keys = []

    # Calculate the input resistance on a sweep-by-sweep basis:
    for sweep in channels_df.columns:
        ## Load sweep data: Channel A (recording in current-clamp) and Output B (command)
        sweep_IA = np.array(channels_df.at['Channel A', sweep])
        # sweep_IB = np.array(channels_df.at['Channel B', sweep]) # Not needed as we recorded in current-clamp
        sweep_OA = np.array(channels_df.at['Output A', sweep])

        ## Get the indices corresponding to the test_pulse using the Output Channel
        test_pulse = np.where(sweep_OA < 0)
        test_pulse_OA_indices = test_pulse[0]

        ## Get test_pulse magnitude
        # Use the indices of the test_pulse command (Output A) to define baseline period and test period
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

    # Create dataframe of results across sweeps:
    InputR_dataframe = pd.DataFrame([test_pulse_command, test_pulse_membrane, holding_mV, input_resistance], index = ['test_pulse_command_pA', 'test_pulse_membrane_mV', 'holding_mV', 'input_resistance_MOhm'], columns = trial_keys)
    
    # Create dataframe of average InputR and cell ID
    InputR_avg_dataframe = pd.DataFrame([[np.round(np.mean(InputR_dataframe.loc['test_pulse_command_pA']), 2), np.round(np.mean(InputR_dataframe.loc['test_pulse_membrane_mV']), 2), np.round(np.mean(InputR_dataframe.loc['holding_mV']), 2), np.round(np.mean(InputR_dataframe.loc['input_resistance_MOhm']), 2)]], columns =  ['test_pulse_command_pA', 'test_pulse_membrane_mV', 'holding_mV', 'input_resistance_MOhm'], index = cell_id)


    # Plot recording together with results.
    # Extract full data for plotting purposes (in current-clamp, Channel A is recorded voltage, and Output A is the protocol output)
    all_sweeps_IA = np.array(channels_dataframe.loc['Channel A', :])
    all_sweeps_OA = np.array(channels_dataframe.loc['Output A', :])

    # Get color palette and generate one color for each sweep
    import matplotlib.cm as cm
    sweep_colors = cm.viridis(np.linspace(0, 1, len(all_sweeps_IA)))

    # Generate figure layout
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
    axs = fig.subplot_mosaic(
        """
        AA
        BB
        CC
        """
    )

    # Plot protocol and cell's voltage response
    for sweep in range(len(all_sweeps_IA)):
            axs['A'].plot(all_sweeps_IA[sweep], color = sweep_colors[sweep])
    axs['A'].set_title('Channel A', fontsize = 12)
    axs['A'].set_ylabel('voltage [mV]', fontsize = 10)
    axs['A'].set_xlim([0, (len(all_sweeps_IA[0]))])
    for sweep in range(len(all_sweeps_OA)):
            axs['B'].plot(all_sweeps_OA[sweep], color = sweep_colors[sweep])
    axs['B'].set_title('Output A', fontsize = 12)
    axs['B'].set_ylabel('current [pA]', fontsize = 10)
    axs['B'].set_xlim([0, (len(all_sweeps_IA[0]))])
    
    # Plot InputR across sweeps
    axs['C'].plot(InputR_dataframe.loc['input_resistance_MOhm'], 'k')
    axs['C'].set_title('Input Resistance across sweeps', fontsize = 12)
    axs['C'].set_xlabel('sweep number', fontsize = 10)
    axs['C'].set_ylabel('Input Resistance [MOhm]', fontsize = 10)
    axs['C'].set_xlim([-1, len(InputR_dataframe.loc['input_resistance_MOhm'])])
    axs['C'].set_ylim([0, round(np.max(InputR_dataframe.loc['input_resistance_MOhm'])*2)])

    # Add title
    plt.suptitle(f'Input resistance from {cell_id[0]}', fontsize = 14)

    # Move figure to top left corner
    fig.canvas.manager.window.move(0, 0)
    plt.show(block = True) # Lets you interact with plot and proceeds once figure is closed
    # plt.pause(0.5)
    
    # Check whether you are happy with the recording or whether there is any pre-processing or clean-up left to do
    happy_inputR = input("Are you happy with the result? y/n")
    
    if happy_inputR == 'y':
        print(f"The average input resistance of cell {cell_id[0]} is {np.round(np.mean(InputR_dataframe.loc['input_resistance_MOhm']), 2)} MOhm")
        plt.close()
    else:
        print('Try running getInputResistance() again')
        plt.close()
        return None, None # return empty variables to prevent wrong results from being used

    return InputR_dataframe, InputR_avg_dataframe # pandas dataframe


# %%
# Test function
InputR_df, InputR_avg_df = getInputResistance(file_name, channels_df)
InputR_avg_df

# %%
