import numpy as np
import cv2
import os
import shutil
import argparse


def extract_area_from_file(inputPath, outputPath, x0, y0, x1, y1):
    originalImage = cv2.imread(inputPath)
    offset = 20
    ROI = originalImage[y0-offset:y1+offset, x0-offset:x1+offset]
    cv2.imwrite(outputPath, ROI)

def extract_area_from_matrix(originalImage, outputPath, x0, y0, x1, y1):
    offset = 20
    ROI = originalImage[y0-offset:y1+offset, x0-offset:x1+offset]
    cv2.imwrite(outputPath, ROI)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("x0")
    parser.add_argument("y0")
    parser.add_argument("x1")
    parser.add_argument("y1")
    argv = parser.parse_args()

if not os.path.exists(argv.input):
    exit()

extract_area_from_file(argv.input, argv.output, argv.x0, argv.y0, argv.x1, argv.y1)

