from pdfminer.layout import LTTextLine, LTTextLineHorizontal, LTTextLineVertical, LTChar
import PDFminerLayoutExtractor
import PDFminerLineStreamer
import CoordinatesCalculator
import IgnoreCoordinates
from datastructure.models import Coordinates
import SegmentedPDF
import re
import sys

class TextAnalyser:
    __Pages__ = None
    __BlockTextFontSizes__ = None
    __NextLineIndex__ = None
    __PageIndex__ = None
    __LastLinesFontSize__ = -100000
    __CurrentText__ = None
    __CurrentTextStart__ = None
    __CurrentTextEnd__ = None
    __CurrentTextFontSize__ = None
    __FollowingLine__ = None
    
    def __init__(self, PDFpath, _IgnoreCoordinates: IgnoreCoordinates.IgnoreCoordinates):
        self.PDFpath = PDFpath
        self.IgnoreCoords = _IgnoreCoordinates
        self.CoordsCalc = CoordinatesCalculator.CoordinatesCalculator()
        LayoutExt = PDFminerLayoutExtractor.LayoutExtractor(PDFpath)
        self.LineStreamer = PDFminerLineStreamer.LineStreamer(LayoutExt.AllLayouts(), self.IgnoreCoords)

    def __Test2__(self):
        Page = self.LineStreamer.AllLinesFromPage(8)

        print("coords (%f , %f),(%f , %f).    text: %s" %(Page[1].x0, Page[1].y0, Page[1].x1, Page[1].y1, Page[1].get_text()[:-1]))
        print("coords (%f , %f),(%f , %f).    text: %s" %(Page[0].x0, Page[0].y0, Page[0].x1, Page[0].y1, Page[0].get_text()[:-1]))
        print(self.CoordsCalc.CompareHorizontalDist(Page[1], Page[0]))
        print(self.FontSize(Page[0]) * -2.5)
        print(self.CoordsCalc.CompareHorizontalDist(Page[1], Page[0]) < 0)
        print(self.CoordsCalc.CompareHorizontalDist(Page[1], Page[0]) < self.FontSize(Page[0]) * -2.5)
        print()
        x = 0

        for line in Page:
            print("line nr: %d    coords (%f , %f),(%f , %f).    text: %s" %(x, line.x0, line.y0, line.x1, line.y1, line.get_text()[:-1]))
            x += 1
            if not line.x0 < line.x1 and not line.y0 < line.y1:
                print("ERROR!!!")

        Columns = self.__FindColumns__(Page)

        for Column in Columns:
            print("\n#######################################################\nIn coords: (%f,%f),(%f,%f):" % (Column[0].x0, Column[0].y0, Column[0].x1, Column[0].y1))
            for line in Column[1]:
                print(line.get_text()[:-1])

        print("\n########################################################################")
        print("####################### Sorted Columns #################################")
        print("########################################################################")

        Columns = self.__SortColumns__(Columns)

        for Column in Columns:
            print("\n#######################################################\nIn coords: (%f,%f),(%f,%f):" % (Column[0].x0, Column[0].y0, Column[0].x1, Column[0].y1))
            for line in Column[1]:
                print(line.get_text()[:-1])

    def __Test__(self):
        PDF = self.SegmentText()

        print("TITLE:")
        print(PDF.PDFtitle)
        print()
        print("SubTitle:")
        print(PDF.PDFSubTitle)
        print()

        for section in PDF.Sections:
            self.TestPrintSections(section, 0)

    def TestPrintSections(self, Section, section_level):

        subnum = ""

        for x in range(0, section_level):
            subnum += "SUB"

        print(subnum + "-SECTION:")
        if Section.Title == "":
            print("TITLE: ~~~No Title~~~")
        else:
            print("TITLE: " + Section.Title)
        print("SectionPage: " + str(Section.StartingPage) + ", " + str(Section.EndingPage))

        print("Section Text:\n" + Section.Text)

        for SubSection in Section.Sections:
            if SubSection == Section:
                print("\n###################################### ERROR #################################################")
                print("###################################### ERROR #################################################")
                print("###################################### ERROR #################################################")
                print("           infinite loop subsection error. One of the section subsections is itself")
                print("###################################### ERROR #################################################")
                print("###################################### ERROR #################################################")
                print("###################################### ERROR #################################################\n")
                break
            self.TestPrintSections(SubSection, section_level + 1)

    def SegmentText(self):
        PDF = SegmentedPDF.SegPDF()
        SortedPages = []

        # Iterates though all pages, sorting all text into columns and ordering them
        for x in range(0, self.LineStreamer.NumOfPages):
            Page = self.LineStreamer.AllLinesFromPage(x)
            PageColumns = self.__FindColumns__(Page)
            PageColumns = self.__SortColumns__(PageColumns)
            SortedPages.append(PageColumns)

        PDF.PDFtitle, PDF.PDFSubTitle = self.__FindTitle__(SortedPages[0])

        self.__PrepareSectioning__(SortedPages)

        self.__FindSections__(PDF)

        return PDF

    def __PrepareSectioning__(self, SortedPages):
        """does nessesary setup for section segmentation to begin"""
        self.__Pages__ = []
        for page in SortedPages:
            self.__Pages__.append([line for column in page for line in column])
        
        self.__NextLineIndex__ = 0
        self.__PageIndex__ = 0

        self.__BlockTextFontSizes__ = self.__FindBlockTextFontSizes__(self.__Pages__[0])
        self.__NextLine__()

    def __FindSections__(self, PDF):
        self.__NextText__()

        while self.__CurrentText__ != None:
            NewSection = SegmentedPDF.Section()

            if self.__IsSimularSizeInList__(self.__CurrentTextFontSize__, self.__BlockTextFontSizes__, 0.01):
                NewSection.Text = self.__CurrentText__
                NewSection.StartingPage = self.__CurrentTextStart__
                NewSection.EndingPage = self.__CurrentTextEnd__
                PDF.Sections.append(NewSection)
                self.__NextText__()
            else:
                NewSection.Title = self.__CurrentText__
                TitleFontSize = self.__CurrentTextFontSize__
                NewSection.StartingPage = self.__CurrentTextStart__
                self.__NextText__()
                self.__FindSubSections____(NewSection, TitleFontSize)
                PDF.Sections.append(NewSection)

    def __FindSubSections__(self, CurrentSection, TitleFontSize):
        while self.__CurrentText__ != None:
            if self.__IsSimularSizeInList__(self.__CurrentTextFontSize__, self.__BlockTextFontSizes__, 0.01):
                CurrentSection.Text += self.__CurrentText__
                self.__NextText__()
            elif self.__IsSimularFontSize__(self.__CurrentTextFontSize__, TitleFontSize, 0.01) or TitleFontSize < self.__CurrentTextFontSize__:
                CurrentSection.EndingPage = self.__CurrentTextEnd__
                return
            else:
                NewSection = SegmentedPDF.Section()
                NewSection.Title = self.__CurrentText__
                NewSectionTitleFontSize = self.__CurrentTextFontSize__
                NewSection.StartingPage = self.__CurrentTextStart__
                self.__NextText__()
                self.__FindSubSections____(NewSection, NewSectionTitleFontSize)
                CurrentSection.Sections.append(NewSection)
        
        CurrentSection.EndingPage = self.__CurrentTextEnd__

    def __NextText__(self):
        """Groups all sequential text of simular fontsize, saving results in self.__CurrentText__ and self.__CurrentTextFontSize__"""
        if self.__FollowingLine__ != None:
            self.__CurrentTextFontSize__ = self.FontSize(self.__FollowingLine__)
            self.__CurrentText__ = self.__FollowingLine__.get_text()
            self.__CurrentTextStart__ = self.__PageIndex__ + 1

            self.__NextLine__()

            while self.__IsSimularFontSize__(self.__CurrentTextFontSize__, self.FontSize(self.__FollowingLine__), 0.01):
                self.__CurrentText__ += self.__FollowingLine__.get_text()
                self.__NextLine__()
        else:
            self.__CurrentText__ = None
            self.__CurrentTextFontSize__ = None

        if self.__PageIndex__ < len(self.__Pages__):
            self.__CurrentTextEnd__ = self.__PageIndex__ + 1
        else:
            self.__CurrentTextEnd__ = len(self.__Pages__)

    def __NextLine__(self):
        """Find the next line and saves it in self.__FollowingLine__"""
        if self.__NextLineIndex__ < len(self.__Pages__[self.__PageIndex__]):
            self.__FollowingLine__ = self.__Pages__[self.__PageIndex__][self.__NextLineIndex__]
            self.__NextLineIndex__ += 1
            return
        else:
            self.__PageIndex__ += 1
            if self.__PageIndex__ < len(self.__Pages__):
                self.__BlockTextFontSizes__ = self.__FindBlockTextFontSizes__(self.__Pages__[self.__PageIndex__])
                self.__NextLineIndex__ = 0
                self.__NextLine__()
            else:
                self.__FollowingLine__ = None

    def __FindTitle__(self, FirstPage):
        LargestFontSize = 0

        #locates the line with largest fontsize on first page
        for ColumnIndex in range(0, len(FirstPage)):
            for LineIndex in range(0, len(FirstPage[ColumnIndex])):
                LineFontSize = self.FontSize(FirstPage[ColumnIndex][LineIndex])
                if LineFontSize > LargestFontSize:
                    LargestFontSize = LineFontSize
                    LargestColumnIndex = ColumnIndex
                    LargestLineIndex = LineIndex

        PDFTitle = ""
        PDFSubTitle = ""
        
        # iterates over the column with the largest fontsize line
        # adding anything of simular size as pdftitle
        # adding subsequent lines as Subtitle
        for line in FirstPage[LargestColumnIndex]:
            if self.__IsSimularFontSize__(self.FontSize(line), LargestFontSize, 0.3):
                PDFTitle += line.get_text()
            elif PDFTitle != "":
                PDFSubTitle += line.get_text()

        del FirstPage[LargestColumnIndex]

        return PDFTitle, PDFSubTitle        

    def __FindColumns__(self, Page):
        # Initializes first column
        AllColumns = []
        if len(Page) != 0:
            LastFontSize = self.FontSize(Page[0])
            ColumnLines = [Page[0]]
            ColumnCoords = self.CoordsCalc.ConvertObjectToCoordinates(Page[0])

            # test all lines on page after the first
            for x in range(1, len(Page)):
                VertDist = self.CoordsCalc.CompareVerticalDist(Page[x], ColumnCoords)
                HoriDist = self.CoordsCalc.CompareHorizontalDist(Page[x], ColumnCoords)

                # test whether the new line is above the column coords
                # or if its larger then 2.5 line gab, compared to lastline
                # or if the column doesn't vertically overlap
                if VertDist > 0 or VertDist < LastFontSize * -2.5 or HoriDist != 0:
                    # new column
                    Column = [ColumnCoords, ColumnLines]
                    AllColumns.append(Column)
                    ColumnLines = [Page[x]]
                    ColumnCoords = self.CoordsCalc.ConvertObjectToCoordinates(Page[x])
                    LastFontSize = self.FontSize(Page[x])
                else:
                    # Add to column
                    LastFontSize = self.FontSize(Page[x])
                    ColumnLines.append(Page[x])
                    ColumnCoords.y0 = Page[x].y0
                    if Page[x].x0 < ColumnCoords.x0:
                        ColumnCoords.x0 = Page[x].x0
                    if Page[x].x1 > ColumnCoords.x1:
                        ColumnCoords.x1 = Page[x].x1


            # adds last column to columns
            if len(ColumnLines) != 0:
                Column = [ColumnCoords, ColumnLines]
                AllColumns.append(Column)

        if len(AllColumns) > 0:
            return AllColumns
        else:
            return []

    def __SortColumns__(self, Columns):
        SortedColumns = []

        while len(Columns) != 0:
            SelectedColumnCoords = Columns[0][0]
            SelectedColumnIndex = 0

            for x in range(1, len(Columns)):
                # test if the current column is more then five points further to the left then the selected
                if Columns[x][0].x0 / 5 - SelectedColumnCoords.x0 / 5 < -1:
                    SelectedColumnCoords = Columns[x][0]
                    SelectedColumnIndex = x
                # tests if the current column is futher up on the page then the selected
                elif self.CoordsCalc.CompareVerticalDist(Columns[x][0], SelectedColumnCoords) > 0:
                    SelectedColumnCoords = Columns[x][0]
                    SelectedColumnIndex = x

            SortedColumns.append(Columns[SelectedColumnIndex])
            del Columns[SelectedColumnIndex]

        return [Columns[1] for Columns in SortedColumns]

    def __IsSimularSizeInList__(self, FontSize, FontSizeList, EM):
        """Returns true if there is a fontsize in FontSizeList, of simularsize to FontSize given the error margine(%) EM"""
        for _FontSize in FontSizeList:
            if self.__IsSimularFontSize__(FontSize, _FontSize, EM):
                return True

    def __FindBlockTextFontSizes__(self, Page):
        NumOflines = 0
        FontList = [(0,0)]

        for line in Page:
            NumOflines += 1
            self.__AddToFontList__(FontList, self.FontSize(line))

        del FontList[0]
        LowerBound = NumOflines / 4

        #filters out the fontsizes which didn't appear more then the LowerBound, and only keeps the fontsize
        return [Font[0] for Font in FontList if Font[1] > LowerBound]

    def __AddToFontList__(self, FontApperances, FontSize):
        for Apperance in FontApperances:
            if FontSize == Apperance[0]:
                Apperance[1] += 1
                return
        FontApperances.append([FontSize, 1])

    def __IsSimularFontSize__(self, FontA, FontB, EM):
        #EM = Error Margine in procent (e.g. 0.1 = 10% error margine)
        return FontA / FontB < 1 + EM and FontA / FontB > 1 - EM

    def FontSize(self, Textline):
        """returns Font size of textline"""
        if Textline == None:
            # isn't 0 to avoid needing to do additional checks, to avoid devide by zero errors in later calculations
            return 0.00000000001
        if isinstance(Textline, LTTextLineVertical):
            return round(Textline.x1 - Textline.x0, 4)
        return round(Textline.y1 - Textline.y0, 4)