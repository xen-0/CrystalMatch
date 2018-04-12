# Parse a GDA log file to find instances of CrystalMatch Commands and create a datafile from the images.
import gzip

from os import listdir, remove
from os.path import join

directory = join(".", "gda_logs")
listdir(directory)
files = [f for f in listdir(directory) if f.endswith('.txt') or f.endswith(".log.gz")]

for filename in files:
    filename = join(directory, filename)
    fp = None
    if filename.endswith(".gz"):
        fp = gzip.open(filename)
    else:
        fp = open(filename, "r")
    for line in fp:
        print(line)
    fp.close()
    # remove(filename)
