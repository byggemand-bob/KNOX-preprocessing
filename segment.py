import os
import argparse
import copy
import cv2
import concurrent.futures as cf
import IO_handler
from TextAnalyser import TextAnalyser
from SegmentedPDF import SegPDF
import miner
import classification.infer as mi
import utils.pdf2png as pdf2png
import utils.extract_area as extract_area
import datastructure.models as datastructures
import IO_wrapper.manual_wrapper as wrapper

def segment_documents(args: str, min_score: float):
    """
    Does document segmentation of a pdf file and produces a json file with the information found.
    """
    IO_handler.folder_prep(args.output, args.clean)
    pdf2png.convert_dir_to_files(args.input, os.path.join(args.output, 'images'))

    for file in os.listdir(args.input):
        if file.endswith('.pdf'):
            segment_document(file, args)

def segment_document(file: str, args):
    pages = []
    text_pages = []
    IgnoreCoords = IgnoreCoordinates()
    current_PDF = miner.PDF_file(file, args)
    for page in current_PDF.pages:
        miner.SearchPage(page, args)
        miner.Flip_Y_Coordinates(page)
        miner.LookThroughLineLists(page, args)
        miner.Check_Text_Objects(page)

        image_path = os.path.join(os.getcwd(), 'out', 'images', page.image_name)
        page1 = miner.make_page(page)
        page2 = infer_page(image_path)
        result_page = merge_pages(page1, page2)
        produce_data_from_coords(result_page, image_path)
        pages.append()

       
        for image in page.LTImageList:
            IgnoreCoords.AddCoordinates(page.image_number, image)
        for figure in page.LTRectList:
            IgnoreCoords.AddCoordinates(page.image_number, figure)
        for table in page.TableCoordinates:
            IgnoreCoords.AddCoordinates(page.image_number, table)

        pages.append([element.text_Line_Element for element in page.LTTextLineList])

    TextAnalyzer = TextAnalyser(pages)
    analyzed_text = TextAnalyzer.SegmentText()

    #Create output
    schema_path = "/schema/manuals_v1.1.schema.json"
    output_path = "/"
    wrapper.create_output(analyzed_text, current_PDF.file_name, schema_path, output_path)

def infer_page(image_path: str, min_score: float = 0.7) -> datastructures.Page:
    """
    Acquires tables and figures from MI-inference of documents.
    """
    #TODO: Make split more unique, so that files that naturally include "_page" do not fail
    page_data = datastructures.Page(int(os.path.basename(image_path).split("_page")[1].replace('.png','')))
    image = cv2.imread(image_path)
    prediction = mi.infer_image_from_matrix(image)

    for pred in prediction:
        for idx, mask in enumerate(pred['masks']):
            label = mi.CATEGORIES2LABELS[pred["labels"][idx].item()]
            
            if pred['scores'][idx].item() < min_score:
                continue
            area = convert2coords(image, list(map(int, pred["boxes"][idx].tolist())))
            #score = pred["scores"][idx].item()

            if label == "table":
                table = datastructures.TableSegment(area)
                page_data.tables.append(table)
            elif label == "figure":
                figure = datastructures.ImageSegment(area)
                page_data.images.append(figure)
            else:
                continue

    return page_data

def convert2coords(image, area: list) -> datastructures.Coordinates:
    """
    Converts coordinates from MI-inference format to fit original image format.
    """
    rat = image.shape[0] / 1300
    return datastructures.Coordinates(int(area[0] * rat), int(area[1] * rat),
                                      int(area[2] * rat), int(area[3] * rat))

def merge_pages(page1: datastructures.Page, page2: datastructures.Page) -> datastructures.Page:
    """
    Merges the contents of two page datastructures into one and checks for duplicate elements.
    """
    if page1.page_number != page2.page_number:
        raise Exception("Pages must have the same page-number.")

    # Copies pages to not delete any of the original data
    page1_cpy = copy.deepcopy(page1)
    page2_cpy = copy.deepcopy(page2)
    result = datastructures.Page(page1.page_number)

    # Remove duplicates
    remove_duplicates(page1_cpy.tables, page2_cpy.tables)
    remove_duplicates(page1_cpy.images, page2_cpy.images)

    # Merge page1 and page2 into results.
    result.add_from_page(page1_cpy)
    result.add_from_page(page2_cpy)
    return result

def remove_duplicates(list1: list, list2: list):
    """
    Removes elements that reside in other elements. These would be redundant if left in.
    """
    for object1 in list1:
        for object2 in list2:
            print(str(object1.coordinates.x1))
            print(str(object2.coordinates.x1))
            if (object2.coordinates.x0 >= object1.coordinates.x0 and
                object2.coordinates.x1 <= object1.coordinates.x1 and
                object2.coordinates.y0 >= object1.coordinates.y0 and
                object2.coordinates.y1 <= object1.coordinates.y1):

                list2.remove(object2)

            elif (object1.coordinates.x0 >= object2.coordinates.x0 and
                object1.coordinates.x1 <= object2.coordinates.x1 and
                object1.coordinates.y0 <= object2.coordinates.y0 and
                object1.coordinates.y1 >= object2.coordinates.y1):

                list1.remove(object1)
                break

def produce_data_from_coords(page, image_path):
    """
    Produces matrixes that represent seperate images for all tables and figures on the page.
    """
    image = cv2.imread(image_path)
    for table in page.tables:
        table.value = extract_area.extract_matrix_from_matrix(image, table.coordinates)
    for figure in page.images:
        figure.value = extract_area.extract_matrix_from_matrix(image, figure.coordinates)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="WIP")
    argparser.add_argument("-i", "--input", action="store", default=os.path.join(os.getcwd(), 'src'), help="Path to input folder")
    argparser.add_argument("-o", "--output", action="store", default=os.path.join(os.getcwd(), 'out'), help="Path to output folder")
    argparser.add_argument("-c", "--clean", action="store", type=bool, default=False, help="Activate nice mode.") #NOTE: What does this mean?
    args = argparser.parse_args()

    segment_documents(args, 0.7)

