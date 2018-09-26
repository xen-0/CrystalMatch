

class Pyramid:
    "A data structure which consists of levels. Each level contains an image of a different resolution than other layers."

    def __init__(self):
        self.levels = []

    def add_level(self, level):
        self.levels.append(level)

    def get_level(self, level_number):
        "lowest level of the pyramid hes the highest resolution and number 0"
        #self.levels.sort(key=lambda level : level.get_number)
        for level in self.levels:
            if level.get_level_number() == level_number:
                return level
