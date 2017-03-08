from Tkconstants import X, DISABLED, NORMAL
from Tkinter import Tk, Button


class ExtendedFocusServiceGUI(Tk):
    def __init__(self, ext_focus_service):
        """
        Lays out a GUI for the Extended Focus Service -
        :param services.extended_focus_service.ExtendedFocusService ext_focus_service:
        """
        Tk.__init__(self, "Extended Focus Service", None, "ExtendedFocusServiceGUI")
        self._service = ext_focus_service
        self.wm_title("Extended Focus Service")
        self.button_start = Button(self, text="Start", command=self._start_service)
        self.button_start.pack(fill=X, padx=2, pady=2)
        self.button_stop = Button(self, text="Stop", command=self._stop_service)
        self.button_stop.pack(fill=X, padx=2, pady=2)
        self.button_force_stop = Button(self, text="Force Stop", command=self._force_stop_service)
        self.button_force_stop.pack(fill=X, padx=2, pady=2)
        self._start_service()

    def destroy(self):
        if self._service.is_connected():
            self._stop_service()
        Tk.destroy(self)

    # Button functions

    def _start_service(self):
        self.button_start["state"] = DISABLED
        self.button_stop["state"] = NORMAL
        self.button_force_stop["state"] = NORMAL
        self._service.start()

    def _stop_service(self):
        # TODO: user feedback for shutdown
        self.button_stop["state"] = DISABLED
        self.button_force_stop["state"] = DISABLED
        self._service.safe_stop()
        self.button_start["state"] = NORMAL

    def _force_stop_service(self):
        self.button_stop["state"] = DISABLED
        self.button_force_stop["state"] = DISABLED
        self._service.force_stop()
        self.button_start["state"] = NORMAL