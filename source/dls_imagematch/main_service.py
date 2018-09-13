from pkg_resources import require
require('pygelf==0.2.11')
require("numpy==1.11.1")
require("scipy")

import logging
import time

from dls_imagematch.service.parser_manager import ParserManager
from dls_imagematch.service import CrystalMatch
from dls_imagematch import logconfig

class CrystalMatchService:

    def __init__(self):
       pass

    def run(self):
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        total_start = time.clock()
        try:
            parser_manager = ParserManager()
            parser_manager.build_parser()
            config_directory = parser_manager.get_config_dir()
            scale_override = parser_manager.get_scale_override()
            to_json_flag = parser_manager.get_to_json()

            service = CrystalMatch(config_directory, scale_override=scale_override)
            service_results = service.perform_match(parser_manager)

            total_time = time.clock() - total_start
            service_results.log_final_result(total_time)
            service_results.print_results(to_json_flag)

        except IOError as e:
            log.error(e)

if __name__ == '__main__':
    logconfig.setup_logging()
    service = CrystalMatchService()
    service.run()