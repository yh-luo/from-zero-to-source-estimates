import os.path as op
from functools import partial

import mne
import numpy as np
from scipy import stats

from config import (excludes, map_subjects, meg_dir, n_jobs, rst_dir, spacing,
                    subjects_dir)

# prepare data container
contrasts = list()

subjects = [s for s in map_subjects.values() if s not in excludes]
# For demonstration purpose, the data are simultated to create 7 subjects
subjects = subjects * 7
cond1 = 'aud_left_eq'
cond2 = 'vis_left_eq'
# NOTE: the simulation data takes approx. 10 G memory
for subject in subjects:
    print(f'processing {subject}')
    # auditory
    fname_1 = op.join(
        meg_dir, subject,
        f'{subject}_audvis-dSPM-{spacing}-inverse-morph-filt-sss-{cond1}-stc')
    # why `crop`: only deal with t > 0 to reduce multiple comparisons
    # why `T`: transpose to the correct shape
    stc_1 = mne.read_source_estimate(fname_1).magnitude().crop(0, None)

    # visual
    fname_2 = op.join(
        meg_dir, subject,
        f'{subject}_audvis-dSPM-{spacing}-inverse-morph-filt-sss-{cond2}-stc')
    stc_2 = mne.read_source_estimate(fname_2).magnitude().crop(0, None)

    stc_diff = stc_1 - stc_2
    contrasts.append(stc_diff.data.T)

# Get the right shape of difference data
contrast_X = np.stack(contrasts, axis=0)
# release memory
del stc_1, stc_2, stc_diff, contrasts

# prepare spatial connectivity
fsaverage_src = mne.read_source_spaces(
    op.join(subjects_dir, 'fsaverage', 'bem', 'fsaverage-5-src.fif'))
connectivity = mne.spatial_src_connectivity(fsaverage_src)

n_subjects = len(contrast_X)
# set the threshold quite high to reduce computation
# 0.05 is more practical
p_threshold = 0.001
t_threshold = -stats.distributions.t.ppf(p_threshold / 2., n_subjects - 1)
# To use TFCE, set threshold=threshold_tfce
# threshold_tfce = dict(start=0, step=0.2)

# To use the "hat" adjustment method, sigma=1e-3 may be reasonable
stat_fun = partial(mne.stats.ttest_1samp_no_p, sigma=1e-3)

# Permutation test takes a long time to finish!
t_obs, clusters, cluster_pv, H0 = mne.stats.spatio_temporal_cluster_1samp_test(
    contrast_X,
    connectivity=connectivity,
    n_jobs=n_jobs,
    threshold=t_threshold,
    stat_fun=stat_fun,
    step_down_p=0.05,
    verbose=True)

# save the result
window = '0_to_None'
contrast_name = 'left_auditory_vs_visual'
cluster_name = op.join(rst_dir, f'{contrast_name}_{window}.npz')
np.savez(cluster_name,
         t_obs=t_obs,
         clusters=clusters,
         cluster_pv=cluster_pv,
         H0=H0)
