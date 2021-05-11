import h5py
import numpy as np
import tkinter
from tkinter.filedialog import askopenfilename, askopenfilenames
import os

def importFile():
    tkinter.Tk().withdraw() # Close the root window
    in_path = askopenfilename()
    folder = os.path.split(in_path)[0]
    
    Vm, Ip, IVhold, TTL, time, dt = openFile(in_path)

    return Vm, Ip, IVhold, TTL, time, dt, folder

importFile