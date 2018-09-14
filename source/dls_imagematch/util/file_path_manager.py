from os.path import normpath, exists, isdir, splitext

from services.extended_focus.error_codes import INVALID_OUT_PATH_ERR


class FilePathManager:
    """
    Manages file paths for the Extended Focus Service and automatically converts between Windows
    and Linux network paths.
    """

    ALLOWED_OUTPUT_EXTENSIONS = [".jpg", ".jpeg", ".tif", ".tiff"]

    def __init__(self):
        self._path = None

    def set_path(self, path):
        """
        Set the path.
        """
        self._path = path

    def get_path(self):
        """
        Get the path.
        """
        return self._path

    def validate(self):
        """
        Validate the current directories and return an error message if appropriate.
        :return: An error code and message or None.
        """
        if not self._validate_output_path_extension():
            return INVALID_OUT_PATH_ERR, "Output path is invalid, must have the correct file " \
                   "extension " + self._get_allowed_file_extensions_str() + ": " + self._path()
        #elif not self._validate_target_dir():
            #return INVALID_TARGET_DIR_ERR, "Target directory cannot be reached: " + self.target_dir()
        return None, None

    def _get_allowed_file_extensions_str(self):
        output = "("
        for ext in self.ALLOWED_OUTPUT_EXTENSIONS:
            output += ext + ", "
        return output[:(len(output) - 2)] + ")"

    def _validate_output_path_extension(self):
        file_path, ext = splitext(self._path())
        return ext in self.ALLOWED_OUTPUT_EXTENSIONS
