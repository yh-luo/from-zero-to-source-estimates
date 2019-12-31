import os
import os.path as op
import numpy as np

study_dir = os.getcwd()
subjects_dir = op.join(study_dir, "subjects")
mri_dir = op.join(study_dir, "MRI")
meg_dir = op.join(study_dir, "MEG")
rst_dir = op.join(study_dir, 'results')

l_freq = None
h_freq = 40


spacing = "oct6"
mindist = 5
# Subject mapping
map_subjects = {
    "subject_a": "subject_a",
    "sample": "sample"
}

excludes = ["subject_a"]

n_jobs = 2

# artifacts
n_max_ecg = 3
n_max_eog = 2

# epochs
# We'll create some dummy names for each event type
event_id = {'Auditory/Left': 1, 'Auditory/Right': 2,
            'Visual/Left': 3, 'Visual/Right': 4,
            'smiley': 5, 'button': 32}
tmin = -0.2
tmax = 0.5
baseline = (None, 0)
reject_tmax = None
smooth = 10

ctc = op.join(study_dir, 'ct_sparse_mgh.fif')
cal = op.join(study_dir, 'sss_cal_mgh.dat')
