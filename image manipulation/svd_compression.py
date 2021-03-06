#!/usr/bin/env python

# Author: Douglas Rudd
# Date: 5/3/2014
#
# Apply SVD to crudely compress a greyscale
# image. Requires numpy and PIL (or Pillow)

import numpy as np
from PIL import Image

# load example image as numpy array
img = np.asarray(Image.open("spt.png"))

# compute svd of image
h, d, a = np.linalg.svd(img)

# Generate images with differing compression levels
for k in 10, 50, 100, 200:
    # reconstruct image using k components of decomposition
    img_ = np.dot(np.dot(h[:, :k], np.diag(d[:k])), a[:k, :])

    # compute compression ratio
    ratio = float(k*(1+sum(img.shape)))/np.prod(img.shape)
    print "Compression factor %.5f" % (ratio, )

    # save resulting image
    Image.fromarray(img_.astype(np.uint8)).save("spt_k%03d.png" % (k, ))
    #Image.fromarray(img_.astype(np.uint8)).show()
