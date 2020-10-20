from knox_source_data_io.io_handler import *
from knox_source_data_io.models.model import Model
import os

def main():

    # Make an object which holds information about the content
    # It should be expanded and iterated upon when we have more work
    class Manual(Model):
        text: str

        def __init__(self, values: dict = None, **kwargs):
            values = values if values is not None else kwargs
            self.text = ""

    # Create object and properties
    # Here we should use our tools to crate the objects. 
    export_able_object = Manual()
    export_able_object.text = "Here is some text"

    # Generate
    handler = IOHandler(Generator(app="GrundfosManuals_Handler", version=1.0), "/manuals.schema.json")
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
    handler = IOHandler(Generator(app="GrundfosManuals_Handler", version=1.0), schemaPath)
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'output.json') #Rename when we know what the location is
    
    # Serialize object to json
    with open(filename, 'w', encoding='utf-8') as outfile:
        handler.write_json(export_able_object, outfile)