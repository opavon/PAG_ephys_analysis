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
        # To ensure we evaluate the epoch where the cell response has reached steady state, we average the values corresponding to the second half of the pulse.
        sweep_IA_pulse = np.mean(sweep_IA[(round(len(test_pulse_OA_indices)/2)):(test_pulse_OA_indices[-1])])
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
    save_type = "_input_resistance"
    ):
    """
    `getInputResistance` loops through all the files in a selected folder, loads each file, extracts the relevant channels from a current-clamp recording using the IC_tau_inputresistance protocol, and calculates the input resistance (InputR) from the test pulse size and the cell's response to it.
    It saves a dataframe with the average command (mV), the average membrane response (mV), the average holding potential (mV), the average input resistance (MOhm), as well as four vectors containing the corresponding values across sweeps. The dataframe also contains an averaged trace for both the command (pA) and the membrane response (mV). Each row in the dataframe corresponds to a recording from a cell, and a single cell can have more than one repetition of the same protocol.
    The function will return the final dataframe. If more than one folder is being analysed, it will only output the dataframe corresponding to the last folder in the `folders_to_check` variable.
    
    :folders_to_check: a list containing the paths to the folders to check. Results will be saved in the folders with the same name in the save path.
    :folder_to_save: path to folder where results will be saved.
    :results_type: a string containing the type of result (without its .json extension) to load and combine.
    :save_type: a string containing the type of result you are saving. For example, if `results_type = "_IC_tau_inputresistance"`, setting `save_type = "_input_resistance"` will avoid errors if we re-run the function.
    """

    for folder in folders_to_check:
        folder_id = folder.split('\\')[-1] # grab the name of the subfolder

        cell_temp_list = [] # an empty list to store the data frames
        folder_results_files = [results_file for results_file in os.listdir(folder) if results_type in results_file]  # get the files that contain the type of results you want

        for file in folder_results_files:
            # Get the recording ID
            temp_file_id = [file.split('.')[0]] # Get the file name without the extension

            channels_dataframe, time, dt = openFile(os.path.join(folder, file)) # extract channels from current file

            # Initialize variables to build results dataframe:
            test_pulse_command = []
            test_pulse_membrane = []
            test_pulse_command_baselined = []
            test_pulse_membrane_baselined = []
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
                # To ensure we evaluate the epoch where the cell response has reached steady state, we average the values corresponding to the second half of the pulse.
                sweep_IA_pulse = np.mean(sweep_IA[(round(len(test_pulse_OA_indices)/2)):(test_pulse_OA_indices[-1])])
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

                ## Baseline sweeps
                baselined_sweep_OA = sweep_OA - sweep_OA_baseline
                baselined_sweep_IA = sweep_IA - sweep_IA_baseline
                # Append results
                test_pulse_command_baselined.append(baselined_sweep_OA)
                test_pulse_membrane_baselined.append(baselined_sweep_IA)

            # Compute average trace from all baselined sweeps
            average_test_pulse_command_baselined = np.array(np.mean(test_pulse_command_baselined, 0))
            average_test_pulse_membrane_baselined = np.array(np.mean(test_pulse_membrane_baselined, 0))
            
            # Create dataframe of results across sweeps:
            InputR_dataframe = pd.DataFrame([test_pulse_command, test_pulse_membrane, holding_mV, input_resistance], index = ['test_pulse_command_pA', 'test_pulse_membrane_mV', 'holding_mV', 'input_resistance_MOhm'], columns = trial_keys)
            
            # Create dataframe of average InputR and cell ID
            InputR_avg_dataframe = pd.DataFrame([[
                np.round(np.mean(InputR_dataframe.loc['test_pulse_command_pA']), 2),
                np.round(np.mean(InputR_dataframe.loc['test_pulse_membrane_mV']), 2), 
                np.round(np.mean(InputR_dataframe.loc['holding_mV']), 2), 
                np.round(np.mean(InputR_dataframe.loc['input_resistance_MOhm']), 2),
                test_pulse_command, test_pulse_membrane, holding_mV, input_resistance,
                average_test_pulse_command_baselined, average_test_pulse_membrane_baselined
                ]], 
                columns =  ['command_pA', 'membrane_mV', 'holding_mV', 'input_resistance_MOhm', 'command_sweeps_pA', 'membrane_sweeps_mV', 'holding_sweeps_mV', 'input_resistance_sweeps_MOhm', 'command_avg_pA', 'membrane_avg_mV'], 
                index = temp_file_id)

            cell_temp_list.append(InputR_avg_dataframe)

        folder_results_df = pd.concat(cell_temp_list) # concatenate all the data frames in the list
        folder_results_df.to_json(os.path.join(folder_to_save, folder_id, folder_id + '_pooled' + save_type + '.json')) # save combined results as new .json file
        
    print('results saved')
    
    return folder_results_df # last pandas dataframe