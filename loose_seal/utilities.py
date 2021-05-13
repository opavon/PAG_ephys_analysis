import os
import h5py
import numpy as np
import tkinter
from tkinter.filedialog import askopenfilename, askopenfilenames
from collections import defaultdict
from nptdms import TdmsFile

def importFile():
    "__importFile__ will open a window where you can navigate and select a file to import. It will then store its path and call the __openFile__ function to exctract its contents."
    
    root = tkinter.Tk()
    root.attributes("-topmost", True) # make window appear on top
    in_path = askopenfilename() # open dialogue to select file
    root.destroy() # close the root window

    folder_name = os.path.split(in_path)[0] # get path until folder
    file_name = os.path.split(in_path)[1] # get filename
    
    voltage_mV, current_pA, command, ttl, time, dt = openFile(in_path)
    
    return voltage_mV, current_pA, command, ttl, time, dt, folder_name


def openFile(in_path, curated_channel = None):
    "__openFile__ will check whether you are attempting to open a tdms or a hdf5 file and will attempt to extract the data from each of the useful channels."

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
    "__openTDMSfile__ returns a list of arrays, where each is a sweep/trial i.e. [np.array(trial)]."
    
    tdms_file = TdmsFile(in_path)
    
    dataDict = defaultdict(list)
    
    for group in tdms_file.groups():
        i=0
        for sweep in group.channels():
            dataDict[group.name].append(sweep.data)
            i+=1
                       
    extracted_channels = []
    
    for channel in channel_list: # keep only useful channels
        extracted_channels.append(dataDict[channel])
    
    time = dataDict['Time'][0]
    dt = np.mean(np.diff(time))
    
    return extracted_channels, time, dt