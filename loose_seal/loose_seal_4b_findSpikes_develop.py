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
from utilities import importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps
print("done!")

# %%
# Load data for LIAM cell (contains spikes in test_pulse)
channels_data_frame, time, dt, folder_name, file_name = importFile(curated_channel = 'Sweeps_Analysis')
print("file imported")

# %%
# Concatenate sweeps
sweep_IB_concatenated_test, pseudo_sweep_concatenated_test = concatenateSweeps(file_name, channels_data_frame)

len(pseudo_sweep_concatenated_test) == len(sweep_IB_concatenated_test)

# %% [markdown]
# ## 1 | Make a function to find optimal prominence value

# %%
# Set default parameters
prominence_min = None
prominence_max = None
wlen_value = (10/dt) # this will help find local prominences.

# Find peaks and get their properties.
peaks_tmp, properties_tmp = find_peaks(-sweep_IB_concatenated_test, height = (None, None), threshold = (None, None), distance = None, prominence = (prominence_min, prominence_max), width = (None, None), wlen = wlen_value)

# Plot the distribution of prominences from the detected peaks.
get_ipython().run_line_magic('matplotlib', 'tk')
plt.figure(figsize = (8, 6), dpi = 100) # Set figure size
ax = plt.gca()
plt.hist(properties_tmp['prominences'], bins = 200, density = False, histtype = 'bar', log = True)
plt.title('Figure 1a: Prominence of detected peaks', fontsize = 14)
plt.text(0.95, 0.95, 'Parameters: wlen = (10/dt)', horizontalalignment='right', verticalalignment='top', transform = ax.transAxes)
plt.xlabel('peak prominence [pA]', fontsize = 12)
plt.pause(0.5) # Alternative to waitforbuttonpress() - does not close the figure and proceeds to input().
# if plt.waitforbuttonpress(): # if not using pause(), this is needed to render the figure
#     plt.close()

# Based on the histogram above, select the interval of prominences that will contain the peaks from spikes and not from baseline noise.
prominence_min = int(input("Enter the min value for the desired prominence"))
prominence_max = int(input("Enter the max value for the desired prominence"))
    
plt.close() # needed here if plt.pause() is used instead of plt.waitforbuttonpress()

# Use the selected prominence values to find spikes in the data.
peaks_test, properties_test = find_peaks(-sweep_IB_concatenated_test, height = (None, None), threshold = (None, None), distance = None, prominence = (prominence_min, prominence_max), width = (None, None), wlen = wlen_value)

# Plot the data with the detected peaks.
get_ipython().run_line_magic('matplotlib', 'tk')
plt.figure(figsize = (8, 6), dpi = 100) # Set figure size
plt.plot(peaks_test, sweep_IB_concatenated_test[peaks_test], "xr"); plt.plot(sweep_IB_concatenated_test); plt.legend(['peaks'])
plt.title('Figure 1b: Detected peaks for concatenated sweeps', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
plt.show()

# %%
cell_id = [file_name.split('.')[0]]
parameters_used = pd.DataFrame([[prominence_min, prominence_max, wlen_value, wlen_value*dt]], columns = ['prominence_min', 'prominence_max', 'wlen [samples]', 'wlen [ms]'], index = cell_id)
parameters_used

# %% [markdown]
# ## 2 | Make the function and test it

# %%
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
    get_ipython().run_line_magic('matplotlib', 'qt')
    plt.figure(figsize = (8, 6), dpi = 100) # Set figure size
    ax = plt.gca()
    plt.hist(properties_tmp['prominences'], bins = 200, density = False, histtype = 'bar', log = True)
    plt.title('Figure A: Prominence of detected peaks', fontsize = 14)
    plt.text(0.95, 0.95, f'Parameters: wlen = {wlen_ms}ms', horizontalalignment='right', verticalalignment='top', transform = ax.transAxes)
    plt.xlabel('peak prominence [pA]', fontsize = 12)
    plt.pause(0.5) # Alternative to waitforbuttonpress() - does not close the figure and proceeds to input().
    # if plt.waitforbuttonpress(): # if not using pause(), this is needed to render the figure
    #     plt.close()

    # Based on the histogram above, select the interval of prominences that will contain the peaks from spikes and not from baseline noise.
    prominence_min = int(input("Enter the min value for the desired prominence"))
    prominence_max = int(input("Enter the max value for the desired prominence"))
        
    plt.close() # needed here if plt.pause() is used instead of plt.waitforbuttonpress()

    # Use the selected prominence values to find spikes in the data.
    peaks, properties = find_peaks(-sweep_IB_concatenated, height = (None, None), threshold = (None, None), distance = None, prominence = (prominence_min, prominence_max), width = (None, None), wlen = wlen_ms/dt)

    # Get cell ID and parameters used
    cell_id = [file_name.split('.')[0]]
    parameters_used = pd.DataFrame([[prominence_min, prominence_max, wlen_ms/dt, wlen_ms]], columns = ['prominence_min', 'prominence_max', 'wlen [samples]', 'wlen [ms]'], index = cell_id)

    # Plot the data with the detected peaks.
    get_ipython().run_line_magic('matplotlib', 'qt')
    plt.figure(figsize = (8, 6), dpi = 100) # Set figure size
    plt.plot(peaks, sweep_IB_concatenated[peaks], "xr"); plt.plot(sweep_IB_concatenated); plt.legend(['peaks'])
    plt.title('Figure B: Detected peaks for concatenated sweeps', fontsize = 14)
    plt.xlabel('samples', fontsize = 12)
    plt.ylabel('current [pA]', fontsize = 12)
    #plt.pause(0.5)
    plt.show(block = True) # Lets you interact with plot and proceeds when figure is closed

    happy = input("Are you happy with your choice of prominence? y/n")

    if happy == 'y':
        print(f"found {len(peaks)} spikes")
    else:
        # Empty results just in case.
        peaks = []
        properties = []
        parameters_used = []
        print('Try running findSpikes() again')
    
    plt.close()
    
    return peaks, properties, parameters_used # ndarray, dict, pandas data frame

# %%
# Test function
peaks, properties, parameters_used = findSpikes(file_name, sweep_IB_concatenated_test)

# print(len(peaks))
# print(properties)
# parameters_used
# %%
# Available matplotlib backends: ['tk', 'gtk', 'gtk3', 'wx', 'qt4', 'qt5', 'qt', 'osx', 'nbagg', 'notebook', 'agg', 'svg', 'pdf', 'ps', 'inline', 'ipympl', 'widget']

get_ipython().run_line_magic('matplotlib', 'qt')
plt.figure(figsize = (8, 6), dpi = 100) # Set figure size
plt.plot(peaks, sweep_IB_concatenated_test[peaks], "xr"); plt.plot(sweep_IB_concatenated_test)
plt.title('Figure 1b: Detected peaks for concatenated sweeps', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
plt.show(block = True)

happy = input("Are you happy with your choice of prominence? y/n")

plt.close()

# %%
peaks
# %%
# The code finally works after switching the backend from 'tk' to 'qt'. I had to install PyQt5 to do that, but I can now proceed to the next cell after running the function findSpikes(), which proved impossible when using 'tk'. The rest seems to work the same way.