class Coordinates:
    """
    Describes an area defined by two sets of coordinates.
    """
    def __init__(self, x0: int, y0 : int, x1: int, y1: int):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    def to_string(self) -> str:
        """
        Return the coordinates in string format.
        """
        return "({0}, {1})({2}, {3})".format(self.x0, self.y0, self.x1, self.y1)

    def area(self) -> int:
        """
        Calculates and returns the size of the area spanning the coordinates.
        """
        return abs(self.x0 - self.x1) * abs(self.y0 - self.y1)