"""This module provides datastructures for pages and page-elements"""

class TextSegment():
    def __init__(self, coordinates, header, value):
        self.coordinates = coordinates
        self.header = header
        self.value = value


class ImageSegment():
    byte_value = None
    coordinates = None
    page_number = None
    def __init__(self, coordinates, page_number):
        self.coordinates = coordinates
        self.page_number = page_number


class TableSegment():
    byte_value = None
    coordinates = None
    page_number = None
    def __init__(self, coordinates):
        self.coordinates = coordinates  


class Coordinates(): 
    def __init__(self, x1, y1, x2, y2): 
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2


class Page():
    textSections = []
    images = []
    tables = []
    def __init__(self):
        pass
