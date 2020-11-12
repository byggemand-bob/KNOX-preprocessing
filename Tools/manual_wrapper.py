from knox_source_data_io.io_handler import *
from knox_source_data_io.models.model import Model
import os

# Make an object which holds information about the content
# It should be expanded and iterated upon when we have more work
class Manual(Model):
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

# Input: Some object, schema location, output path (the written output)
def create_output(manual, schemaPath, outputPath):
    #Fill with more information here
    export_able_object = Manual()
    
    # Generate
    handler = IOHandler(Generator(app="GrundfosManuals_Handler", generated_at="", version="1.0"), schemaPath)
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, outputPath) #Rename when we know what the location is
    
    # Serialize object to json
    with open(filename, 'w', encoding='utf-8') as outfile:
        handler.write_json(export_able_object, outfile)

#def create_objects():
    #If the data is not in the models in this file,
    #Create some function to do so here