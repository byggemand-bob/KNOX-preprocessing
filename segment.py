import os
import shutil
import argparse
import copy
import cv2
import classification.infer as mi
import utils.pdf2png as pdf2png
import utils.extract_area as extractArea
import datastructure.models as datastructures

def segment_document(input_path: str, min_score: float):
    """
    Does document segmentation of a pdf file and produces a json file with the information found.
    """
    pages = []
    tmp_dir = os.path.join(os.getcwd(), "tmp", os.path.basename(input_path).replace(".pdf", ""))
    os.makedirs(tmp_dir)
    pdf2png.convert(input_path, tmp_dir)

    for filename in os.listdir(tmp_dir):
        if filename.endswith(".png"):
            mi_page = infer_page(os.path.join(tmp_dir, filename))

        else:
            continue

    shutil.rmtree(tmp_dir)


def infer_page(image_path: str, min_score: float = 0.7) -> datastructures.Page:
    """Acquires tables and figures from MI-inference of documents."""
    #TODO: Make split more unique, so that files that naturally include "_page" do not fail
    page_data = datastructures.Page(os.path.basename(image_path).split("_page")[1])
    image = cv2.imread(image_path)
    prediction = mi.infer_image_from_matrix(image)

    for pred in prediction:
        for idx in enumerate(pred['masks']):
            label = mi.CATEGORIES2LABELS[pred["labels"][idx].item()]
            
            if pred['scores'][idx].item() < min_score:
                continue

            area = convert2coords(image, list(map(int, pred["boxes"][idx].tolist())))
            #score = pred["scores"][idx].item()

            if label == "table":
                table = datastructures.TableSegment(area)
                page_data.tables.append(table)
            elif label == "figure":
                image = datastructures.ImageSegment(area)
                page_data.images.append(image)
            else:
                continue

            # image = cv2.imread(image_path)
            # extractArea.extract_area_from_matrix(image, image_path.split(".png")[0] + label + str(idx) + ".png", area)

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
    for object1 in list1.objects:
        for object2 in list2.objects:
            if object1.coordinates.area() >= object2.coordinates.area():
                if (object2.coordinates.x1 >= object1.coordinates.x1 and
                    object2.coordinates.x2 <= object1.coordinates.x2 and
                    object2.coordinates.y1 >= object1.coordinates.y1 and
                    object2.coordinates.y2 <= object1.coordinates.y2):

                    list2.objects.remove(object2)
            else:
                if (object1.coordinates.x1 >= object2.coordinates.x1 and
                    object1.coordinates.x2 <= object2.coordinates.x2 and
                    object1.coordinates.y1 <= object2.coordinates.y1 and
                    object1.coordinates.y2 >= object2.coordinates.y2):

                    list1.objects.remove(object1)
                    break

if __name__ == "__main__":
    # page1 = datastructures.Page(1)
    # page1.tables.append(datastructures.TableSegment(datastructures.Coordinates(0,0,100,100)))
    # page2 = datastructures.Page(1)
    # page2.tables.append(datastructures.TableSegment(datastructures.Coordinates(25,25,75,75)))

    # print(len(page1.tables))
    # for table in page1.tables:
    #     print(table.coordinates.to_string())

    # print(len(page2.tables))
    # for table in page2.tables:
    #     print(table.coordinates.to_string())

    # page3 = merge_pages(page1, page2)

    # print(len(page3.tables))
    # for table in page3.tables:
    #     print(table.coordinates.to_string())
    # exit()

    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    argv = parser.parse_args()
    segment_document(argv.input, 0.7)
