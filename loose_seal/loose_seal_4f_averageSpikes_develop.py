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
from utilities import importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes, plotSpikesQC, getSpikesQC, denoiseSpikes
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
# Choose the QC metrics and show results
parameters_QC = getSpikesQC(file_name, peaks_properties, cut_spikes_baselined, filter_by=['ph'], QC_ph_min=10)
parameters_QC

# %%
peaks_denoised, cut_spikes_baselined_denoised, parameters_denoise = denoiseSpikes(file_name, peaks, peaks_properties, cut_spikes_baselined, filter_by=['ph'], QC_ph_min=10)

print(len(peaks))
print(len(peaks_denoised))
print(len(cut_spikes_baselined))
print(len(cut_spikes_baselined_denoised))

# %%
import matplotlib.cm as cm
denoised_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined_denoised)))
get_ipython().run_line_magic('matplotlib', 'qt') # avoid 'tk' here
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
for s in range(len(cut_spikes_baselined_denoised)):
    plt.plot(cut_spikes_baselined_denoised[s], color = denoised_spikes_colors[s])
plt.xlim([((len(cut_spikes_baselined_denoised[0])/2)-45), ((len(cut_spikes_baselined_denoised[0])/2)+55)])
plt.title('Cut, baselined, and denoised spikes', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
fig.canvas.manager.window.move(0, 0)
plt.show()

# %% [markdown]
# ## 1 | Make a function to remove poorly baselined spikes before computing average

# %%
# The peak of the cut speaks is at the following index
len(cut_spikes_baselined_denoised[0])/2

# %%
# To find spikes that were not properly baselined, we can compare the values at the peak, and remove those not properly aligned with the others before we proceed to compute the average spike that we will use to extract parameters.

# To do that, we can stack the nested arrays. This will allow us to easily access the same index in all spikes at once, so we can compare where the peak of each baselined spike falls.
spikes_test = np.vstack(cut_spikes_baselined_denoised)
spikes_test[:,125] # get the peak values for each spike to find any not correctly baselined

get_ipython().run_line_magic('matplotlib', 'qt') # avoid 'tk' here
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
plt.hist(spikes_test[:,125], bins = 200, density = False, histtype = 'bar', log = True)
plt.title('Histograme of peak values for baselined spikes', fontsize = 14)
plt.xlabel('peak value [pA]', fontsize = 12)
fig.canvas.manager.window.move(0, 0)
plt.show()

# %%
# This is very useful as we can clearly see that only one cell is different than the rest. Let's put both things together:

spikes_test = np.vstack(cut_spikes_baselined_denoised) # stack nested array to access same position in all spikes
spikes_test[:,125] # get the peak values for each spike to find any not correctly baselined

file_id = [file_name.split('.')[0]] # Get the file name without the extension
cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

# Get color palette and generate one color for each spike
import matplotlib.cm as cm
denoised_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined_denoised)))

# Generate figure layout
get_ipython().run_line_magic('matplotlib', 'qt')
fig, axs = plt.subplots (1, 2, tight_layout = True, figsize = (9, 4), dpi = 100) # Set figure size

# Plot cut, baselined, denoised, and clean spikes
for s in range(len(cut_spikes_baselined_denoised)):
    axs[0].plot(cut_spikes_baselined_denoised[s], color = denoised_spikes_colors[s])
axs[0].set_title('Cut, baselined, and denoised spikes', fontsize = 12)
axs[0].set_xlim([((len(cut_spikes_baselined_denoised[0])/2)-45), ((len(cut_spikes_baselined_denoised[0])/2)+55)])
axs[0].set_xlabel('samples', fontsize = 12)
axs[0].set_ylabel('current [pA]', fontsize = 12)

# Plot Histogram of the peak values for each baselined spike
axs[1].hist(spikes_test[:,125], bins = 200, density = False, histtype = 'bar', log = True, color = 'k')
axs[1].set_title('Histograme of peak values for baselined spikes', fontsize = 12)
axs[1].set_xlabel('peak value [pA]', fontsize = 12)

# Add title
plt.suptitle(f'QC metrics for {cell_id[0]}', fontsize = 14)

# Move figure to top left corner
fig.canvas.manager.window.move(0, 0)
plt.show()


# %%
# Now that we can visually inspect where the peak of the wrongly baseline neurons fall, we can set a threshold to identify that spike and remove it.

# Select the spikes that couldn't be baselined
spikes_to_remove = np.where(spikes_test[:,125] > 0)
cut_spikes_baselined_clean = np.delete(cut_spikes_baselined_denoised, spikes_to_remove, 0)
print(len(cut_spikes_baselined_denoised))
print(len(cut_spikes_baselined_clean))

# %%
# Plot the baselined spikes after removing the ones that do not meet the chosen criteria
import matplotlib.cm as cm
denoised_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined_clean)))
get_ipython().run_line_magic('matplotlib', 'qt') # avoid 'tk' here
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
for s in range(len(cut_spikes_baselined_clean)):
    plt.plot(cut_spikes_baselined_clean[s], color = denoised_spikes_colors[s])
plt.xlim([((len(cut_spikes_baselined_clean[0])/2)-45), ((len(cut_spikes_baselined_clean[0])/2)+55)])
plt.title('Cut, baselined, and denoised spikes', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
fig.canvas.manager.window.move(0, 0)
plt.show()

# %% 

# Let's concatenate all the steps to test how the function would work. In principle, it should be similar to findSpikes() in the way that we can first look at the baselined spikes and the distribution of the peak values (which would be the best indicator of a spike being wrongly baslined), then set a threshold to identify those spikes that need to be removed, and then using that criteria to filter them out and visualize the result. We can finally ask whether the result is satisfactory before exiting the function.

cut_spikes_stack = np.vstack(cut_spikes_baselined_denoised) # stack nested array to access same position in all spikes
cut_spikes_peak_index = int(len(cut_spikes_baselined_denoised[0])/2) # get the index where the peak is

file_id = [file_name.split('.')[0]] # Get the file name without the extension
cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

# Get color palette and generate one color for each spike
import matplotlib.cm as cm
denoised_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined_denoised)))

# Generate figure layout
get_ipython().run_line_magic('matplotlib', 'qt')
fig, axs = plt.subplots (2, 2, tight_layout = True, figsize = (9, 5), dpi = 100) # Set figure size

# Plot cut, baselined, and denoised spikes
for s in range(len(cut_spikes_baselined_denoised)):
    axs[0,0].plot(cut_spikes_baselined_denoised[s], color = denoised_spikes_colors[s])
axs[0,0].set_title('Cut, baselined, and denoised spikes', fontsize = 12)
axs[0,0].set_xlim([((len(cut_spikes_baselined_denoised[0])/2)-45), ((len(cut_spikes_baselined_denoised[0])/2)+55)])
axs[0,0].set_xlabel('samples', fontsize = 12)
axs[0,0].set_ylabel('current [pA]', fontsize = 12)

# Plot Histogram of the peak values for each baselined spike
axs[0,1].hist(cut_spikes_stack[:,cut_spikes_peak_index], bins = 200, density = False, histtype = 'bar', log = True, color = 'k')
axs[0,1].set_title('Histogram of peak values for baselined spikes', fontsize = 12)
axs[0,1].set_xlabel('peak value [pA]', fontsize = 12)

# Add title
plt.suptitle(f'Baselined spikes for {cell_id[0]}', fontsize = 14)

# Move figure to top left corner
fig.canvas.manager.window.move(0, 0)
plt.pause(0.5)

# Based on the histogram above, select the peak value threshold that will identify spikes that were not properly baselined
peak_min = int(input("Enter the min value for the desired prominence"))

# Select the spikes that couldn't be baselined
spikes_to_remove = np.where(cut_spikes_stack[:,cut_spikes_peak_index] > peak_min)
cut_spikes_baselined_clean = np.delete(cut_spikes_baselined_denoised, spikes_to_remove, 0)
print(f"The number of denoised spikes was: {len(cut_spikes_baselined_denoised)}")
print(f"The number of clean spikes is: {len(cut_spikes_baselined_clean)}")

# Now show the results
clean_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined_clean)))

# Plot cut, baselined, denoised, and clean spikes
for s in range(len(cut_spikes_baselined_clean)):
    axs[1,0].plot(cut_spikes_baselined_clean[s], color = clean_spikes_colors[s])
axs[1,0].set_title('Cut, baselined, denoised, and cleaned spikes', fontsize = 12)
axs[1,0].set_xlim([((len(cut_spikes_baselined_clean[0])/2)-45), ((len(cut_spikes_baselined_clean[0])/2)+55)])
axs[1,0].set_xlabel('samples', fontsize = 12)
axs[1,0].set_ylabel('current [pA]', fontsize = 12)

# Plot Histogram of the peak values for each baselined spike
n_1, bins_1, patches_1 = axs[1,1].hist(cut_spikes_stack[:,cut_spikes_peak_index], bins = 200, density = False, histtype = 'bar', log = True)
for i in range(len(patches_1)):
    if (bins_1[i] > peak_min):
            patches_1[i].set_facecolor('r')
    else:
        patches_1[i].set_facecolor('lightgray')
axs[1,1].set_title('Histogram of peak values for baselined spikes', fontsize = 12)
axs[1,1].set_xlabel('peak value [pA]', fontsize = 12)

plt.pause(0.5)

# Check whether clean up is complete
happy = input("Are you happy with your choice of prominence? y/n")

if happy == 'y':
    print(f"The number of spikes removed was: {len(spikes_to_remove)}")
else:
    # Empty results just in case.
    print('Try running cleanSpikes() again')
    
plt.close()

# %%
def cleanSpikes(
    cut_spikes_baselined_denoised
    ):
    """
    `cleanSpikes` 
    
    :??:
    :??:
    """
    
    # Compute average from all detected spikes after baseline, QC, and clean up
    

    return cut_spikes_baselined_clean # ndarray

# %% [markdown]
# ## 2 | Make a function to average detected spikes

# %%
# Once we have removed the spikes we couldn't baseline, we can compute the average
average_spike = np.array(np.mean(cut_spikes_baselined_clean, 0))

get_ipython().run_line_magic('matplotlib', 'qt')
for s in range(len(cut_spikes_baselined_clean)):
    plt.plot(cut_spikes_baselined_clean[s], 'k')
plt.plot(average_spike, color = 'r')
plt.title('Figure 1h: Cut spikes with average in red', fontsize = 14)
plt.ylabel('current [pA]')
plt.xlim([80, 180])
plt.ylim([-200, 100])
plt.show()

# %%
def averageSpikes(
    cut_spikes_baselined_clean
    ):
    """
    `averageSpikes` 
    
    :??:
    :??:
    """
 
    # Compute average from all detected spikes after baseline, QC, and clean up
    average_spike = np.array(np.mean(cut_spikes_baselined_clean, 0))

    return average_spike # ndarray
