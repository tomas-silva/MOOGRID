# MOOGRID

Creates a synthetic spectra for the following inputs:

### Stellar parameters: 
The parameter space of Teff, log g, metallicity and microturbulence that should
be evaluated.

### MOOG wavelength parameters: 
This is the wavelength range to be studied, the steps in wavelength and also the interval of wavelength to be computed at a time. For my final synthesis I used a range from 11680 Å to 13000 Å, with a step of 0.001 Å and in intervals of 10 Å in order to avoid memory errors with MOOG.

### Smoothing and broadening functions: 
The smoothing types (in my case a combination of Gaussian, rotational and macroturbulent) and the full-width-at-half-maximum for the smoothing and broadening functions.

### Folder locations:
To which folders should all the created files be directed, from inputs and atmospheres to final the spectra and possible error information.

---

From all these inputs, the bash script then calls the interpolation code, creates an atmosphere file and follows by creating the input file to be read by MOOG. From these, MOOG will create multiple output files. In the end, I will have a full spectrum built from the concatenation of the 10Å spectra slices created by MOOG. As the script progresses, the entire star parameter space will be covered, resulting in a spectrum for each combination of Teff and metallicity while log g and microturbulence were set to be fixed.

By the end, if any errors arose during this process they will be presented with a message stating if any parameter combination could not be synthesized or any other error detected in the file creation.

Finally, each file will go to the correspondent folder. All the files are also named with the relevant input information, making it simple to identify and use in future steps.
