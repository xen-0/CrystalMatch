import logging
from random import randint

import stomp
from stomp.exception import ConnectFailedException

from services.extended_focus.ext_focus_request_handler import ExtendedFocusServiceRequestHandler
from util.file_path_manager import FilePathManager


class ExtendedFocusService:
    INPUT_QUEUE = '/queue/vmxi_extended_focus_service.input'
    OUTPUT_QUEUE = '/topic/vmxi_extended_focus_service.output'

    def __init__(self, config):
        self._config = config
        self._id = randint(10000, 99999)  # TODO: optionally set in config var?
        self._host = self._config.host.value()
        self._port = self._config.port.value()
        self._connection = None
        self.log("Setting id: " + str(self._id))
        self._file_manager = FilePathManager(self._config)

    def start(self):
        if not self._is_connected():
            self._try_service_start()
        else:
            self.log("Service already active.")

    def maintain_connection(self):
        if not self._is_connected():
            self._try_service_start()

    def _is_connected(self):
        return self._connection is not None and self._connection.is_connected()

    def _try_service_start(self):
        try:
            self.log("Starting service, connecting to '" + self._host + ":" + str(self._port) + "'...")
            self._connection = stomp.Connection(host_and_ports=[(self._host, self._port)])
            self._connection.set_listener('Extended Focus Service',
                                          ExtendedFocusServiceRequestHandler(self._connection,
                                                                             self._file_manager,
                                                                             self.OUTPUT_QUEUE,
                                                                             self._config.parent_directory()))
            self._connection.start()
            self._connection.connect(wait=True)
            self._connection.subscribe(destination=self.INPUT_QUEUE, id=self._id, ack='client-individual')
        except ConnectFailedException as e:
            logging.error(e.message)

    @staticmethod
    def log(msg):
        logging.info("ExtendedFocusService: " + msg)
