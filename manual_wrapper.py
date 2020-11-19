from knox_source_data_io.io_handler import *
from knox_source_data_io.models.model import Model
import os
import text_extraction_example
import datetime

# Make an object which holds information about the content
# It should be expanded and iterated upon when we have more work
class Manual(Model):
    publisher: str
    published_at: str
    title: str
    sections: []

    def __init__(self, file_publisher, file_published_at, file_title, file_sections):
        self.publisher = file_publisher
        self.published_at = file_published_at
        self.title = file_title
        self.sections = file_sections

class Section():
    header: str
    pages: []
    paragraphs: []

    def __init__(self, section_header, section_span, file_paragraphs):
        self.header = section_header
        self.pages = section_span
        self.paragraphs = file_paragraphs

class Paragraph():
    pages: []
    text: str
    
    def __init__(self, paragraph_span, file_text):
        self.pages = paragraph_span
        self.text = file_text

class Illustration():
    pages: []
    image_bytes: str

class Figure(Illustration):

    def __init__(self, page_span, figure_bytes):
        self.pages = page_span
        self.image_bytes = figure_bytes

class Table(Illustration):

    def __init__(self, page_span, table_bytes):
        self.pages = page_span
        self.image_bytes = table_bytes

# Input: Some object, schema location, output path (the written output)
def create_output(manual, schema_path, output_path):
    #Fill with more information here
    export_object = Manual()

    # Generate
    handler = IOHandler(Generator(app="Grundfos_manuals_handler", generated_at=datetime.datetime.now(), version=1.0), schema_path)
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, output_path) #Rename when we know what the location is
    
    # Serialize object to json
    with open(filename, 'w', encoding='utf-8') as outfile:
        handler.write_json(export_object, outfile)
