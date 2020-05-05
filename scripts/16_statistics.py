import os.path as op
from functools import partial

import mne
import numpy as np
from scipy import stats

from config import (excludes, map_subjects, meg_dir, n_jobs, rst_dir,
                    subjects_dir)

# prepare data
aud_l = list()
vis_l = list()

subjects = [s for s in map_subjects.values() if s not in excludes]
# For demonstration purpose, the data are simultated to create 7 subjects
subjects = subjects * 7
# NOTE: the simulation data takes approx. 10 G memory
for subject in subjects:
    print(f'processing {subject}')
    # auditory
    stc = mne.read_source_estimate(
        op.join(
            meg_dir, subject,
            f'{subject}_audvis-dSPM_inverse_morph-filt-sss-aud_left_eq-stc'))
    # why `crop`: only deal with t > 0 to reduce multiple comparisons
    # why `T`: transpose to the correct shape
    aud_l.append(stc.magnitude().crop(0, None).data.T)
    # visual
    stc = mne.read_source_estimate(
        op.join(
            meg_dir, subject,
            f'{subject}_audvis-dSPM_inverse_morph-filt-sss-vis_left_eq-stc'))
    vis_l.append(stc.magnitude().crop(0, None).data.T)

# Create contrast
contrast_X = np.array(aud_l, float) - np.array(vis_l, float)

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
