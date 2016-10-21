#CrystalMatch - Deployment

This application is intended for deployment on a beam line control machine.  Due to dependency on a specific version of OpenCV it would be preferable to deploy it a stand-alone application without relying on the local Python environment.

The recommended method of deployment is therefore to bundle the dependencies into a single executable file using 'pyinstaller' which must be run on a Linux distribution with the correct packages installed (see `setup.md` for requirements).

**NOTE:** At time of writing the Anaconda distribution of Python on the Diamond network (`module load python/ana`) has the correct requirements to build a distribution.

## Creating a Distribution

There is a build script `build_linux.sh` in the root directory of the repository which assumes that the local machine is a RedHat Linux distribution running on the Diamond network.

From the root directory of the repository run the script ('sh build_linux.sh'). This will carry out the following steps:

1. Deleted the existing distribution directory (if applicable).
1. Loads the correct version of Python from the network.
2. Attempts to install `pyinstaller` to the user's local environment.
3. Check that the Python dependency requirements are met (`./scripts/check_requirements.py`).
4. Run `pyinstaller` with the relevant `PATH` and `PYTHONPATH` entries to build the application.

Once the script has run the distribution should be located at `./distribution/dist/`.

## Deployment and Running the application

The entire distribution directory `CrystalMatch` should be deployed to the server (any previous versions should be removed). It should contain an executable with the same name as the directory which can be run from the command line - `CrystalMatch/CrystalMatch`

