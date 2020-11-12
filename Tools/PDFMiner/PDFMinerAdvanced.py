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
local_path_to_LineCoords_folder = local_path_to_start_directory + "\\LineCoords\\"

zoom = 3  # Set PNG resolution here
mat = fitz.Matrix(zoom, zoom)

start_time = time.time()

LTImageList = []
LTRectList = []
LTCurveList = []
LTLineList = []
LTTextLineList = []

TableLines = []

class PDFMinerObject:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

class LT_Line_Class(PDFMinerObject):
    
    def To_String(self):
        return "Coord: (({0}, {1}), ({2}, {3}))".format(round(self.x0), round(self.y0), round(self.x1), round(self.y1))

def main():
    DeleteImagesInFolder()
    print("Deleting and creating folders finished --- %s seconds ---" % (time.time() - start_time))

    ConvertPageToImage()
    print("Converting all PDF pages to PNGs finished --- %s seconds ---" % (time.time() - start_time))

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

                        #SearchPage(layout, imageName, PDFfile_height, PDFfile_width, actualHeightModifier, actualWidthModifier, Firstimage)
                        SearchPage(layout, imageName)
                        LookThroughLists(imageName.replace(".png", ""))
                        PaintPNGs(imageName, PDFfile_height, actualHeightModifier, actualWidthModifier, Firstimage)

                        print("Finished page " + str(PageNum) + " at --- " + str(time.time() - start_time) + " seconds ---")
                        PageNum = PageNum + 1

    print("Program finished at: --- %s seconds ---" % (time.time() - start_time))


def SearchPage(layout, imageName):

    LTImageList.clear()
    LTRectList.clear()
    LTCurveList.clear()
    LTLineList.clear()
    LTTextLineList.clear()

    index = 1
    figureIndex = 1
    #find all images and figures first.
    for lobj in layout:
        if isinstance(lobj, LTImage):
            index = index + 1
            figureIndex = figureIndex + 1

            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]
            newLTImage = PDFMinerObject(x0, y0, x1, y1)
            LTImageList.append(newLTImage)
            SaveFigure(lobj, imageName, figureIndex)


        if isinstance(lobj, LTRect):
            index = index + 1
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]
            newLTRect = PDFMinerObject(x0, y0, x1, y1)
            LTRectList.append(newLTRect)


        if isinstance(lobj, LTFigure):
            for inner_obj in lobj:
                if isinstance(inner_obj, LTImage):
                    index = index + 1
                    figureIndex = figureIndex + 1

                    x0, y0, x1, y1 = inner_obj.bbox[0], inner_obj.bbox[1], inner_obj.bbox[2], inner_obj.bbox[3]
                    newLTImage = PDFMinerObject(x0, y0, x1, y1)
                    LTImageList.append(newLTImage)
                    SaveFigure(inner_obj, imageName, figureIndex)


                #find all lines and curves.
                elif isinstance(inner_obj, LTCurve):
                    index = index + 1
                    x0, y0, x1, y1 = inner_obj.bbox[0], inner_obj.bbox[1], inner_obj.bbox[2], inner_obj.bbox[3]
                    newLTCurve = PDFMinerObject(x0, y0, x1, y1)
                    LTCurveList.append(newLTCurve)


        if isinstance(lobj, LTLine):
            index = index + 1
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]
            newLTLine = LT_Line_Class(x0, y0, x1, y1)
            LTLineList.append(newLTLine)


        #find all text.
        if isinstance(lobj, LTTextBox):
            for obj in lobj:
                if isinstance(obj, LTTextLine):
                    index = index + 1
                    x0, y0, x1, y1 = obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3]
                    newLTTextBox = PDFMinerObject(x0, y0, x1, y1)
                    LTTextLineList.append(newLTTextBox)

    print("There were " + str(index) + " objects on this page")


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


def LookThroughLists(imageName):

    LookThroughLTLineList(imageName)

    
def LookThroughLTLineList(imageName):

    LineDictionary = {}
    for LT_Line_element in LTLineList:
        if(round(LT_Line_element.y0) == round(LT_Line_element.y1)): #Only horizontal lines
            if(round(LT_Line_element.x1) - round(LT_Line_element.x0) > 10): #Only lines longer than 10 (points)
                key = str(round(LT_Line_element.x0)) + str(round(LT_Line_element.x1))
                if key in LineDictionary:
                    LineDictionary[key].append(LT_Line_element) 
                else:
                    LineDictionary[key] = [LT_Line_element]
    
    #print(str(len(LineDictionary)))
    FindTables(LineDictionary)

    f = open(os.path.join(local_path_to_LineCoords_folder, imageName) + ".txt", "w")
    f.write(str(len(LineDictionary)) + "\n")
    for dicelement in LineDictionary.values():
        for element in dicelement:
            f.write(element.To_String() + "\n")
            
    f.close()


def FindTables(LineDictionary):
    for dicelement in LineDictionary.values():
        print(str(len(dicelement)))
        #for element in dicelement:
            


def PaintPNGs(FileName, PDFfile_height, actualHeightModifier, actualWidthModifier, Firstimage):

    thickness = -1
    lineThickness = 40
    image = cv2.rectangle(Firstimage, (0,0), (0,0), (255, 255, 255), 1)

    #LTImage:
    colorGreen = (0, 255, 0) #green - image
    image = Paint(image, actualWidthModifier, PDFfile_height, actualHeightModifier, FileName, LTImageList, colorGreen, thickness)    

    #LTRect:
    image = Paint(image, actualWidthModifier, PDFfile_height, actualHeightModifier, FileName, LTRectList, colorGreen, thickness)    

    #LTCurve:
    colorBlue = (255, 0, 0) #blue - figure
    image = Paint(image, actualWidthModifier, PDFfile_height, actualHeightModifier, FileName, LTCurveList, colorBlue, lineThickness)    

    #LTLines:
    image = Paint(image, actualWidthModifier, PDFfile_height, actualHeightModifier, FileName, LTLineList, colorBlue, lineThickness)    

    #LTTextlines:
    colorBlack = (0, 0, 0) #black - text
    #colorWhite = (255, 255, 255) #white
    image = Paint(image, actualWidthModifier, PDFfile_height, actualHeightModifier, FileName, LTTextLineList, colorBlack, thickness)    

    cv2.imwrite(local_path_to_imageFilled_folder + FileName, image) #save picture


def Paint(image, actualWidthModifier, PDFfile_height, actualHeightModifier, FileName, objectList, color, thickness):
    for text_line_element in objectList:
        start_point = (round(text_line_element.x0*actualWidthModifier), round((PDFfile_height-text_line_element.y0)*actualHeightModifier))
        end_point = (round(text_line_element.x1* actualWidthModifier), round((PDFfile_height-text_line_element.y1)*actualHeightModifier))

        image = cv2.rectangle(image, start_point, end_point, color, thickness)
    
    return image


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