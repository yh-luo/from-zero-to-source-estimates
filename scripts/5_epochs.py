import mne
import os.path as op
from mne.parallel import parallel_func
from autoreject import get_rejection_threshold
from config import meg_dir, map_subjects, reject_tmax, event_id, tmin, tmax, baseline, n_max_ecg, n_max_eog, n_jobs, excludes


def run_epochs(subject):
    raw_fname = op.join(meg_dir, f'{subject}_audvis-filt_raw_sss.fif')
    raw = mne.io.read_raw_fif(raw_fname, preload=True, verbose='error')
    
    # extract events
    # modify stim_channel for your need
    events = mne.find_events(raw,
                            stim_channel="STI 014",
                            verbose='error')

    picks = mne.pick_types(raw.info,
                           meg=True,
                           eog=True,
                           ecg=True,
                           stim=False,
                           exclude=['bads'])
    epochs = mne.Epochs(
        raw,
        events=events,
        picks=picks,
        event_id=event_id,
        tmin=tmin,
        tmax=tmax,
        baseline=baseline,
        decim=5,  # downsample to 400Hz (2000/5)
        preload=False,
        reject_tmax=reject_tmax,
        verbose='error')

    # ICA
    ica_fname = op.join(meg_dir, f'{subject}_audvis-ica.fif')
    ica_outname = op.join(meg_dir,
                               f'{subject}_audvis-applied-ica.fif')
    ica = mne.preprocessing.read_ica(ica_fname)
    ica.exclude = []
    try:
        # ECG
        ecg_epochs = mne.preprocessing.create_ecg_epochs(raw,
                                                         tmin=-.3,
                                                         tmax=.3,
                                                         preload=False,
                                                         verbose='error')
        ecg_epochs.decimate(5)
        ecg_epochs.load_data()
        ecg_epochs.apply_baseline((None, None))
        ecg_inds, scores_ecg = ica.find_bads_ecg(ecg_epochs,
                                                 method='ctps',
                                                 threshold=0.8,
                                                 verbose='error')
    except ValueError:
        pass
    else:
        print(f'Found {len(ecg_inds)} ECG indices for {subject}')
        if len(ecg_inds) != 0:
            if len(ecg_inds) > n_max_ecg:
                ica.exclude.extend(ecg_inds[:n_max_ecg])
            else:
                ica.exclude.extend(ecg_inds[:len(ecg_inds)])
            # for future inspection
            ecg_epochs.average().save(
                op.join(meg_dir, f'{subject}_audvis-ecg-ave.fif'))
            del ecg_epochs, ecg_inds, scores_ecg  # release memory

    try:
        # EOG
        eog_epochs = mne.preprocessing.create_eog_epochs(raw,
                                                         tmin=-.3,
                                                         tmax=.3,
                                                         preload=False,
                                                         verbose='error')
        eog_epochs.decimate(5)
        eog_epochs.load_data()
        eog_epochs.apply_baseline((None, None))
        eog_inds, scores_eog = ica.find_bads_eog(eog_epochs, verbose='error')
    except ValueError:
        pass
    else:
        print(f'Found {len(eog_inds)} EOG indices for {subject}')
        if len(eog_inds) != 0:
            if len(eog_inds) > n_max_eog:
                ica.exclude.extend(eog_inds[:n_max_eog])
            else:
                ica.exclude.extend(eog_inds[:len(eog_inds)])
            # for future inspection
            eog_epochs.average().save(
                op.join(meg_dir, f'{subject}_audvis-eog-ave.fif'))
            del eog_epochs, eog_inds, scores_eog  # release memory

    del raw  # to release memory

    ica.save(ica_outname)
    epochs.load_data()
    ica.apply(epochs)

    reject = get_rejection_threshold(epochs.copy().crop(None, reject_tmax))
    epochs.drop_bad(reject=reject, verbose='error')
    print(
        f'    Dropped {round(epochs.drop_log_stats(), 1)}% of epochs for {subject}'
    )
    epochs.save(op.join(meg_dir, f'{subject}_audvis-filt-sss-epo.fif'),
                overwrite=True)


parallel, run_func, _ = parallel_func(run_epochs, n_jobs=n_jobs)
subjects = [
    subject for subject in map_subjects.values() if subject not in excludes
]
parallel(run_func(subject) for subject in subjects)
