from setuptools import setup

# These lines allow the version to be specified in Makefile.private.
import os
version = os.environ.get("MODULEVER", "0.0")

setup(
    install_requires=['numpy == 1.7.0', 'dill == 0.2.4'],
    # We also require OpenCV but it's already in dls-python's `sys.path`.
    name='dls_imagematch', version=version,
    description='Image registration for VMXi',
    author='Nic Bricknell',
    author_email='nic.bricknell@diamond.ac.uk',
    packages=['dls_imagematch'],
    zip_safe=False,
)
