# Parse a GDA log file to find instances of CrystalMatch Commands and create a datafile from the images.
import argparse
import gzip

from os.path import join, exists, isfile

from dls_imagematch.main_service import _get_argument_parser, _parse_selected_points_from_args
from test_suite import CrystalTestSuite

GDA_KEYPHRASE = "IMAGE MATCH COMMAND: /dls_sw/dasc/CrystalMatch/CrystalMatch"


def parse_log_file(filename, parser, keyphrase, test_suite):
    """
    Search a file for lines containing the keyphrase and use an argparse instance to try to interpret
    everything after the keyphrase.
    :param filename: Log file to search.
    :param parser: Parser object to use.
    :param keyphrase: Key-phrase to look for.
    :return:
    """
    if filename.endswith(".log.gz"):
        log_file = gzip.open(filename)
    elif filename.endswith(".log"):
        log_file = open(filename, "r")
    else:
        print("ERROR: Unrecognised file type.")
        return
    for line in log_file:
        # Find lines with key phrase and extract the arguments
        if keyphrase in line:
            split_list = line.split(keyphrase)
            # DEV NOTE: Assume that filepaths don't have spaces in them - we could parse this better but only this
            # script is not intended to be a complete solution. Report failures in the output
            arg_list = split_list[1].strip().split(" ")
            try:
                parsed_args = parser.parse_args(arg_list)
                test_suite.add_test_case(parsed_args.image_input.name,
                                         parsed_args.image_output.name,
                                         # TODO: refactor parser to make it easier to reference this - interface?
                                         _parse_selected_points_from_args(parsed_args))
            except IOError as e:
                print("ERROR: Failed to parse arguments: " + e.message)
    log_file.close()


parser = argparse.ArgumentParser(
    description="Parse a .log or .log.gz GDA file and extract paired VMXi CrystalMatch images and POI.")
parser.add_argument('output_file',
                    help="Output JSON filepath - overwrites automatically.")
parser.add_argument('log_file',
                    nargs='*',
                    help="file path to a GDA log file.")
args = parser.parse_args()

# Get an argument parser from the main CrystalMatch project
crystal_match_parser = _get_argument_parser()

# Create a new TestSuite or load an existing one based on the filepath provided
test_suite = CrystalTestSuite(args.output_file, "/")

for fp in args.log_file:
    print("Parsing '" + fp + "'...")
    # Check file exists
    if exists(fp):
        if isfile(fp):
            parse_log_file(fp, crystal_match_parser, GDA_KEYPHRASE, test_suite)
        else:
            print("ERROR: Target was a directory!")
    else:
        print("ERROR: File not found!")
test_suite.save_to_file()
