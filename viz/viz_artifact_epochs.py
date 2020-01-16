# import os
# os.chdir('../')
import os.path as op

import mne
from scripts.config import meg_dir

# for vs code interactive terminal
# get_ipython().run_line_magic('matplotlib', 'qt')


def show_ecg_evoked(subject):
    ecg_ave = mne.read_evokeds(op.join(meg_dir, f'{subject}_audvis-ecg-ave.fif'))
    for e in ecg_ave:
        e.plot_joint()


def show_eog_evoked(subject):
    eog_ave = mne.read_evokeds(op.join(meg_dir, f'{subject}_audvis-eog-ave.fif'))
    for e in eog_ave:
        e.plot_joint()


# NOTE: ECG components were not found in sample subject
# show_ecg_evoked('sample')
show_eog_evoked('sample')
