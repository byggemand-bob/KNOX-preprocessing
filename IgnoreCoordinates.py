from datastructure.models import Coordinates

class IgnoreCoordinates:
    Pages = {}

    def AddCoordinates(self, PageNum, x0, y0, x1, y1):
        """Converts x0, y0, x1, y1 into class coordinates and adds to ignore coordinates for PageNum"""
        self.AddCoordinates(PageNum, Coordinates(x0, y0, x1, y1))

    def AddCoordinates(self, PageNum, Coordinates):
        """Add Coordinates to specefic page ignore list"""
        #Coordinates should be a class Coordinates
        if PageNum in self.Pages:
            self.Pages[PageNum].append(Coordinates)
        else:
            self.Pages.update({PageNum : [Coordinates]})

    def PageCoordinates(self, PageNum):
        """returns Ignore Coordinate List of page"""
        if PageNum in self.Pages:
            return self.Pages[PageNum]
        else:
            return []
