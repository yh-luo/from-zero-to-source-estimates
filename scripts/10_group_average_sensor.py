import mne
import os.path as op

from config import meg_dir, map_subjects, excludes

# container for all the evokeds
all_evokeds = {
    'Auditory/Left': [],
    'Auditory/Right': [],
    'Visual/Left': [],
    'Visual/Right': [],
    'Auditory Left - Right': [],
    'Visual Left - Right': [],
    'Auditory/Left Equal': [],
    'Auditory/Right Equal': [],
    'Visual/Left Equal': [],
    'Visual/Right Equal': []
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
mne.evoked.write_evokeds(op.join(meg_dir, 'grand_average-ave.fif'),
                         all_grands)

print(f'Computed group averages (N = {len(subjects)})')
