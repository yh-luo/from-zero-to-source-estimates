import os.path as op

import mne
from mne.parallel import parallel_func

from config import baseline, excludes, map_subjects, meg_dir, n_jobs


def run_covariance(subject, autoreject=True):
    if autoreject:
        epo_fname = op.join(meg_dir, subject,
                            f'{subject}_audvis-filt-sss-ar-epo.fif')
    else:
        epo_fname = op.join(meg_dir, subject,
                            f'{subject}_audvis-filt-sss-epo.fif')
    cov_fname = op.join(meg_dir, subject, f'{subject}_audvis-filt-sss-cov.fif')
    epochs = mne.read_epochs(epo_fname, preload=True)
    cov = mne.compute_covariance(epochs,
                                 tmin=baseline[0],
                                 tmax=baseline[1],
                                 method='shrunk')
    cov.save(cov_fname)

    print(f'Finished computing covariance for {subject}')


parallel, run_func, _ = parallel_func(run_covariance, n_jobs=n_jobs)
subjects = [
    subject for subject in map_subjects.values() if subject not in excludes
]
parallel(run_func(subject) for subject in subjects)
