import fitz
import os

local_path_to_start_directory = os.getcwd()
local_path_to_pdf_folder = os.getcwd() + "\\PDFs"

zoom = 3    # Set resolution here
mat = fitz.Matrix(zoom, zoom)

for root, dirs, files in os.walk(local_path_to_pdf_folder):
    for file in files:
        if file.endswith(".pdf"):

            pdfName = os.path.basename(file)

            #Convert to image:
            doc = fitz.open(local_path_to_pdf_folder + "\\" + pdfName)
            number_of_pagess = doc.pageCount

            os.chdir(local_path_to_start_directory + "\\Output_Images\\")

            for x in range(number_of_pagess):
                page = doc.loadPage(x)
                pix = page.getPixmap(matrix = mat)
                outputName = pdfName.replace(".pdf", "") + str(x+1) + ".png"
                pix.writePNG(outputName)