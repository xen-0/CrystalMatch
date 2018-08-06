import cv2

# A simple python script designed to check known dependencies before a build 

if cv2.__version__ != '2.4.13.3':
    print "BUILD FAILED: v2.4.13.3 OpenCV required, found " + cv2.__version__
    exit(1)

print "Required dependencies found"
exit(0)
