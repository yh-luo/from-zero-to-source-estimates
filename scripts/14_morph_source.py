import os.path as op

import mne
from mne.parallel import parallel_func

from config import (excludes, map_subjects, meg_dir, n_jobs, smooth, spacing,
                    subjects_dir)

src = mne.read_source_spaces(
    op.join(subjects_dir, 'fsaverage', 'bem', 'fsaverage-5-src.fif'))
fsave_vertices = [s['vertno'] for s in src]


def morph_stc(subject):
    for condition in [
            'aud_left_minus_right', 'vis_left_minus_right', 'aud_left_eq',
            'aud_right_eq', 'vis_left_eq', 'vis_right_eq'
    ]:
        stc = mne.read_source_estimate(
            op.join(
                meg_dir, subject,
                f'{subject}_audvis-dSPM-{spacing}-inverse-filt-sss-{condition}'
            ))
        morphed_fname = op.join(
            meg_dir, subject,
            f'{subject}_audvis-dSPM-{spacing}-inverse-morph-filt-sss-{condition}'
        )
        morphed = mne.compute_source_morph(stc,
                                           subject_from=subject,
                                           subject_to='fsaverage',
                                           subjects_dir=subjects_dir,
                                           spacing=fsave_vertices,
                                           smooth=smooth,
                                           verbose='error').apply(stc)
        morphed.save(morphed_fname)
    print(f'Saved morphed source estimates for {subject}')


parallel, run_func, _ = parallel_func(morph_stc, n_jobs=n_jobs)
subjects = [
    subject for subject in map_subjects.values() if subject not in excludes
]
parallel(run_func(subject) for subject in subjects)
