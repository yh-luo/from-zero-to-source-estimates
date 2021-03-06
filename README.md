# From Zero to Source Estimates

If you have questions or want to start a discussion, please use the Disqus comment system below [the post](https://yuhan.netlify.com/posts/from-zero-to-source-estimates/). If you wish to contribute or correct the contents (more than welcome!), please open an issue or create a pull request.

## Cautions

Be aware that this is my learning journey. The materials will change based on my knowledge of MEG and [`mne-python`](https://mne.tools/stable/index.html). If something looks wrong, it could be wrong. Please let me know if something looks confusing!

## Project overview

+ `scripts`: python scripts for processing
+ `viz`: python scripts and jupyter notebooks for visualization
+ `README.md`: instructions and some notes

## Requirements

+ Python 3.6 or higher
+ mne-python 0.21 or higher

## Table of Contents

[The typical M/EEG workflow](https://mne.tools/stable/overview/cookbook.html)

  - [Readings](#readings)
  - [FreeSurfer anatomical pipeline](#freesurfer-anatomical-pipeline)
    - [DICOM to NifTi](#dicom-to-nifti)
    - [FreeSurfer Anatomical reconstructions](#freesurfer-anatomical-reconstructions)
    - [Make BEMs and set up the source space](#make-bems-and-set-up-the-source-space)
  - [Preprocessing MEG data](#preprocessing-meg-data)
    - [Prerequisite](#prerequisite)
    - [Annotating bad data](#annotating-bad-data)
    - [Filtering](#filtering)
    - [Repairing artifacts with ICA](#repairing-artifacts-with-ica)
    - [Epoching and baseline correction](#epoching-and-baseline-correction)
    - [Create evoked responses](#create-evoked-responses)
    - [Compute baseline covariance](#compute-baseline-covariance)
    - [Group averages on sensor level](#group-averages-on-sensor-level)
  - [Source level](#source-level)
    - [Coregistration](#coregistration)
    - [Forward solution](#forward-solution)
    - [Inverse solution](#inverse-solution)
    - [Morph data for group averages](#morph-data-for-group-averages)
    - [Group averages on source level](#group-averages-on-source-level)
    - [Compute statistics](#compute-statistics)
  - [Write reports](#write-reports)

## To-Do

:white_large_square: Chinese translation  

## Readings

+ [MNE Biomag Demo](http://mne.tools/mne-biomag-group-demo/index.html)
+ MNE [tutorials](https://mne.tools/stable/auto_tutorials/index.html) and documentation
+ Andersen, L. M. (2018). Group Analysis in MNE-Python of Evoked Responses from a Tactile Stimulation Paradigm: A Pipeline for Reproducibility at Every Step of Processing, Going from Individual Sensor Space Representations to an across-Group Source Space Representation. Frontiers in Neuroscience, 12, 6. https://doi.org/10.3389/fnins.2018.00006
+ Gramfort, A., Luessi, M., Larson, E., Engemann, D., Strohmeier, D., Brodbeck, C., Goj, R., Jas, M., Brooks, T., Parkkonen, L., & Hämäläinen, M. (2013). MEG and EEG data analysis with MNE-Python. Frontiers in Neuroscience, 7, 267. https://doi.org/10.3389/fnins.2013.00267
+ Jas, M., Larson, E., Engemann, D. A., Leppäkangas, J., Taulu, S., Hämäläinen, M., & Gramfort, A. (2018). A Reproducible MEG/EEG Group Study With the MNE Software: Recommendations, Quality Assessments, and Good Practices. Frontiers in Neuroscience, 12, 530. https://doi.org/10.3389/fnins.2018.00530


## FreeSurfer anatomical pipeline

### DICOM to NifTi

Usually, dicom files (e.g., xxxx.IMG from Siemens MRI scanners) are provided after MRI scans. Before running the FreeSurfer anatomic procedure, convert the dicom files into NifTi format.  
Use any software you like. I used [dcm2niix](https://github.com/rordenlab/dcm2niix) included in [MRIcroGL](https://www.nitrc.org/projects/mricrogl/) at the moment (2020). For older dataset (e.g., data collected in 2016), I used [dcm2nii](https://people.cas.sc.edu/rorden/mricron/dcm2nii.html) in [MRICron 2MAY2016](https://www.nitrc.org/projects/mricron). Mysteriously, dcm2nii works fine on old data while dcm2niix adds additional bytes in the NifTi files and FreeSurfer is unable to process it sometimes.

#### Notes

Though `mri_convert` in FreeSurfer can convert DICOM to NifTi, the output files are sometimes problematic and FreeSurfer is unable to run the reconstruction on it.

### FreeSurfer Anatomical reconstructions

Use command line:

```
recon-all -all -s sample -i sample.nii.gz
```

Or use Python scripts to call FreeSurfer.

#### Notes

If the reconstruction looks incorrect, you may need to adjust the results or the parameters used in reconstruction manually. Refer to [My watershed BEM meshes look incorrect](https://mne.tools/dev/overview/faq.html#my-watershed-bem-meshes-look-incorrect) for advices.

#### Demo

+ Data
  + dicom files from [High frequency SEF dataset](https://mne.tools/stable/overview/datasets_index.html?highlight=dicom#high-frequency-sef)
  + subject_a.nii.gz or subject_b.nii.gz (manually converted to compressed NifTi from dicom files of T1)
+ `0_fetch_dataset.py` to get dataset
+ `01_anatomical_construction.py`

#### Notes

+ The script assumes compressed NifTi (`.nii.gz`)
+ `recon-all` takes hours (~7 hours on AMD Ryzen 5 3600) to complete!
+ FreeSurfer runs on a single thread. If the cpu has multiple cores, open several terminals to process more than one subjects or use `mne.parallel.parallel_func` to loop through all the subjects.
   + Using many terminals at once works great for me.
+ Remember to [install and setup tcsh](https://surfer.nmr.mgh.harvard.edu/fswiki/SetupConfiguration_Linux) for FreeSurfer reconstructions.

### Make BEMs and set up the source space

There are two ways to create BEM surfaces:

1. `mne.bem.make_flash_bem` requires additional processes to prepare fast low-angle shot (FLASH) images.
    + Read the documentation in [`mne.bem.convert_flash_mris`](https://mne.tools/stable/generated/mne.bem.convert_flash_mris.html#mne.bem.convert_flash_mris) and [`mne.bem.make_flash_bem`](https://mne.tools/stable/generated/mne.bem.make_flash_bem.html?highlight=make_flash_bem#mne-bem-make-flash-bem)
2. `mne.bem.make_watershed_bem` create BEM surfaces using the FreeSurfer watershed algorithm (could be less accurate).

After making BEM surfaces, use them to create BEM models, BEM solutions and setup the source space.

Usually, ico4 (2562 sources per hemisphere) is precise enough and efficient for source reconstruction. But ico5 (10242 sources per hemisphere) can be used for extra precision. This demo uses ico4 (`bem_ico = 4` in `config.py`).

#### Notes

+ MNE version < 20 has a bug that makes it impossible to create watershed BEMs when `overwrite=False`.
+ I couldn't figure out how to acquire FLASH images at the moment, so I used watershed BEMs.

#### Demo

+ Data
  + FreeSurfer reconstruction of sample
+ `02_setup_source_space.py`

## Preprocessing MEG data

### Prerequisite

#### Real data

If you are from NTU (National Taiwan University) like me, the data are assumed **Maxwell filtered** using SSS (or tSSS) with MaxFilter provided by Elekta. If the cHPI recordings are available, MaxFilter can also perform movement compensation.

#### Practice

This tutorial utilizes the [sample dataset](https://mne.tools/stable/overview/datasets_index.html#sample) and uses MNE to Maxwell-filter the raw data.

##### Note

+ Use `0_fetch_dataset.py` to get the sample dataset if not already.

#### Directory structure

The structure of your study directory should look like:

```
.
├── MEG
│   └── sample
├── MRI
│   └── sample
├── results
├── scripts
├── subjects
└── viz
```

### Annotating bad data

Before anything, take a look at the data to decide whether the data are worth processing. Also, annotate bad data segments to drop bad epochs afterward.

+ [Annotating continuous data](https://mne.tools/stable/auto_tutorials/raw/plot_30_annotate_raw.html)
+ [Rejecting bad data spans](https://mne.tools/stable/auto_tutorials/preprocessing/plot_20_rejecting_bad_data.html)

#### Demo

`03-1_annotate.py`

### Filtering

Most event-related brain signals are below 40 Hz. Low-pass filter with 40 Hz does not affect most brain signals of interest and attenuates the powerline frequency (60 Hz in Taiwan, 50 Hz in some countries) and all HPI coil frequencies (above 100 Hz). To use ICA to repair artifacts, data of EOG channels would be further high-pass filtered on 1Hz in order to remove slow drifts.

#### Demo

`03-2_filter.py`

### Repairing artifacts with ICA

ICA is a blind source separation technique that maximizes the statistical independence between the components. Because of its peaky distributions, eye blinks and heartbeats can be easily removed using ICA. Because ICA can be affected by high amplitude artifacts, `autoreject (global)` is used on the raw data to determine the rejection threshold before fitting ICA to the data.

+ [Overview of artifact detection](https://mne.tools/stable/auto_tutorials/preprocessing/plot_10_preprocessing_overview.html)
+ [Repairing artifacts with ICA](https://mne.tools/stable/auto_tutorials/preprocessing/plot_40_artifact_correction_ica.html)
+ Jas, M., Engemann, D. A., Bekhti, Y., Raimondo, F., & Gramfort, A. (2017). Autoreject: Automated artifact rejection for MEG and EEG data. NeuroImage, 159, 417–429. https://doi.org/10.1016/j.neuroimage.2017.06.030
+ [autoreject FAQ: Should I apply ICA first or autoreject first?](https://autoreject.github.io/faq.html#should-i-apply-ica-first-or-autoreject-first)

#### Demo

+ `04_ica.py`
+ `04-2_viz_ica.py`

### Epoching and baseline correction

Extract events using `mne.find_events` and create epochs based on the events. Bad epochs according to the annotation file are dropped. ECG and EOG events are detected in this stage and excluded from the ICA to prevent the noise from spreading to all signals. [CTPS method](http://ieeexplore.ieee.org/document/4536072/) is used to detect ECG related IC and the threshold is set to automatic computation (implemented in mne v0.21). The maximum number of excluded IC is confined to 3 for ECG (QRS complex) and 3 for EOG. When creating epochs, it is common practice to use baseline correction so that any constant offsets in the baseline are removed. After creating the epochs, `autoreject (local)` is used to drop bad epochs and interpolate bad channels. Notice that running `autoreject` is not required but recommended to denoise the data. Refer to the paper when in doubt.

+ Dammers, J., Schiek, M., Boers, F., Silex, C., Zvyagintsev, M., Pietrzyk, U., & Mathiak, K. (2008). Integration of Amplitude and Phase Statistics for Complete Artifact Removal in Independent Components of Neuromagnetic Recordings. IEEE Transactions on Biomedical Engineering, 55(10), 2353–2362. https://doi.org/10.1109/TBME.2008.926677
+ Jas, M., Engemann, D. A., Bekhti, Y., Raimondo, F., & Gramfort, A. (2017). Autoreject: Automated artifact rejection for MEG and EEG data. NeuroImage, 159, 417–429. https://doi.org/10.1016/j.neuroimage.2017.06.030

##### Note

+ Alternatively, inspect the ICs and manually remove the artifact-related ICs.
+ For ECG epochs, `l_freq=10` and `h_freq=20` give better results than the default (`l_freq=8`, `h_freq=16`).
+ `autoreject (local)` utilizes machine learning techniques to clean the signals and can be resource-consuming.

#### Demo

+ `05_epochs.py`
+ `05-2_viz_artifact_epochs.py`

### Create evoked responses

The epochs are averaged across conditions to create evoked responses for each subject.

#### Demo

`06_evoked.py`

### Compute baseline covariance

Because inverse solvers usually assume Gaussian noise distribution, M/EEG signals require a whitening step due to the nature of being highly spatially correlated. To denoise the data, one must provide an estimate of the spatial noise covariance matrix. Empty-room recordings for MEG or pre-stimulus period can be used to compute such information.
Here, the pre-stimulus period (baseline) is used.

#### Demo

`07_covariance.py`

### Group averages on sensor level

The evoked responses are averaged for group averages.

#### Demo

`10_group_average_sensor.py`

## Source level

### Coregistration

The recommended way to use the GUI is through command line with:

```
mne coreg
```

or use `mne.gui.coregistration` to initiate the GUI.

#### Notes

+ Instructions of coregistration can be found in [MNE documentation](https://mne.tools/stable/generated/mne.gui.coregistration.html?highlight=coreg#mne.gui.coregistration).
+ It is not neccessary, but may be helpful to use the high-resolution head surfaces to help coregistration. To do this, refer to `11_setup_head_for_coreg.py` and [`mne make_scalp_surfaces`](https://mne.tools/dev/generated/commands.html#mne-make-scalp-surfaces).

### Forward solution

Compute forward solution for the MEG data.

#### Demo

+ Data
  + Use `sample_audvis_raw-trans.fif` from the sample dataset for practice, or create it manually.
+ `12_forward_solution.py`

### Inverse solution

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

Test if the evoked responses are significantly different between conditions across subjects. The multiple comparisons problem is addressed with a cluster-level permutation test across space and time. In this demo, the evoked responses elicited by left auditory stimuli and by left visual stimuli are compared. 
The cluster results are saved to HDF (*.h5) for future use (e.g., visualization). The cluster results are further visualized via `mne.stats.summarize_clusters_stc`.

#### Demo

+ `16_statistics.py`
+ `16-2_viz_statistics.py`

#### Notes

+ [Statistical inference](https://mne.tools/stable/auto_tutorials/discussions/plot_background_statistics.html#statistical-inference)

## Write reports

Congratulations and good luck!