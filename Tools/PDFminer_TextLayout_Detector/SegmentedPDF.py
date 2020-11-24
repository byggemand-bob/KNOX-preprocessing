class SegPDF:
    PDFtitle = ""
    PDFSubTitle = ""
    Text = ""
    Sections = []

    def AddSection(self, section):
        self.Sections.append(section)

class Section:
    Title = ""
    Text = ""
    Sections = []

    def AddSection(self, section):
        self.Sections.append(section)

