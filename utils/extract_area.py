"""
This module provides methods for extracting areas of images
and either write it to a png file or return it as a matrix.
"""

import argparse
import cv2
from datastructure.models import Coordinates

OFFSET = 0 # How many extra pixels outside the ROI should be included

def area_from_file(input_path, output_path, area: Coordinates):
    """
    Reads an image file, extracts the area of interest and saves it as a new image.
    """
    original_image = cv2.imread(input_path)
    roi_matrix = original_image[area.y0-OFFSET:area.y1+OFFSET, area.x0-OFFSET:area.x1+OFFSET]
    cv2.imwrite(output_path, roi_matrix)

def extract_area_from_matrix(original_image, output_path, area: Coordinates):
    """
    Reads an image matrix, extracts the area of interest and saves it as a new image.
    """
    roi_matrix = original_image[area.y0-OFFSET:area.y1+OFFSET, area.x0-OFFSET:area.x1+OFFSET]
    cv2.imwrite(output_path, roi_matrix)

def extract_matrix_from_matrix(original_image, area: Coordinates):
    """
    Reads an image matrix, extracts the area of interest and returns it as a new matrix.
    """
    return original_image[area.y0-OFFSET:area.y1+OFFSET, area.x0-OFFSET:area.x1+OFFSET]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("x0")
    parser.add_argument("y0")
    parser.add_argument("x1")
    parser.add_argument("y1")
    argv = parser.parse_args()

    roi = Coordinates(argv.x1, argv.y1, argv.x2, argv.y2)
    area_from_file(argv.input, argv.output, roi)
