import os.path as op

import mne

from config import cal, ctc, h_freq, l_freq, meg_dir, n_jobs


def run_maxwell_filter(subject):
    raw_fname = op.join(meg_dir, subject, f'{subject}_audvis_raw.fif')
    sss_fname = op.join(meg_dir, subject, f'{subject}_audvis_raw_sss.fif')

    raw = mne.io.read_raw_fif(raw_fname, verbose='error')
    # remove bad channels
    raw.info['bads'].extend(['MEG 1032', 'MEG 2313'])
    raw_sss = mne.preprocessing.maxwell_filter(raw,
                                               calibration=cal,
                                               cross_talk=ctc)
    raw_sss.save(sss_fname)


def run_filter(subject):
    raw_fname = op.join(meg_dir, subject, f'{subject}_audvis_raw_sss.fif')
    out_fname = op.join(meg_dir, subject, f'{subject}_audvis-filt_raw_sss.fif')

    raw = mne.io.read_raw_fif(raw_fname, preload=True, verbose='error')
    # Band-pass MEG data
    raw.filter(l_freq, h_freq, n_jobs=n_jobs)
    # High-pass EOG for ICA
    picks_eog = mne.pick_types(raw.info, meg=False, eog=True)
    raw.filter(1, None, picks=picks_eog, fir_window='hann', n_jobs=n_jobs)
    raw.save(out_fname, overwrite=True)

    print(f'Finished filtering data for {subject}')


run_maxwell_filter('sample')
run_filter('sample')
