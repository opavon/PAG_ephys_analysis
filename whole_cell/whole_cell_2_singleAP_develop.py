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
from whole_cell_utilities import * # includes functions importFile, openFile, openHDF5file, getInputResistance
print("done!")

# %%
# Load data
channels_df, time, dt, folder_name, file_name = importFile(curated_channel = 'Sweeps_Analysis')
print("file imported")

# %%
# Extract data and plot
sweep_IA = np.array(channels_df.loc['Channel A', :])
sweep_OA = np.array(channels_df.loc['Output A', :])

# Get color palette and generate one color for each sweep
import matplotlib.cm as cm
sweep_colors = cm.viridis(np.linspace(0, 1, len(sweep_IA)))

get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (10, 5), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)

for sweep in range(len(sweep_IA)):
    axs['A'].plot(sweep_IA[sweep], color = sweep_colors[sweep])
axs['A'].set_title('Channel A', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]')
axs['A'].set_xlim([0, (len(sweep_IA[0]))])

for sweep in range(len(sweep_OA)):
    axs['B'].plot(sweep_OA[sweep], color = sweep_colors[sweep])
axs['B'].set_title('Output A', fontsize = 12)
axs['B'].set_ylabel('current [pA]')
axs['B'].set_xlim([0, (len(sweep_IA[0]))])

fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
plt.show()

# %%
# Given that we have already curated all the recordings and left only the sweeps with one single spike in the "Sweeps_Analysis" curated channel, we can find the spikes by simply finding where the max value of each sweep is.
# In addition, we get the holding potential of the cell at each sweep and then baseline the curated sweeps

# Initialize variables to build results dataframe:
test_pulse_command_pA = []
injected_current_pA = []
holding_mV = []
peaks_indices = []
peaks_magnitude_mV = []
cut_spikes = []

for sweep in channels_df.columns:
    ## Load sweep data: Channel A (recording in current-clamp) and Output B (command)
    sweep_IA = np.array(channels_df.at['Channel A', sweep]) # voltage
    sweep_IB = np.array(channels_df.at['Channel B', sweep]) # current
    sweep_OA = np.array(channels_df.at['Output A', sweep])

    ## Get the indices corresponding to the test_pulse using the Output Channel
    test_pulse = np.where(sweep_OA > 0)
    test_pulse_OA_indices = test_pulse[0]

    ## Get test_pulse magnitude
    # Use the indices of the test_pulse command (Output A) to define baseline period and test period
    sweep_OA_baseline = np.mean(sweep_OA[:(test_pulse_OA_indices[0]-1)]) # -1 to stop baseline before command starts
    sweep_OA_pulse = np.mean(sweep_OA[test_pulse_OA_indices])
    tp_command = sweep_OA_pulse - sweep_OA_baseline # pA

    ## Get magnitude of current injected to the cell
    # Use the indices of the test_pulse command (Output A) to define baseline period and test period
    sweep_IB_baseline = np.mean(sweep_IB[:(test_pulse_OA_indices[0])])

    # Get the average baseline before the pulse starts to know the voltage at which the cell is sitting.
    # To be exact and account for the delays between digital command and output from the amplifier, you could add +1 to the first index to calculate the baseline.
    sweep_IA_baseline = np.mean(sweep_IA[:(test_pulse_OA_indices[0])])

    #print(max(sweep_IA))
    #print(np.where(sweep_IA == max(sweep_IA))[0])

    # Find the peaks and get their value and indices
    temp_spike_index = np.where(sweep_IA == max(sweep_IA))[0][0]
    temp_peak_magnitude = max(sweep_IA)

    # Cut the spike
    temp_cut_spike = np.array(sweep_IA[(temp_spike_index-2000) : (temp_spike_index+4000)])
    
    # Append results
    test_pulse_command_pA.append(tp_command)
    injected_current_pA.append(sweep_IB_baseline)
    holding_mV.append(sweep_IA_baseline)
    peaks_indices.append(temp_spike_index)
    peaks_magnitude_mV.append(temp_peak_magnitude)
    cut_spikes.append(temp_cut_spike)

print(test_pulse_command_pA)
print(injected_current_pA)
print(holding_mV)
print(peaks_indices)
print(peaks_magnitude_mV)
print(cut_spikes)

# %%
# Plot cut spikes after baselining
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
import matplotlib.cm as cm
baselined_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes)))
for s in range(len(cut_spikes)):
    plt.plot(cut_spikes[s], color = baselined_spikes_colors[s])
plt.title('Cut spikes', fontsize = 14)
plt.ylabel('voltage [mV]', fontsize = 12)
#plt.xlim([((len(cut_spikes[0])/2)-45), ((len(cut_spikes[0])/2)+55)])
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
plt.show()

#%%
# Get the average spike
temp_spike = np.array(np.mean(cut_spikes, 0))

# Get peak, trough, adp, ahp indices
temp_spike_peak_index = int(np.where(temp_spike == max(temp_spike))[0])
temp_spike_trough_index = int(np.where(temp_spike == min(temp_spike[temp_spike_peak_index:temp_spike_peak_index+50]))[0])
temp_spike_adp_index = int(np.where(temp_spike == max(temp_spike[temp_spike_trough_index:temp_spike_trough_index+200]))[0])
temp_spike_ahp_index = int(np.where(temp_spike == min(temp_spike[temp_spike_adp_index:temp_spike_adp_index+1250]))[0])

# Get peak, trough, adp, ahp metrics
peak_mV = temp_spike[temp_spike_peak_index]
trough_mV = temp_spike[temp_spike_trough_index]
adp_peak_mV = temp_spike[temp_spike_adp_index]
ahp_trough_mV = temp_spike[temp_spike_ahp_index]

peak_to_trough_magnitude = trough_mV - peak_mV
trough_to_adp_magnitude = adp_peak_mV - trough_mV
adp_to_ahp_magnitude = ahp_trough_mV - adp_peak_mV

peak_to_trough_ms = (temp_spike_trough_index - temp_spike_peak_index) * dt
trough_to_adp_ms = (temp_spike_adp_index - temp_spike_trough_index) * dt
adp_to_ahp_ms = (temp_spike_ahp_index - temp_spike_adp_index) * dt

# Get half_peak value
half_peak = peak_mV - (abs(peak_to_trough_magnitude) / 2)
# Now, we need to get the first time we cross the half_peak value (before the peak), and the second time (after the peak). To do this, we are going to split the spike in two halves, and do the procedure separately.
from scipy.interpolate import interp1d # load function to interpolate
temp_spike_first_half = temp_spike[:temp_spike_peak_index] # get first half of average spike
temp_f1 = interp1d(temp_spike_first_half,
                    range(0, len(temp_spike_first_half)), 
                    kind = "linear") # make function to interpolate
temp_half_width_start = temp_f1(half_peak) # find value corresponding to the half_peak

temp_spike_second_half = temp_spike[temp_spike_peak_index:] # get second half of average spike
temp_f2 = interp1d(temp_spike_second_half, 
                    range(temp_spike_peak_index, 
                    temp_spike_peak_index+len(temp_spike_second_half)), 
                    kind = "linear") # make function to interpolate
temp_half_width_end = temp_f2(half_peak) # find value corresponding to the half_peak

# Subtract beginning from end and multiply by the sampling rate to obtain the half_width in ms
half_width_ms = (temp_half_width_end - temp_half_width_start) * dt

# Get the derivative of time
diff_t = np.diff(time[0][:len(temp_spike)])
# And the derivative of voltage
diff_v = np.diff(temp_spike)
# Now get dvdt
dvdt = diff_v / diff_t
# Define threshold as 5% of the maximum value of dvdt
threshold_value = max(dvdt) * 0.05

from scipy.interpolate import interp1d # load function to interpolate
temp_2_f1 = interp1d(dvdt,
                    range(0, len(dvdt)), 
                    kind = "linear") # make function to interpolate
dvdt_threshold_index = temp_2_f1(threshold_value) # find index corresponding to threshold

temp_2_f2 = interp1d(range(0, len(temp_spike_first_half)), 
                    temp_spike_first_half,
                    kind = "linear") # make function to interpolate
spike_threshold_mV = temp_2_f2(dvdt_threshold_index+1) # find value corresponding to threshold, adding one to make up for the index lost due to the derivative

temp_2_f3 = interp1d(temp_spike_first_half,
                    range(0, len(temp_spike_first_half)), 
                    kind = "linear") # make function to interpolate
spike_threshold_index = temp_2_f3(spike_threshold_mV) # find index corresponding to threshold

threshold_to_peak_ms = (temp_spike_peak_index - spike_threshold_index) * dt

# %%
# Plot the average spike shape against its derivative
get_ipython().run_line_magic('matplotlib', 'qt')

fig = plt.figure(tight_layout = True, figsize = (6, 10), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)

axs['A'].plot(temp_spike, 'k')
axs['A'].plot(int(spike_threshold_index), temp_spike[int(spike_threshold_index)], "or")
axs['A'].plot(temp_spike_peak_index, temp_spike[temp_spike_peak_index], "or")
axs['A'].plot(temp_spike_trough_index, temp_spike[temp_spike_trough_index], "or")
axs['A'].plot(temp_spike_adp_index, temp_spike[temp_spike_adp_index], "or")
axs['A'].set_title('Average spike', fontsize = 14)
axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
axs['A'].set_xlim([temp_spike_index-100, temp_spike_index+200])

axs['B'].plot(temp_spike[1:], dvdt, 'k')
axs['B'].set_title('Phase plot', fontsize = 14)
axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
axs['B'].set_xlim([-100, 50])

fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
plt.show()

#%%
# Print the extracted parameters
print(f'The test pulse command is       {np.mean(test_pulse_command_pA)} pA')
print(f'The injected current is         {np.round(np.mean(injected_current_pA), 2)} pA')
print(f'The holding is                  {np.round(np.mean(holding_mV), 2)} mV')
print(f'The peak is                     {np.round(peak_mV, 2)} mV')
print(f'The trough is                   {np.round(trough_mV, 2)} mV')
print(f'The adp is                      {np.round(adp_peak_mV, 2)} mV')
print(f'The ahp is                      {np.round(ahp_trough_mV, 2)} mV')
print(f'The peak to trough is           {np.round(peak_to_trough_magnitude, 2)} mV')
print(f'The trough to adp is            {np.round(trough_to_adp_magnitude, 2)} mV')
print(f'The adp to ahp is               {np.round(adp_to_ahp_magnitude, 2)} mV')
print(f'The peak to trough is           {np.round(peak_to_trough_ms, 2)} ms')
print(f'The trough to adp is            {np.round(trough_to_adp_ms, 2)} ms')
print(f'The adp to ahp is               {np.round(adp_to_ahp_ms, 2)} ms')
print(f'The half width is               {np.round(half_width_ms, 2)} ms')
print(f'The spike threshold is          {np.round(spike_threshold_mV, 2)} mV')
print(f'The the threshold to peak is    {np.round(threshold_to_peak_ms, 2)} ms')

# %%
# Now let's put it into a function
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
            print(temp_file_id)
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
                temp_cut_spike = np.array(sweep_IA[(temp_spike_index-2000) : (temp_spike_index+4000)])
                
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

            # Get peak, trough, adp, ahp indices
            temp_avg_spike_peak_index = np.where(temp_avg_spike == max(temp_avg_spike))[0][0] # overall positive peak
            temp_avg_spike_trough_index = np.where(temp_avg_spike == min(temp_avg_spike[temp_avg_spike_peak_index:temp_avg_spike_peak_index+50]))[0][0] # negative peak within 2 ms after the action potential peak
            temp_avg_spike_adp_index = np.where(temp_avg_spike == max(temp_avg_spike[temp_avg_spike_trough_index:temp_avg_spike_trough_index+200]))[0][0] # positive peak within 8 ms after the trough (afterdepolarization)
            temp_avg_spike_ahp_index = np.where(temp_avg_spike == min(temp_avg_spike[temp_avg_spike_adp_index:temp_avg_spike_adp_index+1250]))[0][0] # negative peak within 50 ms after the afterdepolarization (afterhyperpolarization)
            print(temp_avg_spike_trough_index)
            print(temp_avg_spike_adp_index)
            print(temp_avg_spike_ahp_index)

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
            half_peak = peak_mV - (abs(peak_to_trough_magnitude) / 2) # mV
            # Now, we need to get the first time we cross the half_peak value (before the peak), and the second time (after the peak). To do this, we are going to split the spike in two halves, and do an interpolation separately.
            from scipy.interpolate import interp1d # load function to interpolate
            temp_avg_spike_first_half = temp_avg_spike[:temp_avg_spike_peak_index] # get first half of average spike
            temp_1_f1 = interp1d(temp_avg_spike_first_half,
                                range(0, len(temp_avg_spike_first_half)), 
                                kind = "linear") # make function to interpolate
            temp_half_width_start = temp_1_f1(half_peak) # find value corresponding to the half_peak

            temp_avg_spike_second_half = temp_avg_spike[temp_avg_spike_peak_index:] # get second half of average spike
            temp_1_f2 = interp1d(temp_avg_spike_second_half, 
                                range(temp_avg_spike_peak_index, 
                                temp_avg_spike_peak_index+len(temp_avg_spike_second_half)), 
                                kind = "linear") # make function to interpolate
            temp_half_width_end = temp_1_f2(half_peak) # find value corresponding to the half_peak

            # Subtract beginning from end and multiply by the sampling rate to obtain the half_width in ms
            half_width_ms = (temp_half_width_end - temp_half_width_start) * dt # ms

            # Now we want to get the threshold of the action potential. To do that, we will find the voltage at which the dV/dt value crosses the 5% of the maximum dV/dt value
            # Get the derivative of time for the length of the cut and averaged spike
            diff_t = np.diff(time[0][:len(temp_avg_spike)]) # must be same lenth as `temp_avg_spike`
            # Get the derivative of voltage
            diff_v = np.diff(temp_avg_spike)
            # Now get dV/dt
            dvdt = diff_v / diff_t
            # Define action potential threshold as 5% of the maximum value of dV/dt
            dvdt_threshold_value = max(dvdt) * 0.05
            print(dvdt_threshold_value)

            from scipy.interpolate import interp1d # load function to interpolate
            temp_2_f1 = interp1d(dvdt[:len(temp_avg_spike_first_half)],
                                range(0, len(temp_avg_spike_first_half)), 
                                kind = "linear") # make function to interpolate
            dvdt_threshold_index = temp_2_f1(dvdt_threshold_value) # find index corresponding to threshold
            print(dvdt_threshold_index)
            print(np.where(dvdt > 20)[0][0])
            # Once we have the index at which the dV/dt crosses our threshold, we need to find the value corresponding to the averaged spike. To do that, we will interplate the first half of the spike, but reversing the order of the variables. This will allow us to obtain the voltage at the index we just obtained. We will need to add 1 to the index to make up for the derivative.
            temp_2_f2 = interp1d(range(0, len(temp_avg_spike_first_half)), 
                                temp_avg_spike_first_half,
                                kind = "linear") # make function to interpolate
            spike_threshold_mV = temp_2_f2(dvdt_threshold_index + 1) # find value corresponding to threshold, adding one to make up for the index lost due to the derivative
            # Now we have the calculated threshold for our average action potential. We can obtain the index in the average spike so we can compute further parameters.
            temp_2_f3 = interp1d(temp_avg_spike_first_half,
                                range(0, len(temp_avg_spike_first_half)), 
                                kind = "linear") # make function to interpolate
            spike_threshold_index = temp_2_f3(spike_threshold_mV) # find index corresponding to threshold

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
            axs['A'].plot(int(spike_threshold_index), temp_avg_spike[int(spike_threshold_index)], "or")
            axs['A'].plot(temp_avg_spike_peak_index, temp_avg_spike[temp_avg_spike_peak_index], "or")
            axs['A'].plot(temp_avg_spike_trough_index, temp_avg_spike[temp_avg_spike_trough_index], "or")
            axs['A'].plot(temp_avg_spike_adp_index, temp_avg_spike[temp_avg_spike_adp_index], "oc")
            axs['A'].plot(temp_avg_spike_ahp_index, temp_avg_spike[temp_avg_spike_ahp_index], "oy")
            axs['A'].set_title('Average spike', fontsize = 14)
            axs['A'].set_ylabel('voltage [mV]', fontsize = 12)
            axs['A'].set_xlim([temp_avg_spike_peak_index-100, temp_avg_spike_peak_index+2000])
            axs['B'].plot(temp_avg_spike[1:], dvdt, 'k')
            axs['B'].set_title('Phase plot', fontsize = 14)
            axs['B'].set_xlabel('voltage [mV]', fontsize = 12)
            axs['B'].set_ylabel('dV/dt [mV/ms]', fontsize = 12)
            axs['B'].set_xlim([-100, 100])
            axs['B'].set_xlim([-100, 100])
            fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
            plt.show(block = True) # Lets you interact with plot and proceeds once figure is closed

            # Check whether spike analysis is complete
            happy_results = input("Are you happy with the results for this recording? y/n")

            if happy_results == 'y':
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
                    test_pulse_command_pA, injected_current_pA, holding_mV, peaks_magnitude_mV,
                    cut_spikes, temp_avg_spike,
                    temp_avg_spike_peak_index, temp_avg_spike_trough_index, temp_avg_spike_adp_index, temp_avg_spike_ahp_index,
                    peak_mV, trough_mV, adp_peak_mV, ahp_trough_mV,
                    peak_to_trough_magnitude, trough_to_adp_magnitude, adp_to_ahp_magnitude, 
                    peak_to_trough_ms, trough_to_adp_ms, adp_to_ahp_ms,
                    half_peak, temp_half_width_start, temp_half_width_end, half_width_ms,
                    dvdt, dvdt_threshold_value, spike_threshold_mV, spike_threshold_index, threshold_to_peak_ms
                    ]], 
                    columns = ['command_pA', 'injected_pA', 'holding_mV', 'peaks_magnitude_mV',
                                'command_bysweep_pA', 'injected_bysweep_pA', 'holding_bysweep_mV', 'peak_bysweep_mV', 
                                'cut_spikes_traces_mV', 'avg_spike_trace_mV',
                                'avg_spike_peak_index', 'avg_spike_trough_index', 'avg_spike_adp_index', 'avg_spike_ahp_index',
                                'avg_spike_peak_mV', 'avg_spike_trough_mV', 'avg_spike_adp_mV', 'avg_spike_ahp_mV', 
                                'peak_to_trough_mV', 'trough_to_adp_mV', 'adp_to_ahp_mV',
                                'peak_to_trough_ms', 'trough_to_adp_ms', 'adp_to_ahp_ms',
                                'half_peak_mV', 'half_width_start', 'half_width_end', 'half_width_ms',
                                'dvdt_trace', 'dvdt_threshold_mV_ms', 'avg_spike_threshold_mV', 'avg_spike_threshold_index', 'threshold_to_peak_ms'
                                ], 
                    index = temp_file_id)
            else:
                print(f'Fix the recording from cell {temp_file_id} and try running getSpikeParameters() again')
                plt.close()
                return None # return empty variables to prevent wrong results from being used
            
            plt.close()
            cell_temp_list.append(avg_AP_parameters_dataframe)

        folder_results_df = pd.concat(cell_temp_list) # concatenate all the data frames in the list
        folder_results_df.to_json(os.path.join(folder_to_save, folder_id + '_pooled' + save_type + '.json')) # save combined results as new .json file
        
    print('results saved')
    
    return folder_results_df # last pandas dataframe

#%%n

# Choose folders
vgat_dopamine_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_data\IC_single_AP\vgat_dopamine"
folders_to_check = [vgat_dopamine_save_path]
folder_to_save = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\whole_cell\whole_cell_results\IC_single_AP"

# Choose type of results and suffix for saved file
results_type_single_AP = "_IC_single_AP"
save_type_single_AP = "_single_AP_parameters"
curated_channel = "Sweeps_Analysis"

folder_results_df = getSpikeParameters(folders_to_check, folder_to_save, results_type_single_AP, save_type_single_AP, curated_channel)
folder_results_df
# %%
