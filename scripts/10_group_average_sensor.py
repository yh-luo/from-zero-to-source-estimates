import os.path as op

import mne

from config import excludes, map_subjects, meg_dir

# container for all the evokeds
all_evokeds = {
    'aud_left': [],
    'aud_right': [],
    'vis_left': [],
    'vis_right': [],
    'aud_left_minus_right': [],
    'vis_left_minus_right': [],
    'aud_left_eq': [],
    'aud_right_eq': [],
    'vis_left_eq': [],
    'vis_right_eq': []
}
all_grands = list()
subjects = [s for s in map_subjects.values() if s not in excludes]

for subject in subjects:
    evokeds = mne.read_evokeds(op.join(meg_dir,
                                       f'{subject}_audvis-filt-sss-ave.fif'),
                               verbose='error')
    assert len(evokeds) == len(all_evokeds)

    for evoked in evokeds:
        all_evokeds[evoked.comment].append(evoked)

for condition, evokeds in all_evokeds.items():
    grand_ave = mne.combine_evoked(evokeds, 'equal')  # all subjects
    grand_ave.comment = condition
    all_grands.append(grand_ave)

# Sensor space
mne.evoked.write_evokeds(op.join(meg_dir, 'grand_average-ave.fif'), all_grands)

print(f'Computed group averages (N = {len(subjects)})')
