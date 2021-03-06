import os.path as op

import mne
from mne.parallel import parallel_func

from config import excludes, map_subjects, meg_dir, n_jobs


def run_evoked(subject, autoreject=True):
    if autoreject:
        epo_fname = op.join(meg_dir, subject,
                            f'{subject}_audvis-filt-sss-ar-epo.fif')
    else:
        epo_fname = op.join(meg_dir, subject,
                            f'{subject}_audvis-filt-sss-ar-epo.fif')
    evoked_fname = op.join(meg_dir, subject,
                           f'{subject}_audvis-filt-sss-ave.fif')
    epochs = mne.read_epochs(epo_fname, preload=True)

    # define evokeds
    evoked_al = epochs['Auditory/Left'].average()
    evoked_ar = epochs['Auditory/Right'].average()
    evoked_vl = epochs['Visual/Left'].average()
    evoked_vr = epochs['Visual/Right'].average()

    # define contrasts
    contrast_aud = mne.combine_evoked([evoked_al, -evoked_ar], 'equal')
    contrast_vis = mne.combine_evoked([evoked_vl, -evoked_vr], 'equal')

    # let's make trial-count-normalized ones for group statistics
    epochs_eq = epochs.copy().equalize_event_counts(
        ['Auditory/Left', 'Auditory/Right', 'Visual/Left', 'Visual/Right'])[0]
    evoked_al_eq = epochs_eq['Auditory/Left'].average()
    evoked_ar_eq = epochs_eq['Auditory/Right'].average()
    evoked_vl_eq = epochs_eq['Visual/Left'].average()
    evoked_vr_eq = epochs_eq['Visual/Right'].average()
    assert evoked_al_eq.nave == evoked_ar_eq.nave == evoked_vl_eq.nave
    assert evoked_al_eq.nave == evoked_vr_eq.nave

    # simplify comment
    evoked_al.comment = 'aud_left'
    evoked_ar.comment = 'aud_right'
    evoked_vl.comment = 'vis_left'
    evoked_vr.comment = 'vis_right'
    contrast_aud.comment = 'aud_left_minus_right'
    contrast_vis.comment = 'vis_left_minus_right'
    evoked_al_eq.comment = 'aud_left_eq'
    evoked_ar_eq.comment = 'aud_right_eq'
    evoked_vl_eq.comment = 'vis_left_eq'
    evoked_vr_eq.comment = 'vis_right_eq'

    mne.write_evokeds(evoked_fname, [
        evoked_al, evoked_ar, evoked_vl, evoked_vr, contrast_aud, contrast_vis,
        evoked_al_eq, evoked_ar_eq, evoked_vl_eq, evoked_vr_eq
    ])
    print(f'Created Evoked for {subject}')


parallel, run_func, _ = parallel_func(run_evoked, n_jobs=n_jobs)
subjects = [
    subject for subject in map_subjects.values() if subject not in excludes
]
parallel(run_func(subject) for subject in subjects)
