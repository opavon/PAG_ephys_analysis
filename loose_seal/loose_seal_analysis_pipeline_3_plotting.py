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

# %%
# Load data from excel file
vgat_ctrl_summary_data = pd.read_excel("D:\\Dropbox (UCL)\\Project_paginhibition\\analysis\\loose_seal\\loose_seal_metadata\\PAG_data_summary_loose_seal.xlsx", sheet_name = "vgat_control", header = 0, index_col = None
)

vgat_kynac_ptx_summary_data = pd.read_excel("D:\\Dropbox (UCL)\\Project_paginhibition\\analysis\\loose_seal\\loose_seal_metadata\\PAG_data_summary_loose_seal.xlsx", sheet_name = "vgat_kynac_ptx", header = 0, index_col = None
)

vglut2_ctrl_summary_data = pd.read_excel("D:\\Dropbox (UCL)\\Project_paginhibition\\analysis\\loose_seal\\loose_seal_metadata\\PAG_data_summary_loose_seal.xlsx", sheet_name = "vglut2_control", header = 0, index_col = None
)

vglut2_ptx_summary_data = pd.read_excel("D:\\Dropbox (UCL)\\Project_paginhibition\\analysis\\loose_seal\\loose_seal_metadata\\PAG_data_summary_loose_seal.xlsx", sheet_name = "vglut2_ptx", header = 0, index_col = None
)

# Inspect first 5 rows of data
vgat_ctrl_summary_data[:5]

# %%
# Check the names of the columns
vgat_ctrl_summary_data.columns

# %%
sns.violinplot(data = [vgat_ctrl_summary_data['firing.rate'],
                        vgat_kynac_ptx_summary_data['firing.rate'],
                        vglut2_ctrl_summary_data['firing.rate'],
                        vglut2_ptx_summary_data['firing.rate']]
)


# %%
plt.scatter(vgat_ctrl_summary_data['firing.rate'], vgat_ctrl_summary_data['Rseal.avg'])