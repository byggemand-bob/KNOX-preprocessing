class TextSegment(): 
    def __init__(self, coordinates, header, value):
        self.coordinates = coordinates
        self.header = header
        self.value = value


class ImageSegment():
    def __init__(self, coordinates, value):
        self.coordinates = coordinates
        self.byte_value = value


class TableSegment():
    def __init__(self, coordinates, value):
        self.coordinates = coordinates
        self.byte_value = value


class Coordinates(): 
    def __init__(self, x1, x2, y1, y2): 
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2