import pdfminer.layout
from datastructure.models import Coordinates

class CoordinatesCalculator:
    # All CoordinatesCalculator's calculations assumes the coordinates is set up like in PDFMiner i.e.
    # (x0,y0) is the lowest left corner, and (x1,y1) is the upper right
    # X coordinates are, distance from left edge, and y coordinates are distance from bottom edge
    def CreateCoordinates(self, x0, y0, x1, y1):
        """converts varibles  x0, y0, x1, y1 into Coordinates class"""
        return Coordinates(x0, y0, x1, y1)

    def ConvertObjectToCoordinates(self, Object: pdfminer.layout.LTComponent):
        """converts PDFminer object into a Coordinate class"""
        return Coordinates(Object.x0, Object.y0, Object.x1, Object.y1)

    def CompareVerticalDist(self, x, y):
        """Returns the vertical distance of x compared to y, positive num means x is above y, negative meaning below, and 0 meas x and y overlap vertically"""
        #test if x bottom-most coordinate is higher then y topmost coordiante.
        if x.y0 > y.y1:
            return x.y0 - y.y1
        #test if x topmost coordinate is lower then y bottom-most coordinate
        elif x.y1 < y.y0:
            return x.y1 - y.y0
        else:
            return 0

    def CompareHorizontalDist(self, x, y):
        """Returns the horizontal distance of x compared to y, positive num means x is further right y, negative meaning further left, and 0 meas x and y overlap horizontally"""
        #test if x leftmost coordinate is further right then y rightmost coordinate
        if x.x0 > y.x1:
            return x.x0 - y.x1
        #test if X rightmost coordinate if further left then y leftmost coordinate
        elif x.x1 < y.x0:
            return x.x1 - y.x0
        else:
            return 0

    def IsObjectWithinCoordinateList(self, ObjectsCoordinates, CoordinateList):
        """returns true if object is within or partially within any of the coordiantes in CoordinateList"""
        for Coords in CoordinateList:
            if self.IsObjectWithinCoordinates(ObjectsCoordinates, Coords) >= 0:
                return True

        return False

    def IsObjectWithinCoordinates(self, ObjectsCoords, TestCoords):
        """Will return 1 if the ObjectCoords is within TestCoords, -1 if not, and 0 if partially"""
        #assuming that the most likely senario is that the object isn't within the coordinates
        #this is what we'll check for first

        #is the the objects left most coordinate, further right then the right most test-coordinate.
        if ObjectsCoords.x0 > TestCoords.x1:
            return -1

        #is the objects bottom most coordinates, higher then the top most test-coordinate
        if ObjectsCoords.y0 > TestCoords.y1:
            return -1

        #is the objects right most coordinate, further left the left most test-coordinate
        if ObjectsCoords.x1 < TestCoords.x0:
            return -1

        #is the objects top most coordinate, lower then the bottom most test-coordinate
        if ObjectsCoords.y1 < TestCoords.y0:
            return -1
        
        #If nothing above was true then, the object can only be within or partially with the test-coordinates
        #now we'll check if any edge of the object bleeds over the edge of the test-coordinates

        #Checks if the objects left most cordinate is further left then the left most test-coordinate 
        if ObjectsCoords.x0 < TestCoords.x0:
            return 0

        #Checks if the objects Bottom most cordinate is further down then the bottom most test-coordinate 
        if ObjectsCoords.y0 < TestCoords.y0:
            return 0

        #Checks if the objects right most cordinate is further right then the right most test-coordinate 
        if ObjectsCoords.x1 > TestCoords.x1:
            return 0

        #Checks if the objects top most cordinate is further up then the top most test-coordinate 
        if ObjectsCoords.y1 > TestCoords.y1:
            return 0

        #if nothing above is true, then the object must be within the test-coordinates
        return 1