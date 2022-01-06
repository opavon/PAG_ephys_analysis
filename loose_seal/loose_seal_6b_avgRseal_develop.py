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
from utilities import * # includes functions importFile, openFile, openHDF5file, getLooseRseal, concatenateSweeps, findSpikes, cutSpikes, plotSpikesQC, spikesQC, cleanSpikes, averageSpikes, getSpikeParameters, getFiringRate, getInterspikeInterval, saveLooseSealResults, combineJSONresults
print("done!")

# Paths to results
vgat_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
vgat_kynac_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_kynurenic_picrotoxin"
vglut2_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_control"
vglut2_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_picrotoxin"

# %%
# To retrieve the data from a .json file into a dataframe do:
    # df_name = pd.read_json(os.path.join(save_path, file_name))

vgat_ctrl_firing_frequency = pd.read_json(os.path.join(vgat_ctrl_save_path, "dlpag_vgat_171113_c5_LIAI_OP_clear_VC_1_df_firing_frequency.json"))

# To retrieve the data from a .npz file into a variable do:
    # results_data = np.load(os.path.join(save_path, file_id[0] + "_results.npz"))
    # print([key for key in results_data])
    # Then you can retrieve one specific variable
    # average_spike = results_data['average_spike']
results_data = np.load(os.path.join(vgat_ctrl_save_path, "dlpag_vgat_171113_c5_LIAI_OP_clear_VC_1_results.npz"))

print([key for key in results_data])

