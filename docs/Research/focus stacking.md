# Focus Stacking Research

Focus Stacking is required to collate the images taken on the beamline into a single extended focus image similar to those produced by the Formulatrix.  The document below is intended as an informal record of the solutions tried as I may have to return to this investigation between other tasks.

## Outline

Focus stacking is necessary for two reasons; firstly because crystals may be at different heights in the sample.  Secondly the plate is bowed slightly so each sample may be at a different z-axis position depending on it's location on the plate.

The OAV (on-axis viewer) provides a stack of images taken at different heights / focal lengths (need to confirm which).  We need to develop a method to quickly combine these images into an extended focus image in under a second.

## Pilot Study

A pilot study was conducted by Kris Ward prior to my involvement in the project.  The prototype uses Laplacian analysis to select each pixel based on the highest value.  This was moderately effective but results in significant noise in the output degrading the quality of the final image.  This effect is enhanced by adding redundant levels of the stack - ie: levels at which sample is entirely out of focus.

There was also an alignment step which was removed as it should be unnecessary (the goniometer is accurate enough that the images should be considered aligned) as well as being limited by the fact that the features between the stack levels are obfuscated by the changing focus.

## Proposed Solution

The Laplacian Pyramid seems to be an effective method of Focus Stacking but may need adapting.  The biggest challenge will be obtaining a high enough quality image in limited time - the method used in the pilot study takes far too long to process a stack.

The quality of the image can be improved by changing the method used to select pixels.  Calculating the entropy between each pixel and it's neighbours would be a good place to start here.

The primary concern should be the quality of the final image - the speed can be improved once an acceptable method has been found.

# Open Investigations

* Calculate pixel entropy and select pixels which give the most information.  This should improve the quality but is an expensive operation as it must be calculated per pixel. Numpy may be able to do it as a mask calculation.

* Scaling - Kris attempted to use a Gaussian blur on the images prior to calculating the Laplacian, a similar effect can be gained by down-scaling the images before calculation and up-scaling the final result.  This would also make the operation quicker but may lose too much information.

* Tree methods - Merging the levels in a tree structure would allow multiple processes to be used.

* Selecting the optimum root image - currently the stack is processed from the top down, selecting the base image as the one with the greatest Laplacian value could improve the result. 

* Thresholding the Laplacian values and using a sparse array to combine/compare values - this will speed up the calculation.

* Wavelet Transform - this is an alternative to Laplacian which is used extensively in biological imaging.

## Notes

I have been able to speed up the prototype by using Numpy matrix operation instead of Python for loops but it will still need to be improved.  Combining the levels in a tree structure would allow the work to be split over multiple processes.