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
from utilities import importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes, plotSpikesQC, getSpikesQC
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

# %% [markdown]
# ## 1 | Make a function to remove peaks that are not spikes

# %%
parameters_QC['QC_wh_min'][0]

# %%
getSpikesQC(file_name, peaks_properties, cut_spikes_baselined, filter_by=['ph'], QC_ph_min=10)

# %%
noise_indices_tmp = np.where(peaks_properties['width_heights'] < 10)
noise_indices = noise_indices_tmp[0]
cut_spikes_baselined_denoised = np.delete(cut_spikes_baselined, noise_indices, 0)
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
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner

# %%
peaks_denoised = np.delete(peaks, noise_indices, 0)
print(len(peaks)) # original peaks detected
print(len(peaks_denoised)) # denoised peaks to be used for firing rate
print(len(cut_spikes_baselined_denoised))

# %%
def denoiseSpikes(
    file_name,
    peaks,
    peaks_properties,
    cut_spikes_baselined,
    filter_by = ['wh', 'pw', 'ph'],
    QC_wh_min = float('-inf'),
    QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'),
    QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'),
    QC_ph_max = float('inf'),
    ):
    """
    `denoiseSpikes` removes detected peaks according to the chosen parameters. It first plots the cut, baselined, and denoised spikes to visualise whether the selected parameters lead to a successful denoising. It then removes the indices corresponding to noise from `peaks` and `cut_spikes_baselined`. It returns an array containing the `peaks_denoised` and another containing the `cut_spikes_baselined_denoised`, which can be used for downstream analysis to compute firing rate and other parameters. It also returns a data frame with the filters used for denoising.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :peaks: indices of detected spikes obtained from `findSpikes()`.
    :peaks_properties: dictionary containing properties of the peaks returned by scipy's `find_peaks` in `findSpikes`.
    :cut_spikes_baselined: numpy array containing the baselined cut spikes.
    :filter_by: metrics to be used to detect noise. Defaults to ['wh', 'pw', 'ph']. `width_heights`, `widths`, and `peak_heights`
    :QC_wh_min: value of `width_heights` below which a peak will be considered noise. Defaults to -inf.
    :QC_wh_max: value of `width_heights` above which a peak will be considered noise. Defaults to inf.
    :QC_pw_min: value of `widths` below which a peak will be considered noise. Defaults to -inf.
    :QC_pw_max: value of `widths` above which a peak will be considered noise. Defaults to inf.
    :QC_ph_min: value of `peak_heights` below which a peak will be considered noise. Defaults to -inf.
    :QC_ph_max: value of `peak_heights` above which a peak will be considered noise. Defaults to inf.
    """
    
    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

    # Use the selected parameters to find the indices of peaks that are not spikes
    noise_indices = []
    
    if 'wh' in filter_by:
        noise_indices_wh = np.where((peaks_properties['width_heights'] < QC_wh_min) | (peaks_properties['width_heights'] > QC_wh_max))
        noise_indices.append(noise_indices_wh[0])
    elif 'pw' in filter_by:
        noise_indices_pw = np.where((peaks_properties['widths'] < QC_pw_min) | (peaks_properties['widths'] > QC_pw_max))
        noise_indices.append(noise_indices_pw[0])
    elif 'ph' in filter_by:
        noise_indices_ph = np.where((peaks_properties['peak_heights'] < QC_ph_min) | (peaks_properties['peak_heights'] > QC_ph_max))
        noise_indices.append(noise_indices_ph[0])

    # Remove the indices corresponding to noise 
    cut_spikes_baselined_denoised = np.delete(cut_spikes_baselined, noise_indices, 0)
    peaks_denoised = np.delete(peaks, noise_indices, 0)

    # Plot cut, baselined, and denoised spikes to check whether denoising is complete.
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
    fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
    plt.show(block = True)

    # Check whether denoising is complete
    happy = input("Are you happy with your choice of parameters for denoising? y/n")

    if happy == 'y':
        print('denoising completed')
        parameters_denoise = pd.DataFrame([[QC_wh_min, QC_wh_max, QC_pw_min, QC_pw_max, QC_ph_min, QC_ph_max, filter_by]], columns = ['QC_wh_min', 'QC_wh_max', 'QC_pw_min', 'QC_pw_max', 'QC_ph_min', 'QC_ph_max', 'filter_by'], index = cell_id)
    else:
        print('Try running denoiseSpikes() again with different parameters')
        parameters_denoise = []

    plt.close()

    return peaks_denoised, cut_spikes_baselined_denoised, parameters_denoise # ndarray, ndarray, pandas data frame

# %%
peaks_denoised, cut_spikes_baselined_denoised, parameters_denoise = denoiseSpikes(file_name, peaks, peaks_properties, cut_spikes_baselined, filter_by=['ph'], QC_ph_min=10)

print(len(cut_spikes_baselined))
print(len(peaks))

print(len(cut_spikes_baselined_denoised))
print(len(peaks_denoised))
parameters_denoise
