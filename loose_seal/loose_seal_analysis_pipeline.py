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
# Load data
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
peaks, peaks_properties, cut_spikes, cut_spikes_holding, cut_spikes_baselined = cutSpikes(sweep_IB_concatenated, peaks, peaks_properties)
print("spikes cut")

# %%
# Examine cut spikes before quality control
plotSpikesQC(file_name, peaks, peaks_properties, cut_spikes_baselined)

# %%
# Choose the QC metrics and remove detected peaks that correspond to noise and not spikes
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC = spikesQC(
    file_name, peaks, peaks_properties,
    cut_spikes, cut_spikes_holding, cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'), QC_p_max = float('inf'),
    QC_wh_min = float('-inf'), QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'), QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'), QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'), QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'), QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'), QC_rb_max = float('inf')
    )
parameters_QC

# %%
# Remove the spikes that were incorrectly baselined
cut_spikes_baselined_clean, parameters_clean = cleanSpikes(file_name, cut_spikes_baselined_QC)
parameters_clean

# %%
# Compute average spike
average_spike = averageSpikes(cut_spikes_baselined_clean)

# %%
# Compute average spike parameters
parameters_avg_spike = getSpikeParameters(file_name, cut_spikes_baselined_clean, average_spike)
parameters_avg_spike

# %%
# Compute firing frequency
firing_frequency_df, spikes_by_sweep_df, spikes_by_window_df = getFiringRate(file_name, channels_df, sweep_IB_concatenated, pseudo_sweep_concatenated, Rseal_df, peaks_QC, n_bins = 100)
firing_frequency_df

# %%
# Compute interspike intervals
interspike_interval_df = getInterspikeInterval(sweep_IB_concatenated, pseudo_sweep_concatenated, peaks_QC)
interspike_interval_df

# %%
# Save Results
vgat_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
vgat_kynac_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_kynerinc_picrotoxin"
vglut2_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_control"
vglut2_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_picrotoxin"

saveLooseSealResults(vgat_kynac_ptx_save_path, file_name, sweep_IB_concatenated, pseudo_sweep_concatenated, peaks, cut_spikes, cut_spikes_holding, cut_spikes_baselined, peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, cut_spikes_baselined_clean, average_spike, Rseal_df, peaks_properties, parameters_find_peaks, parameters_QC, parameters_clean, parameters_avg_spike, firing_frequency_df, spikes_by_sweep_df, spikes_by_window_df, interspike_interval_df)
# %%
