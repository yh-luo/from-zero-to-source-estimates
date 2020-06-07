#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
os.chdir('../')
import os.path as op
import mne

from scripts.config import baseline, meg_dir, subjects_dir

get_ipython().run_line_magic('matplotlib', 'qt')


# In[2]:


evokeds = mne.read_evokeds(op.join(meg_dir, 'grand_average-ave.fif'))

# Baseline correction
for evoked in evokeds:
    evoked.apply_baseline(baseline=baseline)

mapping = {
    'aud_left': evokeds[0],
    'aud_right': evokeds[1],
    'vis_left': evokeds[2],
    'vis_right': evokeds[3]
}
# to show it
get_ipython().run_line_magic('matplotlib', 'inline')
mne.viz.plot_compare_evokeds(mapping)
get_ipython().run_line_magic('matplotlib', 'qt')


# In[3]:


# Source space contrast
os.environ["SUBJECTS_DIR"] = subjects_dir
stc_aud = mne.read_source_estimate(
    op.join(meg_dir, 'aud_left_minus_right-grand_average-ave-stc'))

# mayavi provides better visualization
# stc_aud.plot(hemi='lh', initial_time=0.1)
stc_aud.magnitude().plot(hemi='lh', initial_time=0.1, backend='matplotlib')


# In[4]:


stc_vis = mne.read_source_estimate(
    op.join(meg_dir, 'vis_left_minus_right-grand_average-ave-stc'))
stc_vis.magnitude().plot(hemi='lh', initial_time=0.1, backend='matplotlib')

