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
from utilities import importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes, plotSpikesQC, getSpikesQC, denoiseSpikes, cleanSpikes, averageSpikes
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
# Remove detected peaks that correspond to noise and not spikes
peaks_denoised, cut_spikes_baselined_denoised, parameters_denoise = denoiseSpikes(file_name, peaks, peaks_properties, cut_spikes_baselined, filter_by=['ph'], QC_ph_min=10)

# %%
# Remove the spikes that were incorrectly baselined
cut_spikes_baselined_clean = cleanSpikes(file_name, cut_spikes_baselined_denoised)

# %%
# Compute average spike
average_spike = averageSpikes(cut_spikes_baselined_clean)


# %% [markdown]
# ## 1 | Make a function to extract key parameters from averages spike

# %%