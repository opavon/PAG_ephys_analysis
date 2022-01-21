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
from utilities import * # includes functions importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes, plotSpikesQC, spikesQC, cleanSpikes, averageSpikes, getSpikeParameters, getFiringRate, getInterspikeInterval, saveLooseSealResults, combineJSONresults
print("done!")

# Paths to results
vgat_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
vgat_kynac_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_kynurenic_picrotoxin"
vglut2_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_control"
vglut2_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_picrotoxin"

# %%
# Load the extracted results for the average spike of a cell

# To retrieve the data from a .json file into a dataframe do:
    # df_name = pd.read_json(os.path.join(save_path, file_name))

average_spike_results = pd.read_json(os.path.join(vgat_ctrl_save_path, "dlpag_vgat_171113_c5_LIAI_OP_clear_VC_1_df_parameters_avg_spike.json"))

average_spike_results

# %%
# Load the average spike trace

# To retrieve the data from a .npz file into a variable do:
    # results_data = np.load(os.path.join(save_path, file_id[0] + "_results.npz"))
    # print([key for key in results_data])
    # Then you can retrieve one specific variable
    # average_spike = results_data['average_spike']
results_data = np.load(os.path.join(vgat_ctrl_save_path, "dlpag_vgat_171113_c5_LIAI_OP_clear_VC_1_results.npz"))

print([key for key in results_data])

average_spike = results_data["average_spike"]
plt.plot(average_spike)

# %%
# Get the index for where the peak is, defined by the cutSpikes() function (should be sample 150)
average_spike_peak_index = int(np.where(average_spike == min(average_spike))[0])
print(average_spike_peak_index)

# Check the peak magnitude you can recalculate and the one stored are the same:
print(min(average_spike))
print(average_spike_results["spike_magnitude_pA"][0])

# %%
# Check that the baseline you could recalculate and the one stored are the same:
baseline_average_spike = average_spike[(average_spike_peak_index-100):(average_spike_peak_index-25)]
baseline_average_spike_mean = np.mean(baseline_average_spike)

print(baseline_average_spike_mean)
print(average_spike_results['baseline_start_mean'][0])

# %%
# Compute the half_peak value (baseline to peak divided by two) that will be used to measure the half-width
half_peak = (average_spike_results["spike_magnitude_pA"][0] - average_spike_results['baseline_start_mean'][0]) / 2
half_peak

# %%
# One simple way to find the half-width would be to count how many samples we have below the half_peak value and multiply by the sampling rate to get ms.
half_width = len(np.where(average_spike < half_peak)[0])*0.04
print(half_width)

# However, that means that if by chance the sampling points falls right before or right after the cutoff, we may be facing an error of up to 1 sampling point, which in this case would be an error of 33%. Ideally, we would like to just find the x-value for the exact half_peak value as below, but unfortunately the following does not work.
np.where(average_spike == half_peak)[0]

# %%
# To work around this issue, we can interpolate our data. Scipy's interpolate allows us to generate a function that fits our data.
from scipy.interpolate import interp1d
temp_f1 = interp1d(average_spike, range(0, len(average_spike)), kind = "linear")

# We can then plot both our sampled points and the function
plt.plot(average_spike, "o", temp_f1(average_spike), average_spike, "-")

# We can also use the function to get the x value for a particular magnitude.
print(temp_f1(half_peak))
print(temp_f1(average_spike_results["spike_magnitude_pA"][0])) # should be 150

# %%
# Now, we need to get the first time we cross the half_peak value (before the peak), and the second time (after the peak). To do this, we are going to split the spike in two halves, and do the procedure separately.
average_spike_first_half = average_spike[:average_spike_peak_index]
temp_f2 = interp1d(average_spike_first_half, range(0, len(average_spike_first_half)), kind = "linear")
plt.plot(average_spike_first_half, "o", temp_f2(average_spike_first_half), average_spike_first_half, "-")
half_width_beginning = temp_f2(half_peak)

# %%
average_spike_second_half = average_spike[average_spike_peak_index:]
temp_f3 = interp1d(average_spike_second_half, range(150, 150+len(average_spike_second_half)), kind = "linear")
plt.plot(range(150, 150+len(average_spike_second_half)), average_spike_second_half, "o", temp_f3(average_spike_second_half), average_spike_second_half, "-")
half_width_end = temp_f3(half_peak)

# %%
# Finally, we can subtract beginning from end and multiply by the sampling rate to obtain a more accurate half_width
half_width_interpolated = (half_width_end - half_width_beginning) * 0.04
half_width_interpolated

# %%
print(half_width_interpolated)
print(half_width)

# %%
# Let's append the results to the original dataframe
average_spike_results["half_width_start"] = half_width_beginning
average_spike_results["half_width_end"] = half_width_end
average_spike_results["half_width_ms"] = half_width_interpolated
average_spike_results

# %%
# ##### Let's now try to iterate through all the files in a folder #####
# Choose folders
folders_to_check = [vgat_ctrl_save_path, 
                    vgat_kynac_ptx_save_path, 
                    vglut2_ctrl_save_path, 
                    vglut2_ptx_save_path]

results_type_avg_spike = '_df_parameters_avg_spike'
save_type = '_avg_spike'

sampling_rate_khz = 25
dt = 1 / sampling_rate_khz

for folder in folders_to_check:
    if 'vgat_control' in folder:
        vgat_ctrl_temp_list = [] # an empty list to store the data frames
        vgat_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type_avg_spike in results_file] # get the files that contain the type of results you want
        for file in vgat_ctrl_results_files:
            # Get the cell ID and assign it to the row label
            temp_file_id = [file.split('.')[0]]
            temp_cell_id = ['_'.join((temp_file_id[0].split('_'))[0:-4])]
            print(temp_cell_id)
            temp_1_avg_spike_results = pd.read_json(os.path.join(folder, file)) # read data frame from json file

            # We need to check wheter the cell we are looking at had any spikes. If number of spikes is zero, then we don't need to calculate anything.
            if isinstance(temp_1_avg_spike_results["spike_magnitude_pA"][0], float):
                temp_1_npz_results = np.load(os.path.join(folder, temp_cell_id[0] + '_results.npz'))
                temp_1_avg_spike = temp_1_npz_results["average_spike"]
                temp_1_avg_spike_peak_index = int(np.where(temp_1_avg_spike == min(temp_1_avg_spike))[0])
                
                # Compute the half_peak value (baseline to peak divided by two) that will be used to measure the half-width
                temp_1_half_peak = (temp_1_avg_spike_results["spike_magnitude_pA"][0] - temp_1_avg_spike_results['baseline_start_mean'][0]) / 2

                # Now, we need to get the first time we cross the half_peak value (before the peak), and the second time (after the peak). To do this, we are going to split the spike in two halves, and do the procedure separately.
                from scipy.interpolate import interp1d # load function to interpolate
                temp_1_avg_spike_first_half = temp_1_avg_spike[:temp_1_avg_spike_peak_index] # get first half of average spike
                temp_1_f1 = interp1d(temp_1_avg_spike_first_half, 
                                    range(0, len(temp_1_avg_spike_first_half)), 
                                    kind = "linear") # make function to interpolate
                temp_half_width_start = temp_1_f1(temp_1_half_peak) # find value corresponding to the half_peak
                
                temp_1_avg_spike_second_half = temp_1_avg_spike[temp_1_avg_spike_peak_index:] # get second half of average spike
                temp_1_f2 = interp1d(temp_1_avg_spike_second_half, 
                                    range(temp_1_avg_spike_peak_index, 
                                    temp_1_avg_spike_peak_index+len(temp_1_avg_spike_second_half)), 
                                    kind = "linear") # make function to interpolate
                temp_half_width_end = temp_1_f2(temp_1_half_peak) # find value corresponding to the half_peak
                
                # Subtract beginning from end and multiply by the sampling rate to obtain the half_width in ms
                temp_1_half_width_interpolated = (temp_half_width_end - temp_half_width_start) * dt

                # Append the results to the data frame
                temp_1_avg_spike_results["half_width_start"] = temp_half_width_start
                temp_1_avg_spike_results["half_width_end"] = temp_half_width_end
                temp_1_avg_spike_results["half_width_ms"] = temp_1_half_width_interpolated
                temp_1_avg_spike_results["avg_spike"] = [temp_1_avg_spike]
            
            # If, on the other hand, we didn't detect any spikes for this cell, we will have "NA" in the "spike_magnitude_pA" field. In that case, we just append "NA" to the new columns to keep the shape of the dataframe.
            if isinstance(temp_1_avg_spike_results["spike_magnitude_pA"][0], str):
                # Append the 'NA' to the data frame
                temp_1_avg_spike_results["half_width_start"] = 'NA'
                temp_1_avg_spike_results["half_width_end"] = 'NA'
                temp_1_avg_spike_results["half_width_ms"] = 'NA'
                temp_1_avg_spike_results["avg_spike"] = 'NA'

            vgat_ctrl_temp_list.append(temp_1_avg_spike_results) # append the data frame to the list
        
        vgat_ctrl_df = pd.concat(vgat_ctrl_temp_list) # concatenate all the data frames in the list
        #vgat_ctrl_df.to_json(os.path.join(folder, 'vgat_control_pooled' + save_type + '.json')) # save combined results as new .json file

vgat_ctrl_df

# %%
# Now we can put this into a function
def getSpikeHalfWidth( 
    folders_to_check,
    results_type = "_df_parameters_avg_spike",
    save_type = '_avg_spike',
    sampling_rate_khz = 25
    ):
    """
    `getSpikeHalfWidth` loads the data extracted from a cell, computes the half-width of its average spike, and appends the result in the JSON file containing the Spike Parameters.
    It returns a dataframe with the spike onset, end, and magnitude, as well as the total duration of the spike, the time from onset to peak, and the half-width. It also returns the average and standard deviation of the start and end baselines used to calculate the thresholds, which can be used to detect any differences in the baseline before and after the average spike.
    
    :folders_to_check: a list containing the paths to the four folders to check.
    :results_type: a string containing the type of result (without its .json extension) to load and combine. Should be '_df_parameters_avg_spike'.
    :save_type: a string to append to the saved file. 
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.
    """

    # Check conditions
    if not len(folders_to_check) == 4:
        print(f"Please provide the path to the four folders corresponding to: vgat_control, vgat_kynurenic_picrotoxin, vglut2_control, vglut2_picrotoxin")
        return None, None, None, None

    dt = 1 / sampling_rate_khz # calculate dt from sampling rate

    for folder in folders_to_check:
        if 'vgat_control' in folder:
            vgat_ctrl_temp_list = [] # an empty list to store the data frames
            vgat_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file] # get the files that contain the type of results you want
            for file in vgat_ctrl_results_files:
                # Get the cell ID
                temp_file_id = [file.split('.')[0]]
                temp_cell_id = ['_'.join((temp_file_id[0].split('_'))[0:-4])]

                temp_1_avg_spike_results = pd.read_json(os.path.join(folder, file)) # read data frame from json file

                # We need to check wheter the cell we are looking at had any spikes. If number of spikes is zero, then we don't need to calculate anything.
                if isinstance(temp_1_avg_spike_results["spike_magnitude_pA"][0], float):
                    temp_1_npz_results = np.load(os.path.join(folder, temp_cell_id[0] + '_results.npz')) # load data from current cell ID
                    temp_1_avg_spike = temp_1_npz_results["average_spike"] # retrieve average spike
                    temp_1_avg_spike_peak_index = int(np.where(temp_1_avg_spike == min(temp_1_avg_spike))[0]) # find peak indez
                    
                    # Compute the half_peak value (baseline to peak divided by two) that will be used to measure the half-width
                    temp_1_half_peak = (temp_1_avg_spike_results["spike_magnitude_pA"][0] - temp_1_avg_spike_results['baseline_start_mean'][0]) / 2

                    # Now, we need to get the first time we cross the half_peak value (before the peak), and the second time (after the peak). To do this, we are going to split the spike in two halves, and do the procedure separately.
                    from scipy.interpolate import interp1d # load function to interpolate
                    temp_1_avg_spike_first_half = temp_1_avg_spike[:temp_1_avg_spike_peak_index] # get first half of average spike
                    temp_1_f1 = interp1d(temp_1_avg_spike_first_half, 
                                        range(0, len(temp_1_avg_spike_first_half)), 
                                        kind = "linear") # make function to interpolate
                    temp_half_width_start = temp_1_f1(temp_1_half_peak) # find value corresponding to the half_peak
                    
                    temp_1_avg_spike_second_half = temp_1_avg_spike[temp_1_avg_spike_peak_index:] # get second half of average spike
                    temp_1_f2 = interp1d(temp_1_avg_spike_second_half, 
                                        range(temp_1_avg_spike_peak_index, 
                                        temp_1_avg_spike_peak_index+len(temp_1_avg_spike_second_half)), 
                                        kind = "linear") # make function to interpolate
                    temp_half_width_end = temp_1_f2(temp_1_half_peak) # find value corresponding to the half_peak

                    # Subtract beginning from end and multiply by the sampling rate to obtain the half_width in ms
                    temp_1_half_width_interpolated = (temp_half_width_end - temp_half_width_start) * dt

                    # Append the results to the data frame
                    temp_1_avg_spike_results["half_width_start"] = temp_half_width_start
                    temp_1_avg_spike_results["half_width_end"] = temp_half_width_end
                    temp_1_avg_spike_results["half_width_ms"] = temp_1_half_width_interpolated
                    temp_1_avg_spike_results["avg_spike"] = [temp_1_avg_spike]
                
                # If, on the other hand, we didn't detect any spikes for this cell, we will have "NA" in the "spike_magnitude_pA" field. In that case, we just append "NA" to the new columns to keep the shape of the dataframe.
                if isinstance(temp_1_avg_spike_results["spike_magnitude_pA"][0], str):
                    # Append the 'NA' to the data frame
                    temp_1_avg_spike_results["half_width_start"] = 'NA'
                    temp_1_avg_spike_results["half_width_end"] = 'NA'
                    temp_1_avg_spike_results["half_width_ms"] = 'NA'
                    temp_1_avg_spike_results["avg_spike"] = 'NA'

                vgat_ctrl_temp_list.append(temp_1_avg_spike_results) # append the data frame to the list
            
            vgat_ctrl_df = pd.concat(vgat_ctrl_temp_list) # concatenate all the data frames in the list
            vgat_ctrl_df.to_json(os.path.join(folder, 'vgat_control_pooled' + save_type + '.json')) # save combined results as new .json file
        
        if 'vgat_kynurenic_picrotoxin' in folder:
            vgat_kynac_ptx_temp_list = [] # an empty list to store the data frames
            vgat_kynac_ptx_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file] # get the files that contain the type of results you want
            for file in vgat_kynac_ptx_results_files:
                # Get the cell ID
                temp_file_id = [file.split('.')[0]]
                temp_cell_id = ['_'.join((temp_file_id[0].split('_'))[0:-4])]

                temp_2_avg_spike_results = pd.read_json(os.path.join(folder, file)) # read data frame from json file

                # We need to check wheter the cell we are looking at had any spikes. If number of spikes is zero, then we don't need to calculate anything.
                if isinstance(temp_2_avg_spike_results["spike_magnitude_pA"][0], float):
                    temp_2_npz_results = np.load(os.path.join(folder, temp_cell_id[0] + '_results.npz')) # load data from current cell ID
                    temp_2_avg_spike = temp_2_npz_results["average_spike"] # retrieve average spike
                    temp_2_avg_spike_peak_index = int(np.where(temp_2_avg_spike == min(temp_2_avg_spike))[0]) # find peak indez
                    
                    # Compute the half_peak value (baseline to peak divided by two) that will be used to measure the half-width
                    temp_2_half_peak = (temp_2_avg_spike_results["spike_magnitude_pA"][0] - temp_2_avg_spike_results['baseline_start_mean'][0]) / 2

                    # Now, we need to get the first time we cross the half_peak value (before the peak), and the second time (after the peak). To do this, we are going to split the spike in two halves, and do the procedure separately.
                    from scipy.interpolate import interp1d # load function to interpolate
                    temp_2_avg_spike_first_half = temp_2_avg_spike[:temp_2_avg_spike_peak_index] # get first half of average spike
                    temp_2_f1 = interp1d(temp_2_avg_spike_first_half, 
                                        range(0, len(temp_2_avg_spike_first_half)), 
                                        kind = "linear") # make function to interpolate
                    temp_half_width_start = temp_2_f1(temp_2_half_peak) # find value corresponding to the half_peak
                    
                    temp_2_avg_spike_second_half = temp_2_avg_spike[temp_2_avg_spike_peak_index:] # get second half of average spike
                    temp_2_f2 = interp1d(temp_2_avg_spike_second_half, 
                                        range(temp_2_avg_spike_peak_index, 
                                        temp_2_avg_spike_peak_index+len(temp_2_avg_spike_second_half)), 
                                        kind = "linear") # make function to interpolate
                    temp_half_width_end = temp_2_f2(temp_2_half_peak) # find value corresponding to the half_peak

                    # Subtract beginning from end and multiply by the sampling rate to obtain the half_width in ms
                    temp_2_half_width_interpolated = (temp_half_width_end - temp_half_width_start) * dt

                    # Append the results to the data frame
                    temp_2_avg_spike_results["half_width_start"] = temp_half_width_start
                    temp_2_avg_spike_results["half_width_end"] = temp_half_width_end
                    temp_2_avg_spike_results["half_width_ms"] = temp_2_half_width_interpolated
                    temp_2_avg_spike_results["avg_spike"] = [temp_2_avg_spike]
                
                # If, on the other hand, we didn't detect any spikes for this cell, we will have "NA" in the "spike_magnitude_pA" field. In that case, we just append "NA" to the new columns to keep the shape of the dataframe.
                if isinstance(temp_2_avg_spike_results["spike_magnitude_pA"][0], str):
                    # Append the 'NA' to the data frame
                    temp_2_avg_spike_results["half_width_start"] = 'NA'
                    temp_2_avg_spike_results["half_width_end"] = 'NA'
                    temp_2_avg_spike_results["half_width_ms"] = 'NA'
                    temp_2_avg_spike_results["avg_spike"] = 'NA'

                vgat_kynac_ptx_temp_list.append(temp_2_avg_spike_results) # append the data frame to the list
            
            vgat_kynac_ptx_df = pd.concat(vgat_kynac_ptx_temp_list) # concatenate all the data frames in the list
            vgat_kynac_ptx_df.to_json(os.path.join(folder, 'vgat_kynurenic_picrotoxin_pooled' + save_type + '.json')) # save combined results as new .json file

        if 'vglut2_control' in folder:
            vglut2_ctrl_temp_list = [] # an empty list to store the data frames
            vglut2_ctrl_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file] # get the files that contain the type of results you want
            for file in vglut2_ctrl_results_files:
                # Get the cell ID
                temp_file_id = [file.split('.')[0]]
                temp_cell_id = ['_'.join((temp_file_id[0].split('_'))[0:-4])]

                temp_3_avg_spike_results = pd.read_json(os.path.join(folder, file)) # read data frame from json file

                # We need to check wheter the cell we are looking at had any spikes. If number of spikes is zero, then we don't need to calculate anything.
                if isinstance(temp_3_avg_spike_results["spike_magnitude_pA"][0], float):
                    temp_3_npz_results = np.load(os.path.join(folder, temp_cell_id[0] + '_results.npz')) # load data from current cell ID
                    temp_3_avg_spike = temp_3_npz_results["average_spike"] # retrieve average spike
                    temp_3_avg_spike_peak_index = int(np.where(temp_3_avg_spike == min(temp_3_avg_spike))[0]) # find peak indez
                    
                    # Compute the half_peak value (baseline to peak divided by two) that will be used to measure the half-width
                    temp_3_half_peak = (temp_3_avg_spike_results["spike_magnitude_pA"][0] - temp_3_avg_spike_results['baseline_start_mean'][0]) / 2

                    # Now, we need to get the first time we cross the half_peak value (before the peak), and the second time (after the peak). To do this, we are going to split the spike in two halves, and do the procedure separately.
                    from scipy.interpolate import interp1d # load function to interpolate
                    temp_3_avg_spike_first_half = temp_3_avg_spike[:temp_3_avg_spike_peak_index] # get first half of average spike
                    temp_3_f1 = interp1d(temp_3_avg_spike_first_half, 
                                        range(0, len(temp_3_avg_spike_first_half)), 
                                        kind = "linear") # make function to interpolate
                    temp_half_width_start = temp_3_f1(temp_3_half_peak) # find value corresponding to the half_peak
                    
                    temp_3_avg_spike_second_half = temp_3_avg_spike[temp_3_avg_spike_peak_index:] # get second half of average spike
                    temp_3_f2 = interp1d(temp_3_avg_spike_second_half, 
                                        range(temp_3_avg_spike_peak_index, 
                                        temp_3_avg_spike_peak_index+len(temp_3_avg_spike_second_half)), 
                                        kind = "linear") # make function to interpolate
                    temp_half_width_end = temp_3_f2(temp_3_half_peak) # find value corresponding to the half_peak

                    # Subtract beginning from end and multiply by the sampling rate to obtain the half_width in ms
                    temp_3_half_width_interpolated = (temp_half_width_end - temp_half_width_start) * dt

                    # Append the results to the data frame
                    temp_3_avg_spike_results["half_width_start"] = temp_half_width_start
                    temp_3_avg_spike_results["half_width_end"] = temp_half_width_end
                    temp_3_avg_spike_results["half_width_ms"] = temp_3_half_width_interpolated
                    temp_3_avg_spike_results["avg_spike"] = [temp_3_avg_spike]
                
                # If, on the other hand, we didn't detect any spikes for this cell, we will have "NA" in the "spike_magnitude_pA" field. In that case, we just append "NA" to the new columns to keep the shape of the dataframe.
                if isinstance(temp_3_avg_spike_results["spike_magnitude_pA"][0], str):
                    # Append the 'NA' to the data frame
                    temp_3_avg_spike_results["half_width_start"] = 'NA'
                    temp_3_avg_spike_results["half_width_end"] = 'NA'
                    temp_3_avg_spike_results["half_width_ms"] = 'NA'
                    temp_3_avg_spike_results["avg_spike"] = 'NA'

                vglut2_ctrl_temp_list.append(temp_3_avg_spike_results) # append the data frame to the list
            
            vglut2_ctrl_df = pd.concat(vglut2_ctrl_temp_list) # concatenate all the data frames in the list
            vglut2_ctrl_df.to_json(os.path.join(folder, 'vglut2_control_pooled' + save_type + '.json')) # save combined results as new .json file

        if 'vglut2_picrotoxin' in folder:
            vglut2_ptx_temp_list = [] # an empty list to store the data frames
            vglut2_ptx_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file] # get the files that contain the type of results you want
            for file in vglut2_ptx_results_files:
                # Get the cell ID
                temp_file_id = [file.split('.')[0]]
                temp_cell_id = ['_'.join((temp_file_id[0].split('_'))[0:-4])]

                temp_4_avg_spike_results = pd.read_json(os.path.join(folder, file)) # read data frame from json file

                # We need to check wheter the cell we are looking at had any spikes. If number of spikes is zero, then we don't need to calculate anything.
                if isinstance(temp_4_avg_spike_results["spike_magnitude_pA"][0], float):
                    temp_4_npz_results = np.load(os.path.join(folder, temp_cell_id[0] + '_results.npz')) # load data from current cell ID
                    temp_4_avg_spike = temp_4_npz_results["average_spike"] # retrieve average spike
                    temp_4_avg_spike_peak_index = int(np.where(temp_4_avg_spike == min(temp_4_avg_spike))[0]) # find peak indez
                    
                    # Compute the half_peak value (baseline to peak divided by two) that will be used to measure the half-width
                    temp_4_half_peak = (temp_4_avg_spike_results["spike_magnitude_pA"][0] - temp_4_avg_spike_results['baseline_start_mean'][0]) / 2

                    # Now, we need to get the first time we cross the half_peak value (before the peak), and the second time (after the peak). To do this, we are going to split the spike in two halves, and do the procedure separately.
                    from scipy.interpolate import interp1d # load function to interpolate
                    temp_4_avg_spike_first_half = temp_4_avg_spike[:temp_4_avg_spike_peak_index] # get first half of average spike
                    temp_4_f1 = interp1d(temp_4_avg_spike_first_half, 
                                        range(0, len(temp_4_avg_spike_first_half)), 
                                        kind = "linear") # make function to interpolate
                    temp_half_width_start = temp_4_f1(temp_4_half_peak) # find value corresponding to the half_peak
                    
                    temp_4_avg_spike_second_half = temp_4_avg_spike[temp_4_avg_spike_peak_index:] # get second half of average spike
                    temp_4_f2 = interp1d(temp_4_avg_spike_second_half, 
                                        range(temp_4_avg_spike_peak_index, 
                                        temp_4_avg_spike_peak_index+len(temp_4_avg_spike_second_half)), 
                                        kind = "linear") # make function to interpolate
                    temp_half_width_end = temp_4_f2(temp_4_half_peak) # find value corresponding to the half_peak

                    # Subtract beginning from end and multiply by the sampling rate to obtain the half_width in ms
                    temp_4_half_width_interpolated = (temp_half_width_end - temp_half_width_start) * dt

                    # Append the results to the data frame
                    temp_4_avg_spike_results["half_width_start"] = temp_half_width_start
                    temp_4_avg_spike_results["half_width_end"] = temp_half_width_end
                    temp_4_avg_spike_results["half_width_ms"] = temp_4_half_width_interpolated
                    temp_4_avg_spike_results["avg_spike"] = [temp_4_avg_spike]
                
                # If, on the other hand, we didn't detect any spikes for this cell, we will have "NA" in the "spike_magnitude_pA" field. In that case, we just append "NA" to the new columns to keep the shape of the dataframe.
                if isinstance(temp_4_avg_spike_results["spike_magnitude_pA"][0], str):
                    # Append the 'NA' to the data frame
                    temp_4_avg_spike_results["half_width_start"] = 'NA'
                    temp_4_avg_spike_results["half_width_end"] = 'NA'
                    temp_4_avg_spike_results["half_width_ms"] = 'NA'
                    temp_4_avg_spike_results["avg_spike"] = 'NA'

                vglut2_ptx_temp_list.append(temp_4_avg_spike_results) # append the data frame to the list
            
            vglut2_ptx_df = pd.concat(vglut2_ptx_temp_list) # concatenate all the data frames in the list
            vglut2_ptx_df.to_json(os.path.join(folder, 'vglut2_picrotoxin_pooled' + save_type + '.json')) # save combined results as new .json file

    print('results saved')

    return vgat_ctrl_df, vgat_kynac_ptx_df, vglut2_ctrl_df, vglut2_ptx_df # pandas dataframes

# %%
# Test function

vgat_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
vgat_kynac_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_kynurenic_picrotoxin"
vglut2_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_control"
vglut2_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_picrotoxin"
print("done!")

# Choose folders
folders_to_check = [vgat_ctrl_save_path, 
                    vgat_kynac_ptx_save_path, 
                    vglut2_ctrl_save_path, 
                    vglut2_ptx_save_path]

# Choose type of results and suffix for saved file
results_type_avg_spike = '_df_parameters_avg_spike'
save_type_avg_spike = '_avg_spike'

# Run function
vgat_ctrl_avg_spike_df, vgat_kynac_ptx_avg_spike_df, vglut2_ctrl_avg_spike_df, vglut2_ptx_avg_spike_df = getSpikeHalfWidth(folders_to_check, results_type_avg_spike, save_type_avg_spike)

# Print results number of cells in each group and inspect one of the resulting data frames
print(len(vgat_ctrl_avg_spike_df))
print(len(vgat_kynac_ptx_avg_spike_df))
print(len(vglut2_ctrl_avg_spike_df))
print(len(vglut2_ptx_avg_spike_df))
vgat_ctrl_avg_spike_df
