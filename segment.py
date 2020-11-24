import classification.infer as infer
import utils.pdf2png as pdf2png
import utils.ExtractArea as ExtractArea
import argparse
import os
import shutil
import json
import cv2


def segment_document(input_path: str, min_score: float):
    pages = []
    tmp_dir = os.path.join(os.getcwd(), "tmp", os.path.basename(input_path).replace(".pdf", ""))
    os.makedirs(tmp_dir)
    pdf2png.convert(input_path, tmp_dir)

    for filename in os.listdir(tmp_dir):
        if filename.endswith(".png"):
            pages.append(infer_page(filename))
        else:
            continue

    #shutil.rmtree(tmp_dir)


            

def infer_page(image_path: str, min_score: float = 0.7):
    # (titles, tables, figures)
    pageData = ([], [], [], os.path.basename(image_path).split("_page")[1]) #TODO: Make split more unique, so that files that naturally include "_page" do not fail

    prediction = infer.infer_image(image_path)

    for pred in prediction:
        for idx, mask in enumerate(pred['masks']):
            label = infer.CATEGORIES2LABELS[pred["labels"][idx].item()]
            
            if pred['scores'][idx].item() < min_score:
                continue

            t_index = -1

            if label == "title":
                t_index = 0
            elif label == "table":
                t_index = 1
            elif label == "figure":
                t_index = 2
            else:
                continue

            # area = (x0, y0, x1, y1)
            area = list(map(int, pred["boxes"][idx].tolist()))
            score = pred["scores"][idx].item()

            pageData[t_index].append((area, score))

            image = cv2.imread(image_path)
            ExtractArea.extract_area_from_matrix(image, image_path.split(".png")[0] + label + idx, area[0], area[1],area[2], area[3])
            
            
    return pageData



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    argv = parser.parse_args()
    segment_document(argv.input, 0.7)