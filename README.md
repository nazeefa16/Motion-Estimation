# Motion-Estimation
Uses Exhaustive Search and Diamond Search Algorithm for motion compensation.

Motion estimation plays an important role in motion compensated image sequence coding. Fast motion estimation algorithms are an import element in practical video compression. In this code we have explored the effect of the search strategy on the computational cost and its effect on the motion compensated image in terms of its difference to the target image.
Diamond Search (DS) Algorithm, which is one of the earliest fast block matching algorithms is implemented here. DS algorithm is used to create a motion compensated reference of an I-Picture that will is used as the reference to code a P-picture. The results are compared to the motion compensated image using an exhaustive search and the DS, for the supplied reference and target images, using the PSNR metric. 
Only pixel displacements are considered in this code.

The analysis is applied to each of the three extracted pictures sequences (coastguard,container, stefan).
• The experiment is repeated twice to examine the performance of the motion compensationprocess for the following GOP structures; IP, IBBP.
• The pictures are numbered by their position in the display order. For example, coastguard-60 is the I-picture, coastguard-61 and coastguard-62 would be coded as B-pictures and coastguard-63 would be coded as a P-picture as an IBBP sequence; in this example you would choose coastguard-60 as the I-Picture reference and coastguard-63 as the target P-picture. Choose coastguard-60 and coastguard-61 in the simpler IP structure
