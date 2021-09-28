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
cut_spikes_baselined_clean, parameters_clean = cleanSpikes(file_name, cut_spikes_baselined_QC)
parameters_clean

# %%
# Compute average spike
average_spike = averageSpikes(cut_spikes_baselined_clean)
print("average spike calculated")

# %%
# Compute average spike parameters
parameters_avg_spike = getSpikeParameters(file_name, average_spike, threshold_onset_factor = 0.04, threshold_end_factor = 50)

# %%
# Compute firing frequency
firing_frequency_df, spikes_by_sweep_df, spikes_by_window_df = getFiringRate(file_name, channels_df, sweep_IB_concatenated, pseudo_sweep_concatenated, Rseal_df, peaks_QC, n_bins = 100)

# %%
interspike_interval_df = getInterspikeInterval(sweep_IB_concatenated, pseudo_sweep_concatenated, peaks_QC, sampling_rate_khz = 25)
interspike_interval_df

# %% [markdown]
#########################################################################
# ## 1 | Make a function to save results from one cell
# The final step is to save all the results we have extracted from a cell, in a way that can be easily retrieved later on to summarise, test, and plot across groups and conditions.
#########################################################################

# %%
# Info
folder_name
file_name 

# Results
Rseal_df #data frame
sweep_IB_concatenated, pseudo_sweep_concatenated #array, array
peaks, peaks_properties, parameters_find_peaks #array, dict, data frame
cut_spikes, cut_spikes_holding, cut_spikes_baselined #array, array, array,
peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC #array, array, array, array, data frame
cut_spikes_baselined_clean #array
average_spike #array
parameters_avg_spike #data frame
firing_frequency_df, spikes_by_sweep_df, spikes_by_window_df #data frame, data frame, data frame
interspike_interval_df #data frame

# %%
# Save numpy arrays as .npz
# This allows to save several variables in one file and can be easily retrieved. For now we will save everything we extract during the analysis, but the number of variables saved could potentially be reduced if it becomes too heavy.
# sweep_IB_concatenated, pseudo_sweep_concatenated
# peaks, cut_spikes, cut_spikes_holding, cut_spikes_baselined
# peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC 
# cut_spikes_baselined_clean
# average_spike

save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\analysis_sample_cells\results_test"
file_id = [file_name.split('.')[0]] # Get the file name without the extension

# Save results
np.savez_compressed(os.path.join(save_path, file_id[0] + "_results.npz"), sweep_IB_concatenated = sweep_IB_concatenated, pseudo_sweep_concatenated = pseudo_sweep_concatenated, peaks = peaks, cut_spikes = cut_spikes, cut_spikes_holding = cut_spikes_holding, cut_spikes_baselined = cut_spikes_baselined, peaks_QC = peaks_QC, cut_spikes_QC = cut_spikes_QC, cut_spikes_holding_QC = cut_spikes_holding_QC, cut_spikes_baselined_QC = cut_spikes_baselined_QC, cut_spikes_baselined_clean = cut_spikes_baselined_clean, average_spike = average_spike)

# Load saved results
data_test = np.load(os.path.join(save_path, file_id[0] + "_results.npz"))
print([key for key in data_test])
data_test['cut_spikes_baselined_clean']


# %%
# Test how to save one dataframe into a json file and retrieve it
import json
save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\analysis_sample_cells\results_test"
file_id = [file_name.split('.')[0]] # Get the file name without the extension

# Save Rseal
Rseal_df.to_json(os.path.join(save_path, file_id[0] + "_Rseal.json"))

# Load saved results
Rseal_df_test = pd.read_json(os.path.join(save_path, file_id[0] + "_Rseal.json"))
Rseal_df_test

# %%
# Test how to convert a dictionary into dataframe and then save it into a json file and retrieve it

save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\analysis_sample_cells\results_test"
file_id = [file_name.split('.')[0]] # Get the file name without the extension

pd.DataFrame.from_dict(peaks_properties, orient = 'index').to_json(os.path.join(save_path, file_id[0] + "_df_peaks_properties.json"))

peaks_properties_test = pd.read_json(os.path.join(save_path, file_id[0] + "_df_peaks_properties.json"))
peaks_properties_test

# %%
# Save pandas dataframes as .json
save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\analysis_sample_cells\results_test"
file_id = [file_name.split('.')[0]] # Get the file name without the extension

# Rseal_df
Rseal_df.to_json(os.path.join(save_path, file_id[0] + "_df_Rseal.json"))

# peaks_properties, parameters_find_peaks
pd.DataFrame.from_dict(peaks_properties, orient = 'index').to_json(os.path.join(save_path, file_id[0] + "_df_peaks_properties.json"))
parameters_find_peaks.to_json(os.path.join(save_path, file_id[0] + "_df_parameters_find_peaks.json"))

# parameters_QC
parameters_QC.to_json(os.path.join(save_path, file_id[0] + "_df_parameters_QC.json"))

# parameters_avg_spike
parameters_avg_spike.to_json(os.path.join(save_path, file_id[0] + "_df_parameters_avg_spike.json"))


# firing_frequency_df, spikes_by_sweep_df, spikes_by_window_df
firing_frequency_df.to_json(os.path.join(save_path, file_id[0] + "_df_firing_frequency.json"))
spikes_by_sweep_df.to_json(os.path.join(save_path, file_id[0] + "_df_spikes_by_sweep.json"))
spikes_by_window_df.to_json(os.path.join(save_path, file_id[0] + "_df_spikes_by_window.json"))

# interspike_interval_df
interspike_interval_df.to_json(os.path.join(save_path, file_id[0] + "_df_interspike_interval.json"))

# To retrieve the data do:
# df_name = pd.read_json(os.path.join(save_path, file_id[0] + "_df_name.json"))

# %%
# Put it into a function
def saveLooseSealResults(
    save_path,
    file_name,
    sweep_IB_concatenated,
    pseudo_sweep_concatenated,
    peaks,
    cut_spikes,
    cut_spikes_holding,
    cut_spikes_baselined,
    peaks_QC,
    cut_spikes_QC,
    cut_spikes_holding_QC,
    cut_spikes_baselined_QC,
    cut_spikes_baselined_clean,
    average_spike,
    Rseal_df,
    peaks_properties,
    parameters_find_peaks,
    parameters_QC,
    parameters_clean,
    parameters_avg_spike,
    firing_frequency_df,
    spikes_by_sweep_df,
    spikes_by_window_df,
    interspike_interval_df
    ):
    """
    `saveLooseSealResults` takes all the outputs from the loose-seal analysis pipeline and saves them into the specified path. It first takes all the arrays and saves them into a single `.npz` file. It then saves each dataframe as an individual `.json` file.
    It prints "results saved" as an output.
    
    :save_path: path to the directory where the data will be saved.
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :sweep_IB_concatenated: numpy array containing the concatenated data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    :pseudo_sweep_concatenated: concatenated pseudo-sweep that has the same length and number of sweeps as the original data, with the difference that each sweep within the pseudo-sweep will be comprised of the number that reflects the real sweep ID.
    :peaks: indices of detected spikes obtained from `findSpikes()`.
    :cut_spikes: numpy array containing the cut spikes.
    :cut_spikes_holding: numpy array containing the baseline before each peak.
    :cut_spikes_baselined: numpy array containing the baselined cut spikes.
    :peaks_QC: indices of the detected spikes obtained from `findSpikes()`, after quality control.
    :cut_spikes_QC: numpy array containing the cut spikes after quality control.
    :cut_spikes_holding_QC: numpy array containing the baseline before each peak after quality control.
    :cut_spikes_baselined_QC: array containing the detected spikes after baselining and removing noise.
    :cut_spikes_baselined_clean: array containing the detected spikes after baselining, quality control, and removing the spikes incorrectly baselined.
    :average_spike: array containing the values of the average spike.
    :Rseal_df: data frame with the Rseal values across sweeps for the time of recording.
    :peaks_properties: dictionary containing the properties of the peaks returned by scipy's `find_peaks` in `findSpikes`.
    :parameters_find_peaks: dataframe with the parameters selected by the user when running `findSpikes`.
    :parameters_QC: dataframe with the filters used for quality control.
    :parameters_clean: dataframe with the filters used for spike clean up.
    :parameters_avg_spike: dataframe with the spike onset, end, and magnitude, as well as the total duration of the spike and the time from onset to peak.
    :firing_frequency_df: dataframe with the calculated firing frequency obtained by dividing the total number of detected spikes over length of recording.
    :spikes_by_sweep_df: dataframe with the calculated firing frequency for each sweep.
    :spikes_by_window_df: dataframe with the calculated firing frequency for each time window of our choice.
    :interspike_interval_df: dataframe containing the interspike interval together with the average and standard deviation of the  injected current between each pair of spikes.
    """
    file_id = [file_name.split('.')[0]] # Get the file name without the extension

    # Save all numpy arrays as a single .npz file
    np.savez_compressed(os.path.join(save_path, file_id[0] + "_results.npz"), sweep_IB_concatenated = sweep_IB_concatenated, pseudo_sweep_concatenated = pseudo_sweep_concatenated, peaks = peaks, cut_spikes = cut_spikes, cut_spikes_holding = cut_spikes_holding, cut_spikes_baselined = cut_spikes_baselined, peaks_QC = peaks_QC, cut_spikes_QC = cut_spikes_QC, cut_spikes_holding_QC = cut_spikes_holding_QC, cut_spikes_baselined_QC = cut_spikes_baselined_QC, cut_spikes_baselined_clean = cut_spikes_baselined_clean, average_spike = average_spike)

    # To retrieve the data from a .npz file into a variable do:
    # results_data = np.load(os.path.join(save_path, file_id[0] + "_results.npz"))
    # print([key for key in results_data])
    # Then you can retrieve one specific variable
    # average_spike = results_data['average_spike']

    # Save each pandas dataframe as .json file
    # Rseal_df
    Rseal_df.to_json(os.path.join(save_path, file_id[0] + "_df_Rseal.json"))
    # peaks_properties - first convert dict to dataframe and then save as .json
    pd.DataFrame.from_dict(peaks_properties, orient = 'index').to_json(os.path.join(save_path, file_id[0] + "_df_peaks_properties.json"))
    # parameters_find_peaks
    parameters_find_peaks.to_json(os.path.join(save_path, file_id[0] + "_df_parameters_find_peaks.json"))
    # parameters_QC
    parameters_QC.to_json(os.path.join(save_path, file_id[0] + "_df_parameters_QC.json"))
    # parameters_clean
    parameters_clean.to_json(os.path.join(save_path, file_id[0] + "_df_parameters_clean.json"))
    # parameters_avg_spike
    parameters_avg_spike.to_json(os.path.join(save_path, file_id[0] + "_df_parameters_avg_spike.json"))
    # firing_frequency_df, spikes_by_sweep_df, spikes_by_window_df
    firing_frequency_df.to_json(os.path.join(save_path, file_id[0] + "_df_firing_frequency.json"))
    spikes_by_sweep_df.to_json(os.path.join(save_path, file_id[0] + "_df_spikes_by_sweep.json"))
    spikes_by_window_df.to_json(os.path.join(save_path, file_id[0] + "_df_spikes_by_window.json"))
    # interspike_interval_df
    interspike_interval_df.to_json(os.path.join(save_path, file_id[0] + "_df_interspike_interval.json"))
    
    # To retrieve the data from a .json file into a dataframe do:
    # df_name = pd.read_json(os.path.join(save_path, file_id[0] + "_df_name.json"))

    print('results saved')

# %%
# Test function
save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\analysis_sample_cells\results_test"

saveLooseSealResults(
    save_path,
    file_name,
    sweep_IB_concatenated,
    pseudo_sweep_concatenated,
    peaks,
    cut_spikes,
    cut_spikes_holding,
    cut_spikes_baselined,
    peaks_QC,
    cut_spikes_QC,
    cut_spikes_holding_QC,
    cut_spikes_baselined_QC,
    cut_spikes_baselined_clean,
    average_spike,
    Rseal_df,
    peaks_properties,
    parameters_find_peaks,
    parameters_QC,
    parameters_clean,
    parameters_avg_spike,
    firing_frequency_df,
    spikes_by_sweep_df,
    spikes_by_window_df,
    interspike_interval_df
)