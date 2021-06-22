import os
import h5py
import numpy as np
import pandas as pd
import tkinter
from tkinter.filedialog import askopenfilename, askopenfilenames
from collections import defaultdict
from nptdms import TdmsFile

def importFile(
    channel_list = ['Channel A', 'Channel B', 'Output A', 'Output B'],
    curated_channel = None,
    sampling_rate_khz = 25
    ):
    """
    `importFile` opens a window to select a file to import.
    It then uses the path to the selected file to call `openFile` to extract data.

    :channel_list: list of channels to extract. If empty, defaults to 'Channel A', 'Channel B', 'Output A', 'Output B'.
    :curated_channel: e.g. copy of a 'Channel' where some sweeps/trials have been deleted due to noise or quality. Defaults to None.
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.
    """

    root = tkinter.Tk()
    root.attributes("-topmost", True) # Make window appear on top
    in_path = askopenfilename() # Open dialogue to select file
    root.destroy() # Close the root window

    folder_name = os.path.split(in_path)[0] # Get path until folder
    file_name = os.path.split(in_path)[1] # Get filename
    
    extracted_channels_data_frame, time, dt = openFile(in_path, channel_list, curated_channel, sampling_rate_khz) # Call openFile() function
    
    return extracted_channels_data_frame, time, dt, folder_name, file_name # pandas data frame, list, float, str, str

def openFile(
    in_path,
    channel_list = ['Channel A', 'Channel B', 'Output A', 'Output B'],
    curated_channel = None,
    sampling_rate_khz = 25
    ):
    """
    `openFile` checks whether you are attempting to open a `.tdms` or a `.hdf5` file.
    It then calls the right function to extract the data from selected channels.

    :channel_list: list of channels to extract. If empty, defaults to 'Channel A', 'Channel B', 'Output A', 'Output B'.
    :curated_channel: e.g. copy of a 'Channel' where some sweeps/trials have been deleted due to noise or quality. Defaults to None.
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.
    """

    if '.tdms' in in_path:
        extracted_channels_data_frame, time, dt = openTDMSfile(in_path, channel_list, sampling_rate_khz)
    elif '.hdf5' in in_path:
        extracted_channels_data_frame, time, dt = openHDF5file(in_path, channel_list, curated_channel, sampling_rate_khz)
    
    return extracted_channels_data_frame, time, dt # pandas data frame, list, float

def openHDF5file(
    in_path,
    channel_list = ['Channel A', 'Channel B', 'Output A', 'Output B'],
    curated_channel = None,
    sampling_rate_khz = 25
    ):
    """
    `openHDF5file` Opens the selected `.hdf5` file and extracts sorted data from chosen channels.
    
    :channel_list: list of channels to extract. If empty, defaults to 'Channel A', 'Channel B', 'Output A', 'Output B'.
    :curated_channel: e.g. copy of a 'Channel' where some sweeps/trials have been deleted due to noise or quality. Defaults to None.
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.
    """

    # Read hdf5 file:
    hdf5_file = h5py.File(in_path, 'r')
    
    # Define empty dictionary to populate with correctly sorted data:
    data_dict = defaultdict(list)
    # Define empty dictionary to populate with corrected trialKeys:
    key_dict = defaultdict(list)
    
    # Iterate through channels to find trial indices and sort them numerically:
    for channel in hdf5_file.keys():
        
        # Fix hdf5 indexing. Otherwise it sorts sweeps alphabetically (as 1, 10, 11, [...], 2, 21, 22...)
        if 'Channel' in channel:
            # Get keys from hdf5 (i.e. the name of each sweep/trial)
            # These have been sorted alphabetically as in strings: 
            trialKeysInHDF5 = list(hdf5_file[channel].keys())
            
            # Convert to integers so you can sort numerically:
            trialKeysInHDF5_int = [int(x) for x in trialKeysInHDF5]
            
            # Get the indices that will sort the array:
            trialKeysInHDF5_sorting_indices = list(np.argsort(trialKeysInHDF5_int))
            
            if curated_channel is not None:
                # Use trial keys from curated_channel to ensure same number of trials are present in all channels.
                trialKeysInHDF5 = list(hdf5_file[curated_channel].keys())
                trialKeysInHDF5_int = [int(x) for x in trialKeysInHDF5]
                trialKeysInHDF5_sorting_indices = list(np.argsort(trialKeysInHDF5_int))
        
        # In the case of 'Output' channels, we need to add an extra step.
        # Whereas trialKeys for "Channel" always start at "1", "Output" starts at random values like "14197".
        elif 'Output' in channel:
            trialKeysInHDF5 = list(hdf5_file[channel].keys())
            trialKeysInHDF5_int = [int(x) for x in trialKeysInHDF5]
            trialKeysInHDF5_sorting_indices = list(np.argsort(trialKeysInHDF5_int))
            # Transform them so they start from 1 and can be compared to the curated_channel keys:
            trialKeysInHDF5_int_from1 = [(x-min(trialKeysInHDF5_int)+1) for x in trialKeysInHDF5_int]
     
            if curated_channel is not None:
                # Compare the trial keys starting from 1 to those from the curated channel.
                # Then use the indices of matching keys to extract only the curated trials to analyse.
                trialKeysInHDF5_curated = list(hdf5_file[curated_channel].keys())
                trialKeysInHDF5_curated_int = [int(x) for x in trialKeysInHDF5_curated]
                trialKeysInHDF5_curated_sorting_indices = list(np.argsort(trialKeysInHDF5_curated_int))
                # Sort the curated integer keys so you can use them in the list.index() step.
                trialKeysInHDF5_curated_int_sorted = sorted(trialKeysInHDF5_curated_int)
                # For the sorted curated trial keys, find the index of the value matching each curated_channel trial.
                # Use this as the sorting indices.
                trialKeysInHDF5_sorting_indices = [trialKeysInHDF5_int_from1.index(trialKeysInHDF5_curated_int_sorted[i]) for i in range(len(trialKeysInHDF5_curated_int_sorted))]

        # 'Sweeps_Analysis' will be a copy of either 'Channel A' or 'Channel B' that has been curated.
        # Should be the same provided as curated_channel, which will be used to subset all the channels.
        # Won't be extracted as would only be a duplication.
        elif 'Sweeps_Analysis' in channel:
            trialKeysInHDF5 = list(hdf5_file[channel].keys())
            trialKeysInHDF5_int = [int(x) for x in trialKeysInHDF5]
            trialKeysInHDF5_sorting_indices = list(np.argsort(trialKeysInHDF5_int))

        # To extract 'Time':
        elif 'Time' in channel:
            trialKeysInHDF5 = list(hdf5_file[channel].keys())
            trialKeysInHDF5_sorting_indices = range(len(trialKeysInHDF5))
        
        # In case there is any other channel in the hdf5 file you haven't accounted for:
        else:
            # Print a warning:
            print(f"Unrecognised {channel}: check function. This channel may not be properly sorted.")
            trialKeysInHDF5 = list(hdf5_file[curated_channel].keys())
            trialKeysInHDF5_int = [int(x) for x in trialKeysInHDF5]
            trialKeysInHDF5_sorting_indices = list(np.argsort(trialKeysInHDF5_int))

        # Once you have the correct indices to obtain sorted trial keys, extract the ordered data:
        for i in range(len(trialKeysInHDF5_sorting_indices)):
            correctedTrialKey = trialKeysInHDF5[trialKeysInHDF5_sorting_indices[i]] 
            data_dict[channel].append(np.array(hdf5_file[channel][correctedTrialKey]))
            key_dict[channel].append(correctedTrialKey)
    
    extracted_channels = []
    corrected_trial_keys = []

    # Keep only the useful channels and their trial keys:
    for channel in channel_list:
        extracted_channels.append(data_dict[channel])
        corrected_trial_keys.append(key_dict[channel])
    
    # Get time and delta_t
    if len(data_dict['Time']) > 0:
        dt = 1/sampling_rate_khz # could try to objectively do np.mean(np.diff(time)), but that would always underestimate the value as len(np.diff(x)) will always be one value shorter than len(x) 
        time = data_dict['Time']
    
    else:
        dt = 1/sampling_rate_khz # could try to objectively do np.mean(np.diff(time)), but that would always underestimate the value as len(np.diff(x)) will always be one value shorter than len(x) 
        time = np.linspace(0, len(data_dict['Channel A'][0])*dt, len(['Channel A'][0]))
    
    # Create data frame of data:
    extracted_channels_data_frame = pd.DataFrame(extracted_channels, index = channel_list, columns = corrected_trial_keys[0])

    return extracted_channels_data_frame, time, dt # pandas data frame, list, float

def openTDMSfile(
    in_path,
    channel_list = ['Channel A', 'Channel B', 'Output A', 'Output B'],
    sampling_rate_khz = 25
    ):
    """
    `openTDMSfile` returns a list of arrays, where each is a sweep/trial.

    :channel_list: list of channels to extract. If empty, defaults to 'Channel A', 'Channel B', 'Output A', 'Output B'.
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.
    """
    
    # Load .tdms file
    tdms_file = TdmsFile(in_path)
    # Define empty dictionary to populate with correctly sorted data:
    data_dict = defaultdict(list)
    # Define empty list to populate with trial keys:
    trial_keys = []
    
    # Iterate through channels and extract data from sweeps/trials
    for group in tdms_file.groups():
        # Iterate through sweeps and append data to dictionary
        for sweep in group.channels():
            data_dict[group.name].append(sweep.data)
            # Assign the names of each sweep for Channel A to use for the data frame
            # We take Channel A (or B) as they start from 1 (Output channels start from a random number
            if group.name == 'Channel A':
                trial_keys.append(sweep.name)
                       
    # Keep only useful channels
    extracted_channels = []

    for channel in channel_list: 
        extracted_channels.append(data_dict[channel])
    
    # Get time and delta_t
    dt = 1/sampling_rate_khz # could try to objectively do np.mean(np.diff(time)), but that would always underestimate the value as len(np.diff(x)) will always be one value shorter than len(x) 
    time = data_dict['Time'][0]

    # Create data frame of data:
    extracted_channels_data_frame = pd.DataFrame(extracted_channels, index = channel_list, columns = trial_keys)
    
    return extracted_channels_data_frame, time, dt # pandas data frame, list, float

def getLooseRseal(
    file_name,
    channels_data_frame
    ):
    """
    `getLooseRseal` calculates the seal resistance (Rseal) from the test pulse size and the cell's response.
    Takes a data frame and returns the Rseal value across sweeps for the time of recording.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :extracted_channels_data_frame: data frame with extracted data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    """

    # Initialize variables to build results data frame:
    cell_name = [file_name.split('.')[0]] # Get the file name without the extension
    seal_resistance = []
    trial_keys = []

    for sweep in channels_data_frame.columns:
        
        ## Load data: Output A (command) and Channel B (recording in Voltage Clamp)
        # sweep_IA = np.array(channels_data_frame.at['Channel A', sweep]) # Not needed as we record in Voltage Clamp
        sweep_IB = np.array(channels_data_frame.at['Channel B', sweep])
        sweep_OA = np.array(channels_data_frame.at['Output A', sweep])

        ## Get the indices corresponding to the test_pulse using the Output Channel
        test_pulse = np.where(sweep_OA < 0)
        test_pulse_OA_indices = test_pulse[0]

        ## Get test_pulse magnitude
        # Use the indices of the test_pulse command (Output A) to define baseline period and test period
        sweep_OA_baseline = np.mean(sweep_OA[:(test_pulse_OA_indices[0]-1)]) # -1 to stop baseline before command starts
        sweep_OA_pulse = np.mean(sweep_OA[test_pulse_OA_indices])
        test_pulse_command = sweep_OA_baseline - sweep_OA_pulse # mV

        ## Get cell response to test_pulse:
        # Use the test_pulse indices to get the baseline and cell response to calculate the seal resistance
        # To be exact and account for the delays between digital command and output from the amplifier, you could add +1 to the first index to calculate the baseline.
        sweep_IB_baseline = np.mean(sweep_IB[:(test_pulse_OA_indices[0])])
        # Similary, to avoid using the values recorded while the test pulse command begins, you can skip a milisecond (+4 indices) to the beginning, to ensure you start averaging once the signal has reached the cell. 
        # To be extra exact, you could add +2 to the last index so you use all the samples. 
        # However, this shouldn't make a big difference, so we just skip the milisecond to avoid the transition period.
        sweep_IB_pulse = np.mean(sweep_IB[(test_pulse_OA_indices[0]+4):(test_pulse_OA_indices[-1])])
        test_pulse_membrane = sweep_IB_baseline - sweep_IB_pulse # pA

        ## Get seal resistance = mV/pA
        Rseal = (test_pulse_command / test_pulse_membrane) * 1000 # to get MOhm
        # Append results
        seal_resistance.append(Rseal)

        ## Get trial name for results data frame
        trial_keys.append(sweep)

    # Create data frame of data:
    extracted_Rseal_data_frame = pd.DataFrame([seal_resistance], index = cell_name, columns = trial_keys)

    return extracted_Rseal_data_frame # pandas data frame