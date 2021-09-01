# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

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
from utilities import importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes
print("done!")

# %%
# Load data for LIAM cell (contains spikes in test_pulse)
channels_data_frame, time, dt, folder_name, file_name = importFile(curated_channel = 'Sweeps_Analysis')
print("file imported")

# %%
# Concatenate sweeps
sweep_IB_concatenated, pseudo_sweep_concatenated = concatenateSweeps(file_name, channels_data_frame)
print("sweeps concatenated")

# %%
# Find spikes
peaks, properties, parameters_used = findSpikes(file_name, sweep_IB_concatenated)

# %% [markdown]
# ## 1 | Make a function to cut and baseline spikes

# %%
cut_spikes = [sweep_IB_concatenated[peaks[p]-125 : peaks[p]+125] for p in range(len(peaks))]
len(cut_spikes)

# %%
cut_spikes_holding = [np.mean(sweep_IB_concatenated[peaks[p]-100 : peaks[p]-25]) for p in range(len(peaks))]
len(cut_spikes_holding)

# %%
cut_spikes_baselined = [cut_spikes[i] - cut_spikes_holding[i] for i in range(len(cut_spikes))]
len(cut_spikes_baselined)
# %%

# %%
def cutSpikes(
    file_name,
    sweep_IB_concatenated,
    peaks
    ):
    """
    `cutSpikes` cuts an interval of 10 ms around each peak for plotting and further analysis. It then calculates a baseline for each peak by averaging 1-3 ms, leaving out the first ms before the peak index as it will contain the spike itself. Finally, it subtracts the calculated value to baseline the cut spikes, which will facilitate visualisation and quality control. It returns three numpy arrays of the same length containing the cut spikes, the baseline before each peak, and the resulting baselined cut spikes.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :sweep_IB_concatenated: numpy array containing the concatenated data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    :peaks: indices of detected spikes obtained from `findSpikes()`.
    """
    
    # Cut 125 samples (5 ms) before and after each peak
    cut_spikes = np.array([sweep_IB_concatenated[(peaks[p]-125) : (peaks[p]+125)] for p in range(len(peaks))])

    # Get baseline for each spike by averaging 1-3 ms before each peak
    cut_spikes_holding = np.array([np.mean(sweep_IB_concatenated[(peaks[p]-100) : (peaks[p]-25)]) for p in range(len(peaks))])

    # Subtract baseline from cut spikes
    cut_spikes_baselined = np.array([cut_spikes[i] - cut_spikes_holding[i] for i in range(len(cut_spikes))])

    return cut_spikes, cut_spikes_holding, cut_spikes_baselined # ndarray, ndarray, ndarray


# %% 
# Test function
cut_spikes, cut_spikes_holding, cut_spikes_baselined = cutSpikes(file_name, sweep_IB_concatenated, peaks)

#%%
# Plot cut and baselined spikes
import matplotlib.cm as cm
baselined_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined)))

for s in range(len(cut_spikes_baselined)):
    plt.plot(cut_spikes_baselined[s], color = baselined_spikes_colors[s])

plt.title('Cut and baselined spikes', fontsize = 14)
plt.ylabel('current [pA]')
plt.xlim([80, 180])
plt.show()
# %%
