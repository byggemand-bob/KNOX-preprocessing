from knox_source_data_io.io_handler import *
from knox_source_data_io.models.model import Model
import os
import datetime
import SegmentedPDF

class Schema_Manual(Model):
    """
    Data structure for manuals.
    """
    def __init__(self, pdf_title, publisher, published_at, pdf_sections):
        self.title = pdf_title
        self.publisher = publisher
        self.published_at = published_at #Can we get this information??
        self.sections = pdf_sections
        
class Schema_Section():
    """
    Data structure for sections in the manuals.
    """
    def __init__(self, section_header, section_pages, section_paragraphs, subsections):
        self.header = section_header
        self.pages = section_pages
        self.paragraphs = section_paragraphs
        self.subsections = subsections

class Schema_Paragraph():
    """
    Data structure for text paragraphs in the manuals.
    """    
    def __init__(self, file_text):
        self.text = file_text

class Figure():
    """
    Data structure for figures in manuals.
    """
    def __init__(self, page_span, figure_code):
        self.pages = page_span
        self.value = figure_code

class Table():
    """
    Data structure for the tables in manuals.
    """
    def __init__(self, page_span, table_code):
        self.pages = page_span
        self.value = table_code


def create_output(segmented_PDF: SegmentedPDF.SegPDF, schema_path, output_path):
    """
    Creates the output to JSON using knox-source-data-io module: https://git.its.aau.dk/Knox/source-data-io
    """
    output_sections = []
    for section in segmented_PDF.Sections:
        output_sections.append(visit_subsections(section))  

    export_able_object = Schema_Manual(segmented_PDF.PDFtitle, "Grundfos A/S", "", output_sections)

    # Generate
    handler = IOHandler(Generator(app="GrundfosManuals_Handler", generated_at= str(datetime.datetime.now()), version="1.1.0"), schema_path)
    dirname = os.path.dirname(__file__) #Change if the output is args-controlled
    filename = os.path.join(dirname, str("segmented_PDF.PDFtitle" + "_output.json")) #Rename when we know what the location is
    
    # Serialize object to json
    with open(filename, 'w', encoding='utf-16') as outfile:
        handler.write_json(export_able_object, outfile)


def visit_subsections(root: SegmentedPDF.Section):
    """
    Recursive visitor for the sections and their subsections.
    """
    schema_section = []
    if root.Sections is not None:
        for section in root.Sections:
            paragraph = Schema_Paragraph(section.Text)
            page = str(str(section.StartingPage) + "-" + str(section.EndingPage))
            schema_section.append(Schema_Section(section.Title, page, paragraph, visit_subsections(section)))
        return schema_section
    return None