#!/bin/sh
# Build a linux distribution of the Crystal Matching Service on a Diamond workstation

# Clear the current distribution dir
rm -rf distribution
mkdir distribution
cd distribution

# Select anaconda python on the Diamond network, ensure pyinstaller is installed and check req dependencies
module load python/ana && pip install pyinstaller --user && python ../scripts/check_requirements.py

if [ $? -eq 0 ]; then
# Build the service
PATH=$PATH:~/.local/bin/ PYTHONPATH="../source/" pyinstaller ../source/dls_imagematch/main_service.py
else:
print "BUILD FAILED"
fi

#Return to root
cd ..
