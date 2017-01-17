import argparse

from os.path import split, exists, isdir, isfile

from os import makedirs, remove

CONFIG_FILE = "../config/focus_stack.ini"


def _get_argument_parser():
    parser = argparse.ArgumentParser(description="Takes a z-stack of images and creates a composite using the "
                                                 "in-focus sections of each image.")
    # TODO: check images exist
    parser.add_argument('image_stack',
                        metavar="image_path",
                        type=file,
                        nargs="*",
                        help="A list of image files - each image represents a level of the z-stack.")
    parser.add_argument('-o',
                        metavar="output_path",
                        help="Specify output file - default is to create a file called 'output.png' in the working "
                             "directory. This will overwrite existing files, if the path does not exist the app "
                             "will attempt to make it.")
    # TODO: add verbose and debug modes
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        help="Increase output verbosity.")
    parser.add_argument('-d', '--debug',
                        action="store_true",
                        help="Output debug information to the console.")
    return parser


def process_output_file_path(path):
    output_dir, output_file = split(path)
    if output_dir is not "":
        if not (exists(output_dir) and isdir(output_dir)):
            makedirs(output_dir)
    if exists(path) and isfile(path):
        remove(path)


def handle_error(e):
    """
    A placeholder method for dealing with errors raised during runtime - these need to be reported in JSON mode.
    :param e: Exception being raised
    """
    print "ERROR"
    print e


def main():
    try:
        parser = _get_argument_parser()
        args = parser.parse_args()
        process_output_file_path(args.o)
    except IOError as e:
        handle_error(e)

if __name__ == '__main__':
    main()
