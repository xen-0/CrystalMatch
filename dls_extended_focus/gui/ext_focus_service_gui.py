from Tkconstants import X, DISABLED, NORMAL, SUNKEN, Y, LEFT, W
from Tkinter import Tk, Button, LabelFrame, Entry, StringVar, Label


class ExtendedFocusServiceGUI(Tk):
    def __init__(self, ext_focus_service):
        """
        Lays out a GUI for the Extended Focus Service -
        :param services.extended_focus_service.ExtendedFocusService ext_focus_service:
        """
        Tk.__init__(self, "Extended Focus Service", None, "ExtendedFocusServiceGUI")
        self._service = ext_focus_service
        self.wm_title("Extended Focus Service")

        # Controls Frame
        self.frm_controls = LabelFrame(self, text="Controls", borderwidth=1, relief=SUNKEN)
        self.button_start = Button(self.frm_controls, text="Start", command=self._start_service)
        self.button_start.pack(fill=X, padx=2, pady=2)
        self.button_stop = Button(self.frm_controls, text="Stop", command=self._stop_service)
        self.button_stop.pack(fill=X, padx=2, pady=2)
        self.button_force_stop = Button(self.frm_controls, text="Force Stop", command=self._force_stop_service)
        self.button_force_stop.pack(fill=Y, padx=2, pady=2)
        self.frm_controls.pack(fill=Y, side=LEFT, padx=2, pady=2)

        # Test Request Frame
        self.frm_request = LabelFrame(self, text="Send Request", borderwidth=1, relief=SUNKEN)

        self.val_job_id = self._create_field(self.frm_request, "Job ID", "TEST_00000")
        self.val_target_dir = self._create_field(self.frm_request, "Target Dir", "")
        self.val_target_dir = self._create_field(self.frm_request, "Output Path", "")

        self.button_send_req = Button(self.frm_request, text="Send Request", command=self._send_request())
        self.button_send_req.pack(fill=X, padx=2, pady=2)
        self.frm_request.pack(fill=X, padx=2, pady=2)

        self._start_service()

    @staticmethod
    def _create_field(parent, label_txt, default_val):
        """
        Create a a label and field pair returning the StringVar object which will be tied to it.
        :param parent: The parent element to which this field will be added.
        :param label_txt: Text for label.
        :param default_val: Default value for text box.
        :return: The StringVal for the text box.
        """
        string_var = StringVar()
        string_var.set(default_val)
        label = Label(parent, text=label_txt, anchor=W)
        label.pack(fill=X, padx=2, pady=2)
        entry_box = Entry(parent, textvariable=string_var)
        entry_box.pack(fill=X, padx=2, pady=2)
        return string_var

    def destroy(self):
        if self._service.is_connected():
            self._stop_service()
        Tk.destroy(self)

    # Button functions

    def _send_request(self):
        # TODO: send request
        pass

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
