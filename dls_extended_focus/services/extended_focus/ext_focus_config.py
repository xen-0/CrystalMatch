import logging
from os.path import join

from dls_util.config.config import Config
from dls_util.config.item import StringItem, IntConfigItem, EnumConfigItem


class PlatformEnumConfigItem(object, EnumConfigItem):
    CONFIG_AUTO = "AUTO"
    CONFIG_WINDOWS = "WINDOWS"
    CONFIG_OFF = "OFF"
    DETECTION_SETTINGS = [CONFIG_AUTO, CONFIG_WINDOWS, CONFIG_OFF]


class LogLevelEnumConfigItem(object, EnumConfigItem):
    ERROR = "ERROR"
    INFO = "INFO"
    DEBUG = "DEBUG"
    OFF = "OFF"
    LOG_LEVEL_SETTINGS = [ERROR, INFO, DEBUG, OFF]

    def value(self):
        value = super(LogLevelEnumConfigItem, self).value()
        if value is self.ERROR:
            return logging.ERROR
        elif value is self.INFO:
            return logging.INFO
        elif value is self.DEBUG:
            return logging.DEBUG
        else:
            return None


class ExtendedFocusConfig(Config):
    """
    Configuration file for the extended focus services. The service is designed to run a script to combine
    multiple images into a single image of optimum focus. It communicates over the network using the STOMP protocol.
    """
    CONFIG_FILE_NAME = "ext_focus_service.ini"

    def __init__(self, config_dir):
        self._config_dir = config_dir
        Config.__init__(self, join(config_dir, self.CONFIG_FILE_NAME))

        add = self.add

        self.set_title("Extended Focus Service Configuration File")
        self.set_comment("Configuration options for the Extended Focus Service which combines a stack of "
                         "images with different focal lengths into an optimum or extended-focus image.")

        self.host = add(StringItem, "Host", "localhost")
        self.host.set_comment("Address of the STOMP broker (Active MQ server or similar).")

        self.port = add(IntConfigItem, "Port", 61613)
        self.port.set_comment("Port number for the STOMP broker (Active MQ server or similar).")

        self.platform_detection = add(EnumConfigItem, "Platform Detection",
                                      PlatformEnumConfigItem.CONFIG_AUTO,
                                      PlatformEnumConfigItem.DETECTION_SETTINGS)
        self.platform_detection.set_comment("By default the app will try to determine if the Windows platform is "
                                            "being used and append a prefix to file paths to account for a modified "
                                            "network path.  This app was written to support a Linux path format and "
                                            "it is assumed that to run on a Windows device a mapped drive or "
                                            "alternative network path must be used.  The Windows Network Prefix can "
                                            "be used to set the prefix.  If the value is OFF then both setting "
                                            "will be ignored, the value WINDOWS will force it's use.")

        self.win_net_prefix = add(StringItem, "Windows Network Prefix", "\\\\dc")
        self.win_net_prefix.set_comment("This service will be called from a Linux environment but may run on "
                                        "Windows.  If Platform Detection is set to WINDOWS or AUTO and Windows is "
                                        "detected this prefix will be added to all filepaths received by the service.")

        self.log_level = add(EnumConfigItem, "Log level",
                             LogLevelEnumConfigItem.DEBUG, LogLevelEnumConfigItem.LOG_LEVEL_SETTINGS)
        self.log_level.set_comment("Sets the logging level")

        self.log_length = add(IntConfigItem, "Log length (hours)", 672)
        self.log_length.set_comment("Sets the length of log records - the default is 28 days")

        self.initialize_from_file()

    def parent_directory(self):
        return self._config_dir
