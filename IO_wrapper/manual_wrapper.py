from knox_source_data_io.io_handler import *
from knox_source_data_io.models.model import Model
import os
import text_extraction_example
import datetime
import SegmentedPDF

class Schema_Manual(Model):
    """
    Data structure for manuals.
    """
    def __init__(self, pdf_title, publisher, published_at, pdf_sections):
        self.title = pdf_title
        self.publisher = publisher
        self.published_at = published_at
        self.sections = pdf_sections
        

class Schema_Section():
    """
    Data structure for sections in the manuals.
    """
    def __init__(self, section_header, section_pages, file_paragraphs):
        self.header = section_header
        self.pages = section_pages
        self.paragraphs = file_paragraphs

class Schema_Paragraph():
    """
    Data structure for text paragraphs in the manuals.
    """    
    def __init__(self, file_text):
        self.text = file_text

class Illustration():
    pages: str
    path: str

class Figure(Illustration):

    def __init__(self, page_span, figure_path):
        self.pages = page_span
        self.path = figure_path

class Table(Illustration):

    def __init__(self, page_span, table_path):
        self.pages = page_span
        self.path = table_path


def convert_objects(file_pages):
    """
    Used to convert from data structures in models.py to the models in this file for json serrialization
    """
    
    return Manual()


def create_output(segmented_PDF: SegmentedPDF.SegPDF, schema_path, output_path):
    """
    Creates the output to JSON.
    """
    output_sections = []

    for section in segmented_PDF:
        paragraph = Schema_Paragraph(section.Text)
        span = [1,2]
        output_section.append(Schema_Section(section.Title, paragraph))
    

    export_able_object = Schema_Manual(segmented_PDF.PDFtitle, "Grundfos", "", output_sections)

    # Generate
    handler = IOHandler(Generator(app="GrundfosManuals_Handler", generated_at=datetime.datetime.now(), version="1.0"), schema_path)
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, output_path) #Rename when we know what the location is
    
    # Serialize object to json
    with open(filename, 'w', encoding='utf-16') as outfile:
        handler.write_json(export_able_object, outfile)