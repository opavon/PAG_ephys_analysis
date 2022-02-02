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
from whole_cell_utilities import * # includes functions importFile, openFile, openHDF5file, getInputResistance
print("done!")

# %%
# Load data
channels_df, time, dt, folder_name, file_name = importFile(curated_channel = 'Sweeps_Analysis')
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
# Given that we have already curated all the recordings and left only the sweeps with one single spike in the "Sweeps_Analysis" curated channel, we can find the spikes by simply finding where the max value of each sweep is.
# In addition, we get the holding potential of the cell at each sweep and then baseline the curated sweeps

# Initialize variables to build results dataframe:
test_pulse_command_pA = []
injected_current_pA = []
holding_mV = []
peaks_indices = []
peaks_magnitude_mV = []
cut_spikes = []

for sweep in channels_df.columns:
    ## Load sweep data: Channel A (recording in current-clamp) and Output B (command)
    sweep_IA = np.array(channels_df.at['Channel A', sweep]) # voltage
    sweep_IB = np.array(channels_df.at['Channel B', sweep]) # current
    sweep_OA = np.array(channels_df.at['Output A', sweep])

    ## Get the indices corresponding to the test_pulse using the Output Channel
    test_pulse = np.where(sweep_OA > 0)
    test_pulse_OA_indices = test_pulse[0]

    ## Get test_pulse magnitude
    # Use the indices of the test_pulse command (Output A) to define baseline period and test period
    sweep_OA_baseline = np.mean(sweep_OA[:(test_pulse_OA_indices[0]-1)]) # -1 to stop baseline before command starts
    sweep_OA_pulse = np.mean(sweep_OA[test_pulse_OA_indices])
    tp_command = sweep_OA_pulse - sweep_OA_baseline # pA

    ## Get magnitude of current injected to the cell
    # Use the indices of the test_pulse command (Output A) to define baseline period and test period
    sweep_IB_baseline = np.mean(sweep_IB[:(test_pulse_OA_indices[0])])

    # Get the average baseline before the pulse starts to know the voltage at which the cell is sitting.
    # To be exact and account for the delays between digital command and output from the amplifier, you could add +1 to the first index to calculate the baseline.
    sweep_IA_baseline = np.mean(sweep_IA[:(test_pulse_OA_indices[0])])

    #print(max(sweep_IA))
    #print(np.where(sweep_IA == max(sweep_IA))[0])

    # Find the peaks and get their value and indices
    temp_spike_index = np.where(sweep_IA == max(sweep_IA))[0][0]
    temp_peak_magnitude = max(sweep_IA)

    # Cut the spike
    temp_cut_spike = np.array(sweep_IA[(temp_spike_index-2000) : (temp_spike_index+4000)])
    
    # Append results
    test_pulse_command_pA.append(tp_command)
    injected_current_pA.append(sweep_IB_baseline)
    holding_mV.append(sweep_IA_baseline)
    peaks_indices.append(temp_spike_index)
    peaks_magnitude_mV.append(temp_peak_magnitude)
    cut_spikes.append(temp_cut_spike)

print(test_pulse_command_pA)
print(injected_current_pA)
print(holding_mV)
print(peaks_indices)
print(peaks_magnitude_mV)
print(cut_spikes)

# %%
# Plot cut spikes after baselining
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
import matplotlib.cm as cm
baselined_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes)))
for s in range(len(cut_spikes)):
    plt.plot(cut_spikes[s], color = baselined_spikes_colors[s])
plt.title('Cut spikes', fontsize = 14)
plt.ylabel('voltage [mV]', fontsize = 12)
#plt.xlim([((len(cut_spikes[0])/2)-45), ((len(cut_spikes[0])/2)+55)])
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
plt.show()

#%%
# Get the average spike
temp_spike = np.array(np.mean(cut_spikes, 0))

# Get peak, trough, adp, ahp indices
temp_spike_peak_index = int(np.where(temp_spike == max(temp_spike))[0])
temp_spike_trough_index = int(np.where(temp_spike == min(temp_spike[temp_spike_peak_index:temp_spike_peak_index+50]))[0])
temp_spike_adp_index = int(np.where(temp_spike == max(temp_spike[temp_spike_trough_index:temp_spike_trough_index+200]))[0])
temp_spike_ahp_index = int(np.where(temp_spike == min(temp_spike[temp_spike_adp_index:temp_spike_adp_index+1250]))[0])

# Get peak, trough, adp, ahp metrics
peak_mV = temp_spike[temp_spike_peak_index]
trough_mV = temp_spike[temp_spike_trough_index]
adp_peak_mV = temp_spike[temp_spike_adp_index]
ahp_trough_mV = temp_spike[temp_spike_ahp_index]

peak_to_trough_magnitude = trough_mV - peak_mV
trough_to_adp_magnitude = adp_peak_mV - trough_mV
adp_to_ahp_magnitude = ahp_trough_mV - adp_peak_mV

peak_to_trough_ms = (temp_spike_trough_index - temp_spike_peak_index) * dt
trough_to_adp_ms = (temp_spike_adp_index - temp_spike_trough_index) * dt
adp_to_ahp_ms = (temp_spike_ahp_index - temp_spike_adp_index) * dt

# Get half_peak value
half_peak = peak_mV - (abs(peak_to_trough_magnitude) / 2)
# Now, we need to get the first time we cross the half_peak value (before the peak), and the second time (after the peak). To do this, we are going to split the spike in two halves, and do the procedure separately.
from scipy.interpolate import interp1d # load function to interpolate
temp_spike_first_half = temp_spike[:temp_spike_peak_index] # get first half of average spike
temp_f1 = interp1d(temp_spike_first_half,
                    range(0, len(temp_spike_first_half)), 
                    kind = "linear") # make function to interpolate
temp_half_width_start = temp_f1(half_peak) # find value corresponding to the half_peak

temp_spike_second_half = temp_spike[temp_spike_peak_index:] # get second half of average spike
temp_f2 = interp1d(temp_spike_second_half, 
                    range(temp_spike_peak_index, 
                    temp_spike_peak_index+len(temp_spike_second_half)), 
                    kind = "linear") # make function to interpolate
temp_half_width_end = temp_f2(half_peak) # find value corresponding to the half_peak

# Subtract beginning from end and multiply by the sampling rate to obtain the half_width in ms
half_width_ms = (temp_half_width_end - temp_half_width_start) * dt

# Get the derivative of time
diff_t = np.diff(time[0][:len(temp_spike)])
# And the derivative of voltage
diff_v = np.diff(temp_spike)
# Now get dvdt
dvdt = diff_v / diff_t
# Define threshold as 5% of the maximum value of dvdt
threshold_value = max(dvdt) * 0.05

from scipy.interpolate import interp1d # load function to interpolate
temp_2_f1 = interp1d(dvdt,
                    range(0, len(dvdt)), 
                    kind = "linear") # make function to interpolate
dvdt_threshold_index = temp_2_f1(threshold_value) # find index corresponding to threshold

temp_2_f2 = interp1d(range(0, len(temp_spike_first_half)), 
                    temp_spike_first_half,
                    kind = "linear") # make function to interpolate
spike_threshold_mV = temp_2_f2(dvdt_threshold_index+1) # find value corresponding to threshold, adding one to make up for the index lost due to the derivative

temp_2_f3 = interp1d(temp_spike_first_half,
                    range(0, len(temp_spike_first_half)), 
                    kind = "linear") # make function to interpolate
spike_threshold_index = temp_2_f3(spike_threshold_mV) # find index corresponding to threshold

threshold_to_peak_ms = (temp_spike_peak_index - spike_threshold_index) * dt

# %%
# Plot the average spike shape against its derivative
get_ipython().run_line_magic('matplotlib', 'qt')

fig = plt.figure(tight_layout = True, figsize = (6, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)

axs['A'].plot(temp_spike, 'k')
axs['A'].plot(int(spike_threshold_index), temp_spike[int(spike_threshold_index)], "or")
axs['A'].plot(temp_spike_peak_index, temp_spike[temp_spike_peak_index], "or")
axs['A'].plot(temp_spike_trough_index, temp_spike[temp_spike_trough_index], "or")
axs['A'].plot(temp_spike_adp_index, temp_spike[temp_spike_adp_index], "or")
axs['A'].set_title('Average spike', fontsize = 14)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([temp_spike_index-100, temp_spike_index+200])

axs['B'].plot(temp_spike[1:], dvdt, 'k')
axs['B'].set_title('Phase plot', fontsize = 14)
axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
axs['B'].set_xlim([-100, 50])

fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
plt.show()

#%%
# Print the extracted parameters
print(f'The test pulse command is       {np.mean(test_pulse_command_pA)} pA')
print(f'The injected current is         {np.round(np.mean(injected_current_pA), 2)} pA')
print(f'The holding is                  {np.round(np.mean(holding_mV), 2)} mV')
print(f'The peak is                     {np.round(peak_mV, 2)} mV')
print(f'The trough is                   {np.round(trough_mV, 2)} mV')
print(f'The adp is                      {np.round(adp_peak_mV, 2)} mV')
print(f'The ahp is                      {np.round(ahp_trough_mV, 2)} mV')
print(f'The peak to trough is           {np.round(peak_to_trough_magnitude, 2)} mV')
print(f'The trough to adp is            {np.round(trough_to_adp_magnitude, 2)} mV')
print(f'The adp to ahp is               {np.round(adp_to_ahp_magnitude, 2)} mV')
print(f'The peak to trough is           {np.round(peak_to_trough_ms, 2)} ms')
print(f'The trough to adp is            {np.round(trough_to_adp_ms, 2)} ms')
print(f'The adp to ahp is               {np.round(adp_to_ahp_ms, 2)} ms')
print(f'The half width is               {np.round(half_width_ms, 2)} ms')
print(f'The spike threshold is          {np.round(spike_threshold_mV, 2)} mV')
print(f'The the threshold to peak is    {np.round(threshold_to_peak_ms, 2)} ms')

# %%
