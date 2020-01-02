import subprocess
import os.path as op

from config import mri_dir, subjects_dir, map_subjects


def run_command(command, log_file):
    with open(log_file, "wb") as f:
        proc = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        for line in proc.stdout:
            f.write(line)
    if proc.wait() != 0:
        raise RuntimeError("command failed")


def process_subject_head(subject_id):
    subject_mri_dir = op.join(mri_dir, subject_id)
    subject = map_subjects[subject_id]
    run_command([
        "mne", "make_scalp_surfaces", "-s", subject, "-d", subjects_dir,
        "--no-decimate", "--overwrite"
    ], op.join(subject_mri_dir, f"{subject_id}_make_scalp_surfaces.txt"))
    print(f"Created high-resolution head surfaces for {subject}")

process_subject_head('sample')
