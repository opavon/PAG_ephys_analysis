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
from whole_cell_utilities import * # includes functions importFile, openFile, openHDF5file
print("done!")

# %%
# Load data
channels_df, time, dt, folder_name, file_name = importFile(curated_channel = None)
print("file imported")

# %%
# Extract data and plot
sweep_IA = np.array(channels_df.loc['Channel A', :])
sweep_OA = np.array(channels_df.loc['Output A', :])

# Get color palette and generate one color for each sweep
import matplotlib.cm as cm
sweep_colors = cm.viridis(np.linspace(0, 1, len(sweep_IA)))

get_ipython().run_line_magic('matplotlib', 'qt')
fig = plt.figure(tight_layout = True, figsize = (10, 5), dpi = 100) # Set figure size
axs = fig.subplot_mosaic(
    """
    AA
    BB
    """
)

for sweep in range(len(sweep_IA)):
    axs['A'].plot(sweep_IA[sweep], color = sweep_colors[sweep])
axs['A'].set_title('Channel A', fontsize = 12)
axs['A'].set_ylabel('voltage [mV]')
axs['A'].set_xlim([0, (len(sweep_IA[0]))])

for sweep in range(len(sweep_OA)):
    axs['B'].plot(sweep_OA[sweep], color = sweep_colors[sweep])
axs['B'].set_title('Output A', fontsize = 12)
axs['B'].set_ylabel('current [pA]')
axs['B'].set_xlim([0, (len(sweep_IA[0]))])

fig.canvas.manager.window.move(0, 0) # Move figure to top left corner
plt.show()
# %%
