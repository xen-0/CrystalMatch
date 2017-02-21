from os.path import join

from dls_util.config.config import Config
from dls_util.config.item import StringItem, IntConfigItem


class ExtendedFocusConfig(Config):
    """
    Configuration file for the extended focus services. The service is designed to run a script to combine
    multiple images into a single image of optimum focus. It communicates over the network using the STOMP protocol.
    """
    CONFIG_FILE_NAME = "ext_focus_service.ini"

    def __init__(self, config_dir):
        Config.__init__(self, join(config_dir, self.CONFIG_FILE_NAME))

        add = self.add

        self.set_title("Extended Focus Service Configuration File")
        self.set_comment("Configuration options for the Extended Focus Service which combines a stack of "
                         "images with different focal lengths into an optimum or extended-focus image.")

        self.host = add(StringItem, "Host", "localhost")
        self.host.set_comment("Address of the STOMP broker (Active MQ server or similar).")

        self.port = add(IntConfigItem, "Port", 61613)
        self.port.set_comment("Port number for the STOMP broker (Active MQ server or similar).")

        self.path_conversions = add(StringItem, "File Path Conversions", "dls@//dc/dls")
        self.path_conversions.set_comment("This service was originally designed to run on a Windows machine "
                                          "within the Diamond network. GDA provides network paths in Linux "
                                          "style which need to be converted for use on Windows - by default "
                                          "/dls will be converted to //dc/dls. Additional entries can be "
                                          "added by appending a semi-colon (;), the @ symbol denotes the "
                                          "conversion from left to right.")

        self.initialize_from_file()
