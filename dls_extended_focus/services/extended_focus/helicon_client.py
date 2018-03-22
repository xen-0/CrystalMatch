# noinspection PyPackageRequirements
from subprocess32 import TimeoutExpired, Popen, PIPE

from services.extended_focus.error_codes import HELICON_TIMEOUT_ERR, HELICON_ERR
from services.extended_focus.helicon_config import HeliconConfig


class HeliconRunner:
    # TODO: Document subprocess32
    def __init__(self, config_dir):
        self._config = HeliconConfig(config_dir)
        self._exe_path = self._config.path.value()
        self._method = self._config.method.value()
        self._smoothing = self._config.smoothing.value()
        self._radius = self._config.radius.value()
        self._timeout = self._config.timeout.value()

    def run(self, response, file_manager):
        """
        Attempt to run Helicon Focus in a shell to focus-stack images in the target directory.  There is a timeout
        value set in the configuration file which is required because Helicon Focus does not fully support
        automation - if an error occurs it is displayed in a pop-up text box which must be manually dismissed
        causing the process to hang.
        :param ExtendedFocusServiceResponse response: An response object pre-prepared with information about
        the ActiveMQ request.
        :param FilePathManager file_manager: File manager which returns local filepaths.
        :return ExtendedFocusServiceResponse: An updated response object which will be returned to the broker.
        """
        # Build command line
        cmd_line = '"' + self._exe_path + '" '
        cmd_line += '-silent -noprogress '
        cmd_line += '-mp:' + str(self._method) + ' '
        cmd_line += '-rp:' + str(self._radius) + ' '
        cmd_line += '-sp:' + str(self._smoothing) + ' '
        cmd_line += '-save:"' + file_manager.output_path() + '" '
        cmd_line += '"' + file_manager.target_dir() + '"'

        # Attempt to run Helicon Focus
        process = None
        try:
            process = Popen(cmd_line, stdout=PIPE, shell=True)
            return_val = process.wait(timeout=self._timeout)
            # return call(cmd_line, shell=True, timeout=self._timeout)
            if return_val != 0:
                response.set_err_message(HELICON_ERR)
        except TimeoutExpired:
            # FIXME: A Helicon process gets left running at this point.  Work out how to shut it down to prevent
            #        them building up on the server.
            if process is not None:
                process.kill()
            response.set_err_message(HELICON_TIMEOUT_ERR)

        return response
