# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %% [markdown]
# ## 0 | Import packages and load test data

# %%
import os
import h5py
import numpy as np
import pandas as pd
import seaborn as sns
import tkinter
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from utilities import importFile, openFile, openHDF5file, getLooseRseal
from tkinter.filedialog import askopenfilename, askopenfilenames
from collections import defaultdict
from nptdms import TdmsFile
from scipy import stats
from scipy.signal import find_peaks
print("done!")

# %%
# Load data for LIAM cell (contains spikes in test_pulse)
channels_data_frame, time, dt, folder_name, file_name = importFile(curated_channel = 'Sweeps_Analysis')
print("file imported")

# %% [markdown]
# ## 1 | Make a function to extract and concatenate sweeps

# %%
# Extract sweeps
sweep_IB_tmp = np.array(channels_data_frame.loc['Channel B', :])
# Concatenate sweeps
sweep_IB_concatenated = np.concatenate(sweep_IB_tmp)
print('done!')

# %%
# Create and concatenate pseudo-sweep

pseudo_sweep_keys = []

for i, sweep in enumerate(sweep_IB_tmp):
    sweep_key = int(channels_data_frame.columns[i])
    sweep_keys_tmp = np.zeros(len(sweep), dtype = int) + sweep_key
    pseudo_sweep_keys.append(sweep_keys_tmp)

pseudo_sweep_concatenated = np.concatenate(pseudo_sweep_keys)

len(pseudo_sweep_concatenated) == len(sweep_IB_concatenated)

# %%
def concatenateSweeps(
    file_name,
    channels_data_frame
    ):
    """
    `concatenateSweeps` extracts the sweeps containing the recorded signal from `channels_data_frame` and concatenates them. It also creates a concatenated pseudo-sweep that has the same length and number of sweeps as the original data, with the difference that each sweep within the pseudo-sweep will be comprised of the number that reflects the real sweep ID.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :extracted_channels_data_frame: data frame with extracted data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    """

    # Extract sweeps
    sweep_IB = np.array(channels_data_frame.loc['Channel B', :])
    
    # Concatenate sweeps
    sweep_IB_concatenated = np.concatenate(sweep_IB)
    
    # Create and concatenate pseudo-sweep
    pseudo_sweep_keys = []
    
    for i, sweep in enumerate(sweep_IB):
        sweep_key = int(channels_data_frame.columns[i])
        sweep_keys_tmp = np.zeros(len(sweep), dtype = int) + sweep_key
        pseudo_sweep_keys.append(sweep_keys_tmp)
    
    pseudo_sweep_concatenated = np.concatenate(pseudo_sweep_keys)

    return sweep_IB_concatenated, pseudo_sweep_concatenated

# %%
# Test the function
sweep_IB_concatenated_test, pseudo_sweep_concatenated_test = concatenateSweeps(file_name, channels_data_frame)

len(pseudo_sweep_concatenated_test) == len(sweep_IB_concatenated_test)