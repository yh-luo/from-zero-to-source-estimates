import os
import subprocess

from config import map_subjects, mri_dir, subjects_dir


def run_command(command, log_file):
    with open(log_file, "wb") as f:
        proc = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        for line in proc.stdout:
            f.write(line)
    if proc.wait() != 0:
        raise RuntimeError("command failed")


def process_subject_anat(subject_id, force=False):
    subject_mri_dir = os.path.join(mri_dir, subject_id)
    subject = map_subjects[subject_id]

    if os.path.isdir(os.path.join(subjects_dir, subject)) and not force:
        print(f"Skipping reconstruction for {subject_id} (folder exist)")
    else:
        # Run recon-all
        print(f"Reconstructing {subject_id} (usually take hours)")
        run_command(
            [
                "recon-all",
                "-all",
                "-s",
                subject,
                "-sd",
                subjects_dir,
                "-i",
                os.path.join(subject_mri_dir, f"{subject_id}.nii.gz"),
            ],
            os.path.join(subject_mri_dir, f"{subject_id}_recon-all.txt"),
        )


# NOTE: it takes hours to run on a decent computer, you can use the FreeSurfer
# reconstruction in the dataset.
process_subject_anat('subject_a')
