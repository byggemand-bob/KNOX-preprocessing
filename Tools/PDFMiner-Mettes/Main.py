import os
import sys
import time
import fitz
import cv2
import numpy as ny
import shutil
from binascii import b2a_hex
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTText, LTChar, LTFigure, LTImage, LTRect, LTCurve, LTLine
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

local_path_to_start_directory = os.getcwd()
local_path_to_pdf_folder = local_path_to_start_directory + "\\PDFs\\"
local_path_to_image_folder = local_path_to_start_directory + "\\Images\\"
local_path_to_imageFilled_folder = local_path_to_start_directory + "\\ImagesFilled\\"
local_path_to_Figure_folder = local_path_to_start_directory + "\\Figures\\"

zoom = 3  # Set PNG resolution here
mat = fitz.Matrix(zoom, zoom)

start_time = time.time()

def main():
    DeleteImagesInFolder()
    ConvertPageToImage()

    os.chdir(local_path_to_start_directory)

    for root, dirs, files in os.walk(local_path_to_pdf_folder):
            for file in files:
                if file.endswith(".pdf"):

                    fileName = os.path.basename(file)

                    fp = open(local_path_to_pdf_folder + fileName, 'rb')
                    rsrcmgr = PDFResourceManager()
                    laparams = LAParams(detect_vertical=False)
                    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
                    pages = PDFPage.get_pages(fp)

                    #text_file = open(local_path_to_start_directory + "\\Text\\" + fileName.replace(".pdf", ".txt"), "wb")

                    PageNum = 1
                    for page in pages:
                        interpreter.process_page(page)
                        layout = device.get_result()
                        
                        #mediabox_text = ("0: " + str(page.mediabox[0]) + "1: " + str(page.mediabox[1]) + "2: " + str(page.mediabox[2]) + "3: " + str(page.mediabox[3]) + "\n")
                        #text_file.write(mediabox_text.encode(encoding='UTF-16',errors='strict'))
                        PDFfile_width = page.mediabox[2] #- 35
                        PDFfile_height = page.mediabox[3] #- 31

                        #Prerequisites for image processing
                        imageName = fileName.replace(".pdf", "") + str(PageNum) + ".png"

                        Firstimage = cv2.imread(local_path_to_image_folder + imageName)
                        height, width = Firstimage.shape[:2]

                        actualHeightModifier = height/PDFfile_height
                        actualWidthModifier = width/PDFfile_width

                        SearchPage(layout, imageName, PDFfile_height, PDFfile_width, actualHeightModifier, actualWidthModifier, Firstimage)
                        
                        PageNum = PageNum + 1

    print("Process finished --- %s seconds ---" % (time.time() - start_time))


def SearchPage(layout, imageName, PDFfile_height, PDFfile_width, actualHeightModifier, actualWidthModifier, Firstimage):
    
    #colorBlack = (255, 255, 255) #black - text
    colorBlack = (0, 0, 0) #black - text
    colorBlue = (255, 0, 0) #blue - figure
    colorGreen = (0, 255, 0) #green - image
    
    index = 1
    figureIndex = 1
    for lobj in layout:
        if isinstance(lobj, LTTextBox):

            #x0, y0, x1, y1, text = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3], lobj.get_text()

            for obj in lobj:
                if isinstance(obj, LTTextLine):

                    x0, y0, x1, y1, text = obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3], obj.get_text().rstrip("\n")

                    if not(text == "\n" or text == " " or text == "\t" or text == "  " or text == ""):# or text == "•" or text == "• "):

                        EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorBlack)
                        index = index + 1
                                        
                        #encodedText = text.encode(encoding='UTF-16',errors='strict')
                        #encodedCoords = ("At" + str(x0) + ", " + str(PDFfile_height-(y0-30)) + "\n").encode(encoding='UTF-16',errors='strict')
                        #encodedABCoords = ("And " + str(x1) + ", " + str(PDFfile_height-(y1-30)) + " is text:\n").encode(encoding='UTF-16',errors='strict')

                        # text_file.write(encodedCoords) #coords
                        # text_file.write(encodedABCoords) #coordsab
                        # text_file.write(encodedText) #text

                        # EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorBlack)
                        # index = index + 1

        elif isinstance(lobj, LTImage):
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]

            EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorGreen)
            SaveFigure(lobj, imageName, figureIndex)

            index = index + 1
            figureIndex = figureIndex + 1

        elif isinstance(lobj, LTFigure):
            for inner_obj in lobj:
                if isinstance(inner_obj, LTImage):
                    x0, y0, x1, y1 = inner_obj.bbox[0], inner_obj.bbox[1], inner_obj.bbox[2], inner_obj.bbox[3]

                    EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorGreen)
                    SaveFigure(inner_obj, imageName, figureIndex)

                    index = index + 1
                    figureIndex = figureIndex + 1
                
                elif isinstance(inner_obj, LTCurve):
                    x0, y0, x1, y1 = inner_obj.bbox[0], inner_obj.bbox[1], inner_obj.bbox[2], inner_obj.bbox[3]

                    EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorBlue)
                    #SaveFigure(inner_obj, imageName, figureIndex)

                    index = index + 1
                    figureIndex = figureIndex + 1


        elif isinstance(lobj, LTLine):
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]

            EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorBlue)
            #SaveFigure(lobj, imageName, figureIndex)

            index = index + 1
            figureIndex = figureIndex + 1

                        
        elif isinstance(lobj, LTRect):
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]

            EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorGreen)
            #SaveFigure(lobj, imageName, figureIndex)

            index = index + 1
            figureIndex = figureIndex + 1


def SaveFigure(lobj, imageName, figureIndex):
    file_stream = lobj.stream.get_rawdata()
    fileExtension = GetFileExtension(file_stream[0:4])

    if(fileExtension != None):
        figureName = imageName.replace(".png", "") + str(figureIndex) + fileExtension

        file_obj = open(local_path_to_Figure_folder + figureName, 'wb')
        file_obj.write(lobj.stream.get_rawdata())
        file_obj.close()


def GetFileExtension(stream_first_4_bytes):
    file_type = None
    bytes_as_hex = b2a_hex(stream_first_4_bytes).decode()
    if bytes_as_hex.startswith('ffd8'):
        file_type = '.jpeg'
    elif bytes_as_hex == '89504e47':
        file_type = ',png'
    elif bytes_as_hex == '47494638':
        file_type = '.gif'
    elif bytes_as_hex.startswith('424d'):
        file_type = '.bmp'
    return file_type


def EditImage(FileName, x0, y0, x1, y1, PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, color):
    # image = cv2.imread(local_path_to_image_folder + FileName)

    # height, width = image.shape[:2]

    # actualHeightModifier = height/PDFfile_height
    # actualWidthModifier = width/PDFfile_width

    start_point = (round(x0*actualWidthModifier), round(y0*actualHeightModifier))
    end_point = (round(x1* actualWidthModifier), round(y1*actualHeightModifier))

    # print(FileName)
    # print("PDF x0: " + str(x0))
    # print("PDF y0: " + str(y0))
    # print("PDF x1: " + str(x1))
    # print("PDF y1: " + str(y1))
    # print("Start p: " + str(start_point))
    # print("end p: " + str(end_point))

    # color = (0, 0, 0) 
    thickness = 3

    if(index == 1):
        image = cv2.rectangle(Firstimage, start_point, end_point, color, thickness)
    else:
        image = cv2.imread(local_path_to_imageFilled_folder + FileName)
        image = cv2.rectangle(image, start_point, end_point, color, thickness)

    cv2.imwrite(local_path_to_imageFilled_folder + FileName, image)


def DeleteImagesInFolder():
    shutil.rmtree(local_path_to_image_folder)
    shutil.rmtree(local_path_to_imageFilled_folder)
    shutil.rmtree(local_path_to_Figure_folder)

    os.mkdir(local_path_to_image_folder)
    os.mkdir(local_path_to_imageFilled_folder)
    os.mkdir(local_path_to_Figure_folder)


def ConvertPageToImage():
    for root, dirs, files in os.walk(local_path_to_pdf_folder):
        for file in files:
            if file.endswith(".pdf"):

                pdfName = os.path.basename(file)

                #Convert to image:
                doc = fitz.open(local_path_to_pdf_folder + "\\" + pdfName)
                number_of_pagess = doc.pageCount

                os.chdir(local_path_to_image_folder)

                for x in range(number_of_pagess):
                    page = doc.loadPage(x)
                    pix = page.getPixmap(matrix = mat)
                    outputName = pdfName.replace(".pdf", "") + str(x+1) + ".png"
                    pix.writePNG(outputName)


main()