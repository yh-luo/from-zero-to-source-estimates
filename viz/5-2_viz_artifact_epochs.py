#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
os.chdir('../')
import os.path as op

import mne
from scripts.config import meg_dir

get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


def show_ecg_evoked(subject):
    ecg_ave = mne.read_evokeds(op.join(meg_dir, subject, f'{subject}_audvis-ecg-ave.fif'))
    for e in ecg_ave:
        e.plot_joint()


def show_eog_evoked(subject):
    eog_ave = mne.read_evokeds(op.join(meg_dir, subject, f'{subject}_audvis-eog-ave.fif'))
    for e in eog_ave:
        e.plot_joint()


# In[3]:


show_ecg_evoked('sample')


# In[4]:


show_eog_evoked('sample')

