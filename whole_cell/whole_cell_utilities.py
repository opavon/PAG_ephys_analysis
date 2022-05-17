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
    `importFile` opens a dialog window to select a file to import. It then uses the path to the selected file to call `openFile` to extract the data.

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
    `openFile` checks whether you are attempting to open a `.tdms` or a `.hdf5` file. It then calls the right function to extract the data from the selected channels.

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

def getCellInputResistance(
    file_name,
    channels_dataframe
    ):
    """
    `getCellInputResistance` takes the dataframe containing the extracted channel data from a current-clamp recording using the IC_tau_inputresistance protocol and calculates the input resistance (InputR) from the test pulse size and the cell's response to it.

    It returns a dataframe with the InputR value (MOhm) across sweeps for the time of recording (where the columns are sweeps) together with the magnitude of the test_pulse command (pA), the response of the cell (mV), and the holding potential (mV). It also plots the calculated InputR across sweeps and returns a second dataframe with the average values and cell ID.
    
    :file_name: contains useful metadata (PAG subdivision, cell type, date, cell ID, protocol name).
    :channels_dataframe: dataframe with extracted data from a whole-cell current-clamp recording (e.g. several repetitions of a sweep with a hyperpolarising pulse to record the cell's response).
    """

    file_id = [file_name.split('.')[0]] # Get the file name without the extension
    cell_id = ['_'.join((file_id[0].split('_'))[0:5])] # Get cell id

    # Initialize variables to build results dataframe:
    test_pulse_command = []
    test_pulse_membrane = []
    input_resistance = []
    holding_mV = []
    trial_keys = []

    # Calculate the input resistance on a sweep-by-sweep basis:
    for sweep in channels_dataframe.columns:
        ## Load sweep data: Channel A (recording in current-clamp) and Output B (command)
        sweep_IA = np.array(channels_dataframe.at['Channel A', sweep])
        # sweep_IB = np.array(channels_dataframe.at['Channel B', sweep]) # Not needed as we recorded in current-clamp
        sweep_OA = np.array(channels_dataframe.at['Output A', sweep])

        ## Get the indices corresponding to the test_pulse using the Output Channel
        test_pulse = np.where(sweep_OA < 0)
        test_pulse_OA_indices = test_pulse[0]

        ## Get test_pulse magnitude
        # Use the indices of the test_pulse command (Output A) to define baseline period and test period
        sweep_OA_baseline = np.mean(sweep_OA[:(test_pulse_OA_indices[0]-1)]) # -1 to stop baseline before command starts
        sweep_OA_pulse = np.mean(sweep_OA[test_pulse_OA_indices])
        tp_command = sweep_OA_pulse - sweep_OA_baseline # pA

        ## Get cell response to test_pulse:
        # Use the test_pulse indices to get the baseline and cell response to calculate the input resistance
        # To be exact and account for the delays between digital command and output from the amplifier, you could add +1 to the first index to calculate the baseline.
        sweep_IA_baseline = np.mean(sweep_IA[:(test_pulse_OA_indices[0])])
        # To ensure we evaluate the epoch where the cell response has reached steady state, we average the values corresponding to the final third of the pulse.
        sweep_IA_pulse = np.mean(sweep_IA[(round(len(test_pulse_OA_indices)*2/3)):(test_pulse_OA_indices[-1])])
        tp_membrane = sweep_IA_pulse - sweep_IA_baseline # mV

        ## Get input resistance = mV/pA
        InputR = (tp_membrane / tp_command) * 1000 # to get MOhm
        # Append results
        test_pulse_command.append(tp_command)
        test_pulse_membrane.append(tp_membrane)
        holding_mV.append(sweep_IA_baseline)
        input_resistance.append(InputR)

        ## Get trial name for results dataframe
        trial_keys.append(sweep)

    # Create dataframe of results across sweeps:
    InputR_dataframe = pd.DataFrame([test_pulse_command, test_pulse_membrane, holding_mV, input_resistance], index = ['test_pulse_command_pA', 'test_pulse_membrane_mV', 'holding_mV', 'input_resistance_MOhm'], columns = trial_keys)
    
    # Create dataframe of average InputR and cell ID
    InputR_avg_dataframe = pd.DataFrame([[np.round(np.mean(InputR_dataframe.loc['test_pulse_command_pA']), 2), np.round(np.mean(InputR_dataframe.loc['test_pulse_membrane_mV']), 2), np.round(np.mean(InputR_dataframe.loc['holding_mV']), 2), np.round(np.mean(InputR_dataframe.loc['input_resistance_MOhm']), 2)]], columns =  ['test_pulse_command_pA', 'test_pulse_membrane_mV', 'holding_mV', 'input_resistance_MOhm'], index = cell_id)


    # Plot recording together with results.
    # Extract full data for plotting purposes (in current-clamp, Channel A is recorded voltage, and Output A is the protocol output)
    all_sweeps_IA = np.array(channels_dataframe.loc['Channel A', :])
    all_sweeps_OA = np.array(channels_dataframe.loc['Output A', :])

    # Get color palette and generate one color for each sweep
    import matplotlib.cm as cm
    sweep_colors = cm.viridis(np.linspace(0, 1, len(all_sweeps_IA)))

    # Generate figure layout
    get_ipython().run_line_magic('matplotlib', 'qt')
    fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100) # Set figure size
    axs = fig.subplot_mosaic(
        """
        AA
        BB
        CC
        """
    )

    # Plot protocol and cell's voltage response
    for sweep in range(len(all_sweeps_IA)):
            axs['A'].plot(all_sweeps_IA[sweep], color = sweep_colors[sweep])
    axs['A'].set_title('Channel A', fontsize = 12)
    axs['A'].set_ylabel('voltage [mV]', fontsize = 10)
    axs['A'].set_xlim([0, (len(all_sweeps_IA[0]))])
    for sweep in range(len(all_sweeps_OA)):
            axs['B'].plot(all_sweeps_OA[sweep], color = sweep_colors[sweep])
    axs['B'].set_title('Output A', fontsize = 12)
    axs['B'].set_ylabel('current [pA]', fontsize = 10)
    axs['B'].set_xlim([0, (len(all_sweeps_IA[0]))])
    
    # Plot InputR across sweeps
    axs['C'].plot(InputR_dataframe.loc['input_resistance_MOhm'], 'k')
    axs['C'].set_title('Input Resistance across sweeps', fontsize = 12)
    axs['C'].set_xlabel('sweep number', fontsize = 10)
    axs['C'].set_ylabel('Input Resistance [MOhm]', fontsize = 10)
    axs['C'].set_xlim([-1, len(InputR_dataframe.loc['input_resistance_MOhm'])])
    axs['C'].set_ylim([0, round(np.max(InputR_dataframe.loc['input_resistance_MOhm'])*2)])

    # Add title
    plt.suptitle(f'Input resistance from {cell_id[0]}', fontsize = 14)

    # Move figure to top left corner
    fig.canvas.manager.window.move(0, 0)
    plt.show(block = True) # Lets you interact with plot and proceeds once figure is closed
    # plt.pause(0.5)
    
    # Check whether you are happy with the recording or whether there is any pre-processing or clean-up left to do
    happy_inputR = input("Are you happy with the result? y/n")
    
    if happy_inputR == 'y':
        print(f"The average input resistance of cell {cell_id[0]} is {np.round(np.mean(InputR_dataframe.loc['input_resistance_MOhm']), 2)} MOhm")
        plt.close()
    else:
        print('Try running getInputResistance() again')
        plt.close()
        return None, None # return empty variables to prevent wrong results from being used

    return InputR_dataframe, InputR_avg_dataframe # pandas dataframe

def getInputResistance(
    folders_to_check,
    folder_to_save,
    results_type = "_IC_tau_inputresistance",
    save_type = "_input_resistance",
    curated_channel = None,
    ):
    """
    `getInputResistance` loops through all the files in a selected folder, loads each file, extracts the relevant channels from a current-clamp recording using the IC_tau_inputresistance protocol, and calculates the input resistance (InputR) from the test pulse size and the cell's response to it.

    It saves a dataframe with the average command (mV), the average membrane response (mV), the average holding potential (mV), the average input resistance (MOhm), as well as four vectors containing the corresponding values across sweeps. The dataframe also contains an averaged trace for both the command (pA) and the membrane response (mV). Each row in the dataframe corresponds to a recording from a cell, and a single cell can have more than one repetition of the same protocol.

    The function will return the final dataframe. If more than one folder is being analysed, it will only output the dataframe corresponding to the last folder in the `folders_to_check` variable.
    
    :folders_to_check: a list containing the paths to the folders to check.
    :folder_to_save: path to folder where results will be saved.
    :results_type: a string containing the type of result (without its .json extension) to load and combine.
    :save_type: a string containing the type of result you are saving. For example, if `results_type = "_IC_tau_inputresistance"`, setting `save_type = "_input_resistance"` will avoid errors if we re-run the function.
    :curated_channel: a string pointing to the curated channel (e.g. copy of a 'Channel' where some sweeps/trials have been deleted due to noise or quality). Defaults to None.
    """

    for folder in folders_to_check:
        folder_id = folder.split('\\')[-1] # grab the name of the subfolder

        cell_temp_list = [] # an empty list to store the data frames
        folder_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]  # get the files that contain the type of results you want

        for file in folder_results_files:
            # Get the recording ID
            temp_file_id = [file.split('.')[0]] # Get the file name without the extension

            channels_dataframe, time, dt = openFile(os.path.join(folder, file), curated_channel = curated_channel) # extract channels from current file

            # Initialise variables to build results dataframe:
            test_pulse_command = []
            test_pulse_membrane = []
            test_pulse_command_baselined = []
            test_pulse_membrane_baselined = []
            input_resistance = []
            injected_pA = []
            holding_mV = []
            trial_keys = []

            # Calculate the input resistance on a sweep-by-sweep basis:
            for sweep in channels_dataframe.columns:
                ## Load sweep data: Channel A (voltage recording in current-clamp), Channel B (injected current) and Output B (command)
                sweep_IA = np.array(channels_dataframe.at['Channel A', sweep]) # voltage
                sweep_IB = np.array(channels_dataframe.at['Channel B', sweep]) # current
                sweep_OA = np.array(channels_dataframe.at['Output A', sweep]) # command

                ## Get the indices corresponding to the test_pulse using the Output Channel
                test_pulse = np.where(sweep_OA < 0)
                test_pulse_OA_indices = test_pulse[0]

                ## Get test_pulse magnitude
                # Use the indices of the test_pulse command (Output A) to define baseline period and test period
                sweep_OA_baseline = np.mean(sweep_OA[:(test_pulse_OA_indices[0]-1)]) # -1 to stop baseline before command starts
                sweep_OA_pulse = np.mean(sweep_OA[test_pulse_OA_indices])
                tp_command = sweep_OA_pulse - sweep_OA_baseline # pA

                ## Get average current injected to the cell to keep at the current voltage
                # Use the indices of the test_pulse command (Output A) to define baseline period and test period
                sweep_IB_baseline = np.mean(sweep_IB[:(test_pulse_OA_indices[0])])

                ## Get cell response to test_pulse:
                # Use the test_pulse indices to get the baseline and cell response to calculate the input resistance
                # To be exact and account for the delays between digital command and output from the amplifier, you could add +1 to the first index to calculate the baseline.
                sweep_IA_baseline = np.mean(sweep_IA[:(test_pulse_OA_indices[0])])
                # To ensure we evaluate the epoch where the cell response has reached steady state, we average the values corresponding to the final third of the pulse.
                sweep_IA_pulse = np.mean(sweep_IA[(round(len(test_pulse_OA_indices)*2/3)):(test_pulse_OA_indices[-1])])
                tp_membrane = sweep_IA_pulse - sweep_IA_baseline # mV

                ## Get input resistance = mV/pA
                InputR = (tp_membrane / tp_command) * 1000 # to get MOhm
                # Append results
                test_pulse_command.append(tp_command)
                test_pulse_membrane.append(tp_membrane)
                injected_pA.append(sweep_IB_baseline)
                holding_mV.append(sweep_IA_baseline)
                input_resistance.append(InputR)

                ## Get trial name for results dataframe
                trial_keys.append(sweep)

                ## Baseline sweeps
                baselined_sweep_OA = sweep_OA - sweep_OA_baseline
                baselined_sweep_IA = sweep_IA - sweep_IA_baseline
                # Append results
                test_pulse_command_baselined.append(baselined_sweep_OA)
                test_pulse_membrane_baselined.append(baselined_sweep_IA)

            # Compute average trace from all baselined sweeps
            avg_test_pulse_command_baselined = np.array(np.mean(test_pulse_command_baselined, 0))
            avg_test_pulse_membrane_baselined = np.array(np.mean(test_pulse_membrane_baselined, 0))

            # Compute input resistance from average trace. Sanity check to compare both methods yield the same results
            avg_trace_test_pulse = np.where(avg_test_pulse_command_baselined < 0)
            avg_trace_test_pulse_OA_indices = avg_trace_test_pulse[0]
            avg_trace_command_baseline = np.mean(avg_test_pulse_command_baselined[:(avg_trace_test_pulse_OA_indices[0]-1)])
            avg_trace_command_pulse = np.mean(avg_test_pulse_command_baselined[avg_trace_test_pulse_OA_indices])
            avg_trace_command = avg_trace_command_pulse - avg_trace_command_baseline # pA
            avg_trace_membrane_baseline = np.mean(avg_test_pulse_membrane_baselined[:(avg_trace_test_pulse_OA_indices[0])])
            avg_trace_membrane_pulse = np.mean(avg_test_pulse_membrane_baselined[(round(len(avg_trace_test_pulse_OA_indices)*2/3)):(avg_trace_test_pulse_OA_indices[-1])])
            avg_trace_membrane = avg_trace_membrane_pulse - avg_trace_membrane_baseline # mV
            avg_trace_input_resistance = (avg_trace_membrane / avg_trace_command) * 1000 # to get MOhm
            
            # Create dataframe of results across sweeps:
            InputR_dataframe = pd.DataFrame([test_pulse_command, test_pulse_membrane, injected_pA, holding_mV, input_resistance], index = ['test_pulse_command_pA', 'test_pulse_membrane_mV', 'injected_pA', 'holding_mV', 'input_resistance_MOhm'], columns = trial_keys)
            
            # Create dataframe of average InputR and cell ID
            InputR_avg_dataframe = pd.DataFrame([[
                np.round(np.mean(InputR_dataframe.loc['test_pulse_command_pA']), 2),
                np.round(np.mean(InputR_dataframe.loc['test_pulse_membrane_mV']), 2),
                np.round(np.mean(InputR_dataframe.loc['injected_pA']), 2), 
                np.round(np.mean(InputR_dataframe.loc['holding_mV']), 2), 
                np.round(np.mean(InputR_dataframe.loc['input_resistance_MOhm']), 2),
                test_pulse_command, test_pulse_membrane, injected_pA, holding_mV, input_resistance,
                avg_test_pulse_command_baselined, avg_test_pulse_membrane_baselined,
                np.round(avg_trace_command, 2),
                np.round(avg_trace_membrane, 2),
                np.round(avg_trace_input_resistance, 2)
                ]], 
                columns = ['command_pA', 'membrane_mV', 'injected_pA', 'holding_mV', 'IR_MOhm',
                            'command_bysweep_pA', 'membrane_bysweep_mV', 
                            'injected_bysweep_pA', 'holding_bysweep_mV', 'IR_bysweep_MOhm', 
                            'command_avg_trace_pA', 'membrane_avg_trace_mV',
                            'command_avg_pA', 'membrane_avg_mV', 'IR_avg_MOhm'], 
                index = temp_file_id)

            cell_temp_list.append(InputR_avg_dataframe)

        folder_results_df = pd.concat(cell_temp_list) # concatenate all the data frames in the list
        folder_results_df.to_json(os.path.join(folder_to_save, folder_id + '_pooled' + save_type + '.json')) # save combined results as new .json file
        folder_results_df.to_csv(os.path.join(folder_to_save, folder_id + '_pooled' + save_type + '.csv'), index = True, header = True) # save combined results as a .csv file
        print(f'{folder_id} results saved')
        
    print('all results saved')
    
    return folder_results_df # last pandas dataframe

def getSpikeParameters(
    folders_to_check,
    folder_to_save,
    results_type = "_IC_single_AP",
    save_type = "_single_AP_parameters",
    curated_channel = "Sweeps_Analysis",
    ):
    """
    `getSpikeParameters` loops through all the files in a selected folder, loads each file, extracts the relevant channels from a current-clamp recording using the IC_single_AP protocol, and calculates various parameters that can be used to characterise the averge spike shape.

    It saves a dataframe with several parameters calculated from the average action potential, including the threshold, peak, afterdepolarisation, afterhyperpolarisation, and half-width. It also stores the vectors containing the corresponding values across sweeps, the cut spikes, and a trace for the average spike. Each row in the dataframe corresponds to a recording from a cell, and a single cell can have more than one repetition of the same protocol.

    The function will return the final dataframe. If more than one folder is being analysed, it will only output the dataframe corresponding to the last folder in the `folders_to_check` variable.
    
    :folders_to_check: a list containing the paths to the folders to check.
    :folder_to_save: path to folder where results will be saved.
    :results_type: a string containing the type of result (without its .json extension) to load and combine.
    :save_type: a string containing the type of result you are saving. For example, if `results_type = "_IC_single_AP"`, setting `save_type = "_single_AP_parameters"` will avoid errors if we re-run the function.
    :curated_channel: a string pointing to the curated channel (e.g. copy of a 'Channel' where some sweeps/trials have been deleted due to noise or quality, leaving only the ones were a single action potential was elicited). Defaults to 'Sweeps_Analysis', but should be changed to the name of the curated channel or the function will not work as intended.
    """

    for folder in folders_to_check:
        folder_id = folder.split('\\')[-1] # grab the name of the subfolder

        cell_temp_list = [] # an empty list to store the data frames
        folder_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]  # get the files that contain the type of results you want

        for file in folder_results_files:
            # Get the recording ID
            temp_file_id = [file.split('.')[0]] # Get the file name without the extension
            channels_df, time, dt = openFile(os.path.join(folder, file), curated_channel = curated_channel) # extract channels from current file

            # Given that we have already curated all the recordings and left only the sweeps with one single spike in the "Sweeps_Analysis" curated channel, we can find the spikes by simply finding where the max value of each sweep is.
            # In addition, we get the holding potential of the cell at each sweep and then baseline the curated sweeps

            # Initialize variables to build results dataframe:
            test_pulse_command_pA = []
            injected_current_pA = []
            holding_mV = []
            peaks_indices = []
            peaks_magnitude_mV = []
            cut_spikes = []
            trial_keys = []

            for sweep in channels_df.columns:
                ## Load sweep data: Channel A (voltage recording in current-clamp), Channel B (injected current) and Output B (command)
                sweep_IA = np.array(channels_df.at['Channel A', sweep]) # voltage
                sweep_IB = np.array(channels_df.at['Channel B', sweep]) # current
                sweep_OA = np.array(channels_df.at['Output A', sweep]) # command

                ## Get the indices corresponding to the test_pulse using the Output Channel
                test_pulse = np.where(sweep_OA > 0)
                test_pulse_OA_indices = test_pulse[0]

                ## Get test_pulse magnitude
                # Use the indices of the test_pulse command (Output A) to define baseline period and test period
                sweep_OA_baseline = np.mean(sweep_OA[:(test_pulse_OA_indices[0]-1)]) # -1 to stop baseline before command starts
                sweep_OA_pulse = np.mean(sweep_OA[test_pulse_OA_indices])
                tp_command = sweep_OA_pulse - sweep_OA_baseline # pA

                ## Get average current injected to the cell to keep at the current voltage
                # Use the indices of the test_pulse command (Output A) to define baseline period and test period
                sweep_IB_baseline = np.mean(sweep_IB[:(test_pulse_OA_indices[0])])

                # Get the average baseline before the pulse starts to know the voltage at which the cell is sitting.
                # To be exact and account for the delays between digital command and output from the amplifier, you could add +1 to the first index to calculate the baseline.
                sweep_IA_baseline = np.mean(sweep_IA[:(test_pulse_OA_indices[0])])

                # Find the peaks and get their value and indices. This assumes only the sweeps containing exactly one action potential have been left in the curated channel.
                temp_spike_index = np.where(sweep_IA == max(sweep_IA))[0][0]
                temp_peak_magnitude = max(sweep_IA) # mV
                # Cut the spike around the peak
                temp_cut_spike = np.array(sweep_IA[(temp_spike_index-2250) : (temp_spike_index+2750)])
                
                # Append results
                test_pulse_command_pA.append(tp_command)
                injected_current_pA.append(sweep_IB_baseline)
                holding_mV.append(sweep_IA_baseline)
                peaks_indices.append(temp_spike_index)
                peaks_magnitude_mV.append(temp_peak_magnitude)
                cut_spikes.append(temp_cut_spike)

                # Get trial name for results dataframe
                trial_keys.append(sweep)

            ## Once we have extracted the parameters for each sweep, we move on to average the cut spikes and keep working on the average.            
            # Get the average spike
            temp_avg_spike = np.array(np.mean(cut_spikes, 0))

            # Get peak index (positive peak in the trace)
            temp_avg_spike_peak_index = np.where(temp_avg_spike == max(temp_avg_spike))[0][0]
            # Get trough index (negative peak within 3 ms after the action potential peak)
            temp_avg_spike_trough_index = temp_avg_spike_peak_index + (np.where(temp_avg_spike[temp_avg_spike_peak_index:(temp_avg_spike_peak_index+75)] == min(temp_avg_spike[temp_avg_spike_peak_index:(temp_avg_spike_peak_index+75)]))[0][0]) 
            # Get afterdepolarisation index (positive peak within 8 ms after the trough)
            temp_avg_spike_adp_index = (temp_avg_spike_trough_index+5) + (np.where(temp_avg_spike[(temp_avg_spike_trough_index+5):(temp_avg_spike_trough_index+200)] == max(temp_avg_spike[(temp_avg_spike_trough_index+5):(temp_avg_spike_trough_index+200)]))[0][0])
            # Get afterhyperpolarisation index (negative peak within 40 ms after the trough)
            temp_avg_spike_ahp_index = (temp_avg_spike_trough_index+205) + (np.where(temp_avg_spike[(temp_avg_spike_trough_index+205):(temp_avg_spike_trough_index+1000)] == min(temp_avg_spike[(temp_avg_spike_trough_index+205):(temp_avg_spike_trough_index+1000)]))[0][0])

            # Get peak, trough, adp, ahp metrics
            peak_mV = temp_avg_spike[temp_avg_spike_peak_index] # mV
            trough_mV = temp_avg_spike[temp_avg_spike_trough_index] # mV
            adp_peak_mV = temp_avg_spike[temp_avg_spike_adp_index] # mV
            ahp_trough_mV = temp_avg_spike[temp_avg_spike_ahp_index] # mV

            peak_to_trough_magnitude = trough_mV - peak_mV # mV
            trough_to_adp_magnitude = adp_peak_mV - trough_mV # mV
            adp_to_ahp_magnitude = ahp_trough_mV - adp_peak_mV # mV

            peak_to_trough_ms = (temp_avg_spike_trough_index - temp_avg_spike_peak_index) * dt # ms
            trough_to_adp_ms = (temp_avg_spike_adp_index - temp_avg_spike_trough_index) * dt # ms
            adp_to_ahp_ms = (temp_avg_spike_ahp_index - temp_avg_spike_adp_index) * dt # ms

            # Get half_peak value, calculated by subtracting half the absolute magnitude (peak to trough) from the peak value
            half_peak_mV = peak_mV - (abs(peak_to_trough_magnitude) / 2) # mV
            # Now, we need to get the first time we cross the half_peak value (before the peak), and the second time (after the peak). To do this, we are going to split the spike in two halves, and do an interpolation separately.
            from scipy.interpolate import interp1d # load function to interpolate
            temp_avg_spike_first_half = temp_avg_spike[(temp_avg_spike_peak_index-100):temp_avg_spike_peak_index] # get first half of average spike
            temp_1_f1 = interp1d(temp_avg_spike_first_half,
                                range(0, len(temp_avg_spike_first_half)), 
                                kind = "linear") # make function to interpolate
            temp_half_width_start = temp_1_f1(half_peak_mV) + (temp_avg_spike_peak_index-100) # find value corresponding to the half_peak

            temp_avg_spike_second_half = temp_avg_spike[temp_avg_spike_peak_index:(temp_avg_spike_peak_index+100)] # get second half of average spike
            temp_1_f2 = interp1d(temp_avg_spike_second_half, 
                                range(temp_avg_spike_peak_index, 
                                temp_avg_spike_peak_index+len(temp_avg_spike_second_half)), 
                                kind = "linear") # make function to interpolate
            temp_half_width_end = temp_1_f2(half_peak_mV) # find value corresponding to the half_peak

            # Subtract beginning from end and multiply by the sampling rate to obtain the half_width in ms
            half_width_ms = (temp_half_width_end - temp_half_width_start) * dt # ms

            # Now we want to get the threshold of the action potential. To do that, we will find the voltage at which the dV/dt value crosses the 5% of the maximum dV/dt value
            # Get the derivative of time for the length of the cut and averaged spike
            diff_t = np.diff(time[0][:len(temp_avg_spike)]) # must be same lenth as `temp_avg_spike`
            # Get the derivative of voltage
            diff_v = np.diff(temp_avg_spike)
            # Now get dV/dt
            dvdt = diff_v / diff_t
            # Define action potential threshold as 20 mV/ms
            dvdt_threshold_value = 20 # we use 20 mV/ms instead of max(dvdt) * 0.05 as the latter depends too much on the quality of the spike
            # Find the index in the dV/dt trace where this threshold is crossed
            dvdt_threshold_index = np.where(dvdt[(temp_avg_spike_peak_index-100):temp_avg_spike_peak_index] > dvdt_threshold_value)[0][0]
            # Find the voltage value in the average trace corresponding to the threshold index
            spike_threshold_index = dvdt_threshold_index + (temp_avg_spike_peak_index-100) + 1 # add one to make up for the index lost due to the derivative
            spike_threshold_mV = temp_avg_spike[spike_threshold_index]
            # Get threshold to peak
            threshold_to_peak_ms = (temp_avg_spike_peak_index - spike_threshold_index) * dt # ms

            # For each cell, plot the average spike shape against its derivative
            get_ipython().run_line_magic('matplotlib', 'qt')
            fig = plt.figure(tight_layout = True, figsize = (6, 10), dpi = 100) # Set figure size
            axs = fig.subplot_mosaic(
                """
                AA
                BB
                """
            )
            axs['A'].plot(temp_avg_spike, 'k') # plot average spike trace
            axs['A'].plot(spike_threshold_index, temp_avg_spike[spike_threshold_index], "or")
            axs['A'].plot(temp_avg_spike_peak_index, temp_avg_spike[temp_avg_spike_peak_index], "or")
            axs['A'].plot(temp_avg_spike_trough_index, temp_avg_spike[temp_avg_spike_trough_index], "or")
            axs['A'].plot(temp_avg_spike_adp_index, temp_avg_spike[temp_avg_spike_adp_index], "oc")
            axs['A'].plot(temp_avg_spike_ahp_index, temp_avg_spike[temp_avg_spike_ahp_index], "oy")
            axs['A'].set_title(f'Average spike \n {temp_file_id[0]}', fontsize = 14)
            axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
            axs['A'].set_xlim([temp_avg_spike_peak_index-100, temp_avg_spike_peak_index+2000])
            axs['A'].set_ylim([-90, 60])
            axs['B'].plot(temp_avg_spike[1:], dvdt, 'k')
            axs['B'].set_title('Phase plot', fontsize = 14)
            axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
            axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
            axs['B'].set_xlim([-100, 100])
            axs['B'].set_ylim([-700, 700])
            fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
            plt.show(block = True) # Lets you interact with plot and proceeds once figure is closed
            plt.close()

            # Create dataframe of results across sweeps:
            single_AP_parameters_df = pd.DataFrame([
                test_pulse_command_pA, injected_current_pA, holding_mV, peaks_magnitude_mV], 
                index = ['test_pulse_command_pA', 'injected_current_pA', 'holding_mV', 'peaks_magnitude_mV'],
                columns = trial_keys)

            # Once we have computed all the parameters, we store the results in a dataframe
            avg_AP_parameters_dataframe = pd.DataFrame([[
                np.round(np.mean(single_AP_parameters_df.loc['test_pulse_command_pA']), 2),
                np.round(np.mean(single_AP_parameters_df.loc['injected_current_pA']), 2),
                np.round(np.mean(single_AP_parameters_df.loc['holding_mV']), 2), 
                np.round(np.mean(single_AP_parameters_df.loc['peaks_magnitude_mV']), 2),
                peak_mV, trough_mV, adp_peak_mV, ahp_trough_mV,
                spike_threshold_mV, threshold_to_peak_ms, dvdt_threshold_value, 
                half_peak_mV, half_width_ms,
                peak_to_trough_magnitude, peak_to_trough_ms, 
                trough_to_adp_magnitude, trough_to_adp_ms, 
                adp_to_ahp_magnitude, adp_to_ahp_ms,
                spike_threshold_index, temp_avg_spike_peak_index, temp_avg_spike_trough_index, temp_avg_spike_adp_index, temp_avg_spike_ahp_index, 
                np.float64(temp_half_width_start), np.float64(temp_half_width_end),
                test_pulse_command_pA, injected_current_pA, holding_mV, peaks_magnitude_mV,
                cut_spikes, temp_avg_spike, dvdt
                ]],
                columns = ['command_pA', 'injected_pA', 'holding_mV', 'peaks_magnitude_mV',
                            'avg_spike_peak_mV', 'avg_spike_trough_mV', 'avg_spike_adp_mV', 'avg_spike_ahp_mV',
                            'avg_spike_threshold_mV', 'threshold_to_peak_ms', 'dvdt_threshold_mV_ms', 
                            'half_peak_mV', 'half_width_ms',
                            'peak_to_trough_mV', 'peak_to_trough_ms', 
                            'trough_to_adp_mV', 'trough_to_adp_ms',
                            'adp_to_ahp_mV', 'adp_to_ahp_ms', 
                            'avg_spike_threshold_index', 'avg_spike_peak_index', 'avg_spike_trough_index', 'avg_spike_adp_index', 'avg_spike_ahp_index',
                            'half_width_start', 'half_width_end',  
                            'command_bysweep_pA', 'injected_bysweep_pA', 'holding_bysweep_mV', 'peak_bysweep_mV', 
                            'cut_spikes_traces_mV', 'avg_spike_trace_mV', 'dvdt_trace'
                            ],
                index = temp_file_id)

            cell_temp_list.append(avg_AP_parameters_dataframe)

        folder_results_df = pd.concat(cell_temp_list) # concatenate all the data frames in the list
        folder_results_df.to_json(os.path.join(folder_to_save, folder_id + '_pooled' + save_type + '.json')) # save combined results as new .json file
        folder_results_df.to_csv(os.path.join(folder_to_save, folder_id + '_pooled' + save_type + '.csv'), index = True, header = True) # save combined results as a .csv file
        print(f'{folder_id} results saved')
        
    print('all results saved')
    
    return folder_results_df # last pandas dataframe

def getSampleTracesIR(
    path_to_sample_cells,
    file_name,
    curated_channel = "Sweeps_Analysis",
    ):
    """
    `getSampleTracesIR` loads the recording from a selected example cell, extracts the data, baselines and averages the sweeps, and ouputs a the baselined sweeps together with the average so they can be used for plotting.
    
    :path_to_sample_cells: path to where the recordings from the sample cells are saved.
    :file_name: name of the .hdf5 file to open.
    :curated_channel: a string pointing to the curated channel (e.g. copy of a 'Channel' where some sweeps/trials have been deleted due to noise or quality, leaving only the ones were a single action potential was elicited). Defaults to 'Sweeps_Analysis', but should be changed to the name of the curated channel or the function will not work as intended.
    """

    channels_dataframe, time, dt = openFile(os.path.join(path_to_sample_cells, file_name), curated_channel = curated_channel) # extract channels from current file

    # Initialize variables to export:
    test_pulse_command_baselined = []
    test_pulse_membrane_baselined = []

    # Extract and baseline the recorded sweeps:
    for sweep in channels_dataframe.columns:
        ## Load sweep data: Channel A (voltage recording in current-clamp), and Output B (command)
        sweep_IA = np.array(channels_dataframe.at['Channel A', sweep]) # voltage
        sweep_OA = np.array(channels_dataframe.at['Output A', sweep]) # command

        ## Get the indices corresponding to the test_pulse using the Output Channel
        test_pulse = np.where(sweep_OA < 0)
        test_pulse_OA_indices = test_pulse[0]

        ## Compute the baseline for both the command and the recording channel
        sweep_OA_baseline = np.mean(sweep_OA[:(test_pulse_OA_indices[0]-1)]) # -1 to stop baseline before command starts
        sweep_IA_baseline = np.mean(sweep_IA[:(test_pulse_OA_indices[0])])

        ## Baseline sweeps
        baselined_sweep_OA = sweep_OA - sweep_OA_baseline
        baselined_sweep_IA = sweep_IA - sweep_IA_baseline

        ## Append results
        test_pulse_command_baselined.append(baselined_sweep_OA)
        test_pulse_membrane_baselined.append(baselined_sweep_IA)

    # Compute average trace from all baselined sweeps
    avg_test_pulse_command_baselined = np.array(np.mean(test_pulse_command_baselined, 0))
    avg_test_pulse_membrane_baselined = np.array(np.mean(test_pulse_membrane_baselined, 0))

    return test_pulse_membrane_baselined, test_pulse_command_baselined, avg_test_pulse_membrane_baselined, avg_test_pulse_command_baselined, time, dt

