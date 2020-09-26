import os.path as op
import time
from datetime import timedelta
from functools import partial

import mne
import numpy as np
from mne.externals.h5io import write_hdf5
from scipy.stats import t

from config import (excludes, map_subjects, meg_dir, n_jobs, rst_dir, spacing,
                    subjects_dir)


# create a function for multiple attempts
def run_spatio_temporal_cluster_1samp_test(subjects,
                                           cond1,
                                           cond2,
                                           window_l,
                                           window_h,
                                           threshold=None,
                                           step_down_p=0,
                                           n_permutations=1024,
                                           n_jobs=1):
    t0 = time.time()
    contrasts = list()

    for subject in subjects:
        print(f'processing {subject}')
        # auditory
        fname_1 = op.join(
            meg_dir, subject,
            f'{subject}_audvis-dSPM-{spacing}-inverse-morph-filt-sss-{cond1}-stc'
        )
        # why `crop`: only deal with t > 0 to reduce multiple comparisons
        # why `T`: transpose to the correct shape
        stc_1 = mne.read_source_estimate(fname_1).magnitude().crop(
            window_l, window_h)

        # visual
        fname_2 = op.join(
            meg_dir, subject,
            f'{subject}_audvis-dSPM-{spacing}-inverse-morph-filt-sss-{cond2}-stc'
        )
        stc_2 = mne.read_source_estimate(fname_2).magnitude().crop(
            window_l, window_h)

        stc_diff = stc_1 - stc_2
        contrasts.append(stc_diff.data.T)

    # Get the right shape of difference data
    contrast_X = np.stack(contrasts, axis=0)
    # release memory
    del stc_1, stc_2, stc_diff, contrasts

    # prepare spatial adjacency
    fsaverage_src = mne.read_source_spaces(
        op.join(subjects_dir, 'fsaverage', 'bem',
                f'fsaverage-{spacing}-src.fif'))
    adjacency = mne.spatial_src_adjacency(fsaverage_src)

    # To use the "hat" adjustment method, sigma=1e-3 may be reasonable
    stat_fun = partial(mne.stats.ttest_1samp_no_p, sigma=1e-3)

    # Permutation test takes a long time to finish!
    t_obs, clusters, cluster_pv, H0 = \
        mne.stats.spatio_temporal_cluster_1samp_test(
            contrast_X,
            adjacency=adjacency,
            n_jobs=n_jobs,
            threshold=threshold,
            stat_fun=stat_fun,
            verbose=True)

    # save the result
    window = f'{int(window_l*1000)}_to_{int(window_h*1000)}'
    contrast_name = f'{cond1}_vs_{cond2}'
    cluster_name = op.join(rst_dir, f'{contrast_name}_{window}.h5')
    write_hdf5(cluster_name,
               dict(t_obs=t_obs,
                    clusters=clusters,
                    cluster_pv=cluster_pv,
                    H0=H0),
               title='mnepython',
               overwrite=True)
    elaped = time.time() - t0
    print(f'Save {cluster_name} after {timedelta(seconds=round(elaped))}')


subjects = [s for s in map_subjects.values() if s not in excludes]
# For demonstration purpose, the data are simultated to create 7 subjects
# NOTE: the simulation data takes approx. 10 G memory
subjects = subjects * 7

# use the "traditional" threshold:
p_threshold = 0.05
t_threshold = -t.ppf(p_threshold / 2., 7 - 1)

# use TFCE:
# threshold_tfce = dict(start=0, step=0.2)

# 0-200 ms
run_spatio_temporal_cluster_1samp_test(subjects,
                                       'aud_left_eq',
                                       'vis_left_eq',
                                       0,
                                       0.2,
                                       t_threshold,
                                       n_jobs=n_jobs)
