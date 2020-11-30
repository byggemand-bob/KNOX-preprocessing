class SegPDF:
    PDFtitle = ""
    PDFSubTitle = ""
    Text = ""
    
    def __init__(self):
        self.Sections = []

    def AddSection(self, section):
        self.Sections.append(section)

class Section:
    Title = ""
    Text = ""
    StartingPage = None
    EndingPage = None

    def __init__(self):
        self.Sections = []

    def AddSection(self, section):
        self.Sections.append(section)

