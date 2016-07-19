Crystal Matching
================

As discussed in the previous section, the main task that this program needs to be able to perform is to be able to locate a crystal that has been marked in one image in a second image that is taken at a later time.

There are therefore 3 inputs: the 'before' image (Image 1), the location of the crystal in image 1 (x, y coordinates), and the after image (Image 2).



Feature Matching
----------------
The way crystal matching has been achieved in this program is to use a technique called feature matching. In brief, feature matching is a two step process. First an algorithm identifies important features (we will describe what constitutes a feature shortly) in each of the images. Second, another algorithm looks at each feature in image 1 and attempts to find a feature in image 2 that is the same or very similar to it. From this set of matches, we can then calculate the transformation that maps the object shown in image 1 to that shown in image 2, i.e. we can determine if it has moved, rotated, etc.


Detecting Features
------------------
The OpenCV Tutorials have a good article on [Understanding Features](http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_features_meaning/py_features_meaning.html). 



