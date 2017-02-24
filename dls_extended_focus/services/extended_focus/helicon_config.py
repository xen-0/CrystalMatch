from os.path import join

from dls_util.config.config import Config
from dls_util.config.item import IntConfigItem, EnumConfigItem, StringItem


class HeliconConfig(Config):

    CONFIG_FILE_NAME = "ext_focus_helicon.ini"

    def __init__(self, config_dir):
        Config.__init__(self, join(config_dir, self.CONFIG_FILE_NAME))

        add = self.add

        self.set_title("Extended Focus Service - Helicon Focus Configuration File")
        self.set_comment("Command Line options for running Helicon Focus as a service. A full list of "
                         "the command-line parameters can be found on the HeliconSoft homepage "
                         "(http://www.heliconsoft.com/focus/help/english/HeliconFocus.html)")

        self.path = add(StringItem, "Helicon path",
                        default="C:\\Program Files\\Helicon Software\\Helicon Focus 6\\HeliconFocus.exe")
        self.path.set_comment("The local system path to the Helicon Focus exe.  The default value should be "
                              "sufficient for the 64-bit installer.")

        self.method = add(EnumConfigItem, "Method", default=2, extra_arg=[0, 1, 2])
        self.method.set_comment("Set Method (0=method A, 1=method B, 2=method C)\n\n"
                                "Method A computes the weight for each pixel based on its contrast and then "
                                "forms the weighted average of all pixels from all source images. This method "
                                "works better for short stacks and preserves contrast and color.\n\n"
                                "Method B selects the source image containing the sharpest pixel and uses "
                                "this information to form the \"depth map\". This method imposes strict "
                                "requirements on the order of images - it should always be consecutive. "
                                "Perfectly renders textures on smooth surfaces.\n\n"
                                "Method C uses pyramid approach to image processing dividing image signals "
                                "into high and low frequencies. Gives good results in complex cases ("
                                "intersecting objects, deep stacks), though increases contrast and glare.")

        self.radius = add(IntConfigItem, "Radius", 8)
        self.radius.set_comment("The Radius parameter is one of the two main controls to be adjusted, it is "
                                "only available in A and B methods.\n\nWhen performing focus stacking the "
                                "program analyses each pixel of the source image in order to define if it is "
                                "in focus. Then the detected focused areas from the whole stack are combined "
                                "into one output image. Radius is the control that regulates the size of the "
                                "analysed area around each pixel.")

        self.smoothing = add(IntConfigItem, "Smoothing", 4)
        self.smoothing.set_comment("Smoothing is the second of the two main focus stacking parameters for A and "
                                   "B methods. When analyzing the stack, the most sharply focused areas of the "
                                   "source images are found to be combined into one output image. For A method "
                                   "smoothing defines how these sharp areas will be combined. Low smoothing "
                                   "produces a sharper image, but the transition areas may have some artifacts. "
                                   "High smoothing will result in a slightly blurry image, though without any "
                                   "visible transition areas. For B method this value defines how depth map will "
                                   "be smoothed out.")

        self.timeout = add(IntConfigItem, "Timeout Period", 20)
        self.timeout.set_comment("The timeout period when calling Helicon Focus - the command line version of HF will "
                                 "hang if there is an error due to a message box which must be dismissed by hand.  We "
                                 "must time this out to prevent this stalling the service. NOTE: If the service is "
                                 "running correctly but is delayed this may cause the timeout to trigger.")

        self.initialize_from_file()
