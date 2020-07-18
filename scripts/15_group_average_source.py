import os.path as op

import mne
import numpy as np

from config import excludes, map_subjects, meg_dir, spacing

# container for all the stc
all_stc = {
    'aud_left_minus_right': [],
    'vis_left_minus_right': [],
    'aud_left_eq': [],
    'aud_right_eq': [],
    'vis_left_eq': [],
    'vis_right_eq': []
}

subjects = [s for s in map_subjects.values() if s not in excludes]

for condition, stcs in all_stc.items():
    for subject in subjects:
        stc_fname = op.join(
            meg_dir, subject,
            f'{subject}_audvis-dSPM-{spacing}-inverse-morph-filt-sss-{condition}'
        )
        stc = mne.read_source_estimate(stc_fname)
        stcs.append(stc)
    data = np.average([s.data for s in stcs], axis=0)
    stc = mne.VectorSourceEstimate(data, stcs[0].vertices, stcs[0].tmin,
                                   stcs[0].tstep, stcs[0].subject)
    stc.save(op.join(meg_dir, f'{condition}-grand_average-ave'))

print(f'Computed group averages on source level(N = {len(subjects)})')
