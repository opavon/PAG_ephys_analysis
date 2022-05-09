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
# Set path to results
folder_results_loose_seal = r"D:\Dropbox (UCL - SWC)\Project_paginhibition\analysis\loose_seal\loose_seal_results"
folder_results_loose_seal_vgat_ctrl = r"D:\Dropbox (UCL - SWC)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
folder_results_loose_seal_vgat_kynac_ptx = r"D:\Dropbox (UCL - SWC)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_kynurenic_picrotoxin"
folder_results_loose_seal_vglut2_ctrl = r"D:\Dropbox (UCL - SWC)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_control"
folder_results_loose_seal_vglut2_ptx = r"D:\Dropbox (UCL - SWC)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_picrotoxin"

# Load data from excel file for each condition
vgat_ctrl_summary_data = pd.read_excel(os.path.join(folder_results_loose_seal, 'PAG_data_summary_loose_seal.xlsx'), sheet_name = "vgat_control", index_col = "cell.code")
vgat_kynac_ptx_summary_data = pd.read_excel(os.path.join(folder_results_loose_seal, 'PAG_data_summary_loose_seal.xlsx'), sheet_name = "vgat_kynac_ptx", index_col = "cell.code")
vglut2_ctrl_summary_data = pd.read_excel(os.path.join(folder_results_loose_seal, 'PAG_data_summary_loose_seal.xlsx'), sheet_name = "vglut2_control", index_col = "cell.code")
vglut2_ptx_summary_data = pd.read_excel(os.path.join(folder_results_loose_seal, 'PAG_data_summary_loose_seal.xlsx'), sheet_name = "vglut2_ptx", index_col = "cell.code")

# Load .json files with interspike interval results
vgat_ctrl_isi_data = pd.read_json(os.path.join(folder_results_loose_seal_vgat_ctrl, 'vgat_control_pooled_interspike_interval.json'))
vgat_kynac_ptx_isi_data = pd.read_json(os.path.join(folder_results_loose_seal_vgat_kynac_ptx, 'vgat_kynurenic_picrotoxin_pooled_interspike_interval.json'))
vglut2_ctrl_isi_data = pd.read_json(os.path.join(folder_results_loose_seal_vglut2_ctrl, 'vglut2_control_pooled_interspike_interval.json'))
vglut2_ptx_isi_data = pd.read_json(os.path.join(folder_results_loose_seal_vglut2_ptx, 'vglut2_picrotoxin_pooled_interspike_interval.json'))

print("data loaded!")

# %%
# Inspect first 5 rows of one of the dataframes
vgat_ctrl_summary_data[:5]

# %%
# Check the names of the columns
vgat_ctrl_summary_data.columns

# %%
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (6, 10))
sns.violinplot(data = [vgat_ctrl_summary_data["firing.rate.Hz"],
                    vgat_kynac_ptx_summary_data["firing.rate.Hz"],
                    vglut2_ctrl_summary_data["firing.rate.Hz"],
                    vglut2_ptx_summary_data["firing.rate.Hz"]],
                scale = "count",
                inner = "point"
)
plt.title("Firing Frequency across cell types and conditions")
plt.xlabel("X axis")
plt.ylabel("firing frequency [Hz]")
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner

# %%
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (6, 10))
sns.violinplot(x = vgat_ctrl_summary_data['cell.area'],
                y = vgat_ctrl_summary_data['firing.rate.Hz'],
                order = ["dmpag", "dlpag", "lpag", "vlpag"],
                hue = vgat_ctrl_summary_data["mouse.sex"], split = True,
                scale = "count",
                inner = "point"
)
plt.title("Firing Frequency across PAG subdivisions")
plt.xlabel("PAG subdivision")
plt.ylabel("firing frequency [Hz]")
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner

# %%
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (6, 10))
sns.boxplot(x = vgat_ctrl_summary_data['mouse.age'],
                y = vgat_ctrl_summary_data['firing.rate.Hz'],
                #order = ["dmpag", "dlpag", "lpag", "vlpag"],
                hue = vgat_ctrl_summary_data["mouse.sex"]
)
plt.title("Firing Frequency across PAG subdivisions")
plt.xlabel("PAG subdivision")
plt.ylabel("firing frequency [Hz]")
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner

# %%
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (6, 10))
#sns.scatterplot(vgat_ctrl_summary_data['Rseal.avg.Mohm'], vgat_ctrl_summary_data['firing.rate.Hz'])
#sns.regplot(x = vgat_ctrl_summary_data['Rseal.avg.Mohm'], y = vgat_ctrl_summary_data['firing.rate.Hz'])
sns.lmplot(x = 'spike.halfwidth.ms', y = 'firing.rate.Hz', hue = 'mouse.sex', data = vgat_ctrl_summary_data)
plt.title("Firing Frequency vs Seal resistance")
plt.xlabel("seal resistance [MOhm]")
plt.ylabel("firing frequency [Hz]")
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner

# %%
