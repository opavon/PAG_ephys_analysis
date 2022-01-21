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
# Paths to results
vgat_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_control"
vgat_kynac_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vgat_kynurenic_picrotoxin"
vglut2_ctrl_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_control"
vglut2_ptx_save_path = r"D:\Dropbox (UCL)\Project_paginhibition\analysis\loose_seal\loose_seal_results\vglut2_picrotoxin"

# # To retrieve the data from a .json file into a dataframe do:
#     # df_name = pd.read_json(os.path.join(save_path, file_name))

# vgat_ctrl_firing_frequency = pd.read_json(os.path.join(vgat_ctrl_save_path, "dlpag_vgat_171113_c5_LIAI_OP_clear_VC_1_df_firing_frequency.json"))

# # To retrieve the data from a .npz file into a variable do:
#     # results_data = np.load(os.path.join(save_path, file_id[0] + "_results.npz"))
#     # print([key for key in results_data])
#     # Then you can retrieve one specific variable
#     # average_spike = results_data['average_spike']
# results_data = np.load(os.path.join(vgat_ctrl_save_path, "dlpag_vgat_171113_c5_LIAI_OP_clear_VC_1_results.npz"))

# print([key for key in results_data])


# Load .json files containing combined results
vgat_ctrl_df = pd.read_json(os.path.join(vgat_ctrl_save_path, 'vgat_control_pooled_df_firing_frequency.json')) # read data frame from json file
vgat_kynac_ptx_df = pd.read_json(os.path.join(vgat_kynac_ptx_save_path, 'vgat_kynurenic_picrotoxin_pooled_df_firing_frequency.json')) # read data frame from json file
vglut2_ctrl_df = pd.read_json(os.path.join(vglut2_ctrl_save_path, 'vglut2_control_pooled_df_firing_frequency.json')) # read data frame from json file
vglut2_ptx_df = pd.read_json(os.path.join(vglut2_ptx_save_path, 'vglut2_picrotoxin_pooled_df_firing_frequency.json')) # read data frame from json file

print(len(vgat_ctrl_df))
print(len(vgat_kynac_ptx_df))
print(len(vglut2_ctrl_df))
print(len(vglut2_ptx_df))

# %%
# Load data from excel file
vgat_ctrl_summary_data = pd.read_excel("D:\\Dropbox (UCL)\\Project_paginhibition\\analysis\\loose_seal\\loose_seal_metadata\\PAG_data_summary_loose_seal.xlsx", sheet_name = "vgat_control", header = 0, index_col = 23
)

# Inspect first 5 rows of data
vgat_ctrl_summary_data

# %%
sns.violinplot(data = [vgat_ctrl_df['firing_frequency_Hz'],
    vgat_kynac_ptx_df['firing_frequency_Hz'],
    vglut2_ctrl_df['firing_frequency_Hz'],
    vglut2_ptx_df['firing_frequency_Hz']]
)




# %%
# Code from Philip Shamash to generate the kde plot
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from typing import Tuple

def fit_kde(data: np.ndarray, bin_width: float) -> object:
    ''' Take in a data distribution and return a KDE object (support and density)'''
    data = np.array(data).astype(np.float)
    kde = sm.nonparametric.KDEUnivariate(data)
    kde.fit(bw=bin_width)
    return kde

def prepare_data_for_plot_kde(kde, plot_shift: float, area_under_curve: float=None, vertical: bool=False, violin: bool=False) -> Tuple[np.ndarray, np.ndarray]:
    ''' Take in a kde object and options, and produce data to be plotted on the x- and y- axes'''
    if area_under_curve is None:
        density = kde.density
    if area_under_curve is not None:
        density = kde.density / np.sum(kde.density) / np.diff(kde.support)[0] * area_under_curve
    if vertical: 
        x_data        = plot_shift + density
        y_data        = kde.support
        x_data_violin = plot_shift - density
        y_data_violin = kde.support
    if not vertical:
        x_data        = kde.support
        y_data        = plot_shift + density
        x_data_violin = kde.support
        y_data_violin = plot_shift - density
    return x_data, y_data, x_data_violin, y_data_violin

def plot_kde(ax: plt.axis, kde: object, plot_shift: float, vertical: bool=False, area_under_curve: float=None, violin: bool=True,  **kwargs) -> None:
    ''' Take in a kde object and options, and produce a shaded plot'''
    x_data, y_data, x_data_violin, y_data_violin = prepare_data_for_plot_kde(kde, plot_shift, area_under_curve, vertical, violin)
    ax.plot(x_data, y_data, **kwargs)

    if vertical:                ax.fill_betweenx(y_data, x_data, plot_shift, **kwargs)
    if violin and vertical:     ax.fill_betweenx(y_data_violin, x_data_violin, plot_shift,  **kwargs)

    if not vertical:            ax.fill_between(x_data, y_data, plot_shift, **kwargs)
    if violin and not vertical: ax.fill_between(x_data_violin, y_data_violin, plot_shift,  **kwargs)

if __name__ == "__main__":
    data = np.random.random(50)
    kde = fit_kde(data, bin_width=.1)

    fig, ax = plt.subplots()
    plot_kde(ax, kde, plot_shift = 0, vertical=True, area_under_curve=1, violin=False, color = (0,1,1), alpha=.5) 
    plt.show()