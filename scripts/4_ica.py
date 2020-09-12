import os.path as op

import mne
from autoreject import get_rejection_threshold
from mne.parallel import parallel_func

from config import excludes, map_subjects, meg_dir, n_jobs


def run_ica(subject):
    raw_fname = op.join(meg_dir, subject, f'{subject}_audvis-filt_raw_sss.fif')
    annot_fname = op.join(meg_dir, subject, f'{subject}_audvis-annot.fif')
    ica_name = op.join(meg_dir, subject, f'{subject}_audvis-ica.fif')

    raw = mne.io.read_raw_fif(raw_fname)
    if op.isfile(annot_fname):
        annot = mne.read_annotations(annot_fname)
        raw.set_annotations(annot)
    # Because the data were Maxwell filtered,
    # higher threshold would be reasonable.
    n_components = 0.999
    ica = mne.preprocessing.ICA(n_components=n_components)
    picks = mne.pick_types(raw.info,
                           meg=True,
                           eeg=False,
                           eog=True,
                           ecg=True,
                           stim=False)
    # use autoreject to find the rejection threshold to get better ICA results
    tstep = 1
    events = mne.make_fixed_length_events(raw, duration=tstep)
    # do not use baseline correction because autoreject (global) would be used
    even_epochs = mne.Epochs(raw, events, baseline=None, tmin=0, tmax=tstep)
    reject = get_rejection_threshold(even_epochs,
                                     ch_types=['mag', 'grad'],
                                     verbose=False)
    ica.fit(raw, picks=picks, reject=reject, tstep=tstep)
    ica.save(ica_name)
    print(f'Finished computing ICA for {subject}')


# Although only one subject in this tutorial,
# parallel processing for many subjects were demonstrated here.
# NOTE: since ICA consumes a huge amount of memory, it is recommended to
# decrease n_jobs for real data processing.
parallel, run_func, _ = parallel_func(run_ica, n_jobs=n_jobs)
subjects = [
    subject for subject in map_subjects.values() if subject not in excludes
]
parallel(run_func(subject) for subject in subjects)
