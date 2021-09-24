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
from utilities import * # includes functions importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes, plotSpikesQC, spikesQC, cleanSpikes, averageSpikes, getSpikeParameters, getFiringRate, getInterspikeInterval
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

# %%
interspike_interval_dataframe = getInterspikeInterval(sweep_IB_concatenated, pseudo_sweep_concatenated, peaks_QC, sampling_rate_khz = 25)
interspike_interval_dataframe

# %% [markdown]
#########################################################################
# ## 1 | Make a function to save results from one cell
# The final step is to save all the results we have extracted from a cell, in a way that can be easily retrieved later on to summarise, test, and plot across groups and conditions.
#########################################################################

# %%
