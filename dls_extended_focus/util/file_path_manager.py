import platform

from os.path import normpath

from services.extended_focus.ext_focus_config import PlatformEnumConfigItem


class FilePathManager:
    """
    Manages file paths for the Extended Focus Service and automatically converts between Windows
    and Linux network paths.
    """

    def __init__(self, config):
        """
        :param ExtendedFocusConfig config: Configuration instance.
        """
        self._use_network_prefix = self._should_use_network_prefix(config)
        self._network_prefix = config.win_net_prefix.value()

        self._target_dir = None
        self._output_path = None

    @staticmethod
    def _should_use_network_prefix(config):
        """
        Based on the entry in the config file determine whether the Windows network prefix should be applied to
        file paths.
        :param ExtendedFocusConfig config: Configuration instance.
        :return: Boolean.
        """
        option = config.platform_detection.value()
        if option is PlatformEnumConfigItem.CONFIG_AUTO:
            platform_name = platform.system()
            return platform_name == "Windows"
        elif option is PlatformEnumConfigItem.CONFIG_OFF:
            return False
        elif option is PlatformEnumConfigItem.CONFIG_WINDOWS:
            return True

    def set_target_dir(self, target_path):
        """
        Sets the target directory path.
        """
        self._target_dir = target_path

    def set_output_path(self, output_path):
        """
        Set the output path.
        """
        self._output_path = output_path

    def target_dir(self):
        return self._convert_path(self._target_dir)

    def output_path(self):
        return self._convert_path(self._output_path)

    def original_output_path(self):
        return self._output_path

    def _convert_path(self, path):
        """
        Convert a path to a Windows network path.
        :param path: Path to convert.
        :return: Windows network path for the input path.
        """
        if self._use_network_prefix:
            norm_path = normpath(path)
            path = self._network_prefix
            if not norm_path.startswith("\\"):
                path += "\\"
            path += norm_path
        return path
