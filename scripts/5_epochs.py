import os.path as op

import mne
from autoreject import get_rejection_threshold
from mne.parallel import parallel_func

from config import (baseline, event_id, excludes, map_subjects, meg_dir,
                    n_jobs, n_max_ecg, n_max_eog, reject_tmax, tmax, tmin)


def run_epochs(subject):
    raw_fname = op.join(meg_dir, subject, f'{subject}_audvis-filt_raw_sss.fif')
    annot_fname = op.join(meg_dir, subject, f'{subject}_audvis-annot.fif')
    raw = mne.io.read_raw_fif(raw_fname, preload=True, verbose='error')
    ica_fname = op.join(meg_dir, subject, f'{subject}_audvis-ica.fif')
    ica_outname = op.join(meg_dir, subject,
                          f'{subject}_audvis-applied-ica.fif')
    annot = mne.read_annotations(annot_fname)
    raw.set_annotations(annot)
    # extract events
    # modify stim_channel for your need
    events = mne.find_events(raw, stim_channel="STI 014", verbose='error')

    picks = mne.pick_types(raw.info,
                           meg=True,
                           eog=True,
                           ecg=True,
                           stim=False,
                           exclude=['bads'])
    epochs = mne.Epochs(raw,
                        events=events,
                        picks=picks,
                        event_id=event_id,
                        tmin=tmin,
                        tmax=tmax,
                        baseline=baseline,
                        preload=False,
                        reject_tmax=reject_tmax,
                        reject_by_annotation=True,
                        verbose='error')

    # ICA
    ica = mne.preprocessing.read_ica(ica_fname)
    try:
        # ECG
        ecg_epochs = mne.preprocessing.create_ecg_epochs(raw,
                                                         baseline=(None, None),
                                                         preload=True,
                                                         verbose='error')
        ecg_inds, scores_ecg = ica.find_bads_ecg(ecg_epochs,
                                                 method='ctps',
                                                 threshold=0.21,
                                                 verbose='error')
    except ValueError:
        pass
    else:
        print(f'Found {len(ecg_inds)} ECG indices for {subject}')
        if len(ecg_inds) != 0:
            ica.exclude.extend(ecg_inds[:n_max_ecg])
            # for future inspection
            ecg_epochs.average().save(
                op.join(meg_dir, subject, f'{subject}_audvis-ecg-ave.fif'))
        del ecg_epochs, ecg_inds, scores_ecg  # release memory

    try:
        # EOG
        eog_epochs = mne.preprocessing.create_eog_epochs(raw,
                                                         baseline=(None, None),
                                                         preload=True,
                                                         verbose='error')
        eog_inds, scores_eog = ica.find_bads_eog(eog_epochs, verbose='error')
    except ValueError:
        pass
    else:
        print(f'Found {len(eog_inds)} EOG indices for {subject}')
        if len(eog_inds) != 0:
            ica.exclude.extend(eog_inds[:n_max_eog])
            # for future inspection
            eog_epochs.average().save(
                op.join(meg_dir, subject, f'{subject}_audvis-eog-ave.fif'))
            del eog_epochs, eog_inds, scores_eog  # release memory

    del raw  # to release memory

    ica.save(ica_outname)
    epochs.load_data()
    ica.apply(epochs)

    reject = get_rejection_threshold(epochs, ch_types=['mag', 'grad'])
    epochs.drop_bad(reject=reject, verbose='error')
    print(
        '\n',
        f"Dropped {subject}'s {round(epochs.drop_log_stats(), 1)}% of epochs",
        '\n')
    epochs.save(op.join(meg_dir, subject,
                        f'{subject}_audvis-filt-sss-epo.fif'),
                overwrite=True)


parallel, run_func, _ = parallel_func(run_epochs, n_jobs=n_jobs)
subjects = [
    subject for subject in map_subjects.values() if subject not in excludes
]
parallel(run_func(subject) for subject in subjects)
