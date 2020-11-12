import os
import sys
import fitz
import cv2
import argparse
import numpy as ny
import time
import shutil
import IO_handler
import utils.pdf2png as pdf2png
import concurrent.futures as cf
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTText, LTChar, LTFigure, LTImage, LTRect, LTCurve, LTLine
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

FIGURES = 'figures'
IMAGES = 'images'
ANNOTATED = 'images_annotated'
LINES = 'line_cords'

#mat = fitz.Matrix(zoom, zoom)
start_time = time.time()

class PDF_file:
    def __init__(self, file, args):
        self.file_name = os.path.basename(file)
        temp_pages, self.interpreter, self.device = init_file(args, self.file_name)
        self.pages = []
        for page in temp_pages:
            self.pages.append(PDF_page(self, args, page))

class PDF_page:
    def __init__(self, owner, args, page):
        owner.interpreter.process_page(page)
        self.layout = owner.device.get_result()

        self.PDFfile_width = page.mediabox[2] #- 35
        self.PDFfile_height = page.mediabox[3] #- 31

        #Prerequisites for image processing
        self.image_name = owner.file_name.replace(".pdf", "_page") + str(len(owner.pages) + 1) + ".png"

        self.first_image = cv2.imread(os.path.join(os.path.join(args.output, IMAGES), self.image_name))
        self.height, self.width = self.first_image.shape[:2]

        self.actualHeightModifier = self.height/self.PDFfile_height
        self.actualWidthModifier = self.width/self.PDFfile_width

class PDFMinerObject:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

class LT_Line_Class(PDFMinerObject):
    def To_String(self):
        return "Coord: (({0}, {1}), ({2}, {3}))".format(round(self.x0), round(self.y0), round(self.x1), round(self.y1))


LTImageList = []
LTRectList = []
LTCurveList = []
LTLineList = []
LTTextLineList = []

def main(args):
    pageNum = 0
    IO_handler.folder_prep(args.output, args.clean)
    pdf2png.convert_dir(args.input, os.path.join(args.output, 'images'))
    print("Finished page " + str(pageNum) + " at --- " + str(time.time() - start_time) + " seconds ---")

    files = []
    list_args = []
    for file in os.listdir(args.input):
        if file.endswith(".pdf"):
            files.append(file)
            list_args.append(args)

    with cf.ProcessPoolExecutor() as executor:
        executor.map(doshit, files, list_args)
               
    print("Program finished at: --- %s seconds ---" % (time.time() - start_time))

def doshit(file, args):
    print('done structure')
    current_PDF = PDF_file(file, args)
    for page in current_PDF.pages:
        print('got here')
        SearchPage(page, args)
        #LookThroughLTLineList()
        PaintPNGs(page, args)

def init_file(args, fileName):
    fp = open(os.path.join(args.input, fileName), 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(detect_vertical=False)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    return PDFPage.get_pages(fp), PDFPageInterpreter(rsrcmgr, device), device

def SearchPage(page, args):

    LTImageList.clear()
    LTRectList.clear()
    LTCurveList.clear()
    LTLineList.clear()
    LTTextLineList.clear()

    index = 1
    figureIndex = 1
    #find all images and figures first.
    for lobj in page.layout:
        if isinstance(lobj, LTImage):
            index = index + 1
            figureIndex = figureIndex + 1

            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]
            newLTImage = PDFMinerObject(x0, y0, x1, y1)
            LTImageList.append(newLTImage)
            SaveFigure(lobj, page, figureIndex, args)


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
                    SaveFigure(inner_obj, page, figureIndex, args)


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


def SaveFigure(lobj, page, figureIndex, args):
    file_stream = lobj.stream.get_rawdata()
    fileExtension = IO_handler.get_file_extension(file_stream[0:4])

    if(fileExtension != None):
        figureName = page.image_name.replace(".png", "") + str(figureIndex) + fileExtension

        file_obj = open(os.path.join(os.path.join(args.output, FIGURES), figureName), 'wb')
        file_obj.write(lobj.stream.get_rawdata())
        file_obj.close()

def PaintPNGs(page, args):
    thickness = -1
    lineThickness = 40
    image = cv2.rectangle(page.first_image, (0,0), (0,0), (255, 255, 255), 1)

    #LTImage:
    colorGreen = (0, 255, 0) #green - image
    image = Paint(image, page, LTImageList, colorGreen, thickness)    

    #LTRect:
    image = Paint(image, page, LTRectList, colorGreen, thickness)    

    #LTCurve:
    colorBlue = (255, 0, 0) #blue - figure
    image = Paint(image, page, LTCurveList, colorBlue, lineThickness)    

    #LTLines:
    image = Paint(image, page, LTLineList, colorBlue, lineThickness)    

    #LTTextlines:
    colorBlack = (0, 0, 0) #black - text
    #colorWhite = (255, 255, 255) #white
    image = Paint(image, page, LTTextLineList, colorBlack, thickness)    
    print(page.image_name)
    cv2.imwrite(os.path.join(os.path.join(args.output, ANNOTATED), page.image_name), image) #save picture


def Paint(image, page, objectList, color, thickness):
    for text_line_element in objectList:
        start_point = (round(text_line_element.x0*page.actualWidthModifier), round((page.PDFfile_height-text_line_element.y0)*page.actualHeightModifier))
        end_point = (round(text_line_element.x1* page.actualWidthModifier), round((page.PDFfile_height-text_line_element.y1)*page.actualHeightModifier))

        image = cv2.rectangle(image, start_point, end_point, color, thickness)
    
    return image

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
    #FindTables(LineDictionary)

    f = open(os.path.join(local_path_to_LineCoords_folder, imageName) + ".txt", "w")
    f.write(str(len(LineDictionary)) + "\n")
    for dicelement in LineDictionary.values():
        for element in dicelement:
            f.write(element.To_String() + "\n")
            
    f.close()

#def FindTables(LineDictionary):
    #for dicelement in LineDictionary.values():
        #print(str(len(dicelement)))
        #for element in dicelement:

if __name__ == '__main__':
    # Arguments
    argparser = argparse.ArgumentParser(description="WIP")
    argparser.add_argument("-i", "--input", action="store", default=os.path.join(os.getcwd(), 'src'), help="Path to input folder")
    argparser.add_argument("-o", "--output", action="store", default=os.path.join(os.getcwd(), 'out'), help="Path to output folder")
    argparser.add_argument("-c", "--clean", action="store", type=bool, default=False, help="Activate nice mode.")
    args = argparser.parse_args()

    main(args)