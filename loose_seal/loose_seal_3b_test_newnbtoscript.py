# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %% [markdown]
# ## 0 | Import packages

# %%
import os
import h5py
import numpy as np
import pandas as pd
import seaborn as sns
import tkinter
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from utilities import importFile, openFile, openHDF5file, getLooseRseal
from tkinter.filedialog import askopenfilename, askopenfilenames
from collections import defaultdict
from nptdms import TdmsFile
from scipy import stats
from scipy.signal import find_peaks
print("done!")

# %% [markdown]
# ## 1 | Use `find_peaks()` to detect spikes in all concatenated sweeps
# 
# Now that we can detect spikes and are sure we are not counting noise, we can continue to do the same for all the sweeps of the cell we are analysing. We are going to need to (1) be able to plot the histogram of prominences for the detected peaks and (2) be able to ask the user for input so it can set the adequate prominence bracket to detect spikes and not noise.
# %% [markdown]
# First of all, load an example cell to work with:

# %%
# Load data for LIAM cell (contains spikes in test_pulse)
channels_data_frame_1, time_1, dt_1, folder_name_1, file_name_1 = importFile(curated_channel = 'Sweeps_Analysis')
print("file imported")


# %%
# Inspect data frame
channels_data_frame_1


# %%
# Extract sweep
sweep_IB_1 = np.array(channels_data_frame_1.at['Channel B', '30'])

# Plot it
get_ipython().run_line_magic('matplotlib', 'inline')
# matplotlib tk
plt.plot(sweep_IB_1, 'k')
plt.title('Figure 1a: One Sweep', fontsize = 14)
plt.ylabel('current [pA]')
plt.show()

# %% [markdown]
# ### 1.1 | Find a way to plot and ask for input within a loop
# 
# We can ask for input with the input() function, and convert the value to integer.

# %%
prominence_min = int(input("Enter the min value for the desired prominence"))
prominence_max = int(input("Enter the max value for the desired prominence"))

print(prominence_min)
print(prominence_max)

# %% [markdown]
# We next need a way to first show the histogram, and then ask for the user input. The cell below will work as desired if it is run as a script from the command line. Briefly, it will plot a figure, wait for a period of time (or for the user to press a key once the figure has been examined), and then ask for the min and max values of prominence to use to detect peaks. We will build on this backbone to achieve a code that will loop over files in a folder, detect peaks according to a desired prominence, store the peaks and spikes, and proceed to the next cell.

# %%
#this will work if you run it from a script called from the terminal. Right now, it doesn't work as desired in the notebook.
import matplotlib.pyplot as plt
for i in range(10):
    plt.ion()
    plt.figure(figsize = (8, 6), dpi = 100) # Set figure size
    plt.scatter(1, i)
    plt.title(i+1)
    
    plt.pause(0.5) # Alternative to waitforbuttonpress() - does not close the figure and proceeds to input().
    # if plt.waitforbuttonpress(): # if not using pause(), this is needed to render the figure
    #     plt.close()

    prominence_min = int(input("Enter the min value for the desired prominence"))
    prominence_max = int(input("Enter the max value for the desired prominence"))
    print(f'For sweep number {i}, you chose a prominence between {prominence_min} and {prominence_max}')
    
    plt.close() # needed here if plt.pause() is used instead of plt.waitforbuttonpress()

# %% [markdown]
# The next cell contains a close reproduction of the code above to work on a notebook. Unfortunately, in the notebook we need to manually click on the editor to switch focus from the figure to the input prompt in order to enter the desired prominence values, so it is a bit slower. In addition, the figure doesn't close after clicking a button, which in this case is a good thing as we can keep examining it until we have entered both prominence values and the code proceeds to the next iteration.

# %%
get_ipython().run_line_magic('matplotlib', 'tk')
#%matplotlib inline

for i in range(2):
    plt.figure(figsize = (8, 6), dpi = 100)
    plt.scatter(1, i)
    plt.title(i+1)
    plt.pause(0.5) # Alternative to waitforbuttonpress() - does not close the figure and proceeds to input(), but you can't interact with the figure. 
    # if plt.waitforbuttonpress(): # if not using pause(), this is needed to render the figure
    #     plt.close()
    
    prominence_min = int(input("Enter the min value for the desired prominence"))
    prominence_max = int(input("Enter the max value for the desired prominence"))
    print(f'For sweep number {i}, you chose a prominence between {prominence_min} and {prominence_max}')
    
    plt.close() # needed here if plt.pause() is used instead of plt.waitforbuttonpress()

# %% [markdown]
# ### 1.2 | Concatenate all sweeps
# 
# To speed things up a bit, we don't want to loop over sweeps on top of looping over cells. Ideally, we want to run `find_peaks` on the full recording of a cell, get the histogram, fine-tune the prominence values, and then get the spikes.Howeveranif we take a look at, in protocol `VC_clear` (see belwe can see it has was a brief interval between sweeps. This means interspike interval ISI between the last spike of one sweep and the first spike of the next won't be accurate, on top of that and we have ave missed spikes in that short period. For the other protocols this should not be an issue, and we should be able to obtain ISI from the concatenated s. Nonetheless, given that each recording has between 12 and 40 sweeps, if we discard the ISI between last spike of a sweep and first of the next we would only be "loosing" 12-40 ISI out of potentially hundreds. Thus, we will apply the same procedure regardless of the protocol used. eeOne strategy we can use is to create a pseudo-sweep that is concatenated to have the same length and number of sweeps as the original data, with the difference that sweep number one will be comprised of zeroes (or the number that reflects the real sweep ID), sweep number two will be comprised of ones, and so forth. Once we have obtained the indices for all the peaks we can "deconcatenate" them and re-assign each peak to the corresponding sweep, so that we can proceed to calculate ISI and firing rate on a sweep by sweep basis, on top of firing rate for the full recording.er on.
# 
# __Protocols used:__
# 
#  - OP_VC_clear:
#     - Sweep duration: 4950ms
#     - Sweep interval: 50ms
#     - Test pulse: 100ms (50ms delay and 50ms pulse)
#     - Real data per sweep: 4850ms
# 
#  - OP_VC_clear_nointerval:
#    - Sweep duration: 5100ms
#    - Sweep interval: 0ms
#    - Test pulse: 75ms (25ms delay and 50ms pulse)
#    - Real data per sweep: 5025ms
# 
#  - OP_VC_clear_nointerval:
#    - Sweep duration: 10100ms
#    - Sweep interval: 0ms
#    - Test pulse: 75ms (25ms delay and 50ms pulse)
#    - Real data per sweep: 10025ms

# %%
sweep_IB_1_tmp = np.array(channels_data_frame_1.loc['Channel B', :])
sweep_IB_1_concatenated = np.concatenate(sweep_IB_1_tmp)
print('done!')

# %% [markdown]
# Create a pseudo-sweep that is concatenated to have the same length and number of sweeps as the original data, with the difference that sweep number one will be comprised of zeroes (or the number that reflects the real sweep ID), sweep number two will be comprised of ones, and so forth.

# %%
pseudo_sweep_keys = []

for i, sweep in enumerate(sweep_IB_1_tmp):
    sweep_key = int(channels_data_frame_1.columns[i])
    sweep_keys_tmp = np.zeros(len(sweep), dtype = int) + sweep_key
    pseudo_sweep_keys.append(sweep_keys_tmp)

pseudo_sweep_concatenated = np.concatenate(pseudo_sweep_keys)

len(pseudo_sweep_concatenated) == len(sweep_IB_1_concatenated)


# %%
# Plot it using matplotlib tk if you want to zoom in to explore the trace
get_ipython().run_line_magic('matplotlib', 'inline')
plt.plot(sweep_IB_1_concatenated, 'k')
plt.title('Figure 1b: All sweeps concatenated', fontsize = 14)
plt.ylabel('current [pA]')
plt.show()

# %% [markdown]
# Plotting the concatenated sweeps is not very useful in such a small figure, but we can plot using `matplotlib tk` if we want to zoom in and inspect it more closely. 
# 
# At first sight, the test pulses seem to be of different sizes. However, once we zoom in we can see that it actually only looks like that because there is a spike happening during the test pulse. The test pulses are actually quite stable, as we can see in the plot below.

# %%
# Get Rseal data
Rseal_data_frame = getLooseRseal(file_name_1, channels_data_frame_1)
seal_resistance = Rseal_data_frame.loc['seal_resistance']

get_ipython().run_line_magic('matplotlib', 'inline')
plt.plot(seal_resistance, 'k')
plt.title('Figure 1c: Seal Resistance across sweeps', fontsize = 14)
plt.ylabel('Seal Resistance [MOhm]')
plt.xlabel('sweep number')
plt.axis([0, len(seal_resistance), 0, 50])
plt.show()

# %% [markdown]
# ### 1.3 | Detect spikes in concatenated sweeps
# Now we are going to run `find_peaks` with different parameters and plot the histogram of the prominences of the detected peaks. We will try the following:
# 
#  1. Run `find_peaks` with no parameters, so we can examine the prominences of anything detected. This will help us fine-tune the function call.
#  2. Run `find_peaks` with `wlen = (10/dt_1)`.
#  3. Run `find_peaks` with our choice of `prominence` according to the histogram obtained from step 1.
#  4. Run `find_peaks` with both our choice of `prominence` and `wlen = (10/dt_1)`.

# %%
peaks_1a, properties_1a = find_peaks(-sweep_IB_1_concatenated, height = (None, None), threshold = (None, None), distance = None, prominence = (None, None), width = (None, None), wlen = None)
# Reverse the sign of the data to detect the lower peak of the spike (some are unipolar and only go down) and to avoid the noise.
print(len(peaks_1a))

get_ipython().run_line_magic('matplotlib', 'inline')
ax = plt.gca()
plt.hist(properties_1a['prominences'], bins = 200, density = False, histtype = 'bar', log = True)
plt.title('Figure 1d: Prominence of detected peaks', fontsize = 14)
plt.text(0.95, 0.95, 'Parameters: none', horizontalalignment='right', verticalalignment='top', transform = ax.transAxes)
plt.xlabel('peak prominence [pA]', fontsize = 12)
plt.show()

get_ipython().run_line_magic('matplotlib', 'tk')
plt.plot(peaks_1a, sweep_IB_1_concatenated[peaks_1a], "xr"); plt.plot(sweep_IB_1_concatenated); plt.legend(['peaks'])
plt.title('Figure 1d: Detected peaks for concatenated sweeps', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
plt.show()

# %% [markdown]
# __Step 1__ (above) detects everything from baseline noise and test pulses, to high amplitude noise and spikes. We can see the distribution of prominences in the histogram above, and in the pop up plot we can examine all the peaks detected. 
# 
# Interestingly, __Step 2__ (below) shows us a very similar yet very different picture. Although the total number of peaks detected is the same, the distribution of prominence values is very different, and it seems that it is now only detecting baseline noise (0-50pA prominence) or spikes (100-175pA prominence). This is due to the fact of using a value of 10 ms as `wlen`. If we play with that value, we see small shifts in the distribution of prominences in the histogram, but as we test in __Step 4__ it doesn't seem to affect the ability to detect peaks unless we go outside the range of 2-40 ms.
# 
# This is an important point. According to `scipy.signal.find_peaks` documentation, `wlen` defines "a window length in samples that optionally limits the evaluated area for each peak to a subset of x. The peak is always placed in the middle of the window therefore the given length is rounded up to the next odd integer. This parameter can speed up the calculation". 
# 
#  * The function works by extending "a horizontal line from the current peak to the left and right until the line either reaches the window border (see `wlen`) or intersects the signal again at the slope of a higher peak. An intersection with a peak of the same height is ignored. On each side it finds the minimal signal value within the interval defined above. These points are the peak’s bases. The higher one of the two bases marks the peak’s lowest contour line. The prominence is then calculated as the vertical difference between the peaks height itself and its lowest contour line."
# 
#  * Importantly, they point out that "searching for the peak’s bases can be slow for large x with periodic behavior because large chunks or even the full signal need to be evaluated for the first algorithmic step. This evaluation area can be limited with the parameter wlen which restricts the algorithm to a window around the current peak and can shorten the calculation time if the window length is short in relation to x. However, this may stop the algorithm from finding the true global contour line if the peak’s true bases are outside this window. Instead, a higher contour line is found within the restricted window leading to a smaller calculated prominence. In practice, this is only relevant for the highest set of peaks in x. This behavior may even be used intentionally to calculate “local” prominences."
# 
# Indeed, setting `wlen` to the equivalent in samples of 10ms allows us to detect "local" prominences. This is exactly what we want, as a spike will be a very brief peak, and we are not really interested in finding the true global countour. 
# 
# In __Step 4__ after fine-tuning the prominence value, we can play with the values of `wlen`. What we see is that if we set it to anything between 2 and 40 ms, the algorithm is able to find all the spikes. However, if we go higher than that, we start missing the ones happening during the test pulse. Thus, anything between 2-40 ms as `wlen` seems to do the trick, and we think that a 10 ms time window is enough, as we rarely observe anything faster than 200 Hz in our recorded activity.

# %%
peaks_1b, properties_1b = find_peaks(-sweep_IB_1_concatenated, height = (None, None), threshold = (None, None), distance = None, prominence = (None, None), width = (None, None), wlen = (10/dt_1))
# Reverse the sign of the data to detect the lower peak of the spike (some are unipolar and only go down) and to avoid the noise.
print(len(peaks_1b))

get_ipython().run_line_magic('matplotlib', 'inline')
ax = plt.gca()
plt.hist(properties_1b['prominences'], bins = 200, density = False, histtype = 'bar', log = True)
plt.title('Figure 1d: Prominence of detected peaks', fontsize = 14)
plt.text(0.95, 0.95, 'wlen = (10/dt)', horizontalalignment='right', verticalalignment='top', transform = ax.transAxes)
plt.xlabel('peak prominence [pA]', fontsize = 12)
plt.show()

get_ipython().run_line_magic('matplotlib', 'tk')
plt.plot(peaks_1b, sweep_IB_1_concatenated[peaks_1b], "xr"); plt.plot(sweep_IB_1_concatenated); plt.legend(['peaks'])
plt.title('Figure 1d: Detected peaks for concatenated sweeps', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
plt.show()

# %% [markdown]
# __Step 2__ allows us to identify the value we can use to separate baseline noise from spikes. In this case, any prominence value above 75 should do the trick, as it cleanly separates the distribution in two.

# %%
peaks_1c, properties_1c = find_peaks(-sweep_IB_1_concatenated, height = (None, None), threshold = (None, None), distance = None, prominence = (75, None), width = (None, None), wlen = None)
# Reverse the sign of the data to detect the lower peak of the spike (some are unipolar and only go down) and to avoid the noise.
print(len(peaks_1c))

get_ipython().run_line_magic('matplotlib', 'inline')
ax = plt.gca()
plt.hist(properties_1c['prominences'], bins = 200, density = False, histtype = 'bar', log = True)
plt.title('Figure 1d: Prominence of detected peaks', fontsize = 14)
plt.text(0.05, 0.95, 'prominence = (100, 200)', fontsize = 10, horizontalalignment = 'left', verticalalignment = 'top', transform = ax.transAxes)
plt.xlabel('peak prominence [pA]', fontsize = 12)
plt.show()

get_ipython().run_line_magic('matplotlib', 'inline')
plt.plot(peaks_1c, sweep_IB_1_concatenated[peaks_1c], "xr"); plt.plot(sweep_IB_1_concatenated); plt.legend(['peaks'])
plt.title('Figure 1d: Detected peaks for concatenated sweeps', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
plt.show()

# %% [markdown]
# Unfortunately, this doesn't work as desired - depending on the prominence values we choose, we are either missing the spikes happening during test pulses or actually counting the test pulses as peaks! But of course, this is because we tried to be clever and only use prominence as a parameter. If we don't use `wlen`, then we have peaks above a prominence of 75 that correspond to test pulses and other noise. 

# %%
peaks_1d, properties_1d = find_peaks(-sweep_IB_1_concatenated, height = (None, None), threshold = (None, None), distance = None, prominence = (75, None), width = (None, None), wlen = (10/dt_1))
# Reverse the sign of the data to detect the lower peak of the spike (some are unipolar and only go down) and to avoid the noise.
print(len(peaks_1d))

get_ipython().run_line_magic('matplotlib', 'inline')
ax = plt.gca()
plt.hist(properties_1d['prominences'], bins = 200, density = False, histtype = 'bar', log = True)
plt.title('Figure 1d: Prominence of detected peaks', fontsize = 14)
plt.text(0.05, 0.95, 'prominence = (100, 200)\nwlen = (10/dt)', fontsize = 10, horizontalalignment = 'left', verticalalignment = 'top', transform = ax.transAxes)
plt.xlabel('peak prominence [pA]', fontsize = 12)
plt.show()

get_ipython().run_line_magic('matplotlib', 'inline')
plt.plot(peaks_1d, sweep_IB_1_concatenated[peaks_1d], "xr"); plt.plot(sweep_IB_1_concatenated); plt.legend(['peaks'])
plt.title('Figure 1d: Detected peaks for concatenated sweeps', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
plt.show()

# %% [markdown]
# ### 1.4 | Cut, baseline, and average detected spikes
# 
# Once we have detected all the peaks in our concatenated sweep, we proceed to cut and inspect them as a quality chec Cutting 5 ms at either side of the sweep is enough for visualisation purposes.k.

# %%
cut_spikes = [sweep_IB_1_concatenated[peaks_1d[p]-125 : peaks_1d[p]+125] for p in range(len(peaks_1d))]
len(cut_spikes)

# %% [markdown]
# We can plot all the detected spikes as follows.

# %%
get_ipython().run_line_magic('matplotlib', 'inline')
# matplotlib tk

import matplotlib.cm as cm
spike_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes)))

for s in range(len(cut_spikes)):
    plt.plot(cut_spikes[s], color = spike_colors[s])

plt.title('Figure 1e: Cut spikes', fontsize = 14)
plt.ylabel('current [pA]')
plt.show()

# %% [markdown]
# Well, we should probably baseline them first. The spikes at the bottom half probably correspond to those that happen during the test pulse.
# 
# Let's baseline them to try to have them all at the same level to facilitate visualizatio To baseline, we first move 1 ms away from the peak in order to get out from the spike itself and then we can average 1-3 ms to obtain the baseline.n.

# %%
# Get a baseline right before the spike occurs.
cut_spikes_holding = [np.mean(sweep_IB_1_concatenated[peaks_1d[p]-100 : peaks_1d[p]-25]) for p in range(len(peaks_1d))]
len(cut_spikes_holding)

# %% [markdown]
# Subtract the average baseline value from each cut spike trace.

# %%
cut_spikes_baselined = [cut_spikes[i] - cut_spikes_holding[i] for i in range(len(cut_spikes))]
len(cut_spikes_baselined)

# %% [markdown]
# Plot the baselined spikes.

# %%
get_ipython().run_line_magic('matplotlib', 'inline')
# matplotlib tk

import matplotlib.cm as cm
baselined_spikes_colors = cm.viridis(np.linspace(0, 1, len(cut_spikes_baselined)))

for s in range(len(cut_spikes_baselined)):
    plt.plot(cut_spikes_baselined[s], color = baselined_spikes_colors[s])

plt.title('Figure 1f: Cut and baselined spikes', fontsize = 14)
plt.ylabel('current [pA]')
plt.xlim([80, 180])
plt.show()

# %% [markdown]
# From this plot we can make a couple of observations. First, there seems to be at least two instances of noise in our detected peaks. Second, one of the detected spikes seems to be right after the end of a test pulse, as baselining it brings it up and misaligns it with respect to the rest. Finally, we also notice that some spikes seem to have a wider waveform, with a slight bump in the beginning. This could be interesting or a feature of a minority of spikes (it could hint at action potentials being originated from two different sites).
# 
# Although we should remove the noise and the misaligned spike before proceeding, we can obtain an average spike from all the detected ones. We can use this to extract features for that particular neuron.

# %%
average_spike = (np.mean(cut_spikes_baselined, 0))
len(average_spike)


# %%
get_ipython().run_line_magic('matplotlib', 'inline')
# matplotlib tk

plt.plot(average_spike, color = 'k')
plt.title('Figure 1g: Averaged spike', fontsize = 14)
plt.ylabel('current [pA]')
plt.xlim([80, 180])
plt.show()

# %% [markdown]
# Nice! It looks very clean, a sign that the couple of missdetections don't affect the average (it helps that we have over a thousand spikes in this sample). We can take a quick look at the average superimposed on all the detected spikes.

# %%
get_ipython().run_line_magic('matplotlib', 'inline')
for s in range(len(cut_spikes_baselined)):
    plt.plot(cut_spikes_baselined[s], 'k')
plt.plot(average_spike, color = 'r')
plt.title('Figure 1h: Cut spikes with average in red', fontsize = 14)
plt.ylabel('current [pA]')
plt.xlim([80, 180])
plt.show()

# %% [markdown]
# ### 1.5 | QC detected spikes
# 
# (Un)fortunately, and as we have mentioned above, we noticed a couple of detected peaks that do not correspond to spikes. 
# 
# We have different parameters we can look at in order to identify and remove them. If we take a look at the properties of the detected peaks, we can see that spikes and noise differ in the `peak_heights`, the `widths`, and the `width_heights`. We should be able to use this parameters to further optimize our function and remove the instances where noise is still detected, before proceeding to extract any parameters from the data (such as firing rate, ISIs, spike onset, or spike duration). 

# %%
properties_1d


# %%
get_ipython().run_line_magic('matplotlib', 'inline')
plt.hist(properties_1d['peak_heights'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
plt.title('Figure 1i: Histogram of peak_heights', fontsize = 14)
plt.xlabel('peak heights', fontsize = 12)
plt.xlim([None,None])
plt.show()

plt.hist(properties_1d['widths'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
plt.title('Figure 1i: Histogram of widths', fontsize = 14)
plt.xlabel('widths', fontsize = 12)
plt.xlim([None,None])
plt.show()

plt.hist(properties_1d['width_heights'], bins = 100, density = False, histtype = 'bar', log = True, color = 'k')
plt.title('Figure 1i: Histogram of width_heights', fontsize = 14)
plt.xlabel('width heights', fontsize = 12)
plt.xlim([None,None])
plt.show()

# %% [markdown]
# * `peak_heights`: we can see that most peaks have a height of 100-200, with some around 400. The latter ones probably correspond to the spikes riding the test pules. However, we see another peak at zero, which probably correspond to noise.
# 
# * `widths`: most widths fall between 4-6 samples, with a few between 6-8 (corresponding to the spikes with the slight bump in the beginning). The one with a width above 18 is probably noise. 
# 
# * `width_heights`: this is similar to `peak_heights`, and the noise is probably the value below zero. 
# 
# Let's take a look by coloring the spikes according to each of this parameters.

# %%
get_ipython().run_line_magic('matplotlib', 'inline')

cmap = plt.get_cmap('Pastel2')

for s in range(len(cut_spikes_baselined)):
    if properties_1d['width_heights'][s] < 5:
        plt.plot(cut_spikes_baselined[s], color = cmap(3))
    elif properties_1d['widths'][s] > 5.8:
        plt.plot(cut_spikes_baselined[s], color = cmap(1))
    else:
        plt.plot(cut_spikes_baselined[s], color = cmap(0))

plt.title('Figure 1j: Spikes colored by QC parameters', fontsize = 14)
plt.ylabel('current [pA]')
plt.xlim([80, 180])
plt.show()

# %% [markdown]
# Find the index of the peak that is noise and plot it.

# %%
noise_index = peaks_1d[np.where(properties_1d['width_heights'] < 5)]
noise_index[0]


# %%
get_ipython().run_line_magic('matplotlib', 'inline')
plt.plot(peaks_1d, sweep_IB_1_concatenated[peaks_1d], "xr"); plt.plot(sweep_IB_1_concatenated); plt.legend(['peaks'])
plt.title('Figure 1k: Detected peaks for concatenated sweeps', fontsize = 14)
plt.xlabel('samples', fontsize = 12)
plt.ylabel('current [pA]', fontsize = 12)
plt.xlim([noise_index[0]-100, noise_index[0]+100])
plt.show()

# %% [markdown]
# As a last QC, we can run `find_peaks` with prominence values starting at 75-112, and increase the lower limit until we get rid of the noise (aroun 105).

# %%
peaks_1e, properties_1e = find_peaks(-sweep_IB_1_concatenated, height = (None, None), threshold = (None, None), distance = None, prominence = (105, 112), width = (None, None), wlen = (10/dt_1))
# Reverse the sign of the data to detect the lower peak of the spike (some are unipolar and only go down) and to avoid the noise.
print(len(peaks_1e))
print(len(peaks_1e[np.where(properties_1e['width_heights'] < 5)]))

# %% [markdown]
# This is too slow a method to do when analysing all the cells, so we can simply delete the peaks with the paramater value that identifies them as noise.

# %%
peaks_to_delete = np.where(properties_1d['width_heights'] < 5)[0]
peaks_to_delete


# %%
print(len(peaks_1d))
peaks_1d_clean = np.delete(peaks_1d, peaks_to_delete)
print(len(peaks_1d_clean))

# %% [markdown]
# And now we can do the same for the cut spikes and recalculate and plot the average spike.

# %%
print(len(cut_spikes_baselined))
cut_spikes_baselined_denoised = [spike for i, spike in enumerate(cut_spikes_baselined) if i not in peaks_to_delete]
print(len(cut_spikes_baselined_denoised))

# %% [markdown]
# We can also remove the spike that hasn't been baselined properly.

# %%
spikes_to_delete = [i for i, spike in enumerate(cut_spikes_baselined_denoised) if min(spike) > -10]
print(len(spikes_to_delete))


# %%
print(len(cut_spikes_baselined_denoised))
cut_spikes_baselined_clean = [spike for i, spike in enumerate(cut_spikes_baselined_denoised) if i not in spikes_to_delete]
print(len(cut_spikes_baselined_clean))

# %% [markdown]
# Obtain the new average spike after removing the noise.

# %%
average_spike_clean = (np.mean(cut_spikes_baselined_clean, 0))


# %%
get_ipython().run_line_magic('matplotlib', 'inline')
for s in range(len(cut_spikes_baselined_clean)):
    plt.plot(cut_spikes_baselined_clean[s], 'k')
plt.plot(average_spike_clean, color = 'r')
plt.title('Figure 1l: Cut spikes with average in red', fontsize = 14)
plt.ylabel('current [pA]')
plt.xlim([80, 180])
plt.show()

# %% [markdown]
# ## 2 | Calculate parameters of interest
# 
# We want to extract a few parameters from the average spike (time from onset to peak and total duration) as well as the firing frequency from the full recording. We also want to take a look at interspike intervals and the holding current between each pair of spikes to check whether it has an effect on the ISI.
# %% [markdown]
# ### 2.1 | Find the onset and total duration of the average spike

# %%
average_spike_peak_index = int(np.where(average_spike_clean == min(average_spike_clean))[0]) # needs to be an integer
print(average_spike_peak_index)
average_spike_clean_diff = np.diff(average_spike_clean)
average_spike_clean_diff_baseline = abs(np.mean(average_spike_clean_diff[average_spike_peak_index-100:average_spike_peak_index-25]))
print(average_spike_clean_diff_baseline)


# %%
np.round(average_spike_clean_diff[100:160], 1)


# %%
test_threshold = min(average_spike_clean_diff)*0.1
print(test_threshold)

test_end = average_spike_clean_diff_baseline * 100
print(test_end)


# %%
get_ipython().run_line_magic('matplotlib', 'inline')
fig, axs = plt.subplots (2, sharex=True)
axs[0].plot(average_spike_clean,'r')
axs[1].plot(average_spike_clean_diff, 'c')
plt.suptitle('Figure 2a: Averaged spike and its derivative', fontsize = 14)
axs[0].axhline(y = 0, c = 'k', ls = '--')
axs[1].axhline(y = 0, c = 'k', ls = '--')
plt.ylabel('current [pA]')
plt.xlim([80, 180])
plt.show()


# %%
spike_onset_indices = []
spike_end_indices = []

for i, s in enumerate(average_spike_clean_diff):
    if i != 0 and i < average_spike_peak_index and s < test_threshold:
        spike_onset_indices.append(np.where(average_spike_clean_diff == s)[0])
    elif i != 0 and i > average_spike_peak_index and -test_end < average_spike_clean_diff[i-1] < test_end and -test_end < s < test_end:
        spike_end_indices.append(np.where(average_spike_clean_diff == s)[0])

spike_onset = spike_onset_indices[0][0]
spike_end = spike_end_indices[0][0]
spike_length = (spike_end_indices[0][0] - spike_onset_indices[0][0]) * dt_1
spike_onset_to_peak = ((np.where(average_spike_clean == np.min(average_spike_clean))[0][0])-(spike_onset_indices[0][0])) * dt_1

print(f'Spike onset at {spike_onset}')
print(f'Spike end at {spike_end}')
print(f'Spike length of {spike_length} ms')
print(f'Spike onset to peak of {spike_onset_to_peak} ms')


# %%
get_ipython().run_line_magic('matplotlib', 'inline')

fig, axs = plt.subplots (2, sharex=True)
axs[0].plot(spike_onset, average_spike_clean[spike_onset], "xk")
axs[0].plot(spike_end, average_spike_clean[spike_end], "xk")
axs[0].plot(average_spike_clean, 'r')
axs[1].plot(average_spike_clean_diff, 'c')
plt.suptitle('Figure 2b: Averaged spike with onset and end', fontsize = 14)
axs[0].axhline(y = 0, c = 'k', ls = '--')
axs[1].axhline(y = 0, c = 'k', ls = '--')
plt.ylabel('current [pA]')
plt.xlim([80, 180])
plt.show()


# %%
get_ipython().run_line_magic('matplotlib', 'inline')

plt.plot(spike_onset, average_spike_clean[spike_onset], "xr")
plt.plot(spike_end, average_spike_clean[spike_end], "xr")
plt.plot(average_spike_clean, 'k')
plt.suptitle('Figure 2c: Averaged spike with onset and end', fontsize = 14)
plt.axhline(y = 0, c = 'k', ls = '--')
plt.ylabel('current [pA]')
plt.xlim([80, 180])
plt.show()

# %% [markdown]
# ### 2.2 | Calculate firing frequency
# 
# The main parameter we are interested in from our neurons is their firing rate. We could take a look at the following:
# 
#  * Firing rate over full recording
#  * Firing rate over time windows (1s?)
#  * Instantaneous firing rate: inverse of the interspike interval
# 
# We will start by the basic one: dividing the total number of spikes over the total time of recording.

# %%
n_spikes_1d = len(peaks_1d_clean)
time_recording_1d = len(sweep_IB_1_concatenated) * dt_1 / 1000 # in seconds
firing_frequency_1d = n_spikes_1d / time_recording_1d # in Hz
neuron_id = '_'.join(file_name_1.split('_')[0:5])

print(f'Neuron with ID {neuron_id}')
print(f'Detected a total of {n_spikes_1d} spikes')
print(f'During {time_recording_1d} seconds of recording')
print(f'Which gives a firing rate of {round(firing_frequency_1d, 2)} Hz')

# %% [markdown]
# We can also get the firing rate for each sweep or every second, to get a similar plot obtained with the Rseal, to see how the average firing rate changes over time.

# %%
sweep_IB_1_concatenated[0]
peaks_1d_clean[1]
pseudo_sweep_concatenated[peaks_1d_clean[1]]
#channels_data_frame_1.columns[1]
int(channels_data_frame_1.columns[0])


# %%
pseudo_sweep_keys = []
sweep

for i, sweep in enumerate(sweep_IB_1_tmp):
    sweep_key = int(channels_data_frame_1.columns[i])
    sweep_keys_tmp = np.zeros(len(sweep), dtype = int) + sweep_key
    pseudo_sweep_keys.append(sweep_keys_tmp)

pseudo_sweep_concatenated = np.concatenate(pseudo_sweep_keys)


# %%
spikes_by_sweep_keys = []

for sweep in channels_data_frame_1.columns:  
    spikes_in_sweep_tmp = np.array([p if pseudo_sweep_concatenated[peaks_1d_clean[p]] ==  for p in peaks_1d_clean])
spikes_by_sweep.append(spikes_in_sweep_tmp)
spikes_by_sweep_keys.append(int(sweep))


# %%
n_spikes_1d_ = []
n_spikes_1d = []

for p in range(len(peaks_1d_clean)-1):
    # print(pseudo_sweep_concatenated[peaks_1d_clean[p]])
    if pseudo_sweep_concatenated[peaks_1d_clean[p]] == pseudo_sweep_concatenated[peaks_1d_clean[p+1]]: # Check both spikes are in the same sweep
        interspike_tmp = peaks_1d_clean[p+1] - peaks_1d_clean[p]
        interspike_tmp_ms = interspike_tmp * dt_1
        interspike_1d_clean.append(interspike_tmp_ms)

print(len(interspike_1d_clean))

# %% [markdown]
# ### 2.3 | Find interspike interval
# 
# As we have mentioned before, in some cases the protocol has a gap between sweeps. This means we can't directly use the timepoints from the concatenated trace to calculate ISIs, we have to either run `find_peaks()`on a sweep-by-sweep basis, or re-assign the peak indices to the corresponding sweeps before calculating the interspike intervals.
# 
# Below are the parameters we have already computed:

# %%
# Concatenated sweep and pseudo-sweep
sweep_IB_1_concatenated
pseudo_sweep_concatenated

# Seal Resistance
Rseal_data_frame
seal_resistance

# Detected peaks after QC
peaks_1d_clean

# Denoised + baselined spikes, average spike, and onset, end, length, and onset to peak.
cut_spikes_baselined_clean
average_spike_clean
spike_onset
spike_end
spike_length
spike_onset_to_peak

# Number of detected spikes and firing rate
n_spikes_1d
time_recording_1d
firing_frequency_1d
neuron_id

# %% [markdown]
# We will use the pseudo_sweep to make sure we only calculate the interspike intervals between the spikes of the same sweep.

# %%
print(len(sweep_IB_1_concatenated))
print(len(pseudo_sweep_concatenated))
print(len(np.array(channels_data_frame_1.at['Channel B', '30'])))

print(pseudo_sweep_concatenated[123749])
print(pseudo_sweep_concatenated[123750])


# %%
interspike_1d_clean = []

for p in range(len(peaks_1d_clean)-1):
    # print(pseudo_sweep_concatenated[peaks_1d_clean[p]])
    if pseudo_sweep_concatenated[peaks_1d_clean[p]] == pseudo_sweep_concatenated[peaks_1d_clean[p+1]]: # Check both spikes are in the same sweep):
        interspike_tmp = peaks_1d_clean[p+1] - peaks_1d_clean[p]
        interspike_tmp_ms = interspike_tmp * dt_1
        interspike_1d_clean.append(interspike_tmp_ms)

print(len(interspike_1d_clean))

# %% [markdown]
# Let's check that the difference between the number of peaks and interspike intervals matches the number of sweeps in the recording

# %%
print(len(interspike_1d_clean))
print(len(peaks_1d_clean))
print(len(peaks_1d_clean) - len(interspike_1d_clean))
print(len(np.array(channels_data_frame_1.loc['Channel B', :])))


# %%
plt.hist(interspike_1d_clean, bins = 50, density = False, histtype = 'bar', log = False, color = 'k')
plt.title('Figure 2d: ISI of detected spikes', fontsize = 14)
plt.xlabel('Interspike Interval [ms]', fontsize = 12)
plt.xlim([0, None])
plt.show()

# %% [markdown]
# Now that we are sure we are not using any inaccurate ISI, we can check how using the ISI to get the instantaneous firing frequency to get an average of the firing frequency compares to the firing frequency obtained by dividing the total number of spikes detected over recording time.

# %%
instant_firing_frequency_1d = [((1/isi)*1000) for isi in interspike_1d_clean]
print(f'Average instantaneous firing rate: {round(np.mean(instant_firing_frequency_1d), 2)} Hz')
print(f'Firing rate: {round(firing_frequency_1d, 2)} Hz')

# %% [markdown]
# We can see that the instantaneous firing rate provides a higher value than the real one. This is expected as when using the ISI we are discarding the time of recording between the start of the sweep and the first spike, for every sweep. So we are effectually shortening the total length of recording and thus increasing the resulting firing rate.
# %% [markdown]
# ### 2.4 | Find holding current for each spike and plot it against ISI
# 
# Now that we have the interspike intervals, we can try to see whether the holding current (whatever the amplifier is injecting through the pipette) has an effect on the firing rate of the cell. We can examine this by plotting the average holding current between two spikes and the iterspike interval for that same pair of spikes. If there is an effect, we would expect a significant correlation when looking at all the data points.

# %%
holding_for_isi_1d_clean = []

for p in range(len(peaks_1d_clean)-1):
    # print(pseudo_sweep_concatenated[peaks_1d_clean[p]])
    if pseudo_sweep_concatenated[peaks_1d_clean[p]] == pseudo_sweep_concatenated[peaks_1d_clean[p+1]]: # Check both spikes are in the same sweep
        holding_tmp = np.mean(sweep_IB_1_concatenated[peaks_1d_clean[p]+50 : peaks_1d_clean[p+1]-50])
        # average 2 ms after first spike until 2 ms before second spike
        holding_for_isi_1d_clean.append(holding_tmp)

print(len(holding_for_isi_1d_clean))


# %%
get_ipython().run_line_magic('matplotlib', 'inline')
plt.scatter(interspike_1d_clean, holding_for_isi_1d_clean, label = f'Correlation = {np.round(np.corrcoef(interspike_1d_clean, holding_for_isi_1d_clean)[0,1], 2)}')
plt.title('Figure 2g: ISI vs Holding', fontsize = 14), plt.legend()
plt.xlabel('Interspike Interval [ms]', fontsize = 12), plt.ylabel('Holding current [pA]', fontsize = 12)
plt.show()