import os.path as op

import mne
import numpy as np

from config import bem_ico, excludes, map_subjects, meg_dir, spacing

conditions = {
    'aud_left_minus_right', 'vis_left_minus_right', 'aud_left_eq',
    'aud_right_eq', 'vis_left_eq', 'vis_right_eq'
}

subjects = [s for s in map_subjects.values() if s not in excludes]

for condition in conditions:
    stcs = list()
    for subject in subjects:
        stc_fname = op.join(
            meg_dir, subject, '-'.join([
                f'{subject}_audvis', 'dSPM', spacing, 'inverse', 'morph',
                'filt', 'sss', condition
            ]))
        stc = mne.read_source_estimate(stc_fname)
        stcs.append(stc)
    data = np.average([s.data for s in stcs], axis=0)
    stc_ave = mne.VectorSourceEstimate(data, stcs[0].vertices, stcs[0].tmin,
                                       stcs[0].tstep, 'fsaverage')
    ave_fname = op.join(
        meg_dir, '-'.join(
            [spacing, f'ico{bem_ico}', 'dSPM', 'morph', 'condition', 'ave']))
    stc_ave.save(ave_fname)
    print(f'Processed {condition}')
    # release memory
    del stcs, data, stc_ave

print(f'Computed group averages on source level(N = {len(subjects)})')
