import platform

from os.path import normpath


class PlatformDetectionException(Exception):
    def __init__(self, *args, **kwargs):
        super(PlatformDetectionException, self).__init__(*args, **kwargs)
        self.message = "Platform detection failed - please set the platform in the configuration file."


class FilePathManager:
    """
    Manages file paths for the Extended Focus Service and automatically converts between Windows
    and Linux network paths.
    """

    def __init__(self, windows_network_prefix, is_windows=None):
        """
        :param windows_network_prefix: The network prefix to add to paths on Windows machines.
        :param is_windows: Boolean value, if this is declared it will override the automatic detection of Windows.
        """
        self._windows_network_prefix = windows_network_prefix
        platform_name = platform.system()
        if platform_name == "Windows" or platform_name == "Linux":
            self._is_windows = (platform_name == "Windows") if is_windows is None else is_windows
        else:
            raise PlatformDetectionException()
        self._target_dir = None
        self._output_path = None

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
        if self._is_windows:
            norm_path = normpath(path)
            path = self._windows_network_prefix
            if not norm_path.startswith("\\"):
                path += "\\"
            path += norm_path
        return path
