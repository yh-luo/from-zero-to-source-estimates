import mne
import pickle
import os.path as op
import numpy as np

from mayavi import mlab
# in case jupyter kernel starts on the study directory
from scripts.config import meg_dir, rst_dir, subjects_dir
get_ipython().run_line_magic('gui', 'qt')

# change the name to interested cluster result
clu_fname = op.join(rst_dir, 'spatio_temporal_cluster_left_auditory_vs_visual_0_to_200.cluster')

# prepare spatial connectivity
fsaverage_src = mne.read_source_spaces(op.join(subjects_dir, 'fsaverage', 'bem', 'fsaverage-5-src.fif'))
fsaverage_vertices = [s['vertno'] for s in fsaverage_src]

# get info
info_data = mne.read_source_estimate(op.join(meg_dir, 'sample_audvis-dSPM_inverse_morph-filt-sss-aud_left_eq'))
tstep = info_data.tstep

with open(clu_fname, 'rb') as f:
    cluster_result = pickle.load(f)

good_cluster_inds = np.where(cluster_result['cluster_p_values'] < 0.05)

# QQ
stc_all_cluster_vis = mne.stats.summarize_clusters_stc(
    cluster_result['clu'], tstep=tstep, vertices=fsaverage_vertices, subject='fsaverage')
