import os.path as op

import mne
from scripts.config import meg_dir

def show_ecg_evoked(subject):
    ecg_ave = mne.read_evokeds(op.join(meg_dir, f'{subject}_audvis-ecg-ave.fif'))
    for e in ecg_ave:
        e.plot_joint()


def show_eog_evoked(subject):
    eog_ave = mne.read_evokeds(op.join(meg_dir, f'{subject}_audvis-eog-ave.fif'))
    for e in eog_ave:
        e.plot_joint()


show_ecg_evoked('sample')
show_eog_evoked('sample')
