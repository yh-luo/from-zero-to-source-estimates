import os.path as op

import mne
from autoreject import AutoReject

from config import (baseline, event_id, excludes, map_subjects,
                    meg_dir, n_jobs, n_max_ecg, n_max_eog, reject_tmax, tmax,
                    tmin)


def run_epochs(subject, autoreject=True):
    raw_fname = op.join(meg_dir, subject, f'{subject}_audvis-filt_raw_sss.fif')
    annot_fname = op.join(meg_dir, subject, f'{subject}_audvis-annot.fif')
    raw = mne.io.read_raw_fif(raw_fname, preload=False)
    annot = mne.read_annotations(annot_fname)
    raw.set_annotations(annot)
    if autoreject:
        epo_fname = op.join(meg_dir, subject,
                            f'{subject}_audvis-filt-sss-ar-epo.fif')
    else:
        epo_fname = op.join(meg_dir, subject,
                            f'{subject}_audvis-filt-sss-epo.fif')
    # ICA
    ica_fname = op.join(meg_dir, subject, f'{subject}_audvis-ica.fif')
    ica = mne.preprocessing.read_ica(ica_fname)

    # ICA
    ica = mne.preprocessing.read_ica(ica_fname)
    try:
        # ECG
        ecg_epochs = mne.preprocessing.create_ecg_epochs(raw,
                                                         l_freq=10,
                                                         h_freq=20,
                                                         baseline=(None, None),
                                                         preload=True)
        ecg_inds, scores_ecg = ica.find_bads_ecg(ecg_epochs,
                                                 method='ctps',
                                                 threshold='auto',
                                                 verbose='INFO')
    except ValueError:
        # not found
        pass
    else:
        print(f'Found {len(ecg_inds)} ({ecg_inds}) ECG indices for {subject}')
        if len(ecg_inds) != 0:
            ica.exclude.extend(ecg_inds[:n_max_ecg])
            # for future inspection
            ecg_epochs.average().save(
                op.join(meg_dir, subject, f'{subject}_audvis-ecg-ave.fif'))
        # release memory
        del ecg_epochs, ecg_inds, scores_ecg

    try:
        # EOG
        eog_epochs = mne.preprocessing.create_eog_epochs(raw,
                                                         baseline=(None, None),
                                                         preload=True)
        eog_inds, scores_eog = ica.find_bads_eog(eog_epochs)
    except ValueError:
        # not found
        pass
    else:
        print(f'Found {len(eog_inds)} ({eog_inds}) EOG indices for {subject}')
        if len(eog_inds) != 0:
            ica.exclude.extend(eog_inds[:n_max_eog])
            # for future inspection
            eog_epochs.average().save(
                op.join(meg_dir, subject, f'{subject}_audvis-eog-ave.fif'))
            del eog_epochs, eog_inds, scores_eog  # release memory

    # applying ICA on Raw
    raw.load_data()
    ica.apply(raw)

    # extract events for epoching
    # modify stim_channel for your need
    events = mne.find_events(raw, stim_channel="STI 014")
    picks = mne.pick_types(raw.info, meg=True)
    epochs = mne.Epochs(
        raw,
        events=events,
        picks=picks,
        event_id=event_id,
        tmin=tmin,
        tmax=tmax,
        baseline=baseline,
        decim=4,  # raw sampling rate is 600 Hz, subsample to 150 Hz
        preload=True,  # for autoreject
        reject_tmax=reject_tmax,
        reject_by_annotation=True)
    del raw, annot

    # autoreject (local)
    if autoreject:
        # local reject
        # keep the bad sensors/channels because autoreject can repair it via
        # interpolation
        picks = mne.pick_types(epochs.info, meg=True, exclude=[])
        ar = AutoReject(picks=picks, n_jobs=n_jobs, verbose=False)
        print(f'Run autoreject (local) for {subject} (it takes a long time)')
        ar.fit(epochs)
        print(f'Drop bad epochs and interpolate bad sensors for {subject}')
        epochs = ar.transform(epochs)

    print(f'Dropped {round(epochs.drop_log_stats(), 2)}% epochs for {subject}')
    epochs.save(epo_fname, overwrite=True)


for subject in map_subjects.values():
    if subject not in excludes:
        run_epochs(subject)
