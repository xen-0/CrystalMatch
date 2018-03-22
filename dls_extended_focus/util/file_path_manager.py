import platform
from os import walk
from os.path import normpath, exists, isdir, splitext

from services.extended_focus.error_codes import INVALID_OUT_PATH_ERR, INVALID_TARGET_DIR_ERR, EMPTY_TARGET_DIR_ERR
from services.extended_focus.ext_focus_config import PlatformEnumConfigItem


class FilePathManager:
    """
    Manages file paths for the Extended Focus Service and automatically converts between Windows
    and Linux network paths.
    """

    ALLOWED_OUTPUT_EXTENSIONS = [".jpg", ".jpeg", ".tif", ".tiff"]

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

    def validate(self):
        """
        Validate the current directories and return an error message if appropriate.
        :return: An error code and message or None.
        """
        if not self._validate_output_path():
            return INVALID_OUT_PATH_ERR, "Output path is invalid, must have the correct file " \
                   "extension " + self._get_allowed_file_extensions_str() + ": " + self.output_path()
        elif not self._validate_target_dir():
            return INVALID_TARGET_DIR_ERR, "Target directory cannot be reached: " + self.target_dir()
        elif not self._validate_target_dir_not_empty():
            return EMPTY_TARGET_DIR_ERR, "Valid file extensions " + self._get_allowed_file_extensions_str() + \
                   " not found: " + self.target_dir()
        return None, None

    def _get_allowed_file_extensions_str(self):
        output = "("
        for ext in self.ALLOWED_OUTPUT_EXTENSIONS:
            output += ext + ", "
        return output[:(len(output) - 2)] + ")"

    def _validate_target_dir_not_empty(self):
        for dir_path, dir_names, file_names in walk(self.target_dir()):
            for f in file_names:
                fn, ext = splitext(f)
                if ext in self.ALLOWED_OUTPUT_EXTENSIONS:
                    # At least one valid file exists
                    return True
            # We only want immediate children - return after one step of walk
            return False

    def _validate_target_dir(self):
        target_dir = self.target_dir()
        return exists(target_dir) and isdir(target_dir)

    def _validate_output_path(self):
        file_path, ext = splitext(self.output_path())
        return ext in self.ALLOWED_OUTPUT_EXTENSIONS

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
