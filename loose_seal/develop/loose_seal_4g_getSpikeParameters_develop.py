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
from utilities import * # includes functions importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes, plotSpikesQC, spikesQC, cleanSpikes, averageSpikes
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

# %% [markdown]
# ## 1 | Make a function to extract key parameters from averages spike
# We want to extract the onset and total duration of the average spike

#%%
average_spike_peak_index = int(np.where(average_spike == min(average_spike))[0]) # needs to be an integer
print(average_spike_peak_index)
average_spike_clean_diff = np.diff(average_spike)
average_spike_clean_diff_baseline = abs(np.mean(average_spike_clean_diff[average_spike_peak_index-100:average_spike_peak_index-25]))
print(average_spike_clean_diff_baseline)

# %%
np.round(average_spike_clean_diff[100:160], 1)

# %%
test_threshold = min(average_spike_clean_diff)*0.05
print(test_threshold)

test_end = average_spike_clean_diff_baseline * 100
print(test_end)

# %%
# Plot average spike and its derivative
get_ipython().run_line_magic('matplotlib', 'qt')    
fig, axs = plt.subplots (2, sharex=True, figsize = (7, 5), dpi = 100) # Set figure size
axs[0].plot(average_spike, 'r') # average spike
axs[0].set_ylabel('current [pA]', fontsize = 12)
axs[0].axhline(y = 0, c = 'k', ls = '--') # horizontal dashed line at 0
axs[1].plot(average_spike_clean_diff, 'c') # derivative of average spike
axs[1].axhline(y = 0, c = 'k', ls = '--') # horizontal dashed line at 0
plt.suptitle('Averaged spike and its derivative', fontsize = 14)
plt.xlim([((len(average_spike)/2)-45), ((len(average_spike)/2)+55)])
fig.canvas.manager.window.move(0, 0)
plt.show()

# %%
# Calculate spike onset, end, and duration
spike_onset_indices = []
spike_end_indices = []

for i, s in enumerate(average_spike_clean_diff):
    if i != 0 and i < average_spike_peak_index and s < test_threshold:
        spike_onset_indices.append(np.where(average_spike_clean_diff == s)[0])
    elif i != 0 and i > average_spike_peak_index and -test_end < average_spike_clean_diff[i-1] < test_end and -test_end < s < test_end:
        spike_end_indices.append(np.where(average_spike_clean_diff == s)[0])

spike_onset = spike_onset_indices[0][0]
spike_end = spike_end_indices[0][0]
spike_length = (spike_end_indices[0][0] - spike_onset_indices[0][0]) * dt
spike_onset_to_peak = ((np.where(average_spike == np.min(average_spike))[0][0])-(spike_onset_indices[0][0])) * dt

print(f'Spike onset at {spike_onset}')
print(f'Spike end at {spike_end}')
print(f'Spike length of {spike_length} ms')
print(f'Spike onset to peak of {spike_onset_to_peak} ms')

# %%
get_ipython().run_line_magic('matplotlib', 'qt')    
fig, axs = plt.subplots (2, sharex=True, figsize = (7, 5), dpi = 100) # Set figure size
axs[0].plot(spike_onset, average_spike[spike_onset], "xk") # spike onset
axs[0].plot(spike_end, average_spike[spike_end], "xk") # spike end
axs[0].plot(average_spike, 'r') # average spike
axs[0].set_ylabel('current [pA]', fontsize = 12)
axs[0].axhline(y = 0, c = 'k', ls = '--') # horizontal dashed line at 0
axs[1].plot(average_spike_clean_diff, 'c') # derivative of average spike
axs[1].axhline(y = 0, c = 'k', ls = '--') # horizontal dashed line at 0
plt.suptitle('Averaged spike with onset and end and its derivative', fontsize = 14)
plt.xlim([((len(average_spike)/2)-45), ((len(average_spike)/2)+55)])
fig.canvas.manager.window.move(0, 0)
plt.show()

# %%
# Plot the average spike with the calculated onset and end
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
plt.plot(spike_onset, average_spike[spike_onset], "xr")
plt.plot(spike_end, average_spike[spike_end], "xr")
plt.plot(average_spike, 'k')
plt.suptitle('Averaged spike with onset and end', fontsize = 14)
plt.axhline(y = 0, c = 'k', ls = '--')
plt.ylabel('current [pA]', fontsize = 12)
plt.xlim([((len(average_spike)/2)-45), ((len(average_spike)/2)+55)])
fig.canvas.manager.window.move(0, 0)
plt.show()

# %%
def getSpikeParameters(
    file_name,
    average_spike,
    threshold_onset_factor = 0.04,
    threshold_end_factor = 50
    ):
    """
    `getSpikeParameters` computes key parameters to characterise the average spike shape. It returns a data frame with the spike onset and total duration of the spike.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :average_spike: array containing the values of the average spike.
    :threshold_onset_factor: float between 0 and 1 defining the percentage of the spike magnitude to be used to calculate spike onset. It defaults to 0.04. Khalid & Bean 2010 define spike threshold as the point at which dV/dt reached 4% of its maximal value, which corresponds well to a sharp inflection in the phase-plane plot of dV/dt versus voltage. The fact that we are recording extracellularly in Voltage Clamp means that we are mainly picking up capacitative current. The way capacitance is charged means that we can only detect signal when there is a change in the rate of charging. If the current flowing is constant (i.e. rest) the signal will be flat. Only when there is a change in the current (i.e. action potential) will we detect it. Thus, we basically record the change of rate in the capacitative current, which means that our peak corresponds to the point in time where the "change" in current is maximal (i.e. when the action potential rises fastest). By setting the threshold at 4% of the peak magnitude we are using a similar threshold to that defined in Khalid & Bean 2010. 
    :threshold_end_factor: integer defining the factor by which to multiply the value corresponding to the baseline of the derivative. Used to define the interval within which the average spike is considered to have returned to baseline and therefore ended. It defaults to 50.
    """
    
    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

    # Find the peak magnitude and where the peak is, defined by the cutSpikes() function (should be sample 125)
    spike_magnitude = min(average_spike)
    average_spike_peak_index = int(np.where(average_spike == min(average_spike))[0]) # needs to be an integer
    # Compute derivative of average spike
    average_spike_diff = np.diff(average_spike)
    # Compute baseline of derivative by averaging period before spike starts
    average_spike_diff_baseline = abs(np.mean(average_spike_diff[average_spike_peak_index-100:average_spike_peak_index-25]))

    # Define threshold for onset and end
    threshold_onset = spike_magnitude*threshold_onset_factor
    threshold_end = average_spike_diff_baseline*threshold_end_factor

    # Calculate spike onset, end, and duration
    spike_onset_indices = []
    spike_end_indices = []

    # Assess the average spike indices before the peak and keep those that cross the threshold
    for i, s in enumerate(average_spike): # i is the index, s is the value
        if i != 0 and i < average_spike_peak_index and s < threshold_onset:
            spike_onset_indices.append(np.where(average_spike == s)[0])
    # Assess the derivative indices after the peak and keep those where the derivative is back to baseline (baseline defined by threshold_end)
    for i, s in enumerate(average_spike_diff):
        if i != 0 and i > average_spike_peak_index and -threshold_end < average_spike_diff[i-2] < threshold_end and -threshold_end < average_spike_diff[i-1] < threshold_end and -threshold_end < s < threshold_end:
            spike_end_indices.append(np.where(average_spike_diff == s)[0])

    spike_onset = spike_onset_indices[0][0]
    spike_end = spike_end_indices[0][0]
    spike_length = (spike_end_indices[0][0] - spike_onset_indices[0][0]) * dt
    spike_onset_to_peak = ((np.where(average_spike == np.min(average_spike))[0][0])-(spike_onset_indices[0][0])) * dt

    # Plot the average spike and its derivative
    get_ipython().run_line_magic('matplotlib', 'qt')    
    fig, axs = plt.subplots (2, sharex=True, figsize = (7, 5), dpi = 100) # Set figure size
    axs[0].plot(spike_onset, average_spike[spike_onset], "xk") # spike onset
    axs[0].plot(spike_end, average_spike[spike_end], "xk") # spike end
    axs[0].plot(average_spike, 'r') # average spike
    axs[0].set_ylabel('current [pA]', fontsize = 12)
    axs[0].axhline(y = 0, c = 'k', ls = '--') # horizontal dashed line at 0
    axs[1].plot(average_spike_diff, 'c') # derivative of average spike
    axs[1].axhline(y = 0, c = 'k', ls = '--') # horizontal dashed line at 0
    plt.suptitle('Averaged spike with onset and end and its derivative', fontsize = 14)
    plt.xlim([((len(average_spike)/2)-45), ((len(average_spike)/2)+55)])
    fig.canvas.manager.window.move(0, 0)
    plt.show(block = True) # Lets you interact with plot and proceeds once figure is closed

    # Check whether clean up is complete
    happy_onset = input("Are you happy with the calculated onset and end? y/n")

    if happy_onset == 'y':
        average_spike_parameters = pd.DataFrame([[spike_onset, spike_end, spike_length, spike_onset_to_peak, spike_magnitude]], columns = ['onset [sample]', 'end [sample]', 'length [ms]', 'onset to peak [ms]', 'magnitude [pA]'], index = cell_id)
        print('spike parameters calculated')
        print(f'Spike onset at {spike_onset}')
        print(f'Spike end at {spike_end}')
        print(f'Spike length of {spike_length} ms')
        print(f'Spike onset to peak of {spike_onset_to_peak} ms')
        print(f'Spike magnitude of {spike_magnitude} pA')
    else:
        # Empty variables to prevent wrong results from being used.
        average_spike_parameters = []
        print('Try running getSpikeParameters() again')

    plt.close()

    # Plot the average spike with the calculated onset and end
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig_2 = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
    plt.plot(spike_onset, average_spike[spike_onset], "xr")
    plt.plot(spike_end, average_spike[spike_end], "xr")
    plt.plot(average_spike, 'k')
    plt.suptitle('Averaged spike with onset and end', fontsize = 14)
    plt.axhline(y = 0, c = 'k', ls = '--')
    plt.ylabel('current [pA]', fontsize = 12)
    plt.xlim([((len(average_spike)/2)-45), ((len(average_spike)/2)+55)])
    fig_2.canvas.manager.window.move(0, 0)
    plt.show()

    return average_spike_parameters # pandas data frame

# %%
# Test function
average_spike_parameters = getSpikeParameters(file_name, average_spike, threshold_onset_factor = 0.04, threshold_end_factor = 50)
average_spike_parameters
# %%
