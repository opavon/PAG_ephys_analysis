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
from utilities import * # includes functions importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes, plotSpikesQC, spikesQC, cleanSpikes, averageSpikes, getSpikeParameters, getFiringRate, getInterspikeInterval, saveLooseSealResults
print("done!")

# %%
# Load data for LIAM cell (contains spikes in test_pulse)
channels_df, time, dt, folder_name, file_name = importFile(curated_channel = 'Sweeps_Analysis')
print("file imported")

# %%
# Get seal resistance
Rseal_df = getLooseRseal(channels_df)
print("Rseal calculated")

# %%
# Concatenate sweeps
sweep_IB_concatenated, pseudo_sweep_concatenated = concatenateSweeps(channels_df)
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
plotSpikesQC(file_name, peaks, peaks_properties, cut_spikes_baselined)

# %%
# Choose the QC metrics and remove detected peaks that correspond to noise and not spikes
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = 20, QC_wh_max = float('inf'),
    QC_pw_min = 2, QC_pw_max = 5,
    QC_ph_min = 50, QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = -85,
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )
parameters_QC

# Defaults
# peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
#     file_name, peaks, peaks_properties,
#     cut_spikes, cut_spikes_holding, cut_spikes_baselined,
#     filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
#     QC_p_min = float('-inf'), QC_p_max = float('inf'),
#     QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
#     QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
#     QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
#     QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
#     QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
#     QC_rb_min = float('-inf'), QC_rb_max = float('inf')
#     )

# %%
# Remove the spikes that were incorrectly baselined
cut_spikes_baselined_clean, parameters_clean = cleanSpikes(file_name, cut_spikes_baselined_QC)
parameters_clean

# %%
# Compute average spike
average_spike = averageSpikes(cut_spikes_baselined_clean)
print("average spike calculated")

# %%
# Compute average spike parameters
parameters_avg_spike = getSpikeParameters(file_name, cut_spikes_baselined_clean, average_spike, threshold_onset_factor = 0.04, threshold_end_factor = 20)

# %%
# Compute firing frequency
firing_frequency_df, spikes_by_sweep_df, spikes_by_window_df = getFiringRate(file_name, channels_df, sweep_IB_concatenated, pseudo_sweep_concatenated, Rseal_df, peaks_QC, n_bins = 100)
firing_frequency_df

# %%
# Compute interspike intervals
interspike_interval_df = getInterspikeInterval(sweep_IB_concatenated, pseudo_sweep_concatenated, peaks_QC, sampling_rate_khz = 25)
interspike_interval_df

# %%
# Save Results
vgat_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
vgat_kynac_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_kynerinc_picrotoxin"
vglut2_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_control"
vglut2_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_picrotoxin"

saveLooseSealResults(vgat_ctrl_save_path, file_name, sweep_IB_concatenated, pseudo_sweep_concatenated, peaks, cut_spikes, cut_spikes_holding, cut_spikes_baselined, peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, cut_spikes_baselined_clean, average_spike, Rseal_df, peaks_properties, parameters_find_peaks, parameters_QC, parameters_clean, parameters_avg_spike, firing_frequency_df, spikes_by_sweep_df, spikes_by_window_df, interspike_interval_df)

# %%
# Get delta_t from sampling rate:
dt = 1/25

file_id = [file_name.split('.')[0]] # Get the file name without the extension
cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

# Find the peak magnitude and where the peak is, defined by the cutSpikes() function (should be sample 125)
spike_magnitude = min(average_spike)
average_spike_peak_index = int(np.where(average_spike == spike_magnitude)[0]) # needs to be an integer
# Compute derivative of average spike and of all spikes
average_spike_diff = np.diff(average_spike)
average_spike_diff_peak_index = int(np.where(average_spike_diff == min(average_spike_diff))[0])
cut_spikes_diff = np.diff(cut_spikes_baselined_clean)

# %%
# Compute baseline of derivative by averaging period before spike starts
#average_spike_diff_baseline = abs(np.mean(average_spike_diff[average_spike_peak_index-100:average_spike_peak_index-25]))

baseline_cut_spikes = ([cut_spikes_baselined_clean[s][(average_spike_peak_index-100):(average_spike_peak_index-25)] for s in range(len(cut_spikes_baselined_clean))])
baseline_cut_spikes_conc = np.concatenate(baseline_cut_spikes)

baseline_cut_spikes_diff = ([cut_spikes_diff[s][(average_spike_diff_peak_index-100):(average_spike_diff_peak_index-25)] for s in range(len(cut_spikes_diff))])
baseline_cut_spikes_diff_conc = np.concatenate(baseline_cut_spikes_diff)

baseline_average_spike = average_spike[(average_spike_peak_index-100):(average_spike_peak_index-25)]
baseline_average_spike_mean = np.mean(baseline_average_spike)
baseline_average_spike_sd = np.std(baseline_average_spike_mean)
baseline_average_spike_diff = average_spike_diff[(average_spike_diff_peak_index-100):(average_spike_diff_peak_index-25)]

# %%
# Define threshold for onset
onset_threshold_cut_spikes = np.percentile(baseline_cut_spikes_conc, 5)
print(onset_threshold_cut_spikes)
onset_threshold_cut_spikes_diff = np.percentile(baseline_cut_spikes_diff_conc, 5)
print(onset_threshold_cut_spikes_diff)
#onset_threshold_average_spike = np.percentile(baseline_average_spike, 5)
onset_threshold_average_spike = np.std(baseline_average_spike)*-5
print(onset_threshold_average_spike)
#onset_threshold_average_spike_diff = np.percentile(baseline_average_spike_diff, 5)
onset_threshold_average_spike_diff = np.std(baseline_average_spike_diff)*-5

print(onset_threshold_average_spike_diff)

# %%
# Calculate spike onset with each method
for i, s in enumerate(average_spike[(average_spike_peak_index-25):average_spike_peak_index]): # i is the index, s is the value
    if s < onset_threshold_cut_spikes:
        onset_threshold_cut_spikes_index = i + (average_spike_peak_index-25)
        break

for i, s in enumerate(average_spike[(average_spike_peak_index-25):average_spike_peak_index]): # i is the index, s is the value
    if s < onset_threshold_average_spike:
        onset_threshold_average_spike_index = i + (average_spike_peak_index-25)
        break

for i, s in enumerate(average_spike_diff[(average_spike_diff_peak_index-25):average_spike_diff_peak_index]): # i is the index, s is the value
    if s < onset_threshold_cut_spikes_diff:
        onset_threshold_cut_spikes_diff_index = i + (average_spike_diff_peak_index-25)
        break

for i, s in enumerate(average_spike_diff[(average_spike_diff_peak_index-25):average_spike_diff_peak_index]): # i is the index, s is the value
    if s < onset_threshold_average_spike_diff:
        onset_threshold_average_spike_diff_index = i + (average_spike_diff_peak_index-25)
        break

print(onset_threshold_cut_spikes_index)
print(onset_threshold_average_spike_index)
print(onset_threshold_cut_spikes_diff_index)
print(onset_threshold_average_spike_diff_index)

# %%
# Plot the average spike and its derivative
get_ipython().run_line_magic('matplotlib', 'qt')    
fig, axs = plt.subplots (2, sharex=True, figsize = (7, 5), dpi = 100) # Set figure size

axs[0].plot(cut_spikes_baselined_clean.T, 'k') # cut spikes
axs[0].plot(average_spike, 'r') # average spike
axs[0].plot(onset_threshold_cut_spikes_index, average_spike[onset_threshold_cut_spikes_index], "oc") # spike onset
axs[0].plot(onset_threshold_average_spike_index, average_spike[onset_threshold_average_spike_index], "oy") # spike onset
axs[0].set_ylabel('current [pA]', fontsize = 12)
axs[0].axhline(y = -onset_threshold_cut_spikes, c = 'c', ls = '--') # horizontal dashed line at threshold for onset
axs[0].axhline(y = onset_threshold_cut_spikes, c = 'c', ls = '--') # horizontal dashed line at threshold for onset
axs[0].axhline(y = -onset_threshold_average_spike, c = 'y', ls = '--') # horizontal dashed line at threshold for onset
axs[0].axhline(y = onset_threshold_average_spike, c = 'y', ls = '--') # horizontal dashed line at threshold for onset

axs[1].plot(cut_spikes_diff.T, 'k') # derivative of all cut spikes
axs[1].plot(average_spike_diff, 'c') # derivative of average spike
axs[1].plot(onset_threshold_cut_spikes_diff_index, average_spike_diff[onset_threshold_cut_spikes_diff_index], "or") # spike onset
axs[1].plot(onset_threshold_average_spike_diff_index, average_spike_diff[onset_threshold_average_spike_diff_index], "oy") # spike end
axs[1].axhline(y = onset_threshold_cut_spikes_diff, c = 'r', ls = '--') # horizontal dashed line at threshold for onset
axs[1].axhline(y = onset_threshold_average_spike_diff, c = 'y', ls = '--') # horizontal dashed line at threshold for onset

plt.suptitle('Averaged spike with onset and its derivative', fontsize = 14)
#plt.xlim([((len(average_spike)/2)-45), ((len(average_spike)/2)+55)])
fig.canvas.manager.window.move(0, 0)
plt.show()

# %%
# Define threshold for end
end_min_threshold_cut_spikes = np.percentile(baseline_cut_spikes_conc, 2.5)
end_max_threshold_cut_spikes = np.percentile(baseline_cut_spikes_conc, 97.5)
print(end_min_threshold_cut_spikes)
print(end_max_threshold_cut_spikes)

end_min_threshold_cut_spikes_diff = np.percentile(baseline_cut_spikes_diff_conc, 2.5)
end_max_threshold_cut_spikes_diff = np.percentile(baseline_cut_spikes_diff_conc, 97.5)
print(end_min_threshold_cut_spikes_diff)
print(end_max_threshold_cut_spikes_diff)

end_min_threshold_average_spike = np.percentile(baseline_average_spike, 2.5)
end_max_threshold_average_spike = np.percentile(baseline_average_spike, 97.5)
print(end_min_threshold_average_spike)
print(end_max_threshold_average_spike)

end_min_threshold_average_spike_diff = np.percentile(baseline_average_spike_diff, 2.5)
end_max_threshold_average_spike_diff = np.percentile(baseline_average_spike_diff, 97.5)
print(end_min_threshold_average_spike_diff)
print(end_max_threshold_average_spike_diff)

# %%
# Calculate the spike end with the different methods
# Plot the average spike and its derivative
get_ipython().run_line_magic('matplotlib', 'qt')    
fig, axs = plt.subplots (2, sharex=True, figsize = (7, 5), dpi = 100) # Set figure size

axs[0].plot(cut_spikes_baselined_clean.T, 'k') # cut spikes
axs[0].plot(average_spike, 'r') # average spike
#axs[0].plot(onset_threshold_cut_spikes_index, average_spike[onset_threshold_cut_spikes_index], "oc") # spike onset
#axs[0].plot(onset_threshold_average_spike_index, average_spike[onset_threshold_average_spike_index], "oy") # spike onset
axs[0].set_ylabel('current [pA]', fontsize = 12)
axs[0].axhline(y = end_min_threshold_cut_spikes, c = 'c', ls = '--') # horizontal dashed line at threshold for onset
axs[0].axhline(y = end_max_threshold_cut_spikes, c = 'c', ls = '--') # horizontal dashed line at threshold for onset
axs[0].axhline(y = end_min_threshold_average_spike, c = 'y', ls = '--') # horizontal dashed line at threshold for onset
axs[0].axhline(y = end_max_threshold_average_spike, c = 'y', ls = '--') # horizontal dashed line at threshold for onset

axs[1].plot(cut_spikes_diff.T, 'k') # derivative of all cut spikes
axs[1].plot(average_spike_diff, 'c') # derivative of average spike
#axs[1].plot(onset_threshold_cut_spikes_diff_index, average_spike_diff[onset_threshold_cut_spikes_diff_index], "or") # spike onset
#axs[1].plot(onset_threshold_average_spike_diff_index, average_spike_diff[onset_threshold_average_spike_diff_index], "oy") # spike end
axs[1].axhline(y = end_min_threshold_cut_spikes_diff, c = 'r', ls = '--') # horizontal dashed line at threshold for onset
axs[1].axhline(y = end_max_threshold_cut_spikes_diff, c = 'r', ls = '--') # horizontal dashed line at threshold for onset
axs[1].axhline(y = end_min_threshold_average_spike_diff, c = 'y', ls = '--') # horizontal dashed line at threshold for onset
axs[1].axhline(y = end_max_threshold_average_spike_diff, c = 'y', ls = '--') # horizontal dashed line at threshold for onset

plt.suptitle('Averaged spike with and its derivative', fontsize = 14)
#plt.xlim([((len(average_spike)/2)-45), ((len(average_spike)/2)+55)])
fig.canvas.manager.window.move(0, 0)
plt.show()

# %%
##### Assess the average spike indices before the peak and keep those that cross the threshold
for i, s in enumerate(average_spike_diff): # i is the index, s is the value
    if s < threshold_onset:
        spike_onset_diff_index = i
        break
##### Assess the derivative indices after the peak and keep those where the derivative is back to baseline (baseline defined by threshold_end)
for i, s in enumerate(average_spike_diff[::-1]):
    if s < threshold_min_end or s > threshold_max_end:
        spike_end_diff_index = len(average_spike_diff)-i
        break

# Extract onset and end, calculate length and onset to peak
spike_onset = spike_onset_diff_index + 1
spike_end = spike_end_diff_index + 1
spike_length = (spike_end - spike_onset) * dt
spike_onset_to_peak = (average_spike_peak_index-spike_onset) * dt

# Plot the average spike and its derivative
get_ipython().run_line_magic('matplotlib', 'qt')    
fig, axs = plt.subplots (2, sharex=True, figsize = (7, 5), dpi = 100) # Set figure size
axs[0].plot(cut_spikes_baselined_clean.T, 'k') # cut spikes
axs[0].plot(average_spike, 'r') # average spike
axs[0].plot(spike_onset, average_spike[spike_onset], "oc") # spike onset
axs[0].plot(spike_end, average_spike[spike_end], "oc") # spike end
axs[0].set_ylabel('current [pA]', fontsize = 12)
axs[0].axhline(y = 0, c = 'k', ls = '--') # horizontal dashed line at 0
axs[1].plot(cut_spikes_diff.T, 'k') # derivative of all cut spikes
axs[1].plot(average_spike_diff, 'c') # derivative of average spike
axs[1].plot(spike_onset_diff_index, average_spike_diff[spike_onset_diff_index], "or") # spike onset
axs[1].plot(spike_end_diff_index, average_spike_diff[spike_end_diff_index], "or") # spike end
axs[1].axhline(y = threshold_onset, c = 'r', ls = '--') # horizontal dashed line at threshold for onset
axs[1].axhline(y = threshold_min_end, c = 'r', ls = '--') # horizontal dashed line at min threshold for end
axs[1].axhline(y = threshold_max_end, c = 'r', ls = '--') # horizontal dashed line at max threshold for end
#axs[1].axhline(y = 0, c = 'k', ls = '--') # horizontal dashed line at 0
plt.suptitle('Averaged spike with onset and end and its derivative', fontsize = 14)
#plt.xlim([((len(average_spike)/2)-45), ((len(average_spike)/2)+55)])
fig.canvas.manager.window.move(0, 0)
plt.show(block = True) # Lets you interact with plot and proceeds once figure is closed

# Check whether clean up is complete
happy_onset = input("Are you happy with the calculated onset and end? y/n")

if happy_onset == 'y':
    parameters_avg_spike = pd.DataFrame([[spike_onset, spike_end, spike_length, spike_onset_to_peak, spike_magnitude]], columns = ['spike_onset_sample', 'spike_end_sample', 'spike_length_ms', 'spike_onset_to_peak_ms', 'spike_magnitude_pA'], index = file_id)
    print('spike parameters calculated')
    print(f'Spike onset at {spike_onset}')
    print(f'Spike end at {spike_end}')
    print(f'Spike length of {spike_length} ms')
    print(f'Spike onset to peak of {spike_onset_to_peak} ms')
    print(f'Spike magnitude of {round(spike_magnitude, 2)} pA')
else:
    print('Try running getSpikeParameters() again')
    plt.close()
    return None # return empty variables to prevent wrong results from being used

plt.close()

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
# plt.pause(5) # Use this if you are running the full script so it gives you a few seconds to see the plot before it moves to the next chunk of code.

return parameters_avg_spike # pandas dataframe