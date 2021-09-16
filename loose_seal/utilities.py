import os
import tkinter
from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
import h5py
from collections import defaultdict
from nptdms import TdmsFile
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from IPython import get_ipython

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

def getLooseRseal_old(
    file_name,
    channels_data_frame
    ):
    """
    `getLooseRseal` calculates the seal resistance (Rseal) from the test pulse size and the cell's response.
    Takes a data frame and returns the Rseal value across sweeps for the time of recording.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :channels_data_frame: data frame with extracted data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    """

    # Initialize variables to build results data frame:
    file_id = [file_name.split('.')[0]] # Get the file name without the extension
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
    extracted_Rseal_data_frame = pd.DataFrame([seal_resistance], index = file_id, columns = trial_keys)

    return extracted_Rseal_data_frame # pandas data frame

def getLooseRseal(
    file_name,
    channels_data_frame
    ):
    """
    `getLooseRseal` calculates the seal resistance (Rseal) from the test pulse size and the cell's response.
    Takes a data frame and returns the Rseal value across sweeps for the time of recording.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :channels_data_frame: data frame with extracted data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    """

    # Initialize variables to build results data frame:
    # file_id = [file_name.split('.')[0]] # Get the file name without the extension
    test_pulse_command = []
    test_pulse_membrane = []
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
        tp_command = sweep_OA_baseline - sweep_OA_pulse # mV

        ## Get cell response to test_pulse:
        # Use the test_pulse indices to get the baseline and cell response to calculate the seal resistance
        # To be exact and account for the delays between digital command and output from the amplifier, you could add +1 to the first index to calculate the baseline.
        sweep_IB_baseline = np.mean(sweep_IB[:(test_pulse_OA_indices[0])])
        # Similary, to avoid using the values recorded while the test pulse command begins, you can skip a milisecond (+4 indices) to the beginning, to ensure you start averaging once the signal has reached the cell. 
        # To be extra exact, you could add +2 to the last index so you use all the samples. 
        # However, this shouldn't make a big difference, so we just skip the milisecond to avoid the transition period.
        sweep_IB_pulse = np.mean(sweep_IB[(test_pulse_OA_indices[0]+4):(test_pulse_OA_indices[-1])])
        tp_membrane = sweep_IB_baseline - sweep_IB_pulse # pA

        ## Get seal resistance = mV/pA
        Rseal = (tp_command / tp_membrane) * 1000 # to get MOhm
        # Append results
        test_pulse_command.append(tp_command)
        test_pulse_membrane.append(tp_membrane)
        seal_resistance.append(Rseal)

        ## Get trial name for results data frame
        trial_keys.append(sweep)

    # Create data frame of data:
    extracted_Rseal_data_frame = pd.DataFrame([test_pulse_command, test_pulse_membrane, seal_resistance], index = ['test_pulse_command', 'test_pulse_membrane', 'seal_resistance'], columns = trial_keys)

    return extracted_Rseal_data_frame # pandas data frame

def concatenateSweeps(
    channels_data_frame
    ):
    """
    `concatenateSweeps` extracts the sweeps containing the recorded signal from `channels_data_frame` and concatenates them. It also creates a concatenated pseudo-sweep that has the same length and number of sweeps as the original data, with the difference that each sweep within the pseudo-sweep will be comprised of the number that reflects the real sweep ID. It returns two numpy.ndarrays for the concatenated data and the concatenated sweep IDs.
    
    :channels_data_frame: data frame with extracted data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    """

    # Extract sweeps
    sweep_IB = np.array(channels_data_frame.loc['Channel B', :])
    
    # Concatenate sweeps
    sweep_IB_concatenated = np.concatenate(sweep_IB)
    
    # Create pseudo-sweep
    pseudo_sweep_keys = []
    
    for i, sweep in enumerate(sweep_IB):
        # get sweep ID as integer
        sweep_key = int(channels_data_frame.columns[i])
        # create a pseudo-sweep of the same length as the data but consisting of the sweep ID
        sweep_keys_tmp = np.zeros(len(sweep), dtype = int) + sweep_key
        pseudo_sweep_keys.append(sweep_keys_tmp)
    
    # Concatenate the pseudo-sweep
    pseudo_sweep_concatenated = np.concatenate(pseudo_sweep_keys)

    return sweep_IB_concatenated, pseudo_sweep_concatenated # ndarray, ndarray

def findSpikes(
    file_name,
    sweep_IB_concatenated,
    prominence_min = None,
    prominence_max = None,
    wlen_ms = 10,
    sampling_rate_khz = 25
    ):
    """
    `findSpikes` uses scipy's `find_peaks` to detect peaks in the data and obtain their prominences. It then plots the distribution of prominences and allows the user to input the minimal and maximal prominence values to be used to detect peaks. It next runs `find_peaks` one more time with the user selected parameters and plots the data and the detected peaks. It returns the indices of peaks in the data that satisfy all given conditions, the properties of such peaks, and the parameters selected by the user.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :sweep_IB_concatenated: numpy array containing the concatenated data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    :prominence_min: minimal required prominence of peaks. Defaults to None.
    :prominence_max: maximal required prominence of peaks. Defaults to None.
    :wlen_ms: window length in ms that limits the evaluated area for each peak. Defaults 10 ms.
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.
    """

    # Get delta_t from sampling rate:
    dt = 1/sampling_rate_khz
    
    # Run `find_peaks` with no parameters, so we can examine the prominences of anything detected. This will help us fine-tune the function call.
    peaks_tmp, properties_tmp = find_peaks(-sweep_IB_concatenated, height = (None, None), threshold = (None, None), distance = None, prominence = (prominence_min, prominence_max), width = (None, None), wlen = wlen_ms/dt)

    # Plot the distribution of prominences from the detected peaks.
    get_ipython().run_line_magic('matplotlib', 'qt') # avoid 'tk' here
    fig1 = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
    ax = plt.gca()
    plt.hist(properties_tmp['prominences'], bins = 200, density = False, histtype = 'bar', log = True)
    plt.title('Figure A: Prominence of detected peaks', fontsize = 14)
    plt.text(0.95, 0.95, f'Parameters: wlen = {wlen_ms}ms', horizontalalignment='right', verticalalignment='top', transform = ax.transAxes)
    plt.xlabel('peak prominence [pA]', fontsize = 12)
    fig1.canvas.manager.window.move(0, 0) # Move figure to top left corner
    plt.pause(0.5) # Alternative to waitforbuttonpress() or plt.show(block = True)- does not close the figure and proceeds to input(). If we needed to interact with the histogram before inputing the desired values we could either increase the length of the pause or switch to plt.show(block = True), which would leave the figure open until we close it, and only then it proceeds to input().

    # Based on the histogram above, select the interval of prominences that will contain the peaks from spikes and not from baseline noise.
    prominence_min = int(input("Enter the min value for the desired prominence"))
    prominence_max = int(input("Enter the max value for the desired prominence"))
        
    plt.close() # needed here if plt.pause() is used instead of plt.waitforbuttonpress()

    # Use the selected prominence values to find spikes in the data.
    peaks, peaks_properties = find_peaks(-sweep_IB_concatenated, height = (None, None), threshold = (None, None), distance = None, prominence = (prominence_min, prominence_max), width = (None, None), wlen = wlen_ms/dt)

    # Get cell ID and parameters used
    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    parameters_find_peaks = pd.DataFrame([[prominence_min, prominence_max, wlen_ms/dt, wlen_ms]], columns = ['prominence_min', 'prominence_max', 'wlen [samples]', 'wlen [ms]'], index = file_id)

    # Plot the data with the detected peaks.
    get_ipython().run_line_magic('matplotlib', 'qt') # avoid 'tk' here
    fig2 = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
    plt.plot(peaks, sweep_IB_concatenated[peaks], "xr"); plt.plot(sweep_IB_concatenated); plt.legend(['peaks'])
    plt.title('Figure B: Detected peaks for concatenated sweeps', fontsize = 14)
    plt.xlabel('samples', fontsize = 12)
    plt.ylabel('current [pA]', fontsize = 12)
    fig2.canvas.manager.window.move(0, 0) # Move figure to top left corner
    #plt.pause(0.5)
    plt.show(block = True) # Lets you interact with plot and proceeds when figure is closed
    
    happy = input("Are you happy with your choice of prominence? y/n")

    if happy == 'y':
        print(f"found {len(peaks)} spikes")
    else:
        # Empty results just in case.
        peaks = []
        peaks_properties = []
        parameters_find_peaks = []
        print('Try running findSpikes() again')
    
    plt.close()
    
    return peaks, peaks_properties, parameters_find_peaks # ndarray, dict, pandas data frame

def cutSpikes(
    sweep_IB_concatenated,
    peaks
    ):
    """
    `cutSpikes` cuts an interval of 10 ms around each peak for plotting and further analysis. It then calculates a baseline for each peak by averaging 1-3 ms, leaving out the first ms before the peak index as it will contain the spike itself. Finally, it subtracts the calculated value to baseline the cut spikes, which will facilitate visualisation and quality control. It returns three numpy arrays of the same length containing the cut spikes, the baseline before each peak, and the resulting baselined cut spikes.
    
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

def plotSpikesQC(
    file_name,
    peaks_properties,
    cut_spikes_baselined
    ):
    """
    `plotSpikesQC` generates a summary plot that can be used to determine the metrics that can be used to quality check the detected spikes. The summary plot contains (1) a subplot with all the detected spikes after cutting and baselining, and (2) three subplots with the histograms of the main metrics that can be used to detect noise in the detected spikes, which are `width_heights`, `widths`, and `peak_heights`. It only outputs the plot for visualisation purposes and does not return any variable. 
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :peaks_properties: dictionary containing properties of the peaks returned by scipy's `find_peaks` in `findSpikes`.
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
    axs[0,1].hist(peaks_properties['width_heights'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
    axs[0,1].set_title('Width heights ["wh"]', fontsize = 12)
    # Plot Histogram of peak widths
    axs[1,0].hist(peaks_properties['widths'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
    axs[1,0].set_title('Peak widths ["pw"]', fontsize = 12)
    # Plot Histogram of peak heights
    axs[1,1].hist(peaks_properties['peak_heights'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
    axs[1,1].set_title('Peak heights ["ph"]', fontsize = 12)

    # Add title
    plt.suptitle(f'QC metrics for {cell_id[0]}', fontsize = 14)
    
    # Move figure to top left corner
    fig.canvas.manager.window.move(0, 0)
    plt.show()

def getSpikesQC(
    file_name,
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
    `getSpikesQC` allows to quality check the detected spikes by defining thresholds in three different metrics. It then generates a summary plot that can be used to assess whether the chosen metrics correctly remove the noise and leave the true spikes untouched. The summary plot contains (1) a subplot with all the detected spikes after cutting and baselining, coloring the noise traces according to the QC metric that excludes them, and (2) three subplots with the histograms of the metrics used, which are `width_heights`, `widths`, and `peak_heights`. If the result is satisfactory, it return a data frame with the selected filters. 
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
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
    
    # Get color palette and generate one color for each metric
    cmap = plt.get_cmap('tab20')
    c_spikes = 'lightgray' # gray - clean spikes
    c_ph = cmap(3) # orange - noise by peak height
    c_pw = cmap(7) # red - noise by peak width
    c_wh = cmap(9) # purple - noise by width height

    get_ipython().run_line_magic('matplotlib', 'qt')

    fig, axs = plt.subplots (2, 2, tight_layout = True)

    # Plot cut and baselined spikes colored by whether they pass the desired QC or not.
    for s in range(len(cut_spikes_baselined)):
        if 'wh' in filter_by and (peaks_properties['width_heights'][s] < QC_wh_min or peaks_properties['width_heights'][s] > QC_wh_max):
            axs[0,0].plot(cut_spikes_baselined[s], c = c_wh)
        elif 'pw' in filter_by and (peaks_properties['widths'][s] < QC_pw_min or peaks_properties['widths'][s] > QC_pw_max):
            axs[0,0].plot(cut_spikes_baselined[s], c = c_pw)
        elif 'ph' in filter_by and (peaks_properties['peak_heights'][s] < QC_ph_min or peaks_properties['peak_heights'][s] > QC_ph_max):
            axs[0,0].plot(cut_spikes_baselined[s], c = c_ph)
        else:
            axs[0,0].plot(cut_spikes_baselined[s], c = c_spikes)
    axs[0,0].set_title('Spikes colored by QC parameters', fontsize = 12)
    axs[0,0].set_xlim([((len(cut_spikes_baselined[0])/2)-45), ((len(cut_spikes_baselined[0])/2)+55)])
    axs[0,0].set_ylabel('current [pA]')

    # Plot Histogram of the height at which widths where evaluated
    n_1, bins_1, patches_1 = axs[0,1].hist(peaks_properties['width_heights'], bins = 100, density = False, histtype = 'bar', log = True)
    for i in range(len(patches_1)):
        if (bins_1[i] < QC_wh_min or bins_1[i] > QC_wh_max):
            patches_1[i].set_facecolor(c_wh)
        else:
            patches_1[i].set_facecolor('lightgray')
    axs[0,1].set_title('Width heights ["wh"]', fontsize = 12)
    # Plot Histogram of peak widths
    n_2, bins_2, patches_2 = axs[1,0].hist(peaks_properties['widths'], bins = 100, density = False, histtype = 'bar', log = True, color = c_pw)
    for i in range(len(patches_2)):
        if (bins_2[i] < QC_pw_min or bins_2[i] > QC_pw_max):
            patches_2[i].set_facecolor(c_pw)
        else:
            patches_2[i].set_facecolor('lightgray')
    axs[1,0].set_title('Peak widths ["pw"]', fontsize = 12)
    # Plot Histogram of peak heights
    n_3, bins_3, patches_3 = axs[1,1].hist(peaks_properties['peak_heights'], bins = 100, density = False, histtype = 'bar', log = True, color = c_ph)
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

    # Check whether QC is complete
    happy = input("Are you happy with your choice of parameters for QC? y/n")

    if happy == 'y':
        print('QC completed')
        parameters_QC = pd.DataFrame([[QC_wh_min, QC_wh_max, QC_pw_min, QC_pw_max, QC_ph_min, QC_ph_max, filter_by]], columns = ['QC_wh_min', 'QC_wh_max', 'QC_pw_min', 'QC_pw_max', 'QC_ph_min', 'QC_ph_max', 'filter_by'], index = cell_id)
    else:
        print('Try running getSpikesQC() again with different parameters')
        parameters_QC = []

    plt.close()

    return parameters_QC # pandas data frame

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