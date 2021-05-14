import os
import h5py
import numpy as np
import tkinter
from tkinter.filedialog import askopenfilename, askopenfilenames
from collections import defaultdict
from nptdms import TdmsFile

def importFile():
    """
    `importFile` opens a window to select a file to import.
    Returns path and calls `openFile` to extract data."
    """

    root = tkinter.Tk()
    root.attributes("-topmost", True) # Make window appear on top
    in_path = askopenfilename() # Open dialogue to select file
    root.destroy() # Close the root window

    folder_name = os.path.split(in_path)[0] # Get path until folder
    file_name = os.path.split(in_path)[1] # Get filename
    
    voltage_mV, current_pA, command, ttl, time, dt = openFile(in_path) # Call openFile() function
    
    return voltage_mV, current_pA, command, ttl, time, dt, folder_name, file_name


def openFile(in_path, curated_channel = None):
    """
    `openFile` checks whether you are attempting to open a `.tdms` or a `.hdf5` file.
    Extracts the data from selected channels.
    """

    if '.tdms' in in_path:
        extracted_channels, time, dt = openTDMSfile(in_path)
    elif '.hdf5' in in_path:
        extracted_channels, time, dt = openHDF5file(in_path, curated_channel = curated_channel)
    
    voltage_mV = extracted_channels[0]
    current_pA = extracted_channels[1]
    command = extracted_channels[2]
    ttl = extracted_channels[3]
    
    return voltage_mV, current_pA, command, ttl, time, dt

def openTDMSfile(in_path, channel_list = ['Channel A', 'Channel B', 'Output A', 'Output B']):
    """
    `openTDMSfile` returns a list of arrays, where each is a sweep/trial.
    """
    
    # Load .tdms file
    tdms_file = TdmsFile(in_path) 
    dataDict = defaultdict(list)
    
    # Iterate through channels and extract data from sweeps/trials
    for group in tdms_file.groups():
        i=0
        for sweep in group.channels():
            dataDict[group.name].append(sweep.data)
            i+=1
                       
    # Keep only useful channels
    extracted_channels = []

    for channel in channel_list: 
        extracted_channels.append(dataDict[channel])
    
    # Get time and delta_t
    time = dataDict['Time'][0]
    dt = np.mean(np.diff(time))
    
    return extracted_channels, time, dt