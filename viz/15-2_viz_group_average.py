import os
import os.path as op

import mne

from scripts.config import baseline, meg_dir, subjects_dir

evokeds = mne.read_evokeds(op.join(meg_dir, 'grand_average-ave.fif'))

# Baseline correction
for evoked in evokeds:
    evoked.apply_baseline(baseline=baseline)

mapping = {
    'aud_left': evokeds[0],
    'aud_right': evokeds[1],
    'vis_left': evokeds[2],
    'vis_right': evokeds[3]
}

mne.viz.plot_compare_evokeds(mapping)

# Source space contrast
os.environ["SUBJECTS_DIR"] = subjects_dir
stc_aud = mne.read_source_estimate(
    op.join(meg_dir, 'aud_left_minus_right-grand_average-ave-stc'))
stc_aud.plot(hemi='both', initial_time=0.1)

stc_vis = mne.read_source_estimate(
    op.join(meg_dir, 'vis_left_minus_right-grand_average-ave-stc'))
stc_vis.plot(hemi='both', initial_time=0.1)
