from util.image import Color
from .config import Config


class ConfigItem:
    """ Represents a single option/configuration item which is essentially a name/value pair.
    This class should be sub-classed in order to handle different types of value.
    """

    OUTPUT_LINE = line = "{}" + Config.DELIMITER + "{}"

    def __init__(self, tag, default):
        """ Initialize a new config item.

        Parameters
        ----------
        tag - The 'name' of this option, used as an identifier when saved to file and in the UI.
        default - the default value of this option.
        """
        self._value = None
        self._tag = tag
        self._default = default
        self._comment = None

    def value(self):
        """ Get the value of this option. """
        return self._value

    def tag(self):
        """ Get the tag (string name) of this option. """
        return self._tag

    def comment(self):
        """ Get the comment string for this item. """
        return self._comment

    def set(self, value):
        """ Set the value of this option. """
        self._value = self._clean(value)

    def set_comment(self, comment):
        """ Set the comment string for this item. """
        self._comment = comment

    def reset(self):
        """ Set the value of this option to its default. """
        self._value = self._default

    def to_file_string(self):
        """ Creates a string representation that can be saved to and read from file. """
        if self._comment is not None:
            comment_lines = Config.create_comment_lines(self._comment)
            comment = "".join(comment_lines)
            file_string = comment + self.OUTPUT_LINE.format(self._tag, self._value)
        else:
            file_string = self.OUTPUT_LINE.format(self._tag, self._value)

        return file_string

    def from_file_string(self, value_string):
        """ Read the value from its string representation. """
        pass

    def _clean(self, value):
        """ Perform any additional cleanup/processing on the value. Implement in subclass if needed. """
        return value


class IntConfigItem(ConfigItem):
    """ Config item that stores an integer. Constructor may also take a 'units' parameter which is a
    string that represents the units of the value. This can be used in the UI.
    """
    def __init__(self, tag, default, units=""):
        ConfigItem.__init__(self, tag, default)
        self._units = units

    def units(self):
        """ The unit type of the value. """
        return self._units

    def from_file_string(self, string):
        self._value = self._clean(string)

    def _clean(self, value):
        try:
            return int(value)
        except ValueError:
            return self._default


class RangeIntConfigItem(IntConfigItem):
    def __init__(self, tag, default, range=[0,100]):
        IntConfigItem.__init__(self, tag, default)
        if len(range) != 2:
            raise ValueError("range must be a list of 2 elements")

        self._min = range[0]
        self._max = range[1]

        if not self._in_range(default):
            raise ValueError("default must be between {} and {} inclusive".format(self._min, self._max))

    def min(self): return self._min

    def max(self): return self._max

    def _clean(self, value):
        try:
            val = int(value)
        except ValueError:
            return self._default

        if self._in_range(val):
            return val
        else:
            return self._default

    def _in_range(self, value):
        return self._min <= value <= self._max


class FloatConfigItem(ConfigItem):
    """ Config item that stores a float.
    """
    def __init__(self, tag, default):
        ConfigItem.__init__(self, tag, default)

    def from_file_string(self, string):
        self._value = self._clean(string)

    def _clean(self, value):
        try:
            return float(value)
        except ValueError:
            return self._default


class RangeFloatConfigItem(FloatConfigItem):
    def __init__(self, tag, default, limits=[0.0, 1.0]):
        """ Config item that stores a float with a limited range of values. Limits must contain two ordered
        numbers that represent the inclusive range. Either limit can be set to None, if you only want to
        bound the float on one side. """
        FloatConfigItem.__init__(self, tag, default)
        if len(limits) != 2:
            raise ValueError("range must be a list of 2 elements")

        self._min = limits[0]
        self._max = limits[1]

        if not self._in_range(default):
            raise ValueError("default must be between {} and {} inclusive".format(self._min, self._max))

    def min(self): return self._min

    def max(self): return self._max

    def _clean(self, value):
        try:
            val = float(value)
        except ValueError:
            return self._default

        if self._in_range(val):
            return val
        else:
            return self._default

    def _in_range(self, value):
        ok = True
        if self._min is not None:
            ok &= self._min <= value

        if self._max is not None:
            ok &= value <= self._max

        return ok


class DirectoryConfigItem(ConfigItem):
    """ Config item that stores a directory path (can be relative or absolute). """
    def __init__(self, tag, default):
        ConfigItem.__init__(self, tag, default)

    def from_file_string(self, string):
        self._value = self._clean(string)

    def _clean(self, value):
        value = str(value).strip()
        if not value.endswith("/"):
            value += "/"
        return value


class ColorConfigItem(ConfigItem):
    """ Config item that stores a color. """
    def __init__(self, tag, default):
        ConfigItem.__init__(self, tag, default)

    def from_file_string(self, string):
        self._value = Color.from_string(string)


class BoolConfigItem(ConfigItem):
    """ Config item that stores a boolean value. """
    def __init__(self, tag, default):
        ConfigItem.__init__(self, tag, default)

    def from_file_string(self, string):
        self._value = True if string.lower() == 'true' else False


class EnumConfigItem(ConfigItem):
    """ Config item that stores an enum value. """
    def __init__(self, tag, default, enum_values):
        ConfigItem.__init__(self, tag, default)
        self.enum_values = enum_values

        if default not in enum_values:
            self._default = self.enum_values[0]

    def from_file_string(self, string):
        self._value = self._clean(string)

    def _clean(self, value_str):
        value_str = str(value_str).strip()
        for val in self.enum_values:
            if value_str == str(val):
                return val

        return self._default
