import os
import sys
import fitz
import cv2
import argparse
import numpy as ny
import time
import shutil
import IO_handler
import pdf2png
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTText, LTChar, LTFigure, LTImage, LTRect, LTCurve, LTLine
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

FIGURES = 'figures'
IMAGES = 'images'
ANNOTATED = 'images_annotated'

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


def main(args):
    pageNum = 0
    IO_handler.folder_prep(args.output, args.clean)
    pdf2png.convert_dir(args.input, os.path.join(args.output, 'images'))
    for file in os.listdir(args.input):
        if file.endswith(".pdf"):
            print('pdf file found')
            current_PDF = PDF_file(file, args)
            pageNum = pageNum + 1
            print("Finished page " + str(pageNum) + " at --- " + str(time.time() - start_time) + " seconds ---")
            print('done structure')
            for page in current_PDF.pages:
                print('got here')
                SearchPage(page, args)
               
    print("Program finished at: --- %s seconds ---" % (time.time() - start_time))

def init_file(args, fileName):
    fp = open(os.path.join(args.input, fileName), 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(detect_vertical=False)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    return PDFPage.get_pages(fp), PDFPageInterpreter(rsrcmgr, device), device


def SearchPage(page, args):
    
    #colorBlack = (255, 255, 255) #black - text
    colorBlack = (0, 0, 0) #black - text
    colorBlue = (255, 0, 0) #blue - figure
    colorGreen = (0, 255, 0) #green - image

    index = 1
    figureIndex = 1

    #find all images and figures first.
    for lobj in page.layout:
        if isinstance(lobj, LTImage):
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]

            EditImage(page, x0, (page.PDFfile_height-y0), x1, (page.PDFfile_height-y1), index, colorGreen, -1, args)
            SaveFigure(lobj, page.imageName, figureIndex)

            index = index + 1
            figureIndex = figureIndex + 1

        elif isinstance(lobj, LTRect):
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]

            EditImage(page, x0, (page.PDFfile_height-y0), x1, (page.PDFfile_height-y1), index, colorGreen, -1, args)
            #SaveFigure(lobj, page.imageName, figureIndex)

            index = index + 1
            #figureIndex = figureIndex + 1

        elif isinstance(lobj, LTFigure):
            for inner_obj in lobj:
                if isinstance(inner_obj, LTImage):
                    x0, y0, x1, y1 = inner_obj.bbox[0], inner_obj.bbox[1], inner_obj.bbox[2], inner_obj.bbox[3]

                    EditImage(page, x0, (page.PDFfile_height-y0), x1, (page.PDFfile_height-y1), index, colorGreen, -1, args)
                    SaveFigure(inner_obj, page, figureIndex)

                    index = index + 1
                    figureIndex = figureIndex + 1

    #find all lines and curves.
    for lobj in page.layout:
        if isinstance(lobj, LTFigure):
            for inner_obj in lobj:              
                if isinstance(inner_obj, LTCurve):
                    x0, y0, x1, y1 = inner_obj.bbox[0], inner_obj.bbox[1], inner_obj.bbox[2], inner_obj.bbox[3]

                    EditImage(page, x0, (page.PDFfile_height-y0), x1, (page.PDFfile_height-y1), index, colorBlue, 40, args)
                    #SaveFigure(inner_obj, page.imageName, figureIndex)

                    index = index + 1
                    #figureIndex = figureIndex + 1


        elif isinstance(lobj, LTLine):
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]

            EditImage(page, x0, (page.PDFfile_height-y0), x1, (page.PDFfile_height-y1), index, colorBlue, 40, args)
            #SaveFigure(lobj, page.imageName, figureIndex)

            index = index + 1
            #figureIndex = figureIndex + 1 


    #find all text.
    for lobj in page.layout:
        if isinstance(lobj, LTTextBox):
            #x0, y0, x1, y1, text = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3], lobj.get_text()

            for obj in lobj:
                if isinstance(obj, LTTextLine):

                    x0, y0, x1, y1, text = obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3], obj.get_text().rstrip("\n")

                    if not(text == "\n" or text == " " or text == "\t" or text == "  " or text == ""):# or text == "•" or text == "• "):

                        EditImage(page, x0, (page.PDFfile_height-y0), x1, (page.PDFfile_height-y1), index, colorBlack, -1, args)
                        index = index + 1
                                        
                        #encodedText = text.encode(encoding='UTF-16',errors='strict')
                        #encodedCoords = ("At" + str(x0) + ", " + str(PDFfile_height-(y0-30)) + "\n").encode(encoding='UTF-16',errors='strict')
                        #encodedABCoords = ("And " + str(x1) + ", " + str(PDFfile_height-(y1-30)) + " is text:\n").encode(encoding='UTF-16',errors='strict')

                        # text_file.write(encodedCoords) #coords
                        # text_file.write(encodedABCoords) #coordsab
                        # text_file.write(encodedText) #text

    print("There were " + str(index) + " objects on this page")


def SaveFigure(lobj, page, figureIndex):
    file_stream = lobj.stream.get_rawdata()
    fileExtension = IO_handler.get_file_extension(file_stream[0:4])

    if(fileExtension != None):
        figureName = page.image_name.replace(".png", "") + str(figureIndex) + fileExtension

        file_obj = open(os.path.join(os.path.join(args.output, FIGURES), figureName), 'wb')
        file_obj.write(lobj.stream.get_rawdata())
        file_obj.close()

def EditImage(page, x0, y0, x1, y1, index, color, thickness, args):
    start_point = (round(x0*page.actualWidthModifier), round(y0*page.actualHeightModifier))
    end_point = (round(x1* page.actualWidthModifier), round(y1*page.actualHeightModifier))

    if(index == 1):
        image = cv2.rectangle(page.first_image, start_point, end_point, color, thickness)
    else:
        image = cv2.imread(os.path.join(args.output, os.path.join(ANNOTATED, page.image_name)))
        image = cv2.rectangle(image, start_point, end_point, color, thickness)

    cv2.imwrite(os.path.join(args.output, os.path.join(ANNOTATED, page.image_name)), image)

if __name__ == '__main__':
   # Arguments
    argparser = argparse.ArgumentParser(description="WIP")
    argparser.add_argument("-i", "--input", action="store", default=os.path.join(os.getcwd(), 'src'), help="Path to input folder")
    argparser.add_argument("-o", "--output", action="store", default=os.path.join(os.getcwd(), 'out'), help="Path to output folder")
    argparser.add_argument("-c", "--clean", action="store", type=bool, default=False, help="Activate nice mode.")
    args = argparser.parse_args()

    main(args)
