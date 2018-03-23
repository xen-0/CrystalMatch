# Parse a GDA log file to find instances of CrystalMatch Commands and create a datafile from the images.
import gzip

filename = "/dls/science/groups/das/Archive/i02-2/logs/gda-server-20180130.log.gz"
fp = None

if filename.endswith(".gz"):
    fp = gzip.open(filename)
else:
    fp = open(filename, "r")

