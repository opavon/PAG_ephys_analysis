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
print("paths to results set!")

# %% [markdown]
# ## 1 | Plot summary data
# Below follow some attempts to plot and summarise the data in different ways. Skip to section 2 for sample traces.

# %%
# Load data from excel file for each condition
vgat_ctrl_summary_data = pd.read_excel(os.path.join(folder_results_loose_seal, 'PAG_data_summary_loose_seal.xlsx'), sheet_name = "vgat_control", index_col = "cell.code")
vgat_kynac_ptx_summary_data = pd.read_excel(os.path.join(folder_results_loose_seal, 'PAG_data_summary_loose_seal.xlsx'), sheet_name = "vgat_kynac_ptx", index_col = "cell.code")
vglut2_ctrl_summary_data = pd.read_excel(os.path.join(folder_results_loose_seal, 'PAG_data_summary_loose_seal.xlsx'), sheet_name = "vglut2_control", index_col = "cell.code")
vglut2_ptx_summary_data = pd.read_excel(os.path.join(folder_results_loose_seal, 'PAG_data_summary_loose_seal.xlsx'), sheet_name = "vglut2_ptx", index_col = "cell.code")

# # Load .json files with interspike interval results
# vgat_ctrl_isi_data = pd.read_json(os.path.join(folder_results_loose_seal_vgat_ctrl, 'vgat_control_pooled_interspike_interval.json'))
# vgat_kynac_ptx_isi_data = pd.read_json(os.path.join(folder_results_loose_seal_vgat_kynac_ptx, 'vgat_kynurenic_picrotoxin_pooled_interspike_interval.json'))
# vglut2_ctrl_isi_data = pd.read_json(os.path.join(folder_results_loose_seal_vglut2_ctrl, 'vglut2_control_pooled_interspike_interval.json'))
# vglut2_ptx_isi_data = pd.read_json(os.path.join(folder_results_loose_seal_vglut2_ptx, 'vglut2_picrotoxin_pooled_interspike_interval.json'))

# Load .json files with average spike traces
vgat_ctrl_avg_spike_trace = pd.read_json(os.path.join(folder_results_loose_seal_vgat_ctrl, 'vgat_control_pooled_avg_spike.json'))
vgat_kynac_ptx_avg_spike_trace = pd.read_json(os.path.join(folder_results_loose_seal_vgat_kynac_ptx, 'vgat_kynurenic_picrotoxin_pooled_avg_spike.json'))
vglut2_ctrl_avg_spike_trace = pd.read_json(os.path.join(folder_results_loose_seal_vglut2_ctrl, 'vglut2_control_pooled_avg_spike.json'))
vglut2_ptx_avg_spike_trace = pd.read_json(os.path.join(folder_results_loose_seal_vglut2_ptx, 'vglut2_picrotoxin_pooled_avg_spike.json'))

print("data loaded!")

# %%
# Once we have loaded the data, we can generate some plots to visualise the distribution of the metric of our choice.

# Inspect first 5 rows of one of the dataframes
vgat_ctrl_summary_data[:5]

# %%
# Check the names of the columns
vgat_ctrl_summary_data.columns

# %%
# Generate a violin plot to summarise the firing rate across conditions
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
# Generate a violin plot to summarise the firing rate of vgat_ctrl across PAG subdivisions, split by sex
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
# Generate a boxplot to summarise the firing rate of vgat_ctrl across mouse age, split by sex
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (6, 10))
sns.boxplot(x = vgat_ctrl_summary_data['mouse.age'],
                y = vgat_ctrl_summary_data['firing.rate.Hz'],
                #order = ["dmpag", "dlpag", "lpag", "vlpag"],
                hue = vgat_ctrl_summary_data["mouse.sex"]
)
plt.title("Firing Frequency by mouse age and sex")
plt.xlabel("mouse age [weeks]")
plt.ylabel("firing frequency [Hz]")
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner

# %%
# Try to generate a linear regression plot
get_ipython().run_line_magic('matplotlib', 'qt')
#sns.scatterplot(vgat_ctrl_summary_data['Rseal.avg.Mohm'], vgat_ctrl_summary_data['firing.rate.Hz'])
#sns.regplot(x = vgat_ctrl_summary_data['Rseal.avg.Mohm'], y = vgat_ctrl_summary_data['firing.rate.Hz'])
sns.lmplot(x = 'spike.halfwidth.ms', y = 'firing.rate.Hz', hue = 'mouse.sex', data = vgat_ctrl_summary_data)
plt.title("Firing Frequency vs Seal resistance")
plt.xlabel("seal resistance [MOhm]")
plt.ylabel("firing frequency [Hz]")
fig.canvas.manager.window.move(0, 0) # Move figure to top left corner

# %% [markdown]
# ## 2 | Plot average spike traces of sample cells for each condition

# ### 2.1 | Explore potential sample traces for each condition

# %%
# Set path to save folder
folder_sample_traces_loose_seal = r"D:\Dropbox (UCL - SWC)\Project_paginhibition\analysis\loose_seal\loose_seal_plots\sample_traces_average_spike"
print("save path established!")

# %%
## Potential vgat_ctrl sample traces
# dmpag_vgat_190201_c4_LICQ_OP_VC_clear_nointerval_1_results.npz (too big)
# lpag_vgat_171117_c6_LIAW_OP_clear_VC_2_results.npz (no)
# dlpag_vgat_190201_c1_LICN_OP_VC_clear_nointerval_2_results.npz (no)
# dlpag_vgat_180208_c1_LICB_OP_clear_VC_2_results.npz (too small)
# dlpag_vgat_200720_c2_LIDG_OP_VC_clear_nointerval_1_results.npz (too small)
# dmpag_vgat_201202_c3_LIEO_OP_VC_clear_nointerval_1_results.npz (no)
# lpag_vgat_171218_c4_LIBW_OP_clear_VC_2_results.npz (noisy)
# vlpag_vgat_171130_c1_LIBH_OP_clear_VC_2_results.npz (-128.11 pA)

get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100)
axs = fig.subplot_mosaic(
    """
    AB
    CD
    EF
    GH
    """
)
axs['A'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_ctrl, 'dmpag_vgat_190201_c4_LICQ_OP_VC_clear_nointerval_1_results.npz'))["average_spike"])
axs['A'].set_xlim(120, 190)
axs['A'].set_ylim(-225, 125)
axs['A'].set_title('dmpag_vgat_190201_c4_LICQ', fontsize = 12)
axs['A'].set_ylabel('current [pA]')
axs['B'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_ctrl, 'lpag_vgat_171117_c6_LIAW_OP_clear_VC_2_results.npz'))["average_spike"])
axs['B'].set_xlim(120, 190)
axs['B'].set_ylim(-225, 125)
axs['B'].set_title('lpag_vgat_171117_c6_LIAW', fontsize = 12)
axs['B'].set_ylabel('current [pB]')
axs['C'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_ctrl, 'dlpag_vgat_190201_c1_LICN_OP_VC_clear_nointerval_2_results.npz'))["average_spike"])
axs['C'].set_xlim(120, 190)
axs['C'].set_ylim(-225, 125)
axs['C'].set_title('dlpag_vgat_190201_c1_LICN', fontsize = 12)
axs['C'].set_ylabel('current [pA]')
axs['D'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_ctrl, 'dlpag_vgat_180208_c1_LICB_OP_clear_VC_2_results.npz'))["average_spike"])
axs['D'].set_xlim(120, 190)
axs['D'].set_ylim(-225, 125)
axs['D'].set_title('dlpag_vgat_180208_c1_LICB', fontsize = 12)
axs['D'].set_ylabel('current [pA]')
axs['E'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_ctrl, 'dlpag_vgat_200720_c2_LIDG_OP_VC_clear_nointerval_1_results.npz'))["average_spike"])
axs['E'].set_xlim(120, 190)
axs['E'].set_ylim(-225, 125)
axs['E'].set_title('dlpag_vgat_200720_c2_LIDG', fontsize = 12)
axs['E'].set_ylabel('current [pA]')
axs['F'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_ctrl, 'dmpag_vgat_201202_c3_LIEO_OP_VC_clear_nointerval_1_results.npz'))["average_spike"])
axs['F'].set_xlim(120, 190)
axs['F'].set_ylim(-225, 125)
axs['F'].set_title('dmpag_vgat_201202_c3_LIEO', fontsize = 12)
axs['F'].set_ylabel('current [pA]')
axs['G'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_ctrl, 'lpag_vgat_171218_c4_LIBW_OP_clear_VC_2_results.npz'))["average_spike"])
axs['G'].set_xlim(120, 190)
axs['G'].set_ylim(-225, 125)
axs['G'].set_title('lpag_vgat_171218_c4_LIBW', fontsize = 12)
axs['G'].set_ylabel('current [pA]')
axs['H'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_ctrl, 'vlpag_vgat_171130_c1_LIBH_OP_clear_VC_2_results.npz'))["average_spike"])
axs['H'].set_xlim(120, 190)
axs['H'].set_ylim(-225, 125)
axs['H'].set_title('vlpag_vgat_171130_c1_LIBH', fontsize = 12)
axs['H'].set_ylabel('current [pA]')
# Set figure title
plt.suptitle('\nPotential sample traces for VGAT control\n', fontsize = 14)
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_loose_seal, 'overview_vgat_ctrl.png'))

# %%
## Potential vgat_kynac_ptx sample traces
# dmpag_vgat_201203_c7_LDICI_OP_VC_clear_nointerval_1_results (maybe)
# dlpag_vgat_201126_c4_LDIBS_OP_VC_clear_nointerval_3_results (no)
# dlpag_vgat_201202_c5_LDICA_OP_VC_clear_nointerval_1_results (maybe)
# dmpag_vgat_201105_c8_LDIBI_OP_VC_clear_nointerval_2_results (maybe)
# dlpag_vgat_200720_c9_LDIAS_OP_VC_clear_nointerval_1_results (-137.18 pA)
# dmpag_vgat_201105_c7_LDIBH_OP_VC_clear_nointerval_2_results (maybe)
# dmpag_vgat_201203_c8_LDICJ_OP_VC_clear_nointerval_2_results (no)

# Plot the potential example cells
get_ipython().run_line_magic('matplotlib', 'qt')
fig2 = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100)
axs2 = fig2.subplot_mosaic(
    """
    AB
    CD
    EF
    GH
    """
)
axs2['A'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_kynac_ptx, 'dmpag_vgat_201203_c7_LDICI_OP_VC_clear_nointerval_1_results.npz'))["average_spike"])
axs2['A'].set_xlim(120, 190)
axs2['A'].set_ylim(-225, 125)
axs2['A'].set_title('dmpag_vgat_201203_c7_LDICI', fontsize = 12)
axs2['A'].set_ylabel('current [pA]')
axs2['B'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_kynac_ptx, 'dlpag_vgat_201126_c4_LDIBS_OP_VC_clear_nointerval_3_results.npz'))["average_spike"])
axs2['B'].set_xlim(120, 190)
axs2['B'].set_ylim(-225, 125)
axs2['B'].set_title('dlpag_vgat_201126_c4_LDIBS', fontsize = 12)
axs2['B'].set_ylabel('current [pA]')
axs2['C'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_kynac_ptx, 'dlpag_vgat_201202_c5_LDICA_OP_VC_clear_nointerval_1_results.npz'))["average_spike"])
axs2['C'].set_xlim(120, 190)
axs2['C'].set_ylim(-225, 125)
axs2['C'].set_title('dlpag_vgat_201202_c5_LDICA', fontsize = 12)
axs2['C'].set_ylabel('current [pA]')
axs2['D'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_kynac_ptx, 'dmpag_vgat_201105_c8_LDIBI_OP_VC_clear_nointerval_2_results.npz'))["average_spike"])
axs2['D'].set_xlim(120, 190)
axs2['D'].set_ylim(-225, 125)
axs2['D'].set_title('dmpag_vgat_201105_c8_LDIBI', fontsize = 12)
axs2['D'].set_ylabel('current [pA]')
axs2['E'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_kynac_ptx, 'dlpag_vgat_200720_c9_LDIAS_OP_VC_clear_nointerval_1_results.npz'))["average_spike"])
axs2['E'].set_xlim(120, 190)
axs2['E'].set_ylim(-225, 125)
axs2['E'].set_title('dlpag_vgat_200720_c9_LDIAS', fontsize = 12)
axs2['E'].set_ylabel('current [pA]')
axs2['F'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_kynac_ptx, 'dmpag_vgat_201105_c7_LDIBH_OP_VC_clear_nointerval_2_results.npz'))["average_spike"])
axs2['F'].set_xlim(120, 190)
axs2['F'].set_ylim(-225, 125)
axs2['F'].set_title('dmpag_vgat_201105_c7_LDIBH', fontsize = 12)
axs2['F'].set_ylabel('current [pA]')
axs2['G'].plot(np.load(os.path.join(folder_results_loose_seal_vgat_kynac_ptx, 'dmpag_vgat_201203_c8_LDICJ_OP_VC_clear_nointerval_2_results.npz'))["average_spike"])
axs2['G'].set_xlim(120, 190)
axs2['G'].set_ylim(-225, 125)
axs2['G'].set_title('dmpag_vgat_201203_c8_LDICJ', fontsize = 12)
axs2['G'].set_ylabel('current [pA]')
# Set figure title
plt.suptitle('\nPotential sample traces for VGAT in kynac_ptx\n', fontsize = 14)
fig2.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_loose_seal, 'overview_vgat_kynac_ptx.png'))

# %%
## Potential vglut2_ctrl sample traces
# dlpag_vglut2_180122_c3_LEAO_OP_clear_VC_2_results
# dmpag_vglut2_180201_c1_LEAS_OP_clear_VC_3_results
# dmpag_vglut2_180201_c6_LEAX_OP_clear_VC_1_results
# dlpag_vglut2_190118_c6_LEBK_OP_VC_clear_nointerval_2_results
# lpag_vglut2_180201_c4_LEAV_OP_clear_VC_1_results (-111.35 pA)
# vlpag_vglut2_201120_c2_LECZ_OP_VC_clear_nointerval_1_results
# dmpag_vglut2_171127_c7_LEAG_OP_clear_VC_1_results
# vlpag_vglut2_190118_c7_LEBL_OP_VC_clear_nointerval_2_results

# Plot the potential example cells
get_ipython().run_line_magic('matplotlib', 'qt')
fig3 = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100)
axs3 = fig3.subplot_mosaic(
    """
    AB
    CD
    EF
    GH
    """
)
axs3['A'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ctrl, 'dlpag_vglut2_180122_c3_LEAO_OP_clear_VC_2_results.npz'))["average_spike"])
axs3['A'].set_xlim(120, 190)
axs3['A'].set_ylim(-225, 125)
axs3['A'].set_title('dlpag_vglut2_180122_c3_LEAO', fontsize = 12)
axs3['A'].set_ylabel('current [pA]')
axs3['B'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ctrl, 'dmpag_vglut2_180201_c1_LEAS_OP_clear_VC_3_results.npz'))["average_spike"])
axs3['B'].set_xlim(120, 190)
axs3['B'].set_ylim(-225, 125)
axs3['B'].set_title('dmpag_vglut2_180201_c1_LEAS', fontsize = 12)
axs3['B'].set_ylabel('current [pA]')
axs3['C'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ctrl, 'dmpag_vglut2_180201_c6_LEAX_OP_clear_VC_1_results.npz'))["average_spike"])
axs3['C'].set_xlim(120, 190)
axs3['C'].set_ylim(-225, 125)
axs3['C'].set_title('dmpag_vglut2_180201_c6_LEAX', fontsize = 12)
axs3['C'].set_ylabel('current [pA]')
axs3['D'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ctrl, 'dlpag_vglut2_190118_c6_LEBK_OP_VC_clear_nointerval_2_results.npz'))["average_spike"])
axs3['D'].set_xlim(120, 190)
axs3['D'].set_ylim(-225, 125)
axs3['D'].set_title('dlpag_vglut2_190118_c6_LEBK', fontsize = 12)
axs3['D'].set_ylabel('current [pA]')
axs3['E'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ctrl, 'lpag_vglut2_180201_c4_LEAV_OP_clear_VC_1_results.npz'))["average_spike"])
axs3['E'].set_xlim(120, 190)
axs3['E'].set_ylim(-225, 125)
axs3['E'].set_title('lpag_vglut2_180201_c4_LEAV', fontsize = 12)
axs3['E'].set_ylabel('current [pA]')
axs3['F'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ctrl, 'vlpag_vglut2_201120_c2_LECZ_OP_VC_clear_nointerval_1_results.npz'))["average_spike"])
axs3['F'].set_xlim(120, 190)
axs3['F'].set_ylim(-225, 125)
axs3['F'].set_title('vlpag_vglut2_201120_c2_LECZ', fontsize = 12)
axs3['F'].set_ylabel('current [pA]')
axs3['G'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ctrl, 'dmpag_vglut2_171127_c7_LEAG_OP_clear_VC_1_results.npz'))["average_spike"])
axs3['G'].set_xlim(120, 190)
axs3['G'].set_ylim(-225, 125)
axs3['G'].set_title('dmpag_vglut2_171127_c7_LEAG', fontsize = 12)
axs3['G'].set_ylabel('current [pA]')
axs3['H'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ctrl, 'vlpag_vglut2_190118_c7_LEBL_OP_VC_clear_nointerval_2_results.npz'))["average_spike"])
axs3['H'].set_xlim(120, 190)
axs3['H'].set_ylim(-225, 125)
axs3['H'].set_title('vlpag_vglut2_190118_c7_LEBL', fontsize = 12)
axs3['H'].set_ylabel('current [pA]')
# Set figure title
plt.suptitle('\nPotential sample traces for VGluT2 control\n', fontsize = 14)
fig3.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_loose_seal, 'overview_vglut2_ctrl.png'))

# %%
## Potential vglut2_ptx sample traces 
# dmpag_vglut2_190117_c6_LDEBO_OP_VC_clear_nointerval_5_results (-108.20 pA)
# lpag_vglut2_201120_c6_LDEDD_OP_VC_clear_nointerval_1_results (no)
# dlpag_vglut2_190208_c3_LDEBT_OP_VC_clear_nointerval_1_results (no)
# dmpag_vglut2_190115_c5_LDEBF_OP_VC_clear_nointerval_3_results (no)
# lpag_vglut2_201117_c8_LDECU_OP_VC_clear_nointerval_1_results (no)

# Plot the potential example cells
get_ipython().run_line_magic('matplotlib', 'qt')
fig4 = plt.figure(tight_layout = True, figsize = (7, 10), dpi = 100)
axs4 = fig4.subplot_mosaic(
    """
    AB
    CD
    EF
    GH
    """
)
axs4['A'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ptx, 'dmpag_vglut2_190117_c6_LDEBO_OP_VC_clear_nointerval_5_results.npz'))["average_spike"])
axs4['A'].set_xlim(120, 190)
axs4['A'].set_ylim(-225, 125)
axs4['A'].set_title('dmpag_vglut2_190117_c6_LDEBO', fontsize = 12)
axs4['A'].set_ylabel('current [pA]')
axs4['B'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ptx, 'lpag_vglut2_201120_c6_LDEDD_OP_VC_clear_nointerval_1_results.npz'))["average_spike"])
axs4['B'].set_xlim(120, 190)
axs4['B'].set_ylim(-225, 125)
axs4['B'].set_title('lpag_vglut2_201120_c6_LDEDD', fontsize = 12)
axs4['B'].set_ylabel('current [pA]')
axs4['C'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ptx, 'dlpag_vglut2_190208_c3_LDEBT_OP_VC_clear_nointerval_1_results.npz'))["average_spike"])
axs4['C'].set_xlim(120, 190)
axs4['C'].set_ylim(-225, 125)
axs4['C'].set_title('dlpag_vglut2_190208_c3_LDEBT', fontsize = 12)
axs4['C'].set_ylabel('current [pA]')
axs4['D'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ptx, 'dmpag_vglut2_190115_c5_LDEBF_OP_VC_clear_nointerval_3_results.npz'))["average_spike"])
axs4['D'].set_xlim(120, 190)
axs4['D'].set_ylim(-225, 125)
axs4['D'].set_title('dmpag_vglut2_190115_c5_LDEBF', fontsize = 12)
axs4['D'].set_ylabel('current [pA]')
axs4['E'].plot(np.load(os.path.join(folder_results_loose_seal_vglut2_ptx, 'lpag_vglut2_201117_c8_LDECU_OP_VC_clear_nointerval_1_results.npz'))["average_spike"])
axs4['E'].set_xlim(120, 190)
axs4['E'].set_ylim(-225, 125)
axs4['E'].set_title('lpag_vglut2_201117_c8_LDECU', fontsize = 12)
axs4['E'].set_ylabel('current [pA]')
# Set figure title
plt.suptitle('\nPotential sample traces for VGluT2 in ptx\n', fontsize = 14)
fig4.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_loose_seal, 'overview_vglut2_ptx.png'))

# %% [markdown]
# ### 2.2 | Plot all spikes with average spike of selected cells

# %%
# Set path to save folder
folder_sample_traces_loose_seal = r"D:\Dropbox (UCL - SWC)\Project_paginhibition\analysis\loose_seal\loose_seal_plots\sample_traces_average_spike"
print("save path established!")

# How to load and explore the results from .npz files
# # To load and inspect an .npz file with the results of a chosen cell:
# example_vglut2_ptx_results = np.load(os.path.join(folder_results_loose_seal_vglut2_ptx, 'dmpag_vglut2_190117_c6_LDEBO_OP_VC_clear_nointerval_5_results.npz'))
# example_vglut2_ptx_results.files 
# # We care about the 'average_spike' and the 'cut_spikes_baselined_clean'
# example_average_spike = example_vglut2_ptx_results['average_spike']
# example_spikes = example_vglut2_ptx_results['cut_spikes_baselined_clean']

# %%
# Set colours
colour_vgat_ctrl = '#FF8080'
colour_vgat_kynac_ptx = '#FFCCCC'
colour_vglut2_ctrl = '#0F99B2'
colour_vglut2_ptx = '#9FD6E0'
print('colours set!')

# Load vgat_ctrl example cell
vgat_ctrl_results = np.load(os.path.join(folder_results_loose_seal_vgat_ctrl, 'vlpag_vgat_171130_c1_LIBH_OP_clear_VC_2_results.npz'))
vgat_ctrl_spikes = vgat_ctrl_results['cut_spikes_baselined_clean']
vgat_ctrl_average_spike = vgat_ctrl_results['average_spike']

# Load vgat_kynac_ptx example cell
vgat_kynac_ptx_results = np.load(os.path.join(folder_results_loose_seal_vgat_kynac_ptx, 'dlpag_vgat_200720_c9_LDIAS_OP_VC_clear_nointerval_1_results.npz'))
vgat_kynac_ptx_spikes = vgat_kynac_ptx_results['cut_spikes_baselined_clean']
vgat_kynac_ptx_average_spike = vgat_kynac_ptx_results['average_spike']

# Load vglut2_ctrl example cell
vglut2_ctrl_results = np.load(os.path.join(folder_results_loose_seal_vglut2_ctrl, 'lpag_vglut2_180201_c4_LEAV_OP_clear_VC_1_results.npz'))
vglut2_ctrl_spikes = vglut2_ctrl_results['cut_spikes_baselined_clean']
vglut2_ctrl_average_spike = vglut2_ctrl_results['average_spike']

# Load vglut2_ptx example cell
vglut2_ptx_results = np.load(os.path.join(folder_results_loose_seal_vglut2_ptx, 'dmpag_vglut2_190117_c6_LDEBO_OP_VC_clear_nointerval_5_results.npz'))
vglut2_ptx_spikes = vglut2_ptx_results['cut_spikes_baselined_clean']
vglut2_ptx_average_spike = vglut2_ptx_results['average_spike']

print('sample data loaded!')

# %%
# Plot all the example cells together
get_ipython().run_line_magic('matplotlib', 'qt')
final_fig = plt.figure(tight_layout = True, figsize = (10, 10), dpi = 100)
final_axs = final_fig.subplot_mosaic(
    """
    AB
    CD
    """
)
# Plot vgat_ctrl example cell
for s in range(len(vgat_ctrl_spikes)):
    final_axs['A'].plot(vgat_ctrl_spikes[s], colour_vgat_ctrl)
final_axs['A'].plot(vgat_ctrl_average_spike, color = 'k')
final_axs['A'].set_title('vlpag_vgat_171130_c1_LIBH', fontsize = 14)
final_axs['A'].set_xlabel('samples', fontsize = 12)
final_axs['A'].set_ylabel('current [pA]', fontsize = 12)
final_axs['A'].set_xlim(120, 195) # 25 samples = 1 ms
final_axs['A'].set_ylim(-200, 125) # pA
# Plot vgat_kynac_ptx example cell
for s in range(len(vgat_kynac_ptx_spikes)):
    final_axs['B'].plot(vgat_kynac_ptx_spikes[s], colour_vgat_kynac_ptx)
final_axs['B'].plot(vgat_kynac_ptx_average_spike, color = 'k')
final_axs['B'].set_title('dlpag_vgat_200720_c9_LDIAS', fontsize = 14)
final_axs['B'].set_xlabel('samples', fontsize = 12)
final_axs['B'].set_ylabel('current [pA]', fontsize = 12)
final_axs['B'].set_xlim(120, 195) # 25 samples = 1 ms
final_axs['B'].set_ylim(-200, 125) # pA
# Plot vglut2_ctrl example cell
for s in range(len(vglut2_ctrl_spikes)):
    final_axs['C'].plot(vglut2_ctrl_spikes[s], colour_vglut2_ctrl)
final_axs['C'].plot(vglut2_ctrl_average_spike, color = 'k')
final_axs['C'].set_title('lpag_vglut2_180201_c4_LEAV', fontsize = 14)
final_axs['C'].set_xlabel('samples', fontsize = 12)
final_axs['C'].set_ylabel('current [pA]', fontsize = 12)
final_axs['C'].set_xlim(120, 195) # 25 samples = 1 ms
final_axs['C'].set_ylim(-200, 125) # pA
# Plot vglut2_ctrl example cell
for s in range(len(vglut2_ptx_spikes)):
    final_axs['D'].plot(vglut2_ptx_spikes[s], colour_vglut2_ptx)
final_axs['D'].plot(vglut2_ptx_average_spike, color = 'k')
final_axs['D'].set_title('dmpag_vglut2_190117_c6_LDEBO', fontsize = 14)
final_axs['D'].set_xlabel('samples', fontsize = 12)
final_axs['D'].set_ylabel('current [pA]', fontsize = 12)
final_axs['D'].set_xlim(120, 195) # 25 samples = 1 ms
final_axs['D'].set_ylim(-200, 125) # pA
final_fig.canvas.manager.window.move(0, 0)
# Show and save plot
plt.show()
plt.savefig(os.path.join(folder_sample_traces_loose_seal, 'sample_traces_overview.eps'), format = 'eps') # save figure as .eps

# %%
# Plot vgat_ctrl example cell
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
for s in range(len(vgat_ctrl_spikes)):
    plt.plot(vgat_ctrl_spikes[s], colour_vgat_ctrl)
plt.plot(vgat_ctrl_average_spike, color = 'k')
plt.title('VGAT control: vlpag_vgat_171130_c1_LIBH', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
plt.xlim(120, 195) # 25 samples = 1 ms
plt.ylim(-200, 125) # pA
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_loose_seal, 'vgat_ctrl_sample_trace_LIBH.eps'), format = 'eps') # save figure as .eps

# %%
# Plot vgat_kynac_ptx example cell
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
for s in range(len(vgat_kynac_ptx_spikes)):
    plt.plot(vgat_kynac_ptx_spikes[s], colour_vgat_kynac_ptx)
plt.plot(vgat_kynac_ptx_average_spike, color = 'k')
plt.title('VGAT in kynac_ptx: dlpag_vgat_200720_c9_LDIAS', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
plt.xlim(120, 195) # 25 samples = 1 ms
plt.ylim(-200, 125) # pA
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_loose_seal, 'vgat_kynac_ptx_sample_trace_LDIAS.eps'), format = 'eps') # save figure as .eps

# %%
# Plot vglut2_ctrl example cell
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
for s in range(len(vglut2_ctrl_spikes)):
    plt.plot(vglut2_ctrl_spikes[s], colour_vglut2_ctrl)
plt.plot(vglut2_ctrl_average_spike, color = 'k')
plt.title('VGluT2 control: lpag_vglut2_180201_c4_LEAV', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
plt.xlim(120, 195) # 25 samples = 1 ms
plt.ylim(-200, 125) # pA
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_loose_seal, 'vglut2_ctrl_sample_trace_LEAV.eps'), format = 'eps') # save figure as .eps

# %%
# Plot vglut2_ptx example cell
get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(figsize = (7, 5), dpi = 100) # Set figure size
for s in range(len(vglut2_ptx_spikes)):
    plt.plot(vglut2_ptx_spikes[s], colour_vglut2_ptx)
plt.plot(vglut2_ptx_average_spike, color = 'k')
plt.title('VGluT2 in picrotoxin: dmpag_vglut2_190117_c6_LDEBO', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
plt.xlim(120, 195)
plt.ylim(-200, 125) # pA
fig.canvas.manager.window.move(0, 0)
plt.show()
plt.savefig(os.path.join(folder_sample_traces_loose_seal, 'vglut2_ptx_sample_trace_LDEBO.eps'), format = 'eps') # save figure as .eps

# %%
