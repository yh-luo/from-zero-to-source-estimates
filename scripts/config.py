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

tmin = -1
tmax = 0.8
baseline = (-1, -0.8)
reject_tmax = 0.6
smooth = 10

ctc = op.join(study_dir, 'ct_sparse_mgh.fif')
cal = op.join(study_dir, 'sss_cal_mgh.dat')
