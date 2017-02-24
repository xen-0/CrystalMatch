from subprocess32 import TimeoutExpired, Popen, PIPE

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

    def run(self, target_dir, output_path):
        """
        Attempt to run Helicon Focus in a shell to focus-stack images in the target directory.  There is a timeout
        value set in the configuration file which is required because Helicon Focus does not fully support
        automation - if an error occurs it is displayed in a pop-up text box which must be manually dismissed
        causing the process to hang.
        :param target_dir: Directory containing images to be combined into an extended focus image.
        :param output_path: path to which output will be written (must be tif or jpg extension).
        :return: Exit value of the script - 0 for success, 1 for error.
        """
        cmd_line = '"' + self._exe_path + '" '
        cmd_line += '-silent -noprogress '
        cmd_line += '-mp:' + str(self._method) + ' '
        cmd_line += '-rp:' + str(self._radius) + ' '
        cmd_line += '-sp:' + str(self._smoothing) + ' '
        cmd_line += '-save:"' + output_path + '" '
        cmd_line += '"' + target_dir + '"'
        process = None
        try:
            process = Popen(cmd_line, stdout=PIPE, shell=True)
            return process.wait(timeout=self._timeout)
            # return call(cmd_line, shell=True, timeout=self._timeout)
        except TimeoutExpired:
            # TODO: Check files exist and are accessible - prevent unnecessary timeout if we know this is going to fail
            # FIXME: A Helicon process gets left running at this point.  Work out how to shut it down to prevent
            #        them building up on the server.
            if process is not None:
                process.kill()
            return 1
