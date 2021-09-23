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
from utilities import * # includes functions importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes, plotSpikesQC, spikesQC, cleanSpikes, averageSpikes, getSpikeParameters, getFiringRate
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
# Compute average spike parameters
average_spike_parameters = getSpikeParameters(file_name, average_spike, threshold_onset_factor = 0.04, threshold_end_factor = 50)

# %%
# Compute firing frequency
firing_frequency_dataframe, spikes_by_sweep_dataframe, spikes_by_window_dataframe = getFiringRate(file_name, channels_data_frame, sweep_IB_concatenated, pseudo_sweep_concatenated, Rseal_data_frame, peaks_QC, n_bins = 100)

# %% [markdown]
#########################################################################
# ## 1 | Make a function to extract the interspike interval
# In some cases the protocol we used to record the data has a gap between sweeps. This means we can't directly use the timepoints from the concatenated trace to calculate ISIs. We will use the pseudo_sweep to make sure we only calculate the interspike intervals between the spikes of the same sweep.
#########################################################################

# %%
print(len(sweep_IB_concatenated)) # Check length of concatenated sweeps
print(len(pseudo_sweep_concatenated)) # Check length of concatenated pseudo-sweep
print(len(np.array(channels_data_frame.at['Channel B', '30']))) # Check length of a single sweep

# Triple check where the transition between a sweep is
print(pseudo_sweep_concatenated[123749]) # Sweep 13
print(pseudo_sweep_concatenated[123750]) # Sweep 14

# %%
interspike_clean = []

for p in range(len(peaks_QC)-1):
    # print(pseudo_sweep_concatenated[peaks_QC[p]])
    if pseudo_sweep_concatenated[peaks_QC[p]] == pseudo_sweep_concatenated[peaks_QC[p+1]]: # Check both spikes are in the same sweep):
        interspike_tmp = peaks_QC[p+1] - peaks_QC[p] # get number of samples between spikes
        interspike_tmp_ms = interspike_tmp * dt # convert to ms
        interspike_clean.append(interspike_tmp_ms) # append results

print(len(interspike_clean)) # number of computed ISI.

# %%
# Check that the difference between the number of peaks and interspike intervals matches the number of sweeps in the recording
print(len(interspike_clean))
print(len(peaks_QC))
print(len(peaks_QC) - len(interspike_clean))
print(len(np.array(channels_data_frame.loc['Channel B', :])))

# %%
plt.hist(interspike_clean, bins = 50, density = False, histtype = 'bar', log = False, color = 'k')
plt.title('ISI of detected spikes', fontsize = 14)
plt.xlabel('Interspike Interval [ms]', fontsize = 12)
plt.xlim([0, None])
plt.show()

# %%
# Now that we are sure we are not using any inaccurate ISI, we can check how using the ISI to get the instantaneous firing frequency to get an average of the firing frequency compares to the firing frequency obtained by dividing the total number of spikes detected over recording time.
instant_firing_frequency = [((1/isi)*1000) for isi in interspike_clean]
print(f'Average instantaneous firing rate: {round(np.mean(instant_firing_frequency), 2)} Hz')
firing_rate = firing_frequency_dataframe.loc['firing_frequency'][0]
print(f'Firing rate: {round(firing_rate, 2)} Hz')

# We can see that the instantaneous firing rate provides a higher value than the real one. This is expected as when using the ISI we are discarding the time of recording between the start of the sweep and the first spike, for every sweep. So we are effectually shortening the total length of recording and thus increasing the resulting firing rate.

# %%
# Find holding current for each spike and plot it against ISI

# Now that we have the interspike intervals, we can try to see whether the holding current (whatever the amplifier is injecting through the pipette) has an effect on the firing rate of the cell. We can examine this by plotting the average holding current between two spikes and the iterspike interval for that same pair of spikes. If there is an effect, we would expect a significant correlation when looking at all the data points.

holding_isi_avg = []
holding_isi_std = []

for p in range(len(peaks_QC)-1):
    # print(pseudo_sweep_concatenated[peaks_QC[p]])
    if pseudo_sweep_concatenated[peaks_QC[p]] == pseudo_sweep_concatenated[peaks_QC[p+1]]: # Check both spikes are in the same sweep
        holding_avg_tmp = np.mean(sweep_IB_concatenated[peaks_QC[p]+50 : peaks_QC[p+1]-50])
        holding_std_tmp = np.std(sweep_IB_concatenated[peaks_QC[p]+50 : peaks_QC[p+1]-50])

        # average 2 ms after first spike until 2 ms before second spike
        holding_isi_avg.append(holding_avg_tmp)
        holding_isi_std.append(holding_std_tmp)

print(len(holding_isi_avg))
print(len(holding_isi_std))

# %%
# Plot ISI vs Holding (mean)
get_ipython().run_line_magic('matplotlib', 'qt')
plt.scatter(interspike_clean, holding_isi_avg, label = f'Correlation = {np.round(stats.linregress(interspike_clean, holding_isi_avg)[2],2)}\npvalue = {stats.linregress(interspike_clean, holding_isi_avg)[3]}')
# plt.scatter(interspike_clean, holding_isi_avg, label = f'Correlation = {np.round(np.corrcoef(interspike_clean, holding_isi_avg)[0,1], 2)}')
plt.title('ISI vs Holding (avg)', fontsize = 14), plt.legend()
plt.xlabel('Interspike Interval [ms]', fontsize = 12), plt.ylabel('Holding current [pA]', fontsize = 12)
plt.show()

# %%
# Plot ISI vs Holding (std)
get_ipython().run_line_magic('matplotlib', 'qt')
plt.scatter(interspike_clean, holding_isi_std, label = f'Correlation = {np.round(stats.linregress(interspike_clean, holding_isi_std)[2],2)}\npvalue = {stats.linregress(interspike_clean, holding_isi_std)[3]}')
# plt.scatter(interspike_clean, holding_isi_std, label = f'Correlation = {np.round(np.corrcoef(interspike_clean, holding_isi_std)[0,1], 2)}')
plt.title('ISI vs Holding (std)', fontsize = 14), plt.legend()
plt.xlabel('Interspike Interval [ms]', fontsize = 12), plt.ylabel('Holding current [std]', fontsize = 12)
plt.show()

# %%
test_holding_avg = np.array([isi_hold_avg for i, isi_hold_avg in enumerate(holding_isi_avg) if (-50 < holding_isi_avg[i] < 50)])
print(len(test_holding_avg))
test_isi_avg = np.array([isi for i, isi in enumerate(interspike_clean) if (-50 < holding_isi_avg[i] < 50)])
print(len(test_isi_avg))

# Plot ISI vs Holding (avg)
get_ipython().run_line_magic('matplotlib', 'qt')
plt.scatter(test_isi_avg, test_holding_avg, label = f'Correlation = {np.round(stats.linregress(test_isi_avg, test_holding_avg)[2],2)}\npvalue = {stats.linregress(test_isi_avg, test_holding_avg)[3]}')
# plt.scatter(test_isi_avg, test_holding_avg, label = f'Correlation = {np.round(np.corrcoef(test_isi_avg, test_holding_avg)[0,1], 2)}')
plt.title('ISI vs Holding between 50pA injected', fontsize = 14), plt.legend()
plt.xlabel('Interspike Interval [ms]', fontsize = 12), plt.ylabel('Holding current [pA]', fontsize = 12)
plt.show()

# %%
test_holding_std = np.array([isi_hold_std for i, isi_hold_std in enumerate(holding_isi_std) if (holding_isi_std[i] < 20)])
print(len(test_holding_std))
test_isi_std = np.array([isi for i, isi in enumerate(interspike_clean) if (holding_isi_std[i] < 50)])
print(len(test_isi_std))

# Plot ISI vs Holding (std)
get_ipython().run_line_magic('matplotlib', 'qt')
plt.scatter(test_isi_std, test_holding_std, label = f'Correlation = {np.round(stats.linregress(test_isi_std, test_holding_std)[2],2)}\npvalue = {stats.linregress(test_isi_std, test_holding_std)[3]}')
# plt.scatter(test_isi_std, test_holding_std, label = f'Correlation = {np.round(np.corrcoef(test_isi_std, test_holding_std)[0,1], 2)}')
plt.title('ISI vs Holding between 50pA injected', fontsize = 14), plt.legend()
plt.xlabel('Interspike Interval [ms]', fontsize = 12), plt.ylabel('Holding current [std]', fontsize = 12)
plt.show()

# %%
stats.linregress(test_isi_std, test_holding_std)

# %% 
# Put things together
interspike_interval = []
holding_isi_avg = []
holding_isi_std = []

for p in range(len(peaks_QC)-1):
    # Check that both spikes you are evaluating are in the same sweep:
    if pseudo_sweep_concatenated[peaks_QC[p]] == pseudo_sweep_concatenated[peaks_QC[p+1]]:
        # Calculate interspike interval
        interspike_tmp = peaks_QC[p+1] - peaks_QC[p] # get number of samples between spikes
        interspike_tmp_ms = interspike_tmp * dt # convert to ms
        interspike_interval.append(interspike_tmp_ms) # append results

        # Calculate average and standard deviation of the holding/baseline/injected current between both spikes
        # average the period between 2 ms after first spike until 2 ms before second spike
        holding_avg_tmp = np.mean(sweep_IB_concatenated[peaks_QC[p]+50 : peaks_QC[p+1]-50])
        holding_std_tmp = np.std(sweep_IB_concatenated[peaks_QC[p]+50 : peaks_QC[p+1]-50])            
        holding_isi_avg.append(holding_avg_tmp) # append results
        holding_isi_std.append(holding_std_tmp) # append results

# %%
# Merge plotting results
# Visualise results
# Generate figure layout
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (12, 12), dpi = 100)
axs = fig.subplot_mosaic(
    """
    AA
    BC
    DE
    """
)

# Plot histogram of interspike intervals
axs['A'].hist(interspike_clean, bins = 50, density = False, histtype = 'bar', log = False, color = 'k')
axs['A'].set_title('A) ISI of detected spikes', fontsize = 12)
axs['A'].set_xlabel('Interspike Interval [ms]', fontsize = 10)
axs['A'].set_xlim([0, None])

# Plot ISI vs Holding (mean)
axs['B'].scatter(interspike_clean, holding_isi_avg, label = f'Slope = {np.round(stats.linregress(interspike_clean, holding_isi_avg)[0],5)}\npvalue = {np.round(stats.linregress(interspike_clean, holding_isi_avg)[3],2)}')
# axs['B'].scatter(interspike_clean, holding_isi_avg, label = f'Correlation = {np.round(np.corrcoef(interspike_clean, holding_isi_avg)[0,1], 2)}')
axs['B'].set_title('B) ISI vs Holding (avg)', fontsize = 12), axs['B'].legend()
axs['B'].set_xlabel('Interspike Interval [ms]', fontsize = 10), axs['B'].set_ylabel('Holding current [pA]', fontsize = 10)

# Plot ISI vs Holding (std)
axs['C'].scatter(interspike_clean, holding_isi_std, label = f'Slope = {np.round(stats.linregress(interspike_clean, holding_isi_std)[0],5)}\npvalue = {np.round(stats.linregress(interspike_clean, holding_isi_std)[3],2)}')
# axs['C'].scatter(interspike_clean, holding_isi_std, label = f'Correlation = {np.round(np.corrcoef(interspike_clean, holding_isi_std)[0,1], 2)}')
axs['C'].set_title('C) ISI vs Holding (std)', fontsize = 12), axs['C'].legend()
axs['C'].set_xlabel('Interspike Interval [ms]', fontsize = 10), axs['C'].set_ylabel('Holding current [std]', fontsize = 10)

test_holding_avg = np.array([isi_hold_avg for i, isi_hold_avg in enumerate(holding_isi_avg) if (-50 < holding_isi_avg[i] < 50)])
test_isi_avg = np.array([isi for i, isi in enumerate(interspike_clean) if (-50 < holding_isi_avg[i] < 50)])

# Plot ISI vs Holding (avg)
axs['D'].scatter(test_isi_avg, test_holding_avg, label = f'Slope = {np.round(stats.linregress(test_isi_avg, test_holding_avg)[0],5)}\npvalue = {np.round(stats.linregress(test_isi_avg, test_holding_avg)[3],2)}')
# axs['D'].scatter(test_isi_avg, test_holding_avg, label = f'Correlation = {np.round(np.corrcoef(test_isi_avg, test_holding_avg)[0,1], 2)}')
axs['D'].set_title('D) ISI vs Holding (±50pA injected)', fontsize = 12), axs['D'].legend()
axs['D'].set_xlabel('Interspike Interval [ms]', fontsize = 10), axs['D'].set_ylabel('Holding current [pA]', fontsize = 10)

test_holding_std = np.array([isi_hold_std for i, isi_hold_std in enumerate(holding_isi_std) if (holding_isi_std[i] < 20)])
test_isi_std = np.array([isi for i, isi in enumerate(interspike_clean) if (holding_isi_std[i] < 20)])

# Plot ISI vs Holding (std)
axs['E'].scatter(test_isi_std, test_holding_std, label = f'Slope = {np.round(stats.linregress(test_isi_std, test_holding_std)[0],5)}\npvalue = {np.round(stats.linregress(test_isi_std, test_holding_std)[3],2)}')
# axs['E'].scatter(test_isi_std, test_holding_std, label = f'Correlation = {np.round(np.corrcoef(test_isi_std, test_holding_std)[0,1], 2)}')
axs['E'].set_title('E) ISI vs Holding (<20 std in holding_avg)', fontsize = 12), axs['E'].legend()
axs['E'].set_xlabel('Interspike Interval [ms]', fontsize = 10), axs['E'].set_ylabel('Holding current [std]', fontsize = 10)
 
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
plt.pause(5)

# %%
# Make function
def getInterspikeInterval(
    sweep_IB_concatenated,
    pseudo_sweep_concatenated,
    peaks_QC,
    sampling_rate_khz = 25
    ):
    """
    `getInterspikeInterval` calculates the interspike interval between all the detected spikes on a sweep by sweep basis. It returns a data frame with the results.
    
    :sweep_IB_concatenated: numpy array containing the concatenated data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    :pseudo_sweep_concatenated:concatenated pseudo-sweep that has the same length and number of sweeps as the original data, with the difference that each sweep within the pseudo-sweep will be comprised of the number that reflects the real sweep ID.
    :peaks_QC: indices of the detected spikes obtained from `findSpikes()`, after quality control.
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.
    """
    # Get delta_t from sampling rate:
    dt = 1/sampling_rate_khz

    # Initialise variables
    interspike_interval = []
    holding_isi_avg = []
    holding_isi_std = []

    for p in range(len(peaks_QC)-1):
        # Check that both spikes you are evaluating are in the same sweep:
        if pseudo_sweep_concatenated[peaks_QC[p]] == pseudo_sweep_concatenated[peaks_QC[p+1]]:
            # Calculate interspike interval
            interspike_tmp = peaks_QC[p+1] - peaks_QC[p] # get number of samples between spikes
            interspike_tmp_ms = interspike_tmp * dt # convert to ms
            interspike_interval.append(interspike_tmp_ms) # append results

            # Calculate average and standard deviation of the holding/baseline/injected current between both spikes
            # average the period between 2 ms after first spike until 2 ms before second spike
            holding_avg_tmp = np.mean(sweep_IB_concatenated[peaks_QC[p]+50 : peaks_QC[p+1]-50])
            holding_std_tmp = np.std(sweep_IB_concatenated[peaks_QC[p]+50 : peaks_QC[p+1]-50])            
            holding_isi_avg.append(holding_avg_tmp) # append results
            holding_isi_std.append(holding_std_tmp) # append results
    
    # Visualise results
    # Generate figure layout
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig = plt.figure(tight_layout = True, figsize = (12, 12), dpi = 100)
    axs = fig.subplot_mosaic(
        """
        AA
        BC
        DE
        """
    )

    # Plot histogram of interspike intervals
    axs['A'].hist(interspike_clean, bins = 50, density = False, histtype = 'bar', log = False, color = 'k')
    axs['A'].set_title('A) ISI of detected spikes', fontsize = 12)
    axs['A'].set_xlabel('Interspike Interval [ms]', fontsize = 10)
    axs['A'].set_xlim([0, None])

    # Plot ISI vs Holding (mean)
    axs['B'].scatter(interspike_clean, holding_isi_avg, label = f'Slope = {np.round(stats.linregress(interspike_clean, holding_isi_avg)[0],5)}\npvalue = {np.round(stats.linregress(interspike_clean, holding_isi_avg)[3],2)}')
    # axs['B'].scatter(interspike_clean, holding_isi_avg, label = f'Correlation = {np.round(np.corrcoef(interspike_clean, holding_isi_avg)[0,1], 2)}')
    axs['B'].set_title('B) ISI vs Holding (avg)', fontsize = 12), axs['B'].legend()
    axs['B'].set_xlabel('Interspike Interval [ms]', fontsize = 10), axs['B'].set_ylabel('Holding current [pA]', fontsize = 10)

    # Plot ISI vs Holding (std)
    axs['C'].scatter(interspike_clean, holding_isi_std, label = f'Slope = {np.round(stats.linregress(interspike_clean, holding_isi_std)[0],5)}\npvalue = {np.round(stats.linregress(interspike_clean, holding_isi_std)[3],2)}')
    # axs['C'].scatter(interspike_clean, holding_isi_std, label = f'Correlation = {np.round(np.corrcoef(interspike_clean, holding_isi_std)[0,1], 2)}')
    axs['C'].set_title('C) ISI vs Holding (std)', fontsize = 12), axs['C'].legend()
    axs['C'].set_xlabel('Interspike Interval [ms]', fontsize = 10), axs['C'].set_ylabel('Holding current [std]', fontsize = 10)

    test_holding_avg = np.array([isi_hold_avg for i, isi_hold_avg in enumerate(holding_isi_avg) if (-50 < holding_isi_avg[i] < 50)])
    test_isi_avg = np.array([isi for i, isi in enumerate(interspike_clean) if (-50 < holding_isi_avg[i] < 50)])

    # Plot ISI vs Holding (avg)
    axs['D'].scatter(test_isi_avg, test_holding_avg, label = f'Slope = {np.round(stats.linregress(test_isi_avg, test_holding_avg)[0],5)}\npvalue = {np.round(stats.linregress(test_isi_avg, test_holding_avg)[3],2)}')
    # axs['D'].scatter(test_isi_avg, test_holding_avg, label = f'Correlation = {np.round(np.corrcoef(test_isi_avg, test_holding_avg)[0,1], 2)}')
    axs['D'].set_title('D) ISI vs Holding (±50pA injected)', fontsize = 12), axs['D'].legend()
    axs['D'].set_xlabel('Interspike Interval [ms]', fontsize = 10), axs['D'].set_ylabel('Holding current [pA]', fontsize = 10)

    test_holding_std = np.array([isi_hold_std for i, isi_hold_std in enumerate(holding_isi_std) if (holding_isi_std[i] < 20)])
    test_isi_std = np.array([isi for i, isi in enumerate(interspike_clean) if (holding_isi_std[i] < 20)])

    # Plot ISI vs Holding (std)
    axs['E'].scatter(test_isi_std, test_holding_std, label = f'Slope = {np.round(stats.linregress(test_isi_std, test_holding_std)[0],5)}\npvalue = {np.round(stats.linregress(test_isi_std, test_holding_std)[3],2)}')
    # axs['E'].scatter(test_isi_std, test_holding_std, label = f'Correlation = {np.round(np.corrcoef(test_isi_std, test_holding_std)[0,1], 2)}')
    axs['E'].set_title('E) ISI vs Holding (<20 std in holding_avg)', fontsize = 12), axs['E'].legend()
    axs['E'].set_xlabel('Interspike Interval [ms]', fontsize = 10), axs['E'].set_ylabel('Holding current [std]', fontsize = 10)
    
    fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
    plt.pause(5)

    interspike_interval_dataframe = pd.DataFrame([interspike_interval, holding_isi_avg, holding_isi_std], index = ['interspike_interval', 'holding_isi_avg', 'holding_isi_std'], columns = range(len(interspike_interval)))

    return interspike_interval_dataframe # pandas data frame

# %%
# Test function
interspike_interval_dataframe = getInterspikeInterval(sweep_IB_concatenated, pseudo_sweep_concatenated, peaks_QC, sampling_rate_khz = 25)
interspike_interval_dataframe

# %%
