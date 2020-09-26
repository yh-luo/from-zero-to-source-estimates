#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
os.chdir('../')
import os.path as op

import mne

from scripts.config import meg_dir

get_ipython().run_line_magic('matplotlib', 'qt')


# In[2]:


subject = 'sample'
raw_fname = op.join(meg_dir, subject, f'{subject}_audvis-filt_raw_sss.fif')
ica_fname = op.join(meg_dir, subject, f'{subject}_audvis-ica.fif')
raw = mne.io.read_raw_fif(raw_fname, preload=True)
ica = mne.preprocessing.read_ica(ica_fname)


# In[3]:


# plot estimated source and highlight the ECG-related components
# the indexes were printed by 05_epochs.py
ica.exclude += [3, 22]
ica.plot_sources(raw)


# In[4]:


# plot estimated source and highlight the EOG-related components
# the indexes were printed by 05_epochs.py
ica.exclude = []
ica.exclude += [2, 23]
ica.plot_sources(raw)


# In[5]:


# ECG components
ica.plot_components([3, 22])


# In[6]:


# EOG components
ica.plot_components([2, 23])

