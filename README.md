# AstroNCS
The official submission for the 2021/2022 Astro Pi Challenge by the AstroNCS team.

Analysis Method:

We took the images and converted them into NDVI Images using the tutorial provided by the Raspberry Pi Foundation:
https://projects.raspberrypi.org/en/projects/astropi-ndvi

We used the script that colours red pixels for images (in Python Script folder) which checks the NDVI value for each pixel to be in a certain threshold (-0.9 to 0.2).

We then had to calculate the real world length and height of a pixel on an image using the Ground Sampling Method (see report for further details).

In order to obtain the rotation of the images relative to Earth's north, we had to estimate the most northern point (local image north) on the image and find its coordinates on Google Maps.
Using the initial centre coordinates and the local north coordinates you can calculate the bearing.
Using this bearing you can rotate the image in order for it to be upright and get it as close as possible to the actual orientation.

The "centre" of the image (where the coordinates of the image lay respective to the image) can be deduced with Google Maps again, where you enter the coordinates and the corresponding location is estimated onto the image.
The coordinates of this point is symbolised with a specific shade of green pixel.

Finally, the final script is run which plots the yellow pixels onto the image (by comparing it to land cover viewer data), if a red pixel lies in the Herbaceous vegetation layer.
