"""
This module provides datastructures for pages and page-elements
"""

class Coordinates:
    """
    Describes an area defined by two sets of coordinates.
    """
    def __init__(self, x1: int, y1 : int, x2: int, y2: int):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def to_string(self) -> str:
        """
        Return the coordinates in string format.
        """
        return "({0}, {1})({2}, {3})".format(self.x1, self.y1, self.x2, self.y2)

    def area(self) -> int:
        """
        Calculates and returns the size of the area spanning the coordinates.
        """
        return abs(self.x1 - self.x2) * abs(self.y1 - self.y2)

class TextSegment:
    """
    Describes a textsegment found on a page.
    """
    def __init__(self, coordinates, header, value):
        self.coordinates = coordinates
        self.header = header
        self.value = value


class ImageSegment:
    """
    Describes an imagesegment found on a page.
    """
    byte_value = None
    coordinates: Coordinates = None
    page_number: int
    def __init__(self, coordinates):
        self.coordinates = coordinates


class TableSegment:
    """
    Describes a tablesegment found on a page.
    """
    byte_value = None
    coordinates: Coordinates = None
    page_number: int
    def __init__(self, coordinates: Coordinates):
        self.coordinates = coordinates

class Page:
    """
    Contains the content of a page.
    """
    def __init__(self, page_number: int):
        self.page_number = page_number
        self.text_sections = []
        self.images = []
        self.tables = []

    def add_from_page(self, page):
        """
        Adds the content of a page to this page.
        """
        self.text_sections.extend(page.text_sections)
        self.images.extend(page.images)
        self.tables.extend(page.tables)

        self.tables.extend(page.tables)
    
    def add_from_page_manuel(self, text_sections, images, tables):
        """
        Adds the content of a page to this page.
        """
        self.text_sections.extend(text_sections)
        self.images.extend(images)
        self.tables.extend(tables)