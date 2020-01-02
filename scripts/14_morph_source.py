import mne
import os.path as op
import numpy as np
from mne.parallel import parallel_func

from config import meg_dir, subjects_dir, map_subjects, n_jobs, smooth, excludes

src = mne.read_source_spaces(
    op.join(subjects_dir, 'fsaverage', 'bem', 'fsaverage-5-src.fif'))
fsave_vertices = [s['vertno'] for s in src]


def morph_stc(subject):
    for condition in [
            'aud_left_minus_right', 'vis_left_minus_right', 'aud_left_eq',
            'aud_right_eq', 'vis_left_eq', 'vis_right_eq'
    ]:
        stc = mne.read_source_estimate(
            op.join(meg_dir, f'{subject}_audvis-dSPM_inverse-filt-sss-{condition}'))

        morphed = mne.compute_source_morph(stc,
                                           subject_from=subject,
                                           subject_to='fsaverage',
                                           subjects_dir=subjects_dir,
                                           spacing=fsave_vertices,
                                           smooth=smooth,
                                           verbose='error').apply(stc)
        morphed.save(
            op.join(meg_dir,
                    f'{subject}_audvis-dSPM_inverse_morph-filt-sss-{condition}'))
    print(f'Saved morphed source estimates for {subject}')


parallel, run_func, _ = parallel_func(morph_stc, n_jobs=n_jobs)
subjects = [
    subject for subject in map_subjects.values() if subject not in excludes
]
parallel(run_func(subject) for subject in subjects)
