import mne
import numpy as np
from scipy import stats
import os.path as op
import pickle
from functools import partial
from config import meg_dir, subjects_dir, rst_dir, map_subjects, reject_tmax, n_jobs, excludes

# prepare data
aud_l = list()
vis_l = list()

subjects = [s for s in map_subjects.values() if s not in excludes]
# For demonstration purpose, the data are simultated to create 5 subjects
subjects = subjects * 5
for subject in subjects:
    print(f'processing {subject}')
    # auditory
    stc = mne.read_source_estimate(
        op.join(meg_dir,
                f'{subject}_audvis-dSPM_inverse_morph-filt-sss-aud_left_eq-stc'))
    # why `crop`: only deal with 0 < t < 0.2 to reduce multiple comparisons
    # why `T`: transpose to the correct shape
    aud_l.append(stc.magnitude().crop(0, 0.2).data.T)
    # visual
    stc = mne.read_source_estimate(
        op.join(meg_dir,
                f'{subject}_audvis-dSPM_inverse_morph-filt-sss-vis_left_eq-stc'))
    vis_l.append(stc.magnitude().crop(0, 0.2).data.T)

# Create contrast
contrast_X = np.array(aud_l, float) - np.array(vis_l, float)

# prepare spatial connectivity
fsaverage_src = mne.read_source_spaces(
    op.join(subjects_dir, 'fsaverage', 'bem', 'fsaverage-5-src.fif'))
connectivity = mne.spatial_src_connectivity(fsaverage_src)

# use TFCE
n_subjects = len(contrast_X)
p_threshold = 0.05
t_threshold = -stats.distributions.t.ppf(p_threshold / 2., n_subjects - 1)

# To use the “hat” adjustment method, a value of sigma=1e-3 may be a reasonable choice.
stat_fun = partial(mne.stats.ttest_1samp_no_p, sigma=1e-3)
# set the threshold quite high to reduce computation
p_threshold = 0.001
# To use TFCE, set threshold=threshold_tfce
# threshold_tfce = dict(start=0, step=0.2)

# Permutation test takes a long time to finish!
T_obs, clusters, cluster_p_values, H0 = clu = \
    mne.stats.spatio_temporal_cluster_1samp_test(contrast_X, connectivity=connectivity,
        n_jobs=n_jobs, threshold=p_threshold, stat_fun=stat_fun, buffer_size=None, step_down_p=0.05,
        verbose=True)

# save the result
window = '0_to_200'
contrast_name = 'left_auditory_vs_visual'
cluster_name = op.join(rst_dir, f'spatio_temporal_cluster_{contrast_name}_{window}.cluster')
cluster_result = dict(T_obs=T_obs,
                      clusters=clusters,
                      cluster_p_values=cluster_p_values,
                      H0=H0,
                      clu=clu)

with open(cluster_name, 'wb') as f:
    pickle.dump(cluster_result, f)
