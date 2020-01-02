import mne
import os.path as op
from mne.parallel import parallel_func

from config import meg_dir, subjects_dir, map_subjects, spacing, mindist, n_jobs, excludes

snr = 3.0
lambda2 = 1.0 / snr**2


def run_inverse(subject):
    evoked_fname = op.join(meg_dir, f'{subject}_audvis-filt-sss-ave.fif')
    cov_fname = op.join(meg_dir, f'{subject}_audvis-filt-sss-cov.fif')
    fwd_fname = op.join(meg_dir, f'{subject}_audvis-{spacing}-fwd.fif')
    inv_fname = op.join(meg_dir, f'{subject}_audvis-{spacing}-inv.fif')

    evokeds = mne.read_evokeds(evoked_fname,
                               condition=[
                                   'aud_left', 'aud_right', 'vis_left',
                                   'vis_right', 'aud_left_minus_right',
                                   'vis_left_minus_right', 'aud_left_eq',
                                   'aud_right_eq', 'vis_left_eq',
                                   'vis_right_eq'
                               ],
                               verbose='error')
    cov = mne.read_cov(cov_fname, verbose='error')
    fwd = mne.read_forward_solution(fwd_fname, verbose='error')
    info = evokeds[0].info
    inverse_operator = mne.minimum_norm.make_inverse_operator(info,
                                                              fwd,
                                                              cov,
                                                              verbose='error')
    mne.minimum_norm.write_inverse_operator(inv_fname, inverse_operator)

    for evoked in evokeds:
        stc = mne.minimum_norm.apply_inverse(evoked,
                                             inverse_operator,
                                             lambda2,
                                             'dSPM',
                                             pick_ori='vector',
                                             verbose='error')
        stc.save(
            op.join(
                meg_dir,
                f'{subject}_audvis-dSPM_inverse-filt-sss-{evoked.comment}'))
    print(f'Saved source estimates for {subject}')


parallel, run_func, _ = parallel_func(run_inverse, n_jobs=n_jobs)
subjects = [
    subject for subject in map_subjects.values() if subject not in excludes
]
parallel(run_func(subject) for subject in subjects)
