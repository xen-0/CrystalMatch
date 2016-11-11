from os.path import join

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

    """
    Configuration class that holds application level settings such as logging options etc.
    """
    def __init__(self, config_dir):
        Config.__init__(self, join(config_dir, 'settings.ini'))

        add = self.add

        self.set_title("Crystal Match App Settings")
        self.set_comment("Configuration file for the application - contains settings which affect the application "
                         "itself such as options for outputting logs.")

        self.logging = add(BoolConfigItem, "Activate Logging", True)
        self.logging.set_comment("Turns file logging on and off.")

        self.log_path = add(DirectoryConfigItem, "Log directory", "")
        self.log_path.set_comment("Sets the directory in which log files are stored. Leaving this blank will set the "
                                  "default path - log files will be stored in a directory called 'logs' next to the "
                                  "current config directory.")

        self.log_level = add(EnumConfigItem, "Log Level", default=self.LOG_LEVEL_INFO, extra_arg=self.LOG_LEVEL_LIST)
        self.log_level.set_comment("Sets the log level for the log files being generated.")

        self.log_max_file_size = add(RangeIntConfigItem, "Log File Size Limit (MB)", default=500, extra_arg=[1, None])
        self.log_max_file_size.set_comment("The maximum file size for a single log file - a new log file will be "
                                           "created once the current file exceeds this size.")

        self.log_images = add(BoolConfigItem, "Log Match Images", False)
        self.log_images.set_comment("Option to output an image capture of each crystal match. NOTE: images are "
                                    "150kb+, this option will consume a lot of hard drive space "
                                    "compared to standard log files.")
        self.initialize_from_file()
