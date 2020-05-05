import os.path as op

import mne
from mne.parallel import parallel_func

from config import excludes, map_subjects, meg_dir, n_jobs


def run_ica(subject):
    raw_fname = op.join(meg_dir, f'{subject}_audvis-filt_raw_sss.fif')
    raw = mne.io.read_raw_fif(raw_fname)

    # Because the data were Maxwell filtered,
    # higher threshold would be reasonable.
    n_components = 0.999
    ica_name = op.join(meg_dir, subject, f'{subject}_audvis-ica.fif')
    ica = mne.preprocessing.ICA(n_components=n_components, max_iter=400)
    # Only remove ECG artifacts for now
    picks = mne.pick_types(raw.info,
                           meg=True,
                           eeg=False,
                           eog=False,
                           stim=False,
                           exclude='bads')
    ica.fit(raw,
            picks=picks,
            reject=dict(grad=4000e-13, mag=4e-12),
            verbose='error')
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
