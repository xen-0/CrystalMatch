import logging
from os import makedirs
from os.path import join, exists, isdir, abspath

from dls_util.config.config import Config
from dls_util.config.item import DirectoryConfigItem, BoolConfigItem, EnumConfigItem, RangeIntConfigItem


class SettingsConfig(Config):

    LOG_LEVEL_DEBUG = "debug"
    LOG_LEVEL_INFO = "info"
    LOG_LEVEL_WARNING = "warning"
    LOG_LEVEL_ERROR = "error"

    LOG_LEVEL_LIST = [
        LOG_LEVEL_DEBUG,
        LOG_LEVEL_INFO,
        LOG_LEVEL_WARNING,
        LOG_LEVEL_ERROR,
    ]

    LOG_LEVEL_DICT = {
        LOG_LEVEL_DEBUG: logging.DEBUG,
        LOG_LEVEL_INFO: logging.INFO,
        LOG_LEVEL_WARNING: logging.WARNING,
        LOG_LEVEL_ERROR: logging.ERROR,
    }

    LOG_DIR_NAME = 'logs'
    LOG_FILE_NAME = 'log'
    LOG_IMAGE_DIR = 'images'

    ROTATION_INTERVAL_LIST = ['S', 'M', 'H', 'D']

    """
    Configuration class that holds application level settings such as logging options etc.
    """
    def __init__(self, config_dir, log_dir=None):
        Config.__init__(self, join(config_dir, 'settings.ini'))

        add = self.add

        self.set_title("Crystal Match App Settings")
        self.set_comment("Configuration file for the application - contains settings which affect the application "
                         "itself such as options for outputting logs.")

        self.logging = add(BoolConfigItem, "Activate Logging", True)
        self.logging.set_comment("Turns file logging on and off.")

        self._set_default_log_file_path(config_dir)
        self.log_path = add(DirectoryConfigItem, "Log directory", "")
        self.log_path.set_comment("Sets the directory in which log files are stored. Leaving this blank will set the "
                                  "default path - log files will be stored in a directory called 'logs' next to the "
                                  "current config directory.")

        if log_dir is not None:
            self.log_path.set_override(log_dir)

        self.log_level = add(EnumConfigItem, "Log Level", default=self.LOG_LEVEL_INFO, extra_arg=self.LOG_LEVEL_LIST)
        self.log_level.set_comment("Sets the log level for the log files being generated.")

        self.log_rotation = add(EnumConfigItem, "Log File Rotation Frequency",
                                default='H', extra_arg=self.ROTATION_INTERVAL_LIST)
        self.log_rotation.set_comment("Log files are rotated after a set time period (the default is every hour) to "
                                      "prevent large files accumulating and to make navigation easier. Note that the "
                                      "Log File Count Limit is linked to this value.")

        self.log_count_limit = add(RangeIntConfigItem, "Log File Count Limit", default=672, extra_arg=[1, None])
        self.log_count_limit.set_comment("The maximum number of log files stored by the program - after this older "
                                         "files will be deleted.  Note that this value is related to the Log File "
                                         "Rotation Frequency - with the default value (hourly) one month of log "
                                         "files will be stored.")

        self.log_images = add(BoolConfigItem, "Log Match Images", False)
        self.log_images.set_comment("Option to output an image capture of each crystal match. This option will be "
                                    "disabled automatically if logging is inactive. WARNING: images are "
                                    "150kb+ and are NOT deleted automatically, this option is intended for capture of "
                                    "test data only and will consume a lot of hard drive space compared "
                                    "to standard log files.  This option should be turned off for standard use.")
        self.initialize_from_file()

    def _set_default_log_file_path(self, config_dir):
        # DEV NOTE: join and abspath used over split due to uncertainty over config path ending in a slash
        parent_dir = abspath(join(config_dir, ".."))
        self._default_log_path = join(parent_dir, self.LOG_DIR_NAME)

    def _get_log_file_dir(self):
        if self.log_path.value().strip() == "":
            return self._default_log_path
        return self.log_path.value()

    def get_log_file_path(self):
        """
        Get the path to the log file based on the contents of the config file and the location of the configuration dir.
        :return: A string representing the file path of the log file.
        """
        dir_path = self._get_log_file_dir()
        self._check_make_dirs(dir_path)
        return join(dir_path, self.LOG_FILE_NAME)

    def get_image_log_dir(self):
        """
        Returns a string path to an image directory in the log directory.  If the directory does not currently exist
        it is generated.
        """
        image_dir = join(self._get_log_file_dir(), self.LOG_IMAGE_DIR)
        self._check_make_dirs(image_dir)
        return image_dir

    def get_log_level(self):
        return self.LOG_LEVEL_DICT[self.log_level.value()]

    @staticmethod
    def _check_make_dirs(image_dir):
        if not exists(image_dir) or not isdir(image_dir):
            try:
                makedirs(image_dir)
            except OSError:
                logging.error("Could not create find/create directory, path may be invalid: " + image_dir)
                exit(1)
