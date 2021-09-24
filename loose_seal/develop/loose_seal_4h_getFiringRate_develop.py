# %% [markdown]
# ## 0 | Import packages and load test data

# %%
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
from utilities import * # includes functions importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes, plotSpikesQC, spikesQC, cleanSpikes, averageSpikes, getSpikeParameters
print("done!")

# %%
# Load data for LIAM cell (contains spikes in test_pulse)
channels_data_frame, time, dt, folder_name, file_name = importFile(curated_channel = 'Sweeps_Analysis')
print("file imported")

# %%
# Get seal resistance
Rseal_data_frame = getLooseRseal(file_name, channels_data_frame)
print("Rseal calculated")

# %%
# Concatenate sweeps
sweep_IB_concatenated, pseudo_sweep_concatenated = concatenateSweeps(channels_data_frame)
print("sweeps concatenated")

# %%
# Find spikes
peaks, peaks_properties, parameters_find_peaks = findSpikes(file_name, sweep_IB_concatenated)

# %%
# Cut spikes
cut_spikes, cut_spikes_holding, cut_spikes_baselined = cutSpikes(sweep_IB_concatenated, peaks)
print("spikes cut")

# %%
# Examine cut spikes for quality check
plotSpikesQC(file_name, peaks_properties, cut_spikes_baselined)

# %%
# Choose the QC metrics and remove detected peaks that correspond to noise and not spikes
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(file_name, peaks, peaks_properties, cut_spikes, cut_spikes_holding, cut_spikes_baselined, filter_by=['ph'], QC_ph_min=10)
parameters_QC

# %%
# Remove the spikes that were incorrectly baselined
cut_spikes_baselined_clean = cleanSpikes(file_name, cut_spikes_baselined_QC)

# %%
# Compute average spike
average_spike = averageSpikes(cut_spikes_baselined_clean)
print("average spike calculated")

# %%
average_spike_parameters = getSpikeParameters(file_name, average_spike, threshold_onset_factor = 0.04, threshold_end_factor = 50)

# %% [markdown]
#########################################################################
# ## 1 | Make a function to extract the firing rate from the detected peaks
# The main parameter we are interested in from our neurons is their firing rate. We could take a look at the following:
# 
#  * Firing rate over full recording
#  * Firing rate over time windows (1s?)
#  * Instantaneous firing rate: inverse of the interspike interval
# 
#########################################################################

# %%
# We start by the basic one: dividing the total number of spikes over the total time of recording. 
n_spikes = len(peaks_QC)
time_recording = len(sweep_IB_concatenated) * dt / 1000 # in seconds
firing_frequency = n_spikes / time_recording # in Hz
neuron_id = '_'.join(file_name.split('_')[0:5])

print(f'Neuron with ID {neuron_id}')
print(f'Detected a total of {n_spikes} spikes')
print(f'Duration of recording was {time_recording} seconds')
print(f'Which gives a firing rate of {round(firing_frequency, 2)} Hz')

# %%
# We can also get the firing rate for each sweep or every second, to get a similar plot obtained with the Rseal, to see how the average firing rate changes over time.
spikes_by_sweep_keys = []
spikes_by_sweep = []
n_spikes_sweep = []
sweep_length = []
sweep_firing_rate = []

for sweep in channels_data_frame.columns: 
    # Take the spikes that belong to the current sweep
    spikes_in_sweep_tmp = np.array([p for i, p in enumerate(peaks_QC) if pseudo_sweep_concatenated[peaks_QC[i]] == int(sweep)])

    #Get firing rate for the current sweep
    sweep_length_s_tmp = len(channels_data_frame.loc['Channel B', sweep]) * dt / 1000 #in seconds
    n_spikes_sweep_tmp = len(spikes_in_sweep_tmp)
    firing_rate_tmp = n_spikes_sweep_tmp / sweep_length_s_tmp

    # Copy results
    spikes_by_sweep_keys.append(int(sweep))
    spikes_by_sweep.append(spikes_in_sweep_tmp)
    n_spikes_sweep.append(n_spikes_sweep_tmp)
    sweep_length.append(sweep_length_s_tmp)
    sweep_firing_rate.append(firing_rate_tmp)

spikes_by_sweep_dataframe = pd.DataFrame([spikes_by_sweep, n_spikes_sweep, sweep_length, sweep_firing_rate], index = ['spikes in sweep', 'number of spikes', 'length of sweep', 'firing rate by sweep'], columns = spikes_by_sweep_keys)

spikes_by_sweep_dataframe

# %%
# Plot firing rate by sweep throughout the recording.
get_ipython().run_line_magic('matplotlib', 'inline')
plt.plot(spikes_by_sweep_keys, sweep_firing_rate, 'k')
plt.title('Figure 2d: Firing rate across sweeps', fontsize = 14)
plt.ylabel('Firing Rate [Hz]')
plt.xlabel('sweep number')
plt.show()

# Check whether firing rate correlates with seal resistance
plt.scatter(Rseal_data_frame.loc['seal_resistance'], sweep_firing_rate)
plt.title('Figure 2d: Firing rate vs Seal Resistance', fontsize = 14)
plt.ylabel('Firing Rate [Hz]')
plt.xlabel('Seal Resistance [MOhm]')
plt.show()
# %%
# Finally, we can get the firing rate for a time window of our choice, to get a similar plot obtained with the Rseal, to see how the average firing rate changes over time.
n_bins = 100
time_window_s = len(pseudo_sweep_concatenated) / 1000 * dt / n_bins # divide the length of recording in 100 chunks (1-2s each)
time_window_samples = len(pseudo_sweep_concatenated) / n_bins
spikes_by_window = []
n_spikes_window = []
window_length = []
window_firing_rate = []

for window in range(n_bins): 
    #if window < n_bins:

    # Take the spikes that belong to the current sweep
    spikes_in_window_tmp = np.array([p for p in peaks_QC if ((time_window_samples*window) < p < (time_window_samples*(window+1)))])

    #Get firing rate for the current sweep
    n_spikes_window_tmp = len(spikes_in_window_tmp)
    firing_rate_tmp = n_spikes_window_tmp / time_window_s

    # Copy results
    spikes_by_window.append(spikes_in_window_tmp)
    n_spikes_window.append(n_spikes_window_tmp)
    window_length.append(time_window_s)
    window_firing_rate.append(firing_rate_tmp)

spikes_by_window_dataframe = pd.DataFrame([spikes_by_window, n_spikes_window, window_length, window_firing_rate], index = ['spikes in window', 'number of spikes', 'length of window', 'firing rate by window'], columns = range(n_bins))

spikes_by_window_dataframe


# %%
# Plot firing rate by sweep throughout the recording.
get_ipython().run_line_magic('matplotlib', 'inline')
plt.plot(window_firing_rate, 'k')
plt.title(f'Figure 2e: Firing rate across {round(time_window_s, 2)} s bins', fontsize = 14)
plt.ylabel('Firing Rate [Hz]')
plt.xlabel('Time bin')
plt.show()

# %%
# Make function
def getFiringRate(
    file_name,
    channels_data_frame,
    sweep_IB_concatenated,
    pseudo_sweep_concatenated,
    peaks_QC,
    sampling_rate_khz = 25,
    n_bins = 100
    ):
    """
    `getFiringRate` calculates the firing rate from the recorded cell following three approaches. It returns a data frame with the results from each approach.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :channels_data_frame: data frame with extracted data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    :pseudo_sweep_concatenated:concatenated pseudo-sweep that has the same length and number of sweeps as the original data, with the difference that each sweep within the pseudo-sweep will be comprised of the number that reflects the real sweep ID.
    :sweep_IB_concatenated: numpy array containing the concatenated data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    :peaks_QC: indices of the detected spikes obtained from `findSpikes()`, after quality control.
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.
    :n_bins: number of bins in which to divide the total length of recording. Defaults to 100.
    """

    # Get delta_t from sampling rate:
    dt = 1/sampling_rate_khz

    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

    # Method 1: calculate firing frequency by dividing total number of detected spikes over length of recording
    n_spikes = len(peaks_QC)
    recording_length = len(sweep_IB_concatenated) * dt / 1000 # in seconds
    firing_frequency = n_spikes / recording_length # in Hz

    firing_frequency_dataframe = pd.DataFrame([n_spikes, recording_length, firing_frequency], index = ['n_spikes', 'recording_length', 'firing_frequency'], columns = cell_id)

    print(f'Neuron with ID {cell_id[0]}')
    print(f'Detected a total of {n_spikes} spikes')
    print(f'Duration of recording was {recording_length} seconds')
    print(f'Which gives a firing rate of {round(firing_frequency, 2)} Hz')

    # Method 2: calculate firing frequency separately for each sweep, to examine how the firing rate changes over time.
    # Initialise variables
    spikes_by_sweep_keys = []
    spikes_by_sweep = []
    n_spikes_sweep = []
    sweep_length = []
    sweep_firing_rate = []

    for sweep in channels_data_frame.columns: 
        # Take the spikes that belong to the current sweep
        spikes_in_sweep_tmp = np.array([p for i, p in enumerate(peaks_QC) if pseudo_sweep_concatenated[peaks_QC[i]] == int(sweep)])

        # Get firing rate for the current sweep
        sweep_length_s_tmp = len(channels_data_frame.loc['Channel B', sweep]) * dt / 1000 # in seconds
        n_spikes_sweep_tmp = len(spikes_in_sweep_tmp)
        firing_rate_sweep_tmp = n_spikes_sweep_tmp / sweep_length_s_tmp

        # Append results
        spikes_by_sweep_keys.append(int(sweep))
        spikes_by_sweep.append(spikes_in_sweep_tmp)
        n_spikes_sweep.append(n_spikes_sweep_tmp)
        sweep_length.append(sweep_length_s_tmp)
        sweep_firing_rate.append(firing_rate_sweep_tmp)

    spikes_by_sweep_dataframe = pd.DataFrame([spikes_by_sweep, n_spikes_sweep, sweep_length, sweep_firing_rate], index = ['spikes_by_sweep', 'n_spikes_sweep', 'sweep_length', 'sweep_firing_rate'], columns = spikes_by_sweep_keys)

    # Method 3: calculate firing frequency for a time window of our choice, to examine how the firing rate changes over time.

    time_window_s = len(pseudo_sweep_concatenated) / 1000 * dt / n_bins # divide the length of recording in 100 chunks (1-2s each)
    time_window_samples = len(pseudo_sweep_concatenated) / n_bins
    spikes_by_window = []
    n_spikes_window = []
    window_length = []
    window_firing_rate = []

    for window in range(n_bins): 
        # Take the spikes that belong to the current bin
        spikes_in_window_tmp = np.array([p for p in peaks_QC if ((time_window_samples*window) < p < (time_window_samples*(window+1)))])

        # Get firing rate for the current bin
        n_spikes_window_tmp = len(spikes_in_window_tmp)
        firing_rate_tmp = n_spikes_window_tmp / time_window_s

        # Append results
        spikes_by_window.append(spikes_in_window_tmp)
        n_spikes_window.append(n_spikes_window_tmp)
        window_length.append(time_window_s)
        window_firing_rate.append(firing_rate_tmp)

    spikes_by_window_dataframe = pd.DataFrame([spikes_by_window, n_spikes_window, window_length, window_firing_rate], index = ['spikes_by_window', 'n_spikes_window', 'window_length', 'window_firing_rate'], columns = range(n_bins))

    # Visualise results
    # Generate figure layout
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig, axs = plt.subplots (2, 2, tight_layout = True, figsize = (7, 5), dpi = 100)

    # Plot firing rate by sweep throughout the recording.
    axs[0,0].plot(spikes_by_sweep_keys, sweep_firing_rate, 'k')
    axs[0,0].set_title('Firing rate across sweeps', fontsize = 12)
    axs[0,0].set_xlabel('sweep number', fontsize = 10)
    axs[0,0].set_ylabel('Firing Rate [Hz]', fontsize = 10)
    axs[0,0].set_ylim(0, round(firing_frequency*2))

    # Check whether the sweep firing rate correlates with seal resistance
    axs[0,1].scatter(Rseal_data_frame.loc['seal_resistance'], sweep_firing_rate)
    axs[0,1].set_title('Sweep firing rate vs Seal Resistance', fontsize = 12)
    axs[0,1].set_xlabel('Seal Resistance [MOhm]', fontsize = 10)
    axs[0,1].set_ylabel('Firing Rate [Hz]', fontsize = 10)
    axs[0,1].set_ylim(0, round(firing_frequency*2))

    # Plot firing rate by bin throughout the recording.
    axs[1,0].plot(window_firing_rate, 'k')
    axs[1,0].set_title(f'Firing rate across {round(time_window_s, 2)} s bins', fontsize = 12)
    axs[1,0].set_xlabel('time bin #', fontsize = 10)
    axs[1,0].set_ylabel('Firing Rate [Hz]', fontsize = 10)
    axs[1,0].set_ylim(0, round(firing_frequency*2))

    # Plot firing rate by bin throughout the recording.
    axs[1,1].axis('off')
    axs[1,1].text(0.5, 0.5, s = f'Neuron with ID\n{cell_id[0]}\n\nFiring rate of {round(firing_frequency, 2)} Hz', ha = 'center', va = 'center', wrap = True, in_layout = True)

    fig.canvas.manager.window.move(0, 0) # Move figure to top left corner

    plt.pause(5)

    return firing_frequency_dataframe, spikes_by_sweep_dataframe, spikes_by_window_dataframe # pandas data frame, pandas data frame, pandas data frame

# %%
get_ipython().run_line_magic('matplotlib', 'qt')
fig, axs = plt.subplots (2, 2, tight_layout = True, figsize = (7, 5), dpi = 100)

# Plot firing rate by sweep throughout the recording.
axs[0,0].plot(spikes_by_sweep_keys, sweep_firing_rate, 'k')
axs[0,0].set_title('Firing rate across sweeps', fontsize = 12)
axs[0,0].set_xlabel('sweep number', fontsize = 10)
axs[0,0].set_ylabel('Firing Rate [Hz]', fontsize = 10)
axs[0,0].set_ylim(0, round(firing_frequency*2))

# Check whether the sweep firing rate correlates with seal resistance
axs[0,1].scatter(Rseal_data_frame.loc['seal_resistance'], sweep_firing_rate)
axs[0,1].set_title('Sweep firing rate vs Seal Resistance', fontsize = 12)
axs[0,1].set_xlabel('Seal Resistance [MOhm]', fontsize = 10)
axs[0,1].set_ylabel('Firing Rate [Hz]', fontsize = 10)
axs[0,1].set_ylim(0, round(firing_frequency*2))

# Plot firing rate by bin throughout the recording.
axs[1,0].plot(window_firing_rate, 'k')
axs[1,0].set_title(f'Firing rate across {round(time_window_s, 2)} s bins', fontsize = 12)
axs[1,0].set_xlabel('time bin #', fontsize = 10)
axs[1,0].set_ylabel('Firing Rate [Hz]', fontsize = 10)
axs[1,0].set_ylim(0, round(firing_frequency*2))

# Plot firing rate by bin throughout the recording.
axs[1,1].axis('off')
axs[1,1].text(0.5, 0.5, s = f'Neuron with ID\n{cell_id[0]}\n\nFiring rate of {round(firing_frequency, 2)} Hz', ha = 'center', va = 'center', wrap = True, in_layout = True)

fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
plt.show()

# %%
# Test function
firing_frequency_dataframe, spikes_by_sweep_dataframe, spikes_by_window_dataframe = getFiringRate(file_name, channels_data_frame, sweep_IB_concatenated, pseudo_sweep_concatenated, peaks_QC, n_bins = 100)
firing_frequency_dataframe

# %%
