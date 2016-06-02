import os

TAG_REGION_SIZE = "region_size"
TAG_SEARCH_WIDTH = "search_width"
TAG_SEARCH_HEIGHT = "search_height"
TAG_INPUT_DIR = "input_dir_root"
TAG_SAMPLES_DIR = "samples_dir"
TAG_OUTPUT_DIR = "output_dir"

DELIMITER = "="

DEFAULT_REGION_SIZE = 30
DEFAULT_SEARCH_WIDTH = 200
DEFAULT_SEARCH_HEIGHT = 400
DEFAULT_INPUT_DIR = "../test-images/"
DEFAULT_SAMPLES_DIR = "../test-images/Sample Sets/"
DEFAULT_OUTPUT_DIR = "../test-output/"


class Config:
    def __init__(self, file):
        self._file = file

        self.region_size = None
        self.search_width = None
        self.search_height = None
        self.input_dir = None
        self.samples_dir = None
        self.output_dir = None

        self.reset_all()

        self._load_from_file(file)

    def update_config_file(self):
        """ Save the options to the config file. """
        self._save_to_file(self._file)

    def reset_all(self):
        self.region_size = DEFAULT_REGION_SIZE
        self.search_width = DEFAULT_SEARCH_WIDTH
        self.search_height = DEFAULT_SEARCH_HEIGHT
        self.input_dir = DEFAULT_INPUT_DIR
        self.samples_dir = DEFAULT_SAMPLES_DIR
        self.output_dir = DEFAULT_OUTPUT_DIR

    def _clean_values(self):
        self.input_dir = str(self.input_dir).strip()
        self.samples_dir = str(self.samples_dir).strip()
        self.output_dir = str(self.output_dir).strip()

        if not self.input_dir.endswith("/"):
            self.input_dir += "/"

        if not self.samples_dir.endswith("/"):
            self.samples_dir += "/"

        if not self.output_dir.endswith("/"):
            self.output_dir += "/"

        try:
            self.region_size = int(self.region_size)
        except ValueError:
            self.region_size = DEFAULT_REGION_SIZE

        try:
            self.search_width = int(self.search_width)
        except ValueError:
            self.search_width = DEFAULT_SEARCH_WIDTH

        try:
            self.search_height = int(self.search_height)
        except ValueError:
            self.search_height = DEFAULT_SEARCH_HEIGHT

    def _save_to_file(self, file):
        """ Save the options to the specified file. """
        self._clean_values()
        line = "{}" + DELIMITER + "{}\n"

        with open(file, 'w') as f:
            f.write(line.format(TAG_REGION_SIZE, self.region_size))
            f.write(line.format(TAG_SEARCH_WIDTH, self.search_width))
            f.write(line.format(TAG_SEARCH_HEIGHT, self.search_height))
            f.write(line.format(TAG_INPUT_DIR, self.input_dir))
            f.write(line.format(TAG_SAMPLES_DIR, self.samples_dir))
            f.write(line.format(TAG_OUTPUT_DIR, self.output_dir))

    def _load_from_file(self, file):
        """ Load options from the specified file. """
        if not os.path.isfile(file):
            self._save_to_file(file)
            return

        with open(file) as f:
            lines = f.readlines()

            for line in lines:
                try:
                    tokens = line.strip().split(DELIMITER)
                    self._parse_line(tokens[0], tokens[1])
                except ValueError:
                    pass

        self._clean_values()

    def _parse_line(self, tag, value):
        """ Parse a line from a config file, setting the relevant option. """
        if tag == TAG_REGION_SIZE:
            self.region_size = int(value)
        elif tag == TAG_SEARCH_WIDTH:
            self.search_width = int(value)
        elif tag == TAG_SEARCH_HEIGHT:
            self.search_height = int(value)
        elif tag == TAG_INPUT_DIR:
            self.input_dir = str(value)
        elif tag == TAG_SAMPLES_DIR:
            self.samples_dir = str(value)
        elif tag == TAG_OUTPUT_DIR:
            self.output_dir = str(value)
