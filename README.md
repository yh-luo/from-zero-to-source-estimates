# From Zero to Source Estimates

[Overview](https://mne.tools/stable/overview/cookbook.html)

## FreeSurfer anatomical pipeline

### DICOMs to NifTi

You can use any softwares you like. I used [dcm2nii](https://people.cas.sc.edu/rorden/mricron/dcm2nii.html) in [MRICron 2MAY2016](https://www.nitrc.org/projects/mricron).
dcm2nii works fine for me while dcm2niix adds additional bytes in the NifTi files and FreeSurfer is unable to process it sometimes.

#### Notes

Though `mri_convert` in FreeSurfer can convert DICOMs to NifTi, the output are sometimes problematic and FreeSurfer is unable to reconstruct the surfaces using it.

### recon-all

You can use command line:
```bash
recon-all -all -s sample -i sample.nii.gz
```

Or use Python to call FreeSurfer (unofficially recommended by me).

#### Demo

+ Data
  + DICOM from [High frequency SEF dataset](https://mne.tools/stable/overview/datasets_index.html?highlight=dicom#high-frequency-sef)
  + subject_a.nii.gz or subject_b.nii.gz (converted from DICOM)

+ `0_fetch_dataset.py` to get dataset
+ `1_anatomical_construction.py`

#### Notes

+ `recon-all` takes hours (~7 hours on AMD Ryzen 5 3600) to complete!
+ FreeSurfer uses single thread. To save time, if the cpu has multiple cores, open several terminals to process several subjects or use `mne.parallel.parallel_func` to loop through all the subjects.
   + Using many terminals at once works great for me.
+ Remember to [setup tcsh](https://surfer.nmr.mgh.harvard.edu/fswiki/SetupConfiguration_Linux) for FreeSurfer reconstructions.

### Make BEMs and set up the source space

There are two ways to create BEM surfaces:
1. `mne.bem.make_flash_bem` requires additional processes to prepare fast low-angle shot (FLASH) images.
    + Notes: Read the documentation in [`mne.bem.convert_flash_mris`](https://mne.tools/stable/generated/mne.bem.convert_flash_mris.html#mne.bem.convert_flash_mris) and [`mne.bem.make_flash_bem`](https://mne.tools/stable/generated/mne.bem.make_flash_bem.html?highlight=make_flash_bem#mne-bem-make-flash-bem)
2. `mne.bem.make_watershed_bem` create BEM surfaces using the FreeSurfer watershed algorithm (could be less accurate).

#### Notes

+ MNE version < 20 has a bug that makes it impossible to create watershed BEMs when `overwrite=False`.
+ I couldn't figure out how to acquire FLASH images at the moment, so I used watershed BEMs.

After making BEM surfaces, use them to create BEM mmodels, BEM solutions and the source space.

#### Demo

+ Data
  + FreeSurferreconstruction of subject_a or subject_b

+ `2_setup_source_space.py`

## Preprocessing MEG data

### Prerequisite

#### Real data

If you are from NTU like me, the data are assumed **Maxwell filtered** using SSS with MaxFilter provided by Elekta.

#### Practice

Raw data from [sample dataset](https://mne.tools/stable/overview/datasets_index.html#sample) was used in this tutorial. Maxwell filtering would be performed on it.

##### Note

+ Use `0_fetch_dataset.py` to get dataset if not already.

### Filter

Most event-related brain signals are below 40 Hz. Low-pass filter with 40Hz does not affect most ERP signals of interest and attenuates the powerline frequency (60Hz in Taiwan) and all HPI coil frequencies (above 200Hz).
Data of EOG channels would be further high-pass filtered on 1Hz to use ICA.

#### Demo

+ `3_filter.py`

### Repairing artifacts with ICA

ICA is a blind source separation technique that maximizes the statistical independence between the components.
Because of its peaky distributions, eye blinks and heartbeats can be easily removed using ICA.

+ [Overview of artifact detection](https://mne.tools/stable/auto_tutorials/preprocessing/plot_10_preprocessing_overview.html)

+ [Repairing artifacts with ICA](https://mne.tools/stable/auto_tutorials/preprocessing/plot_40_artifact_correction_ica.html)

#### Demo

`4_ica.py`

### Epoching and baseline correction

We first extract events using `mne.find_events` and create epochs based on the events.
ECG and EOG events are also detected in this stage and excluded from the ICA to prevent the noise spreading to the all signals. It is common practice to use baseline correction so that any constant offsets in the baseline are removed.

#### Demo

`5_epochs.py`

### Create evoked responses

#### Demo

`6_evoked.py`

### Compute baseline covariance

#### Demo

`7_covariance.py`

### FIXME: Time-frequency decomposition

#### Demo

`8_inspect_frequency.py`
`9_time_frequency.py`

### Group averages on sensor level

#### Demo

`10_group_average_sensor.py`

## Source level

### Coregistration

The recommended way to use the GUI is through bash with:

```bash
mne coreg
```

or use `mne.gui.coregistration` to initiate the GUI.


#### Notes

+ use `sample_audvis_raw-trans.fif` from the sample dataset for practice.
+ Instructions can be found in [MNE documentation](https://mne.tools/stable/generated/mne.gui.coregistration.html?highlight=coreg#mne.gui.coregistration).
+ It is not neccessary, but may be helpful to use the high-resolution head surfaces to help coregistration.
To do this, play with subject_a and refer to `11_setup_head_for_coreg.py`.

### Forward solution

#### Demo

+ Data: `sample_audvis_raw-trans.fif`

+ `12_forward_solution.py`

### Inverse soltuion

#### Scripts

`13_inverse_solution.py`

### Morph data for group averages

#### Sripts

`14_morph_source.py`

### Group averages on source level

#### Scripts

`15_group_average_source.py`
`15-2_viz_group_average.py`

### Compute statistics
