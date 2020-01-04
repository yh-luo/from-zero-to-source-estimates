import os.path as op

import mne
from mne.parallel import parallel_func

from config import (excludes, map_subjects, meg_dir, mindist, n_jobs, spacing,
                    subjects_dir)


def run_forward(subject):
    evoked_fname = op.join(meg_dir, f'{subject}_audvis-filt-sss-ave.fif')
    fwd_fname = op.join(meg_dir, f'{subject}_audvis-{spacing}-fwd.fif')
    # If coregistration was done manually, change it to the file name
    # If use the provided trans file from sample dataset, remember to put the trans file in MEG/
    trans_fname = op.join(meg_dir, f'{subject}_audvis_raw-trans.fif')

    # If you follow the step in 2_setup_source_space.py
    # src_fname = op.join(subjects_dir, subject, 'bem',
    #                     f'{subject}-{spacing}-src.fif')
    # bem_fname = op.join(subjects_dir, subject, 'bem',
    #                          f'{subject}_audvis-ico4-bem-sol.fif')

    # If you are practicing with the sample dataset
    src_fname = op.join(subjects_dir, subject, 'bem',
                        f'{subject}-oct-6-src.fif')
    bem_fname = op.join(subjects_dir, subject, 'bem',
                        f'{subject}-5120-5120-5120-bem-sol.fif')

    info = mne.io.read_info(evoked_fname)
    fwd = mne.make_forward_solution(info,
                                    trans_fname,
                                    src_fname,
                                    bem_fname,
                                    meg=True,
                                    eeg=False,
                                    mindist=mindist,
                                    verbose='error')
    mne.write_forward_solution(fwd_fname, fwd, overwrite=True)
    print(f'Computed forward solution for {subject}')


parallel, run_func, _ = parallel_func(run_forward, n_jobs=n_jobs)
subjects = [
    subject for subject in map_subjects.values() if subject not in excludes
]
parallel(run_func(subject) for subject in subjects)
