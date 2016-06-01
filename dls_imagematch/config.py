import os

TAG_REGION_SIZE = "region_size"

DELIMITER = "="

DEFAULT_REGION_SIZE = 30


class Config:
    def __init__(self, file):
        self._file = file

        self.region_size = None

        self.reset_all()

        self._load_from_file(file)

    def update_config_file(self):
        """ Save the options to the config file. """
        self._save_to_file(self._file)

    def reset_all(self):
        self.region_size = DEFAULT_REGION_SIZE

    def _clean_values(self):
        try:
            self.region_size = int(self.region_size)
        except ValueError:
            self.region_size = DEFAULT_REGION_SIZE

    def _save_to_file(self, file):
        """ Save the options to the specified file. """
        self._clean_values()
        line = "{}" + DELIMITER + "{}\n"

        with open(file, 'w') as f:
            f.write(line.format(TAG_REGION_SIZE, self.region_size))

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
