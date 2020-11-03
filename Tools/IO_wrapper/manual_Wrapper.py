from knox_source_data_io.io_handler import *
from knox_source_data_io.models.model import Model
import os
import proc

def main():

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
        
        def __init__(self, sections):
            self.sections = sections

    class Section():
        pages: []
        paragraphs: []

        def __init__(self, paragraphs):
            self.pages = [1,2,3]
            self.paragraphs = paragraphs


    class Paragraph():
        pages: []
        text: str
        
        def __init__(self, string):
            self.pages = [1,2,3]
            self.text = string

    # Create object and properties
    # Here we should use our tools to crate the objects. 
    text = proc.extractLines()
    file_string_array = []
    for string in text:
        file_string_array.append(string)

    file_sections = Section(Paragraph(file_string_array))
    export_able_object = Model()
    export_able_object.publisher = "Grundfos A/S"
    export_able_object.published_at = "Somewhere"
    export_able_object.title = "Some pump"
    export_able_object.sections = file_sections
 

    
    # export_able_object.text = proc.extractLines()

    # Generate
    handler = IOHandler(Generator(app="GrundfosManuals_Handler", generated_at="idk", version="1.0"), "/manuals.schema.json")
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'output.json')

    # Serialize object to json
    with open(filename, 'w', encoding='utf-8') as outfile:
        handler.write_json(export_able_object, outfile)
    print("Json written to output.json")

    # Deserialize json to object
    #with open(filename, 'r', encoding='utf-8') as json_file:
    #obj: Wrapper = handler.read_json(json_file)
    #print("Json read from output.json")

if __name__ == "__main__":
    main()

# Input: Some object, schema location, output path (the written output)
def create_Output(Manual, schemaPath, outputPath):
    export_able_object = Manual()

    # Generate
    handler = IOHandler(Generator(app="GrundfosManuals_Handler", generated_at="", version="1.0"), schemaPath)
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'output.json') #Rename when we know what the location is
    
    # Serialize object to json
    with open(filename, 'w', encoding='utf-8') as outfile:
        handler.write_json(export_able_object, outfile)