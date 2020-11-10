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

        first_image = cv2.imread(os.path.join(os.path.join(args.output, IMAGES), self.image_name))
        self.height, self.width = first_image.shape[:2]

        self.actualHeightModifier = self.height/self.PDFfile_height
        self.actualWidthModifier = self.width/self.PDFfile_width


def main(args):
    IO_handler.folder_prep(args.output, args.clean)
    pdf2png.convert_dir(args.input, os.path.join(args.output, 'images'))
    for file in os.listdir(args.input):
        if file.endswith(".pdf"):
            print('pdf file found')
            current_PDF = PDF_file(file, args)
            print('done structure')


    for file in os.listdir(args.output):
        break
        if file.endswith(".pdf"):
            print('pdf file found')
            current_PDF = PDF_file

            PageNum = 1
            

            SearchPage(layout, imageName, PDFfile_height, PDFfile_width, actualHeightModifier, actualWidthModifier, Firstimage)
                
            print("Finished page " + str(PageNum) + " at --- " + str(time.time() - start_time) + " seconds ---")
            PageNum = PageNum + 1

    print("Program finished at: --- %s seconds ---" % (time.time() - start_time))

def init_file(args, fileName):
    fp = open(os.path.join(args.input, fileName), 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(detect_vertical=False)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    return PDFPage.get_pages(fp), PDFPageInterpreter(rsrcmgr, device), device


def SearchPage(layout, imageName, PDFfile_height, PDFfile_width, actualHeightModifier, actualWidthModifier, Firstimage):
    
    #colorBlack = (255, 255, 255) #black - text
    colorBlack = (0, 0, 0) #black - text
    colorBlue = (255, 0, 0) #blue - figure
    colorGreen = (0, 255, 0) #green - image

    index = 1
    figureIndex = 1

    #find all images and figures first.
    for lobj in layout:
        if isinstance(lobj, LTImage):
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]

            EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorGreen, -1)
            SaveFigure(lobj, imageName, figureIndex)

            index = index + 1
            figureIndex = figureIndex + 1

        elif isinstance(lobj, LTRect):
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]

            EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorGreen, -1)
            #SaveFigure(lobj, imageName, figureIndex)

            index = index + 1
            #figureIndex = figureIndex + 1

        elif isinstance(lobj, LTFigure):
            for inner_obj in lobj:
                if isinstance(inner_obj, LTImage):
                    x0, y0, x1, y1 = inner_obj.bbox[0], inner_obj.bbox[1], inner_obj.bbox[2], inner_obj.bbox[3]

                    EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorGreen, -1)
                    SaveFigure(inner_obj, imageName, figureIndex)

                    index = index + 1
                    figureIndex = figureIndex + 1

    #find all lines and curves.
    for lobj in layout:
        if isinstance(lobj, LTFigure):
            for inner_obj in lobj:              
                if isinstance(inner_obj, LTCurve):
                    x0, y0, x1, y1 = inner_obj.bbox[0], inner_obj.bbox[1], inner_obj.bbox[2], inner_obj.bbox[3]

                    EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorBlue, 40)
                    #SaveFigure(inner_obj, imageName, figureIndex)

                    index = index + 1
                    #figureIndex = figureIndex + 1


        elif isinstance(lobj, LTLine):
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]

            EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorBlue, 40)
            #SaveFigure(lobj, imageName, figureIndex)

            index = index + 1
            #figureIndex = figureIndex + 1 


    #find all text.
    for lobj in layout:
        if isinstance(lobj, LTTextBox):
            #x0, y0, x1, y1, text = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3], lobj.get_text()

            for obj in lobj:
                if isinstance(obj, LTTextLine):

                    x0, y0, x1, y1, text = obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3], obj.get_text().rstrip("\n")

                    if not(text == "\n" or text == " " or text == "\t" or text == "  " or text == ""):# or text == "•" or text == "• "):

                        EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorBlack, -1)
                        index = index + 1
                                        
                        #encodedText = text.encode(encoding='UTF-16',errors='strict')
                        #encodedCoords = ("At" + str(x0) + ", " + str(PDFfile_height-(y0-30)) + "\n").encode(encoding='UTF-16',errors='strict')
                        #encodedABCoords = ("And " + str(x1) + ", " + str(PDFfile_height-(y1-30)) + " is text:\n").encode(encoding='UTF-16',errors='strict')

                        # text_file.write(encodedCoords) #coords
                        # text_file.write(encodedABCoords) #coordsab
                        # text_file.write(encodedText) #text

    print("There were " + str(index) + " objects on this page")


def SaveFigure(lobj, imageName, figureIndex):
    file_stream = lobj.stream.get_rawdata()
    fileExtension = IO_handler.get_file_extension(file_stream[0:4])

    if(fileExtension != None):
        figureName = imageName.replace(".png", "") + str(figureIndex) + fileExtension

        file_obj = open(args.output[0] + figureName, 'wb')
        file_obj.write(lobj.stream.get_rawdata())
        file_obj.close()

def EditImage(FileName, x0, y0, x1, y1, PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, color):
    start_point = (round(x0*actualWidthModifier), round(y0*actualHeightModifier))
    end_point = (round(x1* actualWidthModifier), round(y1*actualHeightModifier))

    if(index == 1):
        image = cv2.rectangle(Firstimage, start_point, end_point, color, thickness)
    else:
        image = cv2.imread(local_path_to_imageFilled_folder + FileName)
        image = cv2.rectangle(image, start_point, end_point, color, thickness)

    cv2.imwrite(local_path_to_imageFilled_folder + FileName, image)

if __name__ == '__main__':
   # Arguments
    argparser = argparse.ArgumentParser(description="WIP")
    argparser.add_argument("-i", "--input", action="store", default=os.path.join(os.getcwd(), 'src'), help="Path to input folder")
    argparser.add_argument("-o", "--output", action="store", default=os.path.join(os.getcwd(), 'out'), help="Path to output folder")
    argparser.add_argument("-c", "--clean", action="store", type=bool, default=False, help="Activate nice mode.")
    args = argparser.parse_args()

    main(args)
