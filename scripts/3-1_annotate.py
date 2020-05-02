import os.path as op
import mne
from config import meg_dir

subject = 'sample'
raw = mne.io.read_raw_fif(
    op.join(meg_dir, subject, f'{subject}_audvis_raw.fif'))

# check whether annotation file exist
annot_fname = op.join(meg_dir, subject, f'{subject}_audvis-annot.fif')
try:
    annot = mne.read_annotations(annot_fname)
    has_annot = True
except FileNotFoundError:
    has_annot = False

if has_annot:
    raw.set_annotations(annot)

# press 'a' for interactive marking
raw.plot()

# safe guard for saving annotations
interactive_annot = raw.annotations
interactive_annot.save(op.join(meg_dir, subject,
                               f'{subject}_audvis-annot.fif'))
