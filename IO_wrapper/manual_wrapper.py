from knox_source_data_io.io_handler import *
from knox_source_data_io.models.model import Model
import os
import text_extraction_example
import datetime

class Manual(Model):
    """
    Data structure for manuals.
    """
    publisher: str
    published_at: str
    title: str
    sections: []

    def __init__(self, values: dict = None, **kwargs):
        values = values if values is not None else kwargs
        self.text = []
    
    #def __init__(self, file_sections):
        #self.sections = file_sections

class Section():
    """
    Data structure for sections in the manuals.
    """
    header: str
    pages: []
    paragraphs: []

    def __init__(self, section_header, section_span, file_paragraphs):
        self.header = section_header
        self.pages = section_span
        self.paragraphs = file_paragraphs

class Paragraph():
    """
    Data structure for text paragraphs in the manuals.
    """
    pages: []
    text: str
    
    def __init__(self, paragraph_span, file_text):
        self.pages = paragraph_span
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



def create_output(PDF_pages:, schema_path, output_path):
    """
    Creates the output to JSON.
    """

    export_able_object = convert_objects()

    # Generate
    handler = IOHandler(Generator(app="GrundfosManuals_Handler", generated_at=datetime.datetime.now(), version="1.0"), schema_path)
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, outputPath) #Rename when we know what the location is
    
    # Serialize object to json
    with open(filename, 'w', encoding='utf-16') as outfile:
        handler.write_json(export_able_object, outfile)

