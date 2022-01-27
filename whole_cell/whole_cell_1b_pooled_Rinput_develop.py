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
from whole_cell_utilities import * # includes functions importFile, openFile, openHDF5file
print("done!")

# %%
# ## 1.0 | Set paths to subfolders where extracted results files are stored
vgat_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vgat_control"
vgat_kynac_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vgat_kynurenic_picrotoxin"
vglut2_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vglut2_control"
vglut2_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_tau_inputresistance\vglut2_picrotoxin"
print("done!")

# %%
# Let's try to repurpose the function and adapt it so it extracts the input resistance from all the curated files in a chosen folder

def getInputResistance(
    folders_to_check,
    folder_to_save,
    results_type = "_IC_tau_inputresistance",
    save_type = "_input_resistance"
    ):
    """
    `getInputResistance` takes the dataframe containing the extracted channel data from a current-clamp recording using the IC_tau_inputresistance protocol and calculates the input resistance (InputR) from the test pulse size and the cell's response to it.
    It returns a dataframe with the InputR value (MOhm) across sweeps for the time of recording (where the columns are sweeps) together with the magnitude of the test_pulse command (pA), the response of the cell (mV), and the holding potential (mV). It also plots the calculated InputR across sweeps and returns a second dataframe with the average values and cell ID.
    
    :folders_to_check: a list containing the paths to the folders to check.
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

# %%
# Test the function
# ## 1.1 | Get average seal resistance for each cell and combine the results in one data frame for each cell in a specific condition

# Choose folders
folders_to_check = [vgat_ctrl_save_path]
folder_to_save = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_results\IC_tau_inputresistance"

# Choose type of results and suffix for saved file
results_type_Rinput = '_IC_tau_inputresistance'
save_type_Rinput = '_input_resistance'

folder_results_df = getInputResistance(folders_to_check, folder_to_save, results_type_Rinput, save_type_Rinput)
folder_results_df

# %%
# Check you can actually plot the averaged trace saved in the last column
plt.plot(folder_results_df.loc['dmpag_vgat_201217_c4_WDIBN_OP_IC_tau_inputresistance_3_2']['membrane_avg_mV'])
plt.show
# It works!
