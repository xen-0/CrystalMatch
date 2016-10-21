#!/bin/sh
# Build a linux distribution of the Crystal Matching Service on a Diamond workstation

# Clear the current distribution dir
echo "Clearing distribution directory..."
rm -rf distribution
mkdir distribution
cd distribution

# Select anaconda python on the Diamond network, ensure pyinstaller is installed and check req dependencies
echo "Loading Python version..."
module load python/ana && pip install pyinstaller --user && python ../scripts/check_requirements.py

if [ $? -eq 0 ]; then
# Build the service
echo "Building..."
PATH=$PATH:~/.local/bin/ PYTHONPATH="../source/" pyinstaller -n "CrystalMatch" ../source/dls_imagematch/main_service.py
if [ $? -eq 0 ]; then
echo "BUILD COMPLETE"
fi
else
echo "BUILD FAILED"
fi

#Return to root
cd ..
