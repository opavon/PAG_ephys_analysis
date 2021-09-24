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
from utilities import importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes
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
peaks, properties, parameters_used = findSpikes(file_name, sweep_IB_concatenated)

# %%
cut_spikes, cut_spikes_holding, cut_spikes_baselined = cutSpikes(sweep_IB_concatenated, peaks)
print("spikes cut")

# %% [markdown]
# ## 1 | Make a function to QC and average detected spikes

# %%
# We have different parameters we can look at in order to identify and remove them. If we take a look at the properties of the detected peaks, we can see that spikes and noise differ in the `peak_heights`, the `widths`, and the `width_heights`. We should be able to use this parameters to further optimize our function and remove the instances where noise is still detected, before proceeding to extract any parameters from the data (such as firing rate, ISIs, spike onset, or spike duration).

# Plot cut and baselined spikes together with the main QC metrics

import matplotlib.cm as cm
baselined_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined)))

get_ipython().run_line_magic('matplotlib', 'qt')
fig, axs = plt.subplots (2, 2, tight_layout=True)

for s in range(len(cut_spikes_baselined)):
    axs[0,0].plot(cut_spikes_baselined[s], color = baselined_spikes_colors[s])
axs[0,0].set_title('Cut and baselined spikes', fontsize = 10)
axs[0,0].set_xlim([80, 180])

axs[0,1].hist(properties['widths'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
axs[0,1].set_title('Peak widths', fontsize = 10)

axs[1,0].hist(properties['peak_heights'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
axs[1,0].set_title('Peak heights', fontsize = 10)

axs[1,1].hist(properties['width_heights'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
axs[1,1].set_title('Width heights', fontsize = 10)

plt.suptitle('Figure: QC metrics', fontsize = 14)
plt.show()

# %%
# Make function
def plotSpikesQC(
    file_name,
    properties,
    cut_spikes_baselined
    ):
    """
    `plotSpikesQC` generates a summary plot that can be used to determine the metrics that can be used to quality check the detected spikes. The summary plot contains (1) a subplot with all the detected spikes after cutting and baselining, (2) and three subplots with the histograms of the main metrics that can be used to detect noise in the detected spikes, which are `widths`, `width_heights`, and `peak_heights`. It only outputs the plot for visualisation purposes and does not return any variable. 
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :properties: dictionary containing properties of the peaks returned by scipy's `find_peaks` in `findSpikes`.
    :cut_spikes_baselined: numpy array containing the baselined cut spikes.
    """

    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

    # Get color palette and generate one color for each spike
    import matplotlib.cm as cm
    baselined_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined)))

    # Generate figure layout
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig, axs = plt.subplots (2, 2, tight_layout = True)

    # Plot cut and baselined spikes
    for s in range(len(cut_spikes_baselined)):
        axs[0,0].plot(cut_spikes_baselined[s], color = baselined_spikes_colors[s])
    axs[0,0].set_title('Cut and baselined spikes', fontsize = 12)
    axs[0,0].set_xlim([((len(cut_spikes_baselined[0])/2)-45), ((len(cut_spikes_baselined[0])/2)+55)])
    axs[0,0].set_ylabel('current [pA]')

    # Plot Histogram of the height at which widths where evaluated
    axs[0,1].hist(properties['width_heights'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
    axs[0,1].set_title('Width heights ["wh"]', fontsize = 12)
    # Plot Histogram of peak widths
    axs[1,0].hist(properties['widths'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
    axs[1,0].set_title('Peak widths ["pw"]', fontsize = 12)
    # Plot Histogram of peak heights
    axs[1,1].hist(properties['peak_heights'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
    axs[1,1].set_title('Peak heights ["ph"]', fontsize = 12)

    # Add title
    plt.suptitle(f'QC metrics for {cell_id[0]}', fontsize = 14)
    
    # Move figure to top left corner
    fig.canvas.manager.window.move(0, 0)
    plt.show()

# %%
# Test function
plotSpikesQC(file_name, properties, cut_spikes_baselined)

# %%
# Choose the QC metrics and show results


# %%
get_ipython().run_line_magic('matplotlib', 'qt')

cmap = plt.get_cmap('Pastel2')

filter_by = None # choose 'wh', 'w', or 'ph'.

QC_wh_min = float('-inf') # width heights
QC_wh_max = float('inf') # width heights

QC_w_min = float('-inf') # widths
QC_w_max = float('inf') # widths

QC_ph_min = float('-inf') # peak heights
QC_ph_max = float('inf') # peak heights

filter_by = 'wh'
QC_wh_max = 0

fig = plt.figure()

for s in range(len(cut_spikes_baselined)):
    if filter_by == 'wh' and QC_wh_min < properties['width_heights'][s] < QC_wh_max:
        plt.plot(cut_spikes_baselined[s], color = cmap(5))
    elif filter_by == 'w' and QC_w_min < properties['widths'][s] < QC_w_max:
        plt.plot(cut_spikes_baselined[s], color = cmap(3))
    elif filter_by == 'ph' and QC_ph_min < properties['peak_heights'][s] < QC_ph_max:
        plt.plot(cut_spikes_baselined[s], color = cmap(1))
    else:
        plt.plot(cut_spikes_baselined[s], color = cmap(0))

plt.title('Spikes colored by QC parameters', fontsize = 14)
plt.ylabel('current [pA]')
plt.xlim([80, 180])
fig.canvas.manager.window.move(0, 0)
plt.show()

# %%
# Make function
def getSpikesQC(
    file_name,
    properties,
    cut_spikes_baselined,
    filter_by = None, # filter to apply
    QC_wh_min = float('-inf'), # width heights
    QC_wh_max = float('inf'), # width heights
    QC_pw_min = float('-inf'), # widths
    QC_pw_max = float('inf'), # widths
    QC_ph_min = float('-inf'), # peak heights
    QC_ph_max = float('inf'), # peak heights
    ):
    """
    `getSpikesQC` . 
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :properties: dictionary containing properties of the peaks returned by scipy's `find_peaks` in `findSpikes`.
    :cut_spikes_baselined: numpy array containing the baselined cut spikes.
    :filter_by:
    :QC_wh_min:
    :QC_wh_max:
    :QC_pw_min:
    :QC_pw_max:
    :QC_ph_min:
    :QC_ph_max:
    """

    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot
    
    # Get color palette and generate one color for each metric
    cmap = plt.get_cmap('tab20')
    c_spikes = cmap(5) # green - clean spikes
    c_ph = cmap(3) # orange - noise by peak height
    c_pw = cmap(7) # red - noise by peak width
    c_wh = cmap(9) # purple - noise by width height

    get_ipython().run_line_magic('matplotlib', 'qt')

    fig, axs = plt.subplots (2, 2, tight_layout = True)

    # Plot cut and baselined spikes colored by whether they pass the desired QC or not.
    for s in range(len(cut_spikes_baselined)):
        if 'wh' in filter_by and (properties['width_heights'][s] < QC_wh_min or properties['width_heights'][s] > QC_wh_max):
            axs[0,0].plot(cut_spikes_baselined[s], c = c_wh)
        elif 'pw' in filter_by and (properties['widths'][s] < QC_pw_min or properties['widths'][s] > QC_pw_max):
            axs[0,0].plot(cut_spikes_baselined[s], c = c_pw)
        elif 'ph' in filter_by and (properties['peak_heights'][s] < QC_ph_min or properties['peak_heights'][s] > QC_ph_max):
            axs[0,0].plot(cut_spikes_baselined[s], c = c_ph)
        else:
            axs[0,0].plot(cut_spikes_baselined[s], c = c_spikes)
    axs[0,0].set_title('Spikes colored by QC parameters', fontsize = 12)
    axs[0,0].set_xlim([((len(cut_spikes_baselined[0])/2)-45), ((len(cut_spikes_baselined[0])/2)+55)])
    axs[0,0].set_ylabel('current [pA]')

    # Plot Histogram of the height at which widths where evaluated
    n_1, bins_1, patches_1 = axs[0,1].hist(properties['width_heights'], bins = 100, density = False, histtype = 'bar', log = True)
    for i in range(len(patches_1)):
        if (bins_1[i] < QC_wh_min or bins_1[i] > QC_wh_max):
            patches_1[i].set_facecolor(c_wh)
        else:
            patches_1[i].set_facecolor('lightgray')
    axs[0,1].set_title('Width heights ["wh"]', fontsize = 12)
    # Plot Histogram of peak widths
    n_2, bins_2, patches_2 = axs[1,0].hist(properties['widths'], bins = 100, density = False, histtype = 'bar', log = True, color = c_pw)
    for i in range(len(patches_2)):
        if (bins_2[i] < QC_pw_min or bins_2[i] > QC_pw_max):
            patches_2[i].set_facecolor(c_pw)
        else:
            patches_2[i].set_facecolor('lightgray')
    axs[1,0].set_title('Peak widths ["pw"]', fontsize = 12)
    # Plot Histogram of peak heights
    n_3, bins_3, patches_3 = axs[1,1].hist(properties['peak_heights'], bins = 100, density = False, histtype = 'bar', log = True, color = c_ph)
    for i in range(len(patches_3)):
        if (bins_3[i] < QC_ph_min or bins_3[i] > QC_ph_max):
            patches_3[i].set_facecolor(c_ph)
        else:
            patches_3[i].set_facecolor('lightgray')
    axs[1,1].set_title('Peak heights ["ph"]', fontsize = 12)

    # Add title
    plt.suptitle(f'QCed spikes from {cell_id[0]}', fontsize = 14)
    
    # Move figure to top left corner
    fig.canvas.manager.window.move(0, 0)
    plt.show(block = True)

    happy = input("Are you happy with your choice of prominence? y/n")

    if happy == 'y':
        print(f"found {len(peaks)} spikes")
        parameters_QC = pd.DataFrame([[QC_wh_min, QC_wh_max, QC_pw_min, QC_pw_max, QC_ph_min, QC_ph_max]], columns = ['QC_wh_min', 'QC_wh_max', 'QC_pw_min', 'QC_pw_max', 'QC_ph_min', 'QC_ph_max'], index = cell_id)
    else:
        print('Try running findSpikes() again')

    plt.close()

    return parameters_QC # pandas data frame

# %%
# Test function
parameters_QC = getSpikesQC(file_name, properties, cut_spikes_baselined, filter_by=['ph'], QC_ph_min=0)
print(parameters_QC)