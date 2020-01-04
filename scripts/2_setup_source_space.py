import os
import os.path as op
import shutil

import mne

from config import spacing, subjects_dir


def process_subject_source_space(subject):
    # make BEMs using watershed bem
    # NOTE: Use MNE version >= 20!
    mne.bem.make_watershed_bem(subject,
                               subjects_dir=subjects_dir,
                               show=False,
                               verbose=False,
                               overwrite=True)

    bem_surf_fname = op.join(subjects_dir, subject, "bem",
                             f"{subject}-ico4-bem.fif")
    bem_sol_fname = op.join(subjects_dir, subject, "bem",
                            f"{subject}-ico4-bem-sol.fif")
    src_fname = op.join(subjects_dir, subject, "bem",
                        f"{subject}-{spacing}-src.fif")

    # make BEM models
    # ico4 is for downsamping
    bem_surf = mne.make_bem_model(
        subject,
        ico=4,
        conductivity=[0.3],  # for MEG data, 1 layer model is enough
        subjects_dir=subjects_dir)
    mne.write_bem_surfaces(bem_surf_fname, bem_surf)
    # make BEM solution
    bem_sol = mne.make_bem_solution(bem_surf)
    mne.write_bem_solution(bem_sol_fname, bem_sol)

    # Create the surface source space
    src = mne.setup_source_space(subject, spacing, subjects_dir=subjects_dir)
    mne.write_source_spaces(src_fname, src, overwrite=True)


process_subject_source_space('subject_a')

# Create source space for fsaverage
# If you use precomputed reconstruction, you don't need to remove the symbolic
# link of fsaverage.
precomputed = True

fsaverage_src_dir = op.join(os.environ['FREESURFER_HOME'], 'subjects',
                            'fsaverage')
fsaverage_dst_dir = op.join(subjects_dir, 'fsaverage')

if not precomputed:
    os.unlink(fsaverage_dst_dir)  # remove symlink
shutil.copytree(fsaverage_src_dir, fsaverage_dst_dir)

fsaverage_bem = op.join(fsaverage_dst_dir, 'bem')
if not op.isdir(fsaverage_bem):
    os.mkdir(fsaverage_bem)

fsaverage_src = op.join(fsaverage_bem, 'fsaverage-5-src.fif')
src = mne.setup_source_space('fsaverage', 'ico5', subjects_dir=subjects_dir)
mne.write_source_spaces(fsaverage_src, src)
