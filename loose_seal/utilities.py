import os
import h5py
import numpy as np
import tkinter
from tkinter.filedialog import askopenfilename, askopenfilenames
from collections import defaultdict

def importFile():
    "What is this function doing?"

    tkinter.Tk().withdraw() # Close the root window
    in_path = askopenfilename()
    folder_name = os.path.split(in_path)[0]
    file_name = os.path.split(in_path)[1]
    
    voltage_mV, current_pA, command, ttl, time, dt = openFile(in_path)

    return voltage_mV, current_pA, command, ttl, time, dt, folder_name


def openFile(in_path, curated_channel = None):
    "What is this function doing?"

    if '.tdms' in in_path:
        extracted_channels, time, dt = openTDMSfile(in_path)
    elif '.hdf5' in in_path:
        extracted_channels, time, dt = openHDF5file(in_path, curated_channel = curated_channel)
    
    voltage_mV = extracted_channels[0]
    current_pA = extracted_channels[1]
    command = extracted_channels[2]
    ttl = extracted_channels[3]
    
    return voltage_mV, current_pA, command, ttl, time, dt