import os.path as op

# Please modify the study directory
study_dir = '/home/yuhan/Project/from-zero-to-source-estimates/'
subjects_dir = op.join(study_dir, "subjects")
mri_dir = op.join(study_dir, "MRI")
meg_dir = op.join(study_dir, "MEG")
rst_dir = op.join(study_dir, 'results')

l_freq = 1
h_freq = 40

# NOTE: https://mne.tools/stable/overview/cookbook.html#setting-up-the-source-space
spacing = "oct6"
bem_ico = 5

# Subject mapping
map_subjects = {"subject_a": "subject_a", "sample": "sample"}
excludes = ["subject_a"]

n_jobs = 4

# artifacts
n_max_ecg = 3
n_max_eog = 3

# epochs
# We'll create some dummy names for each event type
event_id = {
    'Auditory/Left': 1,
    'Auditory/Right': 2,
    'Visual/Left': 3,
    'Visual/Right': 4,
    'smiley': 5,
    'button': 32
}
tmin = -0.2
tmax = 0.5
baseline = (None, 0)
reject_tmax = None
smooth = 10

# Calibration files for Maxwell filter
ctc = op.join(study_dir, 'ct_sparse_mgh.fif')
cal = op.join(study_dir, 'sss_cal_mgh.dat')
