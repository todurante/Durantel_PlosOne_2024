# A Riemannian framework for incorporating white matter bundle prior in orientation distribution function based tractography algorithms.

## Contents
* script_gen_eodf.py
* subjects.txt : HCP subject IDs used for both the atlas and the measurements
* Transformation and ResidualDir : Transformation SVF of each subject to the atlas
* averageDTI8 : DTI image of the atlas

## Requirements
### Soft
* Anima : https://anima.readthedocs.io/en/latest/compile_source.html
* TractSeg : https://github.com/MIC-DKFZ/TractSeg/#install
### Data
* The segmented tracts used to build the atlas and to test the method can be found at https://zenodo.org/records/1477956 which contains segmentations of 72 white matter tracts obtained from 105 subjects.
* The diffusion data of of these subjects can be found at https://www.humanconnectome.org/study/hcp-young-adult, make sure you download the data for the correct subjects (see subjects.txt for the IDs) 

## Usage
Before you can run the script, a few variables need to be defined.  
* Set the paths to Anima and TractSeg
* Set the working directory path
* Set the path to the diffusion data
* Set the path to the segmented tracts
* Specify the bundles for which you want to build EODFs

