import os
import tkinter
from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
import h5py
from collections import defaultdict
from nptdms import TdmsFile
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from IPython import get_ipython

def importFile(
    channel_list = ['Channel A', 'Channel B', 'Output A', 'Output B'],
    curated_channel = None,
    sampling_rate_khz = 25
    ):
    """
    `importFile` opens a dialog window to select a file to import.
    It then uses the path to the selected file to call `openFile` to extract the data.
    It returns a dataframe with the extracted channels (where each row is a channel and each column a sweep) and four objects containing time, delta time, folder name, and file name.

    :channel_list: list of channels to extract. If empty, defaults to 'Channel A', 'Channel B', 'Output A', 'Output B'.
    :curated_channel: e.g. copy of a 'Channel' where some sweeps/trials have been deleted due to noise or quality. Defaults to None.
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.
    """

    root = tkinter.Tk()
    root.attributes("-topmost", True) # Make window appear on top
    in_path = askopenfilename() # Open dialog window to select file
    root.destroy() # Close the root window

    folder_name = os.path.split(in_path)[0] # Get path until folder
    file_name = os.path.split(in_path)[1] # Get filename
    
    extracted_channels_dataframe, time, dt = openFile(in_path, channel_list, curated_channel, sampling_rate_khz) # Call openFile() function
    
    return extracted_channels_dataframe, time, dt, folder_name, file_name # pandas dataframe, list, float, str, str

def openFile(
    in_path,
    channel_list = ['Channel A', 'Channel B', 'Output A', 'Output B'],
    curated_channel = None,
    sampling_rate_khz = 25
    ):
    """
    `openFile` checks whether you are attempting to open a `.tdms` or a `.hdf5` file.
    It then calls the right function to extract the data from the selected channels.
    It returns a dataframe with the extracted channels (where each row is a channel and each column a sweep) and two objects containing time and delta time.

    :in_path: path to the selected file.
    :channel_list: list of channels to extract. If empty, defaults to 'Channel A', 'Channel B', 'Output A', 'Output B'.
    :curated_channel: e.g. copy of a 'Channel' where some sweeps/trials have been deleted due to noise or quality. Defaults to None.
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.
    """

    if '.tdms' in in_path:
        extracted_channels_dataframe, time, dt = openTDMSfile(in_path, channel_list, sampling_rate_khz)
    elif '.hdf5' in in_path:
        extracted_channels_dataframe, time, dt = openHDF5file(in_path, channel_list, curated_channel, sampling_rate_khz)
    
    return extracted_channels_dataframe, time, dt # pandas dataframe, list, float

def openHDF5file(
    in_path,
    channel_list = ['Channel A', 'Channel B', 'Output A', 'Output B'],
    curated_channel = None,
    sampling_rate_khz = 25
    ):
    """
    `openHDF5file` opens the selected `.hdf5` file and extracts sorted data from the selected channels.
    It returns a dataframe with the extracted channels (where each row is a channel and each column a sweep) and two objects containing time and delta time.
    
    :in_path: path to the selected file.
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
    
    # Create dataframe of data:
    extracted_channels_dataframe = pd.DataFrame(extracted_channels, index = channel_list, columns = corrected_trial_keys[0])

    return extracted_channels_dataframe, time, dt # pandas dataframe, list, float

def openTDMSfile(
    in_path,
    channel_list = ['Channel A', 'Channel B', 'Output A', 'Output B'],
    sampling_rate_khz = 25
    ):
    """
    `openTDMSfile` returns a list of arrays, where each is a sweep/trial.
    It returns a dataframe with the extracted channels (where each row is a channel and each column a sweep) and two objects containing time and delta time.

    :in_path: path to the selected file.
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
            # Assign the names of each sweep for Channel A to use for the dataframe
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

    # Create dataframe of data:
    extracted_channels_dataframe = pd.DataFrame(extracted_channels, index = channel_list, columns = trial_keys)
    
    return extracted_channels_dataframe, time, dt # pandas dataframe, list, float

def getLooseRseal(
    channels_dataframe
    ):
    """
    `getLooseRseal` takes the dataframe containing the extracted channel data and calculates the seal resistance (Rseal) from the test pulse size and the cell's response to it.
    It returns a dataframe with the Rseal value (MOhm) across sweeps for the time of recording (where the columns are sweeps) together with the magnitude of the test_pulse command (mV) and the response of the cell (pA). It also plots the calculated Rseal across sweeps.
    
    :channels_dataframe: dataframe with extracted data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    """

    # Initialize variables to build results dataframe:
    test_pulse_command = []
    test_pulse_membrane = []
    seal_resistance = []
    trial_keys = []

    for sweep in channels_dataframe.columns:
        ## Load data: Output A (command) and Channel B (recording in Voltage Clamp)
        # sweep_IA = np.array(channels_dataframe.at['Channel A', sweep]) # Not needed as we record in Voltage Clamp
        sweep_IB = np.array(channels_dataframe.at['Channel B', sweep])
        sweep_OA = np.array(channels_dataframe.at['Output A', sweep])

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

        ## Get trial name for results dataframe
        trial_keys.append(sweep)

    # Create dataframe of data:
    Rseal_dataframe = pd.DataFrame([test_pulse_command, test_pulse_membrane, seal_resistance], index = ['test_pulse_command_mV', 'test_pulse_membrane_pA', 'seal_resistance_MOhm'], columns = trial_keys)

    # Plot Rseal across sweeps
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
    plt.plot(Rseal_dataframe.loc['seal_resistance_MOhm'], 'k')
    plt.title('Seal Resistance across sweeps', fontsize = 14)
    plt.xlabel('sweep number', fontsize = 12)
    plt.ylabel('Seal Resistance [MOhm]', fontsize = 12)
    plt.axis([-1, len(Rseal_dataframe.loc['seal_resistance_MOhm']), 0, round(np.mean(Rseal_dataframe.loc['seal_resistance_MOhm'])*2)])
    fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
    plt.show()
    # plt.pause(5) # Use this if you are running the full script so it gives you a few seconds to see the plot before it moves to the next chunk of code.

    return Rseal_dataframe # pandas dataframe

def concatenateSweeps(
    channels_dataframe
    ):
    """
    `concatenateSweeps` takes the sweeps containing the recorded signal from `channels_dataframe` and concatenates them. It also creates a concatenated pseudo-sweep that has the same length and number of sweeps as the original data, with the difference that each sweep within the pseudo-sweep will be comprised of the number that reflects the real sweep ID.
    It returns two numpy.ndarrays with the concatenated data and the concatenated sweep IDs. It also plots the resulting concatenated sweeps for a quick overview of the data.
    
    :channels_dataframe: dataframe with extracted data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    """

    # Extract sweeps
    sweep_IB = np.array(channels_dataframe.loc['Channel B', :])
    
    # Concatenate sweeps
    sweep_IB_concatenated = np.concatenate(sweep_IB)
    
    # Create pseudo-sweep
    pseudo_sweep_keys = []
    
    for i, sweep in enumerate(sweep_IB):
        # get sweep ID as integer
        sweep_key = int(channels_dataframe.columns[i])
        # create a pseudo-sweep of the same length as the data but consisting of the sweep ID
        sweep_keys_tmp = np.zeros(len(sweep), dtype = int) + sweep_key
        pseudo_sweep_keys.append(sweep_keys_tmp)
    
    # Concatenate the pseudo-sweep
    pseudo_sweep_concatenated = np.concatenate(pseudo_sweep_keys)

    # Plot concatenated sweeps
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig = plt.figure(figsize = (10, 5), dpi = 100) # Set figure size
    plt.plot(sweep_IB_concatenated, 'k')
    plt.title('Concatenated Sweeps', fontsize = 14)
    plt.xlabel('samples', fontsize = 12)
    plt.ylabel('current [pA]', fontsize = 12)
    fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
    plt.show()
    # plt.pause(5) # Use this if you are running the full script so it gives you a few seconds to see the plot before it moves to the next chunk of code.

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
    `findSpikes` uses scipy's `find_peaks` on the concatenated sweeps to detect peaks in the data and obtain their prominences. It then plots the distribution of prominences and allows the user to input the minimal and maximal prominence values to be used to detect peaks. It next runs `find_peaks` one more time with the user selected parameters and plots the data and the detected peaks.
    It returns an array with the indices of the detected peaks in the data that satisfy all given conditions, a dictionary with the properties of such peaks, and a dataframe with the parameters selected by the user.
    
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
    plt.show(block = True) # Lets you interact with plot and proceeds once figure is closed
    # plt.pause(0.5) # Alternative to waitforbuttonpress() or plt.show(block = True)- does not close the figure and proceeds to input(). If we needed to interact with the histogram before inputing the desired values we could either increase the length of the pause or switch to plt.show(block = True), which would leave the figure open until we close it, and only then it proceeds to input().

    # Based on the histogram above, select the interval of prominences that will contain the peaks from spikes and not from baseline noise.
    prominence_min = int(input("Enter the min value for the desired prominence"))
    prominence_max = int(input("Enter the max value for the desired prominence"))
        
    plt.close() # needed here if plt.pause() is used instead of plt.waitforbuttonpress()

    # Use the selected prominence values to find spikes in the data.
    peaks, peaks_properties = find_peaks(-sweep_IB_concatenated, height = (None, None), threshold = (None, None), distance = None, prominence = (prominence_min, prominence_max), width = (None, None), wlen = wlen_ms/dt)

    # Get cell ID and parameters used
    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    parameters_find_peaks = pd.DataFrame([[prominence_min, prominence_max, wlen_ms/dt, wlen_ms]], columns = ['prominence_min', 'prominence_max', 'wlen_samples', 'wlen_ms'], index = file_id)

    # Plot the data with the detected peaks.
    get_ipython().run_line_magic('matplotlib', 'qt') # avoid 'tk' here
    fig2 = plt.figure(figsize = (10, 5), dpi = 100) # Set figure size
    plt.plot(peaks, sweep_IB_concatenated[peaks], "xr"); plt.plot(sweep_IB_concatenated); plt.legend(['peaks'])
    plt.title('Figure B: Detected peaks for concatenated sweeps', fontsize = 14)
    plt.xlabel('samples', fontsize = 12)
    plt.ylabel('current [pA]', fontsize = 12)
    fig2.canvas.manager.window.move(0, 0) # Move figure to top left corner
    #plt.pause(0.5)
    plt.show(block = True) # Lets you interact with plot and proceeds once figure is closed
    
    happy_prominence = input("Are you happy with your choice of prominence? y/n")

    if happy_prominence == 'y':
        print(f"found {len(peaks)} spikes")
    else:
        print('Try running findSpikes() again')
        plt.close()
        return None, None, None # return empty variables to prevent wrong results from being used
    
    plt.close()
    
    return peaks, peaks_properties, parameters_find_peaks # ndarray, dict, pandas dataframe

def cutSpikes(
    sweep_IB_concatenated,
    peaks
    ):
    """
    `cutSpikes` takes the concatenated sweeps and cuts an interval of 10 ms around each detected peak for plotting and further analysis. It then calculates a baseline for each peak by averaging 3 ms before it, leaving out the first ms right before the peak index as it will contain the spike itself. Finally, it subtracts the calculated value to baseline the cut spikes, which will facilitate visualisation and quality control.
    It returns three numpy arrays of the same length containing the cut spikes, the baseline before each peak, and the resulting baselined cut spikes. It also plots the cut and baselined spikes.
    
    :sweep_IB_concatenated: numpy array containing the concatenated data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    :peaks: indices of detected spikes obtained from `findSpikes()`.
    """
    
    # Cut 125 samples (5 ms) before and after each peak
    cut_spikes = np.array([sweep_IB_concatenated[(peaks[p]-125) : (peaks[p]+125)] for p in range(len(peaks))])

    # Get baseline for each spike by averaging 1-3 ms before each peak
    cut_spikes_holding = np.array([np.mean(sweep_IB_concatenated[(peaks[p]-100) : (peaks[p]-25)]) for p in range(len(peaks))])

    # Subtract baseline from cut spikes
    cut_spikes_baselined = np.array([cut_spikes[i] - cut_spikes_holding[i] for i in range(len(cut_spikes))])

    # Plot cut spikes after baselining
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
    import matplotlib.cm as cm
    baselined_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined)))
    for s in range(len(cut_spikes_baselined)):
            plt.plot(cut_spikes_baselined[s], color = baselined_spikes_colors[s])
    plt.title('Cut and baselined spikes', fontsize = 14)
    plt.ylabel('current [pA]', fontsize = 12)
    plt.xlim([((len(cut_spikes_baselined[0])/2)-45), ((len(cut_spikes_baselined[0])/2)+55)])
    fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
    plt.show()
    # plt.pause(5) # Use this if you are running the full script so it gives you a few seconds to see the plot before it moves to the next chunk of code.

    return cut_spikes, cut_spikes_holding, cut_spikes_baselined # ndarray, ndarray, ndarray

def plotSpikesQC(
    file_name,
    peaks,
    peaks_properties,
    cut_spikes_baselined
    ):
    """
    `plotSpikesQC` generates a summary plot that can be used to identify the metrics useful for choosing the parameters to quality control the detected spikes. The summary plot contains (1) a subplot with all the detected spikes after cutting and baselining, and (2) three subplots with the histograms of the main metrics that can be used to detect noise in the detected spikes, which are `width_heights`, `widths`, and `peak_heights`.
    It only outputs the plot for visualisation purposes and does not return any variable. 
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :peaks: indices of detected spikes obtained from `findSpikes()`.
    :peaks_properties: dictionary containing properties of the peaks returned by scipy's `find_peaks` in `findSpikes`.
    :cut_spikes_baselined: numpy array containing the baselined cut spikes.
    """

    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

    # Stack the nested array to access same position in all spikes
    cut_spikes_stack = np.vstack(cut_spikes_baselined)
    cut_spikes_peak_index = int(len(cut_spikes_baselined[0])/2) # get the index where the peak is

    # Get color palette and generate one color for each spike
    import matplotlib.cm as cm
    baselined_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined)))

    # Generate figure layout
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100)
    axs = fig.subplot_mosaic(
        """
        AB
        CD
        EF
        GH
        """
    )

    # Plot cut and baselined spikes
    for s in range(len(cut_spikes_baselined)):
        axs['A'].plot(cut_spikes_baselined[s], color = baselined_spikes_colors[s])
    axs['A'].set_title('Cut and baselined spikes', fontsize = 12)
    axs['A'].set_xlim([((len(cut_spikes_baselined[0])/2)-45), ((len(cut_spikes_baselined[0])/2)+55)])
    axs['A'].set_ylabel('current [pA]')
    
    # Plot Histogram of the peak prominences
    axs['B'].hist(peaks_properties['prominences'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
    axs['B'].set_title('Prominences ["p"]', fontsize = 12)
    # Plot Histogram of the height at which widths where evaluated
    axs['C'].hist(peaks_properties['width_heights'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
    axs['C'].set_title('Width heights ["wh"]', fontsize = 12)
    # Plot Histogram of peak widths
    axs['D'].hist(peaks_properties['widths'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
    axs['D'].set_title('Peak widths ["pw"]', fontsize = 12)
    # Plot Histogram of peak heights
    axs['E'].hist(peaks_properties['peak_heights'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
    axs['E'].set_title('Peak heights ["ph"]', fontsize = 12)
    # Plot Histogram of peak value after baselining
    axs['F'].hist((cut_spikes_stack[:,cut_spikes_peak_index]), bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
    axs['F'].set_title('Peak baselined ["pb"]', fontsize = 12)
    # Plot Histogram of left bases
    axs['G'].hist((peaks - peaks_properties['left_bases']), bins = 100, density = False, histtype = 'bar', log = False, color = 'k')
    axs['G'].set_title('Left bases ["lb"]', fontsize = 12)
    # Plot Histogram of right bases
    axs['H'].hist((peaks_properties['right_bases'] - peaks), bins = 100, density = False, histtype = 'bar', log = False, color = 'k')
    axs['H'].set_title('Right bases ["rb"]', fontsize = 12)

    # Add title
    plt.suptitle(f'QC metrics for {cell_id[0]}', fontsize = 14)
    
    # Move figure to top left corner
    fig.canvas.manager.window.move(0, 0)
    plt.show()
    # plt.pause(5) # Use this if you are running the full script so it gives you a few seconds to see the plot before it moves to the next chunk of code.

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
    `getSpikesQC` allows to perform quality control on the detected spikes by defining thresholds in three different metrics. It then generates a summary plot that can be used to assess whether the chosen metrics correctly remove the noise and leave the true spikes untouched. The summary plot contains (1) a subplot with all the detected spikes after cutting and baselining, coloring the noise traces according to the QC metric that excludes them, and (2) three subplots with the histograms of the metrics used, which are `width_heights`, `widths`, and `peak_heights`.
    If the result is satisfactory, it returns a dataframe with the selected filters. 
    
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

    # Generate figure layout
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig, axs = plt.subplots (2, 2, tight_layout = True, figsize = (7, 5), dpi = 100)

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
    happy_QC = input("Are you happy with your choice of parameters for QC? y/n")

    if happy_QC == 'y':
        parameters_QC = pd.DataFrame([[QC_wh_min, QC_wh_max, QC_pw_min, QC_pw_max, QC_ph_min, QC_ph_max, filter_by]], columns = ['QC_wh_min', 'QC_wh_max', 'QC_pw_min', 'QC_pw_max', 'QC_ph_min', 'QC_ph_max', 'filter_by'], index = file_id)
        print('QC completed')
    else:
        print('Try running getSpikesQC() again with different parameters')
        plt.close()
        return None # return empty variables to prevent wrong results from being used

    plt.close()

    return parameters_QC # pandas dataframe

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
    `denoiseSpikes` removes detected peaks according to the chosen parameters. It first plots the cut, baselined, and denoised spikes to visualise whether the selected parameters lead to a successful denoising. It then removes the indices corresponding to noise from `peaks` and `cut_spikes_baselined`. It returns an array containing the `peaks_denoised` and another containing the `cut_spikes_baselined_denoised`, which can be used for downstream analysis to compute firing rate and other parameters. It also returns a dataframe with the filters used for denoising.
    
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
        if np.any(noise_indices_wh):
            [noise_indices.append(noise_wh) for noise_wh in noise_indices_wh[0]]
    if 'pw' in filter_by:
        noise_indices_pw = np.where((peaks_properties['widths'] < QC_pw_min) | (peaks_properties['widths'] > QC_pw_max))
        if np.any(noise_indices_pw):
            [noise_indices.append(noise_pw) for noise_pw in noise_indices_pw[0]]
    if 'ph' in filter_by:
        noise_indices_ph = np.where((peaks_properties['peak_heights'] < QC_ph_min) | (peaks_properties['peak_heights'] > QC_ph_max))
        if np.any(noise_indices_ph):
            [noise_indices.append(noise_ph) for noise_ph in noise_indices_ph[0]]

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
    plt.show(block = True) # Lets you interact with plot and proceeds when figure is closed

    # Check whether denoising is complete
    happy_denoise = input("Are you happy with your choice of parameters for denoising? y/n")

    if happy_denoise == 'y':
        print('denoising completed')
        parameters_denoise = pd.DataFrame([[QC_wh_min, QC_wh_max, QC_pw_min, QC_pw_max, QC_ph_min, QC_ph_max, filter_by]], columns = ['QC_wh_min', 'QC_wh_max', 'QC_pw_min', 'QC_pw_max', 'QC_ph_min', 'QC_ph_max', 'filter_by'], index = file_id)
    else:
        print('Try running denoiseSpikes() again with different parameters')
        plt.close()
        return None, None, None # return empty variables to prevent wrong results from being used
    
    plt.close()

    return peaks_denoised, cut_spikes_baselined_denoised, parameters_denoise # ndarray, ndarray, pandas dataframe

def spikesQC(
    file_name,
    peaks,
    peaks_properties,
    cut_spikes,
    cut_spikes_holding,
    cut_spikes_baselined,
    filter_by = ['p', 'wh', 'pw', 'ph', 'pb', 'lb', 'rb'],
    QC_p_min = float('-inf'),
    QC_p_max = float('inf'),
    QC_wh_min = float('-inf'),
    QC_wh_max = float('inf'),
    QC_pw_min = float('-inf'),
    QC_pw_max = float('inf'),
    QC_ph_min = float('-inf'),
    QC_ph_max = float('inf'),
    QC_pb_min = float('-inf'),
    QC_pb_max = float('inf'),
    QC_lb_min = float('-inf'),
    QC_lb_max = float('inf'),
    QC_rb_min = float('-inf'),
    QC_rb_max = float('inf')
    ):

    """
    `spikesQC` is a combination of `getSpikesQC`and `denoiseSpikes`. It allows to perform quality control on the detected spikes by defining thresholds in seven different metrics that can be previously explored using `plotSpikesQC`. It first generates a summary plot that contains (1) a subplot with all the detected spikes after cutting and baselining, coloring the noise traces according to the QC metric that excludes them, and (2) seven subplots with the histograms of the metrics used, which are `prominence`, `width_heights`,  `widths`, `peak_heights`, `peak_baselined`, `left_bases`, and `right_bases`. This allows the user to visualise whether the selected parameters lead to a successful denoising. It then removes the indices corresponding to noise from `peaks`, `cut_spikes`, `cut_spikes_holding`, and `cut_spikes_baselined` and generates a plot with all the detected spikes that meet the quality criteria.
    It returns four arrays containing the `peaks_QC`, `cut_spikes_QC`, `cut_spikes_holding_QC`, and `cut_spikes_baselined_QC`, which can be used for downstream analysis to compute firing rate and other parameters. It also returns a dataframe with the filters used for quality control.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :peaks: indices of detected spikes obtained from `findSpikes()`.
    :peaks_properties: dictionary containing properties of the peaks returned by scipy's `find_peaks` in `findSpikes`.
    :cut_spikes: numpy array containing the cut spikes.
    :cut_spikes_holding: numpy array containing the baseline before each peak.
    :cut_spikes_baselined: numpy array containing the baselined cut spikes.
    :filter_by: metrics to be used to detect noise. Defaults to ['p', 'wh', 'pw', 'ph', 'pm', 'lb', 'rb'].
    :QC_p_min: value of `prominence` below which a peak will be considered noise. Defaults to -inf.
    :QC_p_max: value of `prominence` above which a peak will be considered noise. Defaults to inf.
    :QC_wh_min: value of `width_heights` below which a peak will be considered noise. Defaults to -inf.
    :QC_wh_max: value of `width_heights` above which a peak will be considered noise. Defaults to inf.
    :QC_pw_min: value of `widths` below which a peak will be considered noise. Defaults to -inf.
    :QC_pw_max: value of `widths` above which a peak will be considered noise. Defaults to inf.
    :QC_ph_min: value of `peak_heights` below which a peak will be considered noise. Defaults to -inf.
    :QC_ph_max: value of `peak_heights` above which a peak will be considered noise. Defaults to inf.
    :QC_pb_min: value of `peak_baselined` below which a peak will be considered noise. Defaults to -inf.
    :QC_pb_max: value of `peak_baselined` above which a peak will be considered noise. Defaults to inf.
    :QC_lb_min: value of `left_bases` below which a peak will be considered noise. Defaults to -inf.
    :QC_lb_max: value of `left_bases` above which a peak will be considered noise. Defaults to inf.
    :QC_rb_min: value of `right_bases` below which a peak will be considered noise. Defaults to -inf.
    :QC_rb_max: value of `right_bases` above which a peak will be considered noise. Defaults to inf.
    """
    
    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

    # Stack the nested array to access same position in all spikes
    cut_spikes_stack = np.vstack(cut_spikes_baselined)
    cut_spikes_peak_index = int(len(cut_spikes_baselined[0])/2) # get the index where the peak is

    # Get color palette and generate one color for each metric
    cmap = plt.get_cmap('tab20')
    c_p = cmap(17)
    c_wh = cmap(13)
    c_pw = cmap(9)
    c_ph = cmap(3)
    c_pb = cmap(7)
    c_lb = cmap(1)
    c_rb = cmap(19)
    c_spikes = 'lightgray' # gray - clean spikes

    # Generate figure layout
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100)
    axs = fig.subplot_mosaic(
        """
        AB
        CD
        EF
        GH
        """
    )

    # Plot cut and baselined spikes colored by whether they pass the desired QC or not.
    for s in range(len(cut_spikes_baselined)):
        if 'p' in filter_by and (peaks_properties['prominences'][s] < QC_p_min or peaks_properties['prominences'][s] > QC_p_max):
            axs['A'].plot(cut_spikes_baselined[s], c = c_p)
        elif 'wh' in filter_by and (peaks_properties['width_heights'][s] < QC_wh_min or peaks_properties['width_heights'][s] > QC_wh_max):
            axs['A'].plot(cut_spikes_baselined[s], c = c_wh)
        elif 'pw' in filter_by and (peaks_properties['widths'][s] < QC_pw_min or peaks_properties['widths'][s] > QC_pw_max):
            axs['A'].plot(cut_spikes_baselined[s], c = c_pw)
        elif 'ph' in filter_by and (peaks_properties['peak_heights'][s] < QC_ph_min or peaks_properties['peak_heights'][s] > QC_ph_max):
            axs['A'].plot(cut_spikes_baselined[s], c = c_ph)
        elif 'pb' in filter_by and ((cut_spikes_stack[:,cut_spikes_peak_index])[s] < QC_pb_min or (cut_spikes_stack[:,cut_spikes_peak_index])[s] > QC_pb_max):
            axs['A'].plot(cut_spikes_baselined[s], c = c_pb)
        elif 'lb' in filter_by and ((peaks - peaks_properties['left_bases'])[s] < QC_lb_min or (peaks - peaks_properties['left_bases'])[s] > QC_lb_max):
            axs['A'].plot(cut_spikes_baselined[s], c = c_lb)
        elif 'rb' in filter_by and ((peaks_properties['right_bases'] - peaks)[s] < QC_rb_min or (peaks_properties['right_bases'] - peaks)[s] > QC_rb_max):
            axs['A'].plot(cut_spikes_baselined[s], c = c_rb)
        else:
            axs['A'].plot(cut_spikes_baselined[s], c = c_spikes)
    axs['A'].set_title('Spikes colored by QC parameters', fontsize = 12)
    axs['A'].set_xlim([((len(cut_spikes_baselined[0])/2)-45), ((len(cut_spikes_baselined[0])/2)+55)])
    axs['A'].set_ylabel('current [pA]')
    
    # Plot Histogram of the peak prominences
    n_p, bins_p, patches_p = axs['B'].hist(peaks_properties['prominences'], bins = 100, density = False, histtype = 'bar', log = True)
    for i in range(len(patches_p)):
        if (bins_p[i] < QC_p_min or bins_p[i] > QC_p_max):
            patches_p[i].set_facecolor(c_p)
        else:
            patches_p[i].set_facecolor('lightgray')
    axs['B'].set_title('Prominences ["p"]', fontsize = 12)
    # Plot Histogram of the height at which widths where evaluated
    n_wh, bins_wh, patches_wh = axs['C'].hist(peaks_properties['width_heights'], bins = 100, density = False, histtype = 'bar', log = True)
    for i in range(len(patches_wh)):
        if (bins_wh[i] < QC_wh_min or bins_wh[i] > QC_wh_max):
            patches_wh[i].set_facecolor(c_wh)
        else:
            patches_wh[i].set_facecolor('lightgray')
    axs['C'].set_title('Width heights ["wh"]', fontsize = 12)
    # Plot Histogram of peak widths
    n_pw, bins_pw, patches_pw = axs['D'].hist(peaks_properties['widths'], bins = 100, density = False, histtype = 'bar', log = True)
    for i in range(len(patches_pw)):
        if (bins_pw[i] < QC_pw_min or bins_pw[i] > QC_pw_max):
            patches_pw[i].set_facecolor(c_pw)
        else:
            patches_pw[i].set_facecolor('lightgray')
    axs['D'].set_title('Peak widths ["pw"]', fontsize = 12)
    # Plot Histogram of peak heights
    n_ph, bins_ph, patches_ph = axs['E'].hist(peaks_properties['peak_heights'], bins = 100, density = False, histtype = 'bar', log = True)
    for i in range(len(patches_ph)):
        if (bins_ph[i] < QC_ph_min or bins_ph[i] > QC_ph_max):
            patches_ph[i].set_facecolor(c_ph)
        else:
            patches_ph[i].set_facecolor('lightgray')
    axs['E'].set_title('Peak heights ["ph"]', fontsize = 12)
    # Plot Histogram of peak value after baselining
    n_pb, bins_pb, patches_pb = axs['F'].hist((cut_spikes_stack[:,cut_spikes_peak_index]), bins = 100, density = False, histtype = 'bar', log = True)
    for i in range(len(patches_pb)):
        if (bins_pb[i] < QC_pb_min or bins_pb[i] > QC_pb_max):
            patches_pb[i].set_facecolor(c_pb)
        else:
            patches_pb[i].set_facecolor('lightgray')
    axs['F'].set_title('Peak baselined ["pb"]', fontsize = 12)
    # Plot Histogram of left bases
    n_lb, bins_lb, patches_lb = axs['G'].hist((peaks - peaks_properties['left_bases']), bins = 100, density = False, histtype = 'bar', log = False)
    for i in range(len(patches_lb)):
        if (bins_lb[i] < QC_lb_min or bins_lb[i] > QC_lb_max):
            patches_lb[i].set_facecolor(c_lb)
        else:
            patches_lb[i].set_facecolor('lightgray')
    axs['G'].set_title('Left bases ["lb"]', fontsize = 12)
    # Plot Histogram of right bases
    n_rb, bins_rb, patches_rb = axs['H'].hist((peaks_properties['right_bases'] - peaks), bins = 100, density = False, histtype = 'bar', log = False)
    for i in range(len(patches_rb)):
        if (bins_rb[i] < QC_rb_min or bins_rb[i] > QC_rb_max):
            patches_rb[i].set_facecolor(c_rb)
        else:
            patches_rb[i].set_facecolor('lightgray')
    axs['H'].set_title('Right bases ["rb"]', fontsize = 12)

    # Add title
    plt.suptitle(f'QCed spikes from {cell_id[0]}', fontsize = 14)
    
    # Move figure to top left corner
    fig.canvas.manager.window.move(0, 0)
    plt.show(block = True) # Lets you interact with plot and proceeds once figure is closed
    # plt.pause(0.5)
    
    # Check whether chosen parameters are satisfactory
    happy_parameter = input("Are you happy with your choice of parameters for QC? y/n")
    
    if happy_parameter == 'y':
        print('proceeding to remove peaks that do not qualify as spikes')
        plt.close()
    else:
        print('Try running spikesQC() again with different parameters')
        plt.close()
        return None, None, None, None, None # return empty variables to prevent wrong results from being used

    # Use the selected parameters to find the indices of peaks that are not spikes
    noise_indices = []
    if 'p' in filter_by:
        noise_indices_p = np.where((peaks_properties['prominences'] < QC_p_min) | (peaks_properties['prominences'] > QC_p_max))
        if np.any(noise_indices_p):
            [noise_indices.append(noise_p) for noise_p in noise_indices_p[0]]
    if 'wh' in filter_by:
        noise_indices_wh = np.where((peaks_properties['width_heights'] < QC_wh_min) | (peaks_properties['width_heights'] > QC_wh_max))
        if np.any(noise_indices_wh):
            [noise_indices.append(noise_wh) for noise_wh in noise_indices_wh[0]]
    if 'pw' in filter_by:
        noise_indices_pw = np.where((peaks_properties['widths'] < QC_pw_min) | (peaks_properties['widths'] > QC_pw_max))
        if np.any(noise_indices_pw):
            [noise_indices.append(noise_pw) for noise_pw in noise_indices_pw[0]]
    if 'ph' in filter_by:
        noise_indices_ph = np.where((peaks_properties['peak_heights'] < QC_ph_min) | (peaks_properties['peak_heights'] > QC_ph_max))
        if np.any(noise_indices_ph):
            [noise_indices.append(noise_ph) for noise_ph in noise_indices_ph[0]]
    if 'pb' in filter_by:
        noise_indices_pb = np.where((cut_spikes_stack[:,cut_spikes_peak_index] < QC_pb_min) | (cut_spikes_stack[:,cut_spikes_peak_index] > QC_pb_max))
        if np.any(noise_indices_pb):
            [noise_indices.append(noise_pb) for noise_pb in noise_indices_pb[0]]
    if 'lb' in filter_by:
        noise_indices_lb = np.where(((peaks - peaks_properties['left_bases']) < QC_lb_min) | ((peaks - peaks_properties['left_bases']) > QC_lb_max))
        if np.any(noise_indices_lb):
            [noise_indices.append(noise_lb) for noise_lb in noise_indices_lb[0]]
    if 'rb' in filter_by:
        noise_indices_rb = np.where(((peaks_properties['right_bases'] - peaks) < QC_rb_min) | ((peaks_properties['right_bases'] - peaks) > QC_rb_max))
        if np.any(noise_indices_rb):
            [noise_indices.append(noise_rb) for noise_rb in noise_indices_rb[0]]

    # Remove duplicates from noise_indices
    noise_indices_to_delete = np.unique(noise_indices)

    # Remove the indices corresponding to noise 
    peaks_QC = np.delete(peaks, noise_indices_to_delete, 0)
    cut_spikes_QC = np.delete(cut_spikes, noise_indices_to_delete, 0)
    cut_spikes_holding_QC = np.delete(cut_spikes_holding, noise_indices_to_delete, 0)
    cut_spikes_baselined_QC = np.delete(cut_spikes_baselined, noise_indices_to_delete, 0)
    print(f"The number of detected spikes was: {len(cut_spikes_baselined)}")
    print(f"The number of QCed spikes is: {len(cut_spikes_baselined_QC)}")

    # Plot cut, baselined, and QCed spikes to check whether denoising is complete.
    import matplotlib.cm as cm
    denoised_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined_QC)))
    get_ipython().run_line_magic('matplotlib', 'qt') # avoid 'tk' here
    fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
    for s in range(len(cut_spikes_baselined_QC)):
        plt.plot(cut_spikes_baselined_QC[s], color = denoised_spikes_colors[s])
    plt.xlim([((len(cut_spikes_baselined_QC[0])/2)-45), ((len(cut_spikes_baselined_QC[0])/2)+55)])
    plt.title('Cut, baselined, and QCed spikes', fontsize = 14)
    plt.xlabel('samples', fontsize = 12)
    plt.ylabel('current [pA]', fontsize = 12)
    fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
    plt.show(block = True) # Lets you interact with plot and proceeds once figure is closed
    # plt.pause(0.5)
    
    # Check whether QC is complete
    happy_QC = input("Are you happy with the results from this quality control? y/n")

    if happy_QC == 'y':
        parameters_QC = pd.DataFrame([[QC_p_min, QC_p_max, QC_wh_min, QC_wh_max, QC_pw_min, QC_pw_max, QC_ph_min, QC_ph_max, QC_pb_min, QC_pb_max, QC_lb_min, QC_lb_max, QC_rb_min, QC_rb_max, filter_by]], columns = ['QC_p_min', 'QC_p_max', 'QC_wh_min', 'QC_wh_max', 'QC_pw_min', 'QC_pw_max', 'QC_ph_min', 'QC_ph_max', 'QC_pb_min', 'QC_pb_max', 'QC_lb_min', 'QC_lb_max', 'QC_rb_min', 'QC_rb_max', 'filter_by'], index = file_id)
        print('QC completed')
        print(f"The number of spikes removed during QC was: {len(noise_indices_to_delete)}")
    else:
        print('Try running spikesQC() again with different parameters')
        plt.close()
        return None, None, None, None, None # return empty variables to prevent wrong results from being used
    
    plt.close()

    return peaks_QC, cut_spikes_QC, cut_spikes_holding_QC, cut_spikes_baselined_QC, parameters_QC # ndarray, ndarray, ndarray, ndarray,pandas dataframe

def cleanSpikes(
    file_name,
    cut_spikes_baselined_QC
    ):
    """
    `cleanSpikes` allows the user to identify and remove any spikes that have been incorrectly baselined by looking at the value of the peak. It first plots the baselined spikes and a histogram of all the peak values. It then asks the user to define a threshold above which a peak will be deemed incorrectly baselined and will be removed. It finally plots the remaining baselined spikes and colors the removed peaks in the histogram.
    It returns an array containing all the spikes that are properly baselined, which can be used to compute an average spike and its main parameters. It also returns a dataframe with the filters used for spike clean up.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :cut_spikes_baselined_QC: array containing the detected spikes after baselining and removing noise.
    """
    
    # Stack the nested array to access same position in all spikes
    cut_spikes_stack = np.vstack(cut_spikes_baselined_QC)
    cut_spikes_peak_index = int(len(cut_spikes_baselined_QC[0])/2) # get the index where the peak is

    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

    # Get color palette and generate one color for each spike
    import matplotlib.cm as cm
    denoised_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined_QC)))

    # Generate figure layout
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig, axs = plt.subplots (2, 2, tight_layout = True, figsize = (7, 5), dpi = 100) # Set figure size

    # Plot cut, baselined, and QCed spikes
    for s in range(len(cut_spikes_baselined_QC)):
        axs[0,0].plot(cut_spikes_baselined_QC[s], color = denoised_spikes_colors[s])
    axs[0,0].set_title('Cut, baselined, and QCed spikes', fontsize = 12)
    axs[0,0].set_xlim([((len(cut_spikes_baselined_QC[0])/2)-45), ((len(cut_spikes_baselined_QC[0])/2)+55)])
    axs[0,0].set_xlabel('samples', fontsize = 12)
    axs[0,0].set_ylabel('current [pA]', fontsize = 12)

    # Plot Histogram of the peak values for each baselined spike
    axs[0,1].hist(cut_spikes_stack[:,cut_spikes_peak_index], bins = 200, density = False, histtype = 'bar', log = True, color = 'k')
    axs[0,1].set_title('Histogram of peak values for baselined spikes', fontsize = 12)
    axs[0,1].set_xlabel('peak value [pA]', fontsize = 12)

    # Add title
    plt.suptitle(f'Baselined spikes from {cell_id[0]}', fontsize = 14)

    # Move figure to top left corner
    fig.canvas.manager.window.move(0, 0)
    plt.pause(0.5)

    # Based on the histogram above, select the peak value threshold that will identify spikes that were not properly baselined
    peak_min = int(input("Enter the peak value above which to exclude incorrectly baselined spikes"))

    # Select the spikes that couldn't be properly baselined
    spikes_indices_to_remove = np.where(cut_spikes_stack[:,cut_spikes_peak_index] > peak_min)
    # Remove duplicates from spikes_indices_to_remove
    spikes_to_remove = np.unique(spikes_indices_to_remove)
    # Remove spikes that couldn't be properly baselined
    cut_spikes_baselined_clean = np.delete(cut_spikes_baselined_QC, spikes_to_remove, 0)
    print(f"The number of QCed spikes was: {len(cut_spikes_baselined_QC)}")
    print(f"The number of clean spikes is: {len(cut_spikes_baselined_clean)}")

    # Now show the results
    clean_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined_clean)))

    # Plot cut, baselined, QCed, and clean spikes
    for s in range(len(cut_spikes_baselined_clean)):
        axs[1,0].plot(cut_spikes_baselined_clean[s], color = clean_spikes_colors[s])
    axs[1,0].set_title('Cut, baselined, QCed, and cleaned spikes', fontsize = 12)
    axs[1,0].set_xlim([((len(cut_spikes_baselined_clean[0])/2)-45), ((len(cut_spikes_baselined_clean[0])/2)+55)])
    axs[1,0].set_xlabel('samples', fontsize = 12)
    axs[1,0].set_ylabel('current [pA]', fontsize = 12)

    # Plot Histogram of the peak values for each baselined spike
    n_1, bins_1, patches_1 = axs[1,1].hist(cut_spikes_stack[:,cut_spikes_peak_index], bins = 200, density = False, histtype = 'bar', log = True)
    for i in range(len(patches_1)):
        if (bins_1[i] > peak_min):
                patches_1[i].set_facecolor('r')
        else:
            patches_1[i].set_facecolor('lightgray')
    axs[1,1].set_title('Histogram of peak values for baselined spikes', fontsize = 12)
    axs[1,1].set_xlabel('peak value [pA]', fontsize = 12)

    plt.pause(0.5)

    # Check whether clean up is complete
    happy_clean = input("Are you happy with your choice of filter? y/n")

    if happy_clean == 'y':
        parameters_clean = pd.DataFrame([[peak_min]], columns = ['peak_min_pA'], index = file_id)
        print('Clean up completed')
        print(f"The number of spikes removed was: {len(spikes_to_remove)}")
    else:
        print('Try running cleanSpikes() again')
        plt.close()
        return None, None # return empty variables to prevent wrong results from being used
        
    plt.close()

    return cut_spikes_baselined_clean, parameters_clean # ndarray, pandas dataframe

def averageSpikes(
    cut_spikes_baselined_clean
    ):
    """
    `averageSpikes` computes an average spike from all the detected spikes after baseline, QC, and clean up. It then generates a plot with all the detected spikes and the average overlayed.
    It returns an array with the values of the average spike that can be used to compute parameters of interest for further analysis.
    
    :cut_spikes_baselined_clean: array containing the detected spikes after baselining, quality control, and removing the spikes incorrectly baselined.
    """
 
    # Compute average from all detected spikes after baseline, QC, denoising, and clean up
    average_spike = np.array(np.mean(cut_spikes_baselined_clean, 0))
    
    # Plot the detected spikes and the computed average
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
    for s in range(len(cut_spikes_baselined_clean)):
        plt.plot(cut_spikes_baselined_clean[s], 'k')
    plt.plot(average_spike, color = 'r')
    plt.title('Cut spikes with average in red', fontsize = 14)
    plt.ylabel('current [pA]', fontsize = 12)
    plt.xlim([((len(cut_spikes_baselined_clean[0])/2)-45), ((len(cut_spikes_baselined_clean[0])/2)+55)])
    fig.canvas.manager.window.move(0, 0)
    plt.show()
    # plt.pause(5) # Use this if you are running the full script so it gives you a few seconds to see the plot before it moves to the next chunk of code.

    return average_spike # ndarray

def getSpikeParameters(
    file_name,
    cut_spikes_baselined_clean,
    average_spike,
    sampling_rate_khz = 25
    ):
    """
    `getSpikeParameters` computes key parameters that can be used to characterise the average spike shape.
    It returns a dataframe with the spike onset, end, and magnitude, as well as the total duration of the spike and the time from onset to peak.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :cut_spikes_baselined_clean: array containing the detected spikes after baselining, quality control, and removing the spikes incorrectly baselined.
    :average_spike: array containing the values of the average spike.
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.

    """
    # Get delta_t from sampling rate:
    dt = 1/sampling_rate_khz

    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

    # Find the peak magnitude and where the peak is, defined by the cutSpikes() function (should be sample 125)
    spike_magnitude = min(average_spike)
    average_spike_peak_index = int(np.where(average_spike == min(average_spike))[0]) # needs to be an integer
    
    # Compute the mean and std of the 3ms period used to baseline the cut spikes
    baseline_average_spike = average_spike[(average_spike_peak_index-100):(average_spike_peak_index-25)]
    baseline_average_spike_mean = np.mean(baseline_average_spike)
    baseline_average_spike_std = np.std(baseline_average_spike)

    # Define threshold for onset: we set a one-tailed threshold (the spike will always go negative) at the value that corresponds to the mean minus "x" times the std. "x" is defined by using the norm.ppf() function from scipy.stats, which takes a percentage and returns a standard deviation multiplier for what value that percentage occurs at.
    onset_threshold_average_spike = baseline_average_spike_mean - (stats.norm.ppf(0.9973)*baseline_average_spike_std)

    # Calculate spike onset, starting at the index where the baseline epoch ends
    for i, s in enumerate(average_spike[(average_spike_peak_index-25):average_spike_peak_index]): # i is the index, s is the value
        if s < onset_threshold_average_spike:
            average_spike_onset_index = i + (average_spike_peak_index-25)
            break # once you find the index, break the loop

    # Define threshold for end: we set a two-tailed threshold (we cannot know from which side the spike will return to baseline, as this will depend on any currents present after the action potential ends) at the value that corresponds to the mean minus "x" times the std. "x" is defined by using the norm.ppf() function from scipy.stats, which takes a percentage and returns a standard deviation multiplier for what value that percentage occurs at.
    end_min_threshold_average_spike = baseline_average_spike_mean - (stats.norm.ppf(0.99865)*baseline_average_spike_std)
    end_max_threshold_average_spike = baseline_average_spike_mean + (stats.norm.ppf(0.99865)*baseline_average_spike_std)

    # Calculate the spike end: one way to do this is to compare the values after the peak and find the point where n consecutive samples fall back within the baseline distribution.
    for i, s in enumerate(average_spike[average_spike_peak_index:]): # i is the index, s is the value
        if (end_min_threshold_average_spike < s < end_max_threshold_average_spike) and (end_min_threshold_average_spike < average_spike[average_spike_peak_index:][i+1] < end_max_threshold_average_spike) and (end_min_threshold_average_spike < average_spike[average_spike_peak_index:][i+2] < end_max_threshold_average_spike) and (end_min_threshold_average_spike < average_spike[average_spike_peak_index:][i+3] < end_max_threshold_average_spike) and (end_min_threshold_average_spike < average_spike[average_spike_peak_index:][i+4] < end_max_threshold_average_spike) and (end_min_threshold_average_spike < average_spike[average_spike_peak_index:][i+5] < end_max_threshold_average_spike):
            average_spike_end_index = i + average_spike_peak_index
            break

    # Another method to calculate the spike end is to start from the back of the average spike trace and find the point after which n consecutive samples fall outside the baseline distribution:
    # for i, s in enumerate(average_spike[::-1]): # i is the index, s is the value
    #     if (s < end_min_threshold_average_spike or s > end_max_threshold_average_spike) and (average_spike[::-1][i+1] < end_min_threshold_average_spike or average_spike[::-1][i+1] > end_max_threshold_average_spike) and (average_spike[::-1][i+2] < end_min_threshold_average_spike or average_spike[::-1][i+2] > end_max_threshold_average_spike):
    #         average_spike_end_index = len(average_spike) - i
    #         break

    # Plot the average spike with its onset and end
    get_ipython().run_line_magic('matplotlib', 'qt')    
    fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
    plt.plot(cut_spikes_baselined_clean.T, 'k') # cut spikes
    plt.plot(average_spike, 'r') # average spike
    plt.plot(average_spike_onset_index, average_spike[average_spike_onset_index], "oc") # spike onset
    plt.plot(average_spike_end_index, average_spike[average_spike_end_index], "oy") # spike end
    plt.ylabel('current [pA]', fontsize = 12)
    plt.axhline(y = onset_threshold_average_spike, c = 'c', ls = '--') # horizontal dashed line at threshold for onset
    plt.axhline(y = end_min_threshold_average_spike, c = 'y', ls = '--') # horizontal dashed line at negative threshold for onset
    plt.axhline(y = end_max_threshold_average_spike, c = 'y', ls = '--') # horizontal dashed line at positive threshold for onset
    plt.suptitle('Averaged spike with onset and end', fontsize = 14)
    #plt.xlim([((len(average_spike)/2)-45), ((len(average_spike)/2)+55)])
    fig.canvas.manager.window.move(0, 0)
    plt.show(block = True) # Lets you interact with plot and proceeds once figure is closed

    # Extract onset and end, calculate length and onset to peak
    spike_onset = average_spike_onset_index
    spike_end = average_spike_end_index
    spike_length = (spike_end - spike_onset) * dt
    spike_onset_to_peak = (average_spike_peak_index-spike_onset) * dt

    # Check whether spike analysis is complete
    happy_onset = input("Are you happy with the calculated onset and end? y/n")

    if happy_onset == 'y':
        parameters_avg_spike = pd.DataFrame([[spike_onset, spike_end, spike_length, spike_onset_to_peak, spike_magnitude]], columns = ['spike_onset_sample', 'spike_end_sample', 'spike_length_ms', 'spike_onset_to_peak_ms', 'spike_magnitude_pA'], index = file_id)
        print('spike parameters calculated')
        print(f'Spike onset at {spike_onset}')
        print(f'Spike end at {spike_end}')
        print(f'Spike length of {spike_length} ms')
        print(f'Spike onset to peak of {spike_onset_to_peak} ms')
        print(f'Spike magnitude of {round(spike_magnitude, 2)} pA')
    else:
        print('Try running getSpikeParameters() again')
        plt.close()
        return None # return empty variables to prevent wrong results from being used

    plt.close()

    return parameters_avg_spike # pandas dataframe

def getFiringRate(
    file_name,
    channels_dataframe,
    sweep_IB_concatenated,
    pseudo_sweep_concatenated,
    Rseal_dataframe,
    peaks_QC,
    sampling_rate_khz = 25,
    n_bins = 100
    ):
    """
    `getFiringRate` calculates the firing rate from the recorded cell following three approaches. Approach #1 calculates firing frequency by dividing total number of detected spikes over length of recording, approach #2 calculates firing frequency separately for each sweep, to examine how the firing rate changes over time, and approach #3 calculates firing frequency separately for each time window of our choice.
    It returns a separate dataframe with the results from each approach.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :channels_dataframe: dataframe with extracted data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    :sweep_IB_concatenated: numpy array containing the concatenated data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    :pseudo_sweep_concatenated: concatenated pseudo-sweep that has the same length and number of sweeps as the original data, with the difference that each sweep within the pseudo-sweep will be comprised of the number that reflects the real sweep ID.
    :Rseal_dataframe: dataframe with the Rseal values across sweeps for the time of recording.
    :peaks_QC: indices of the detected spikes obtained from `findSpikes()`, after quality control.
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.
    :n_bins: number of bins in which to divide the total length of recording. Defaults to 100.
    """

    # Get delta_t from sampling rate:
    dt = 1/sampling_rate_khz

    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id to print in plot

    # Method 1: calculate firing frequency by dividing total number of detected spikes over length of recording
    n_spikes = len(peaks_QC)
    recording_length = len(sweep_IB_concatenated) * dt / 1000 # in seconds
    firing_frequency = n_spikes / recording_length # in Hz

    firing_frequency_dataframe = pd.DataFrame([[n_spikes, recording_length, firing_frequency]], columns = ['n_spikes', 'recording_length_s', 'firing_frequency_Hz'], index = file_id)

    print(f'Neuron with ID {cell_id[0]}')
    print(f'Detected a total of {n_spikes} spikes')
    print(f'Duration of recording was {recording_length} seconds')
    print(f'Which gives a firing rate of {round(firing_frequency, 2)} Hz')

    # Method 2: calculate firing frequency separately for each sweep, to examine how the firing rate changes over time.
    # Initialise variables
    spikes_by_sweep_keys = []
    spikes_by_sweep = []
    n_spikes_sweep = []
    sweep_length = []
    sweep_firing_rate = []

    for sweep in channels_dataframe.columns: 
        # Take the spikes that belong to the current sweep
        spikes_in_sweep_tmp = np.array([p for i, p in enumerate(peaks_QC) if pseudo_sweep_concatenated[peaks_QC[i]] == int(sweep)])

        # Get firing rate for the current sweep
        sweep_length_s_tmp = len(channels_dataframe.loc['Channel B', sweep]) * dt / 1000 # in seconds
        n_spikes_sweep_tmp = len(spikes_in_sweep_tmp)
        firing_rate_sweep_tmp = n_spikes_sweep_tmp / sweep_length_s_tmp

        # Append results
        spikes_by_sweep_keys.append(int(sweep))
        spikes_by_sweep.append(spikes_in_sweep_tmp)
        n_spikes_sweep.append(n_spikes_sweep_tmp)
        sweep_length.append(sweep_length_s_tmp)
        sweep_firing_rate.append(firing_rate_sweep_tmp)

    spikes_by_sweep_dataframe = pd.DataFrame([spikes_by_sweep, n_spikes_sweep, sweep_length, sweep_firing_rate], index = ['spikes_by_sweep', 'n_spikes_sweep', 'sweep_length', 'sweep_firing_rate'], columns = spikes_by_sweep_keys)

    # Method 3: calculate firing frequency for a time window of our choice, to examine how the firing rate changes over time.

    time_window_s = len(pseudo_sweep_concatenated) / 1000 * dt / n_bins # divide the length of recording in 100 chunks (1-2s each)
    time_window_samples = len(pseudo_sweep_concatenated) / n_bins
    spikes_by_window = []
    n_spikes_window = []
    window_length = []
    window_firing_rate = []

    for window in range(n_bins): 
        # Take the spikes that belong to the current bin
        spikes_in_window_tmp = np.array([p for p in peaks_QC if ((time_window_samples*window) < p < (time_window_samples*(window+1)))])

        # Get firing rate for the current bin
        n_spikes_window_tmp = len(spikes_in_window_tmp)
        firing_rate_tmp = n_spikes_window_tmp / time_window_s

        # Append results
        spikes_by_window.append(spikes_in_window_tmp)
        n_spikes_window.append(n_spikes_window_tmp)
        window_length.append(time_window_s)
        window_firing_rate.append(firing_rate_tmp)

    spikes_by_window_dataframe = pd.DataFrame([spikes_by_window, n_spikes_window, window_length, window_firing_rate], index = ['spikes_by_window', 'n_spikes_window', 'window_length_s', 'window_firing_rate_Hz'], columns = range(n_bins))

    # Visualise results
    # Generate figure layout
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig, axs = plt.subplots (2, 2, tight_layout = True, figsize = (7, 5), dpi = 100)

    # Plot firing rate by sweep throughout the recording.
    axs[0,0].plot(spikes_by_sweep_keys, sweep_firing_rate, 'k')
    axs[0,0].set_title('Firing rate across sweeps', fontsize = 12)
    axs[0,0].set_xlabel('sweep number', fontsize = 10)
    axs[0,0].set_ylabel('Firing Rate [Hz]', fontsize = 10)
    axs[0,0].set_ylim(0, round(firing_frequency*2))

    # Check whether the sweep firing rate correlates with seal resistance
    axs[0,1].scatter(Rseal_dataframe.loc['seal_resistance_MOhm'], sweep_firing_rate)
    axs[0,1].set_title('Sweep firing rate vs Seal Resistance', fontsize = 12)
    axs[0,1].set_xlabel('Seal Resistance [MOhm]', fontsize = 10)
    axs[0,1].set_ylabel('Firing Rate [Hz]', fontsize = 10)
    axs[0,1].set_ylim(0, round(firing_frequency*2))

    # Plot firing rate by bin throughout the recording.
    axs[1,0].plot(window_firing_rate, 'k')
    axs[1,0].set_title(f'Firing rate across {round(time_window_s, 2)} s bins', fontsize = 12)
    axs[1,0].set_xlabel('time bin #', fontsize = 10)
    axs[1,0].set_ylabel('Firing Rate [Hz]', fontsize = 10)
    axs[1,0].set_ylim(0, round(firing_frequency*2))

    # Plot firing rate for the recorded neuron.
    axs[1,1].axis('off')
    axs[1,1].text(0.5, 0.5, s = f'Neuron with ID\n{cell_id[0]}\n\nFiring rate of {round(firing_frequency, 2)} Hz', ha = 'center', va = 'center', wrap = True, in_layout = True)

    fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
    plt.show()
    # plt.pause(5) # Use this if you are running the full script so it gives you a few seconds to see the plot before it moves to the next chunk of code.

    return firing_frequency_dataframe, spikes_by_sweep_dataframe, spikes_by_window_dataframe # pandas dataframe, pandas dataframe, pandas dataframe

def getInterspikeInterval(
    sweep_IB_concatenated,
    pseudo_sweep_concatenated,
    peaks_QC,
    sampling_rate_khz = 25
    ):
    """
    `getInterspikeInterval` calculates the interspike interval between all the detected spikes on a sweep by sweep basis. It generates a summary plot with a histogram of the calculated interspike intervals as well as a scatter plot of the relationship between the interspike interval and the average or standard deviation of the injected current between each pair of spikes.
    It returns a dataframe containing the interspike interval together with the average and standard deviation of the  injected current between each pair of spikes.
    
    :sweep_IB_concatenated: numpy array containing the concatenated data from a loose-seal recording (e.g. gap-free protocol with a short test pulse in the beginning).
    :pseudo_sweep_concatenated: concatenated pseudo-sweep that has the same length and number of sweeps as the original data, with the difference that each sweep within the pseudo-sweep will be comprised of the number that reflects the real sweep ID.
    :peaks_QC: indices of the detected spikes obtained from `findSpikes()`, after quality control.
    :sampling_rate_khz: sampling rate in KHz. Defaults to 25 KHz.
    """
    # Get delta_t from sampling rate:
    dt = 1/sampling_rate_khz

    # Initialise variables
    interspike_interval = []
    holding_isi_avg = []
    holding_isi_std = []

    for p in range(len(peaks_QC)-1):
        # Check that both spikes you are evaluating are in the same sweep:
        if pseudo_sweep_concatenated[peaks_QC[p]] == pseudo_sweep_concatenated[peaks_QC[p+1]]:
            # Calculate interspike interval
            interspike_tmp = peaks_QC[p+1] - peaks_QC[p] # get number of samples between spikes
            interspike_tmp_ms = interspike_tmp * dt # convert to ms
            interspike_interval.append(interspike_tmp_ms) # append results

            # Calculate average and standard deviation of the holding/baseline/injected current between both spikes
            # average the period between 2 ms after first spike until 2 ms before second spike
            holding_avg_tmp = np.mean(sweep_IB_concatenated[peaks_QC[p]+50 : peaks_QC[p+1]-50])
            holding_std_tmp = np.std(sweep_IB_concatenated[peaks_QC[p]+50 : peaks_QC[p+1]-50])            
            holding_isi_avg.append(holding_avg_tmp) # append results
            holding_isi_std.append(holding_std_tmp) # append results
    
    # Visualise results
    # Generate figure layout
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig = plt.figure(tight_layout = True, figsize = (8, 8), dpi = 100)
    axs = fig.subplot_mosaic(
        """
        AA
        BC
        DE
        """
    )

    # Plot histogram of interspike intervals
    axs['A'].hist(interspike_interval, bins = 50, density = False, histtype = 'bar', log = False, color = 'k')
    axs['A'].set_title('A) ISI of detected spikes', fontsize = 12)
    axs['A'].set_xlabel('Interspike Interval [ms]', fontsize = 10)
    axs['A'].set_xlim([0, None])

    # Plot ISI vs Holding (mean)
    axs['B'].scatter(interspike_interval, holding_isi_avg, label = f'Slope = {np.round(stats.linregress(interspike_interval, holding_isi_avg)[0],5)}\npvalue = {np.round(stats.linregress(interspike_interval, holding_isi_avg)[3],2)}')
    # axs['B'].scatter(interspike_interval, holding_isi_avg, label = f'Correlation = {np.round(np.corrcoef(interspike_interval, holding_isi_avg)[0,1], 2)}')
    axs['B'].set_title('B) ISI vs Holding (avg)', fontsize = 12), axs['B'].legend()
    axs['B'].set_xlabel('Interspike Interval [ms]', fontsize = 10), axs['B'].set_ylabel('Holding current [pA]', fontsize = 10)

    # Plot ISI vs Holding (std)
    axs['C'].scatter(interspike_interval, holding_isi_std, label = f'Slope = {np.round(stats.linregress(interspike_interval, holding_isi_std)[0],5)}\npvalue = {np.round(stats.linregress(interspike_interval, holding_isi_std)[3],2)}')
    # axs['C'].scatter(interspike_interval, holding_isi_std, label = f'Correlation = {np.round(np.corrcoef(interspike_interval, holding_isi_std)[0,1], 2)}')
    axs['C'].set_title('C) ISI vs Holding (std)', fontsize = 12), axs['C'].legend()
    axs['C'].set_xlabel('Interspike Interval [ms]', fontsize = 10), axs['C'].set_ylabel('Holding current [std]', fontsize = 10)

    test_holding_avg = np.array([isi_hold_avg for i, isi_hold_avg in enumerate(holding_isi_avg) if (-50 < holding_isi_avg[i] < 50)])
    test_isi_avg = np.array([isi for i, isi in enumerate(interspike_interval) if (-50 < holding_isi_avg[i] < 50)])

    # Plot ISI vs Holding (avg)
    axs['D'].scatter(test_isi_avg, test_holding_avg, label = f'Slope = {np.round(stats.linregress(test_isi_avg, test_holding_avg)[0],5)}\npvalue = {np.round(stats.linregress(test_isi_avg, test_holding_avg)[3],2)}')
    # axs['D'].scatter(test_isi_avg, test_holding_avg, label = f'Correlation = {np.round(np.corrcoef(test_isi_avg, test_holding_avg)[0,1], 2)}')
    axs['D'].set_title('D) ISI vs Holding (±50pA injected)', fontsize = 12), axs['D'].legend()
    axs['D'].set_xlabel('Interspike Interval [ms]', fontsize = 10), axs['D'].set_ylabel('Holding current [pA]', fontsize = 10)

    test_holding_std = np.array([isi_hold_std for i, isi_hold_std in enumerate(holding_isi_std) if (holding_isi_std[i] < 20)])
    test_isi_std = np.array([isi for i, isi in enumerate(interspike_interval) if (holding_isi_std[i] < 20)])

    # Plot ISI vs Holding (std)
    axs['E'].scatter(test_isi_std, test_holding_std, label = f'Slope = {np.round(stats.linregress(test_isi_std, test_holding_std)[0],5)}\npvalue = {np.round(stats.linregress(test_isi_std, test_holding_std)[3],2)}')
    # axs['E'].scatter(test_isi_std, test_holding_std, label = f'Correlation = {np.round(np.corrcoef(test_isi_std, test_holding_std)[0,1], 2)}')
    axs['E'].set_title('E) ISI vs Holding (<20 std in holding_avg)', fontsize = 12), axs['E'].legend()
    axs['E'].set_xlabel('Interspike Interval [ms]', fontsize = 10), axs['E'].set_ylabel('Holding current [std]', fontsize = 10)
    
    fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
    plt.show()
    # plt.pause(5) # Use this if you are running the full script so it gives you a few seconds to see the plot before it moves to the next chunk of code.

    interspike_interval_dataframe = pd.DataFrame([interspike_interval, holding_isi_avg, holding_isi_std], index = ['interspike_interval_ms', 'holding_isi_pA_avg', 'holding_isi_std'], columns = range(len(interspike_interval)))

    return interspike_interval_dataframe # pandas dataframe

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