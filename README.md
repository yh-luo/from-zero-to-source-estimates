# From Zero to Source Estimates

If you have questions or want to start a discussion, please use the DISQUS comment system below [the post](https://yuhan.netlify.com/posts/from-zero-to-source-estimates/). If you want to contribute or update the contents (more than welcome!), please open a issue or even create a pull request.

[Overview](https://mne.tools/stable/overview/cookbook.html)

  - [Readings](#readings)
  - [FreeSurfer anatomical pipeline](#freesurfer-anatomical-pipeline)
    - [DICOMs to NifTi](#dicoms-to-nifti)
    - [FreeSurfer Anatomical reconstructions](#freesurfer-anatomical-reconstructions)
    - [Make BEMs and set up the source space](#make-bems-and-set-up-the-source-space)
  - [Preprocessing MEG data](#preprocessing-meg-data)
    - [Prerequisite](#prerequisite)
    - [Filter](#filter)
    - [Repairing artifacts with ICA](#repairing-artifacts-with-ica)
    - [Epoching and baseline correction](#epoching-and-baseline-correction)
    - [Create evoked responses](#create-evoked-responses)
    - [Compute baseline covariance](#compute-baseline-covariance)
    - [FIXME: Time-frequency decomposition](#fixme-time-frequency-decomposition)
    - [Group averages on sensor level](#group-averages-on-sensor-level)
  - [Source level](#source-level)
    - [Coregistration](#coregistration)
    - [Forward solution](#forward-solution)
    - [Inverse soltuion](#inverse-soltuion)
    - [Morph data for group averages](#morph-data-for-group-averages)
    - [Group averages on source level](#group-averages-on-source-level)
    - [Compute statistics](#compute-statistics)
  - [Write reports](#write-reports)

## To-Do

:white_large_square: Time-frequency decomposition  
:white_large_square: Chinese translation  
:white_large_square: More visualization

## Readings

+ [MNE Biomag Demo](http://mne.tools/mne-biomag-group-demo/index.html)
+ MNE [tutorials](https://mne.tools/stable/auto_tutorials/index.html) and documentation
+ Jas, M., Larson, E., Engemann, D. A., Leppäkangas, J., Taulu, S., Hämäläinen, M., & Gramfort, A. (2018). A Reproducible MEG/EEG Group Study With the MNE Software: Recommendations, Quality Assessments, and Good Practices. Frontiers in Neuroscience, 12, 530. https://doi.org/10.3389/fnins.2018.00530

## FreeSurfer anatomical pipeline

### DICOMs to NifTi

Use any software you like. I used [dcm2nii](https://people.cas.sc.edu/rorden/mricron/dcm2nii.html) in [MRICron 2MAY2016](https://www.nitrc.org/projects/mricron).
dcm2nii works fine for me while dcm2niix adds additional bytes in the NifTi files and FreeSurfer is unable to process it sometimes.

#### Notes

Though `mri_convert` in FreeSurfer can convert DICOMs to NifTi, the output are sometimes problematic and FreeSurfer is unable to reconstruct the surfaces using it.

### FreeSurfer Anatomical reconstructions

Use command line:

```bash
recon-all -all -s sample -i sample.nii.gz
```

Or use Python scripts to call FreeSurfer (unofficially recommended by me).

#### Demo

+ Data
  + DICOM from [High frequency SEF dataset](https://mne.tools/stable/overview/datasets_index.html?highlight=dicom#high-frequency-sef)
  + subject_a.nii.gz or subject_b.nii.gz (converted from DICOM)

+ `0_fetch_dataset.py` to get dataset
+ `1_anatomical_construction.py`

#### Notes

+ `recon-all` takes hours (~7 hours on AMD Ryzen 5 3600) to complete!
+ FreeSurfer uses single thread. If the cpu has multiple cores, open several terminals to process more than one subjects or use `mne.parallel.parallel_func` to loop through all the subjects.
   + Using many terminals at once works great for me.
+ Remember to [install and setup tcsh](https://surfer.nmr.mgh.harvard.edu/fswiki/SetupConfiguration_Linux) for FreeSurfer reconstructions.

### Make BEMs and set up the source space

There are two ways to create BEM surfaces:

1. `mne.bem.make_flash_bem` requires additional processes to prepare fast low-angle shot (FLASH) images.
    + Notes: Read the documentation in [`mne.bem.convert_flash_mris`](https://mne.tools/stable/generated/mne.bem.convert_flash_mris.html#mne.bem.convert_flash_mris) and [`mne.bem.make_flash_bem`](https://mne.tools/stable/generated/mne.bem.make_flash_bem.html?highlight=make_flash_bem#mne-bem-make-flash-bem)
2. `mne.bem.make_watershed_bem` create BEM surfaces using the FreeSurfer watershed algorithm (could be less accurate).

#### Notes

+ MNE version < 20 has a bug that makes it impossible to create watershed BEMs when `overwrite=False`.
+ I couldn't figure out how to acquire FLASH images at the moment, so I used watershed BEMs.

After making BEM surfaces, use them to create BEM models, BEM solutions and setup the source space.

#### Demo

+ Data
  + FreeSurfer reconstruction of subject_a or subject_b

+ `2_setup_source_space.py`

## Preprocessing MEG data

### Prerequisite

#### Real data

If you are from NTU like me, the data are assumed **Maxwell filtered** using SSS with MaxFilter provided by Elekta.

#### Practice

This tutorial utilizes the [sample dataset](https://mne.tools/stable/overview/datasets_index.html#sample) and uses MNE to Maxwell-filter the raw data.

##### Note

+ Use `0_fetch_dataset.py` to get the sample dataset if not already.

#### Directory structure

The structure of your study directory should look like:

```
.
├── MEG
├── MRI
├── results
├── scripts
└── subjects
```

### Filter

Most event-related brain signals are below 40 Hz. Low-pass filter with 40Hz does not affect most ERP signals of interest and attenuates the powerline frequency (60Hz in Taiwan) and all HPI coil frequencies (above 200Hz).
Data of EOG channels would be further high-pass filtered on 1Hz to use ICA.

#### Demo

`3_filter.py`

### Repairing artifacts with ICA

ICA is a blind source separation technique that maximizes the statistical independence between the components.
Because of its peaky distributions, eye blinks and heartbeats can be easily removed using ICA.

+ [Overview of artifact detection](https://mne.tools/stable/auto_tutorials/preprocessing/plot_10_preprocessing_overview.html)

+ [Repairing artifacts with ICA](https://mne.tools/stable/auto_tutorials/preprocessing/plot_40_artifact_correction_ica.html)

#### Demo

`4_ica.py`

### Epoching and baseline correction

Extract events using `mne.find_events` and create epochs based on the events.
ECG and EOG events are also detected in this stage and excluded from the ICA to prevent the noise from spreading to all signals. It is common practice to use baseline correction so that any constant offsets in the baseline are removed.

#### Demo

`5_epochs.py`

### Create evoked responses

The epochs are averaged across conditions to create evoked responses for each subject.

#### Demo

`6_evoked.py`

### Compute baseline covariance

Becauase inverse solvers usually assume Gaussian noise distribution, M/EEG signals require a whitening step due to the  nature of being highly spatially correlated. To denoise the data, one must provide an estimate of the spatial noise covariance matrix. Empty-room recordings for MEG or pre-stimulus period can be used to compute such information.
Here, the pre-stimulus period (baseline) is used.

#### Demo

`7_covariance.py`

### FIXME: Time-frequency decomposition

#### Demo

+ `8_inspect_frequency.py`
+ `9_time_frequency.py`

### Group averages on sensor level

The evoked responses are averaged for group averages.

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

+ Instructions can be found in [MNE documentation](https://mne.tools/stable/generated/mne.gui.coregistration.html?highlight=coreg#mne.gui.coregistration).
+ It is not neccessary, but may be helpful to use the high-resolution head surfaces to help coregistration.
To do this, refer to `11_setup_head_for_coreg.py`.

### Forward solution

Compute forward solution for the MEG data.

#### Demo

+ Data
  + Use `sample_audvis_raw-trans.fif` from the sample dataset for practice, or create it manually.
+ `12_forward_solution.py`

### Inverse soltuion

Compute and apply a dSPM inverse solution for each evoked data set.

#### Demo

`13_inverse_solution.py`

### Morph data for group averages

To analyze data at the group level, data from all subjects need to be transformed to a common source space. This procedure is called **morphing** by MNE.
Here, the data are morphed to the standard FreeSurfer average subject `fsaverage`.

#### Demo

`14_morph_source.py`

### Group averages on source level

After morphing, the source estimates are averaged for group responses on source level.

#### Demo

+ `15_group_average_source.py`
+ `15-2_viz_group_average.py`

### Compute statistics

Test if the evoked reponses are significantly different between conditions across subjects. The multiple comparisons problem is addressed with a cluster-level permutation test across space and time. To demonstrate, the evoked responses elicited by left auditory stimuli and by left visual stimuli are compared. The cluster results are further visualized.

#### Demo

+ `16_statistics.py`
+ `16-2_viz_statistics.py`

## Write reports

Congratulations and goodbye! You are on your own now :)
