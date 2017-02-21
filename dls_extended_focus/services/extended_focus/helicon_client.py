from subprocess import call

from services.extended_focus.helicon_config import HeliconConfig


class HeliconRunner:
    def __init__(self, config_dir):
        self._config = HeliconConfig(config_dir)
        self._exe_path = self._config.path.value()
        self._method = self._config.method.value()
        self._smoothing = self._config.smoothing.value()
        self._radius = self._config.radius.value()

    def run(self, target_dir, output_path):
        cmd_line = '"' + self._exe_path + '" '
        cmd_line += '-silent -noprogress '
        cmd_line += '-mp:' + str(self._method) + ' '
        cmd_line += '-rp:' + str(self._radius) + ' '
        cmd_line += '-sp:' + str(self._smoothing) + ' '
        cmd_line += '-save:"' + output_path + '" '
        cmd_line += '"' + target_dir + '"'
        return call(cmd_line, shell=True)
