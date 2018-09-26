import cv2

class Pyramid:
    "A data structure which consists of levels. Each level contains an image of a different resolution than other layers."

    def __init__(self, layer):
        self.levels = []
        self.layer = layer

    def get_layer_number(self):
        return self.layer

    def add_lower_level(self, level):
        self.levels.append(level)

    def add_upper_level(self, level):
        self.levels.insert(0, level)

    def get_level(self, level_number):
        "lowest level of the pyramid hes the highest resolution and number 0"
        for level in self.levels:
            if level.get_level_number() == level_number:
                return level
    def get_top_level(self):
        for level in self.levels:
            if level.get_level_number() == len(self.levels)-1:
                return level

    def collapse(self):
        """Collapse the pyramid - effectively flatten a fused pyramid along levels to get one all in focus image."""
        image = self.get_top_level().get_array()
        for level_number in range(len(self.levels)-2, 0, -1):
            expanded = cv2.pyrUp(image)
            level = self.get_level(level_number).get_array()
            image = expanded + level

        return image