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

#mat = fitz.Matrix(zoom, zoom)
start_time = time.time()

def main(args):
    IO_handler.folder_prep(args.output, args.clean)
    pdf2png.convert_dir(args.input, os.path.join(args.output, 'Images'))

    for file in os.listdir(args.output):
        if file.endswith(".pdf"):
            break
            fileName = os.path.basename(file)
            pages, interpreter, device = init_file(args, fileName)

            PageNum = 1
            for page in pages:
                interpreter.process_page(page)
                layout = device.get_result()

                PDFfile_width = page.mediabox[2] #- 35
                PDFfile_height = page.mediabox[3] #- 31

                #Prerequisites for image processing
                imageName = fileName.replace(".pdf", "") + str(PageNum) + ".png"

                Firstimage = cv2.imread(args.output[0] + imageName)
                height, width = Firstimage.shape[:2]

                actualHeightModifier = height/PDFfile_height
                actualWidthModifier = width/PDFfile_width

                SearchPage(layout, imageName, PDFfile_height, PDFfile_width, actualHeightModifier, actualWidthModifier, Firstimage)
                
                print("Finished page " + str(PageNum) + " at --- " + str(time.time() - start_time) + " seconds ---")
                PageNum = PageNum + 1

    print("Program finished at: --- %s seconds ---" % (time.time() - start_time))

def init_file(args, fileName):
    fp = open(args.input + fileName, 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(detect_vertical=False)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    return PDFPage.get_pages(fp), PDFPageInterpreter(rsrcmgr, device), device

def SearchPage(layout, imageName, PDFfile_height, PDFfile_width, actualHeightModifier, actualWidthModifier, Firstimage):
    colorBlack = (0, 0, 0) #black - text
    colorBlue = (255, 0, 0) #blue - figure
    colorGreen = (0, 255, 0) #green - image

    index = 1
    figureIndex = 1
    for lobj in layout:
        if isinstance(lobj, LTTextBox):

            for obj in lobj:
                if isinstance(obj, LTTextLine):

                    x0, y0, x1, y1, text = obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3], obj.get_text().rstrip("\n")

                    if not(text == "\n" or text == " " or text == "\t" or text == "  " or text == ""):# or text == "•" or text == "• "):

                        EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorBlack)
                        index = index + 1


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
                
                if isinstance(inner_obj, LTCurve):
                    x0, y0, x1, y1 = inner_obj.bbox[0], inner_obj.bbox[1], inner_obj.bbox[2], inner_obj.bbox[3]

                    EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorBlue)

                    index = index + 1


        elif isinstance(lobj, LTLine):
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]

            EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorBlue)

            index = index + 1

                        
        elif isinstance(lobj, LTRect):
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]

            EditImage(imageName, x0, (PDFfile_height-y0), x1, (PDFfile_height-y1), PDFfile_width, PDFfile_height, index, actualHeightModifier, actualWidthModifier, Firstimage, colorGreen)

            index = index + 1

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
