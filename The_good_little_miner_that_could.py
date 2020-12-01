import os
import sys
import fitz
import cv2
import argparse
import numpy as ny
import time
import shutil
import segment
import IO_handler
import datastructure.models as datastructures
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
        self.LTImageList = []
        self.LTRectList = []
        self.LTRectLineList = []
        self.LTCurveList = []
        self.LTLineList = []
        self.LTTextLineList = []
        self.TableLines = []
        self.TableCoordinates = []
        owner.interpreter.process_page(page)
        self.layout = owner.device.get_result()

        self.PDFfile_width = page.mediabox[2] #- 35
        self.PDFfile_height = page.mediabox[3] #- 31

        #Prerequisites for image processing
        self.image_name = owner.file_name.replace(".pdf", "_page") + str(len(owner.pages) + 1) + ".png"
        self.image_number = len(owner.pages)+1
        self.first_image = cv2.imread(os.path.join(os.path.join(args.output, IMAGES), self.image_name))
        self.height, self.width = self.first_image.shape[:2]

        self.actualHeightModifier = self.height/self.PDFfile_height
        self.actualWidthModifier = self.width/self.PDFfile_width

class Coordinates(): 
    def __init__(self, x0, y0, x1, y1): 
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

class LT_Line_Class(Coordinates):
    def To_String(self):
        return "Coord: (({0}, {1}), ({2}, {3}))".format(round(self.x0), round(self.y0), round(self.x1), round(self.y1))

def main(args):
    IO_handler.folder_prep(args.output, args.clean)
    pdf2png.convert_dir(args.input, os.path.join(args.output, 'images'))

    for file in os.listdir(args.input):
        if file.endswith('.pdf'):
            doshit_single(file, args)
    """ files = []
    list_args = []
    for file in os.listdir(args.input):
        if file.endswith(".pdf"):
            files.append(file)
            list_args.append(args)

    with cf.ProcessPoolExecutor() as executor:
        executor.map(doshit, files, list_args) """
               
    print("Program finished at: --- %s seconds ---" % (time.time() - start_time))

def doshit_single(file, args):
    the_final_pages = []
    pageNum = 0
    current_PDF = PDF_file(file, args)
    for page in current_PDF.pages:
        SearchPage(page, args)
        LookThroughLineLists(page, args)
        page1 = make_page(page)
        page2 = segment.infer_page(os.path.join(os.getcwd(), 'out', 'images', page.image_name))
        print(str(page1.page_number) + ' vs ' + str(page2.page_number))
        the_final_pages.append(segment.merge_pages(page1, page2))

def doshit(file, args): 
    pageNum = 0
    current_PDF = PDF_file(file, args)
    for page in current_PDF.pages:
        SearchPage(page, args)
        Flip_Y_Coordinates(page)
        LookThroughLineLists(page, args)
        Check_Text_Objects(page)
        PaintPNGs(page, args)
        print("Finished page " + str(pageNum) + " at --- " + str(time.time() - start_time) + " seconds ---")
        pageNum = pageNum + 1

def init_file(args, fileName):
    fp = open(os.path.join(args.input, fileName), 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(detect_vertical=False)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    return PDFPage.get_pages(fp), PDFPageInterpreter(rsrcmgr, device), device

def SearchPage(page, args):
    index = 1
    figureIndex = 1
    #find all images and figures first.
    for lobj in page.layout:
        if isinstance(lobj, LTImage):
            index = index + 1
            figureIndex = figureIndex + 1

            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]
            newLTImage = Coordinates(x0, y0, x1, y1)
            page.LTImageList.append(newLTImage)
            SaveFigure(lobj, page, figureIndex, args)


        if isinstance(lobj, LTRect):
            index = index + 1
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]
            result = Check_If_Line(x0, y0, x1, y1) #check if the rectangle is a line instead of a rectangle.
            if(result[0] == True): #it is a line
                if(result[1] == 1): #horizontal line
                    newLTLine = LT_Line_Class(x0, y0, x1, y0) 
                    page.LTRectLineList.append(newLTLine)
                elif(result[1] == 2): #vertical line
                    newLTLine = LT_Line_Class(x0, y0, x0, y1) 
                    page.LTRectLineList.append(newLTLine)
            else:
                newLTRect = Coordinates(x0, y0, x1, y1)
                page.LTRectList.append(newLTRect)


        if isinstance(lobj, LTFigure):
            for inner_obj in lobj:
                if isinstance(inner_obj, LTImage):
                    index = index + 1
                    figureIndex = figureIndex + 1

                    x0, y0, x1, y1 = inner_obj.bbox[0], inner_obj.bbox[1], inner_obj.bbox[2], inner_obj.bbox[3]
                    newLTImage = Coordinates(x0, y0, x1, y1)
                    page.LTImageList.append(newLTImage)
                    SaveFigure(inner_obj, page, figureIndex, args)


                #find all lines and curves.
                elif isinstance(inner_obj, LTCurve):
                    index = index + 1
                    x0, y0, x1, y1 = inner_obj.bbox[0], inner_obj.bbox[1], inner_obj.bbox[2], inner_obj.bbox[3]
                    newLTCurve = Coordinates(x0, y0, x1, y1)
                    page.LTCurveList.append(newLTCurve)


        if isinstance(lobj, LTLine):
            index = index + 1
            x0, y0, x1, y1 = lobj.bbox[0], lobj.bbox[1], lobj.bbox[2], lobj.bbox[3]
            newLTLine = LT_Line_Class(x0, y0, x1, y1)
            page.LTLineList.append(newLTLine)


        #find all text.
        if isinstance(lobj, LTTextBox):
            for obj in lobj:
                if isinstance(obj, LTTextLine):
                    index = index + 1
                    x0, y0, x1, y1 = obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3]
                    newLTTextBox = Coordinates(x0, y0, x1, y1)
                    page.LTTextLineList.append(newLTTextBox)

    print("There were " + str(index) + " objects on this page")
    
def make_page(page: PDF_page):
    result = datastructures.Page(page.image_number)
    result.add_from_page_manuel([], convert_to_datastructure(convert_to_pixel_height(page, page.LTImageList), datastructures.ImageSegment), convert_to_datastructure(convert_to_pixel_height(page, page.LTRectList), datastructures.TableSegment))
    return result

def convert_to_pixel_height(page: PDF_page, object_list: list):
    result_elements = []
    for element in object_list:
        result_elements.append(datastructures.Coordinates(page.actualWidthModifier * element.x0,
                                                          page.actualHeightModifier * element.y0,
                                                          page.actualWidthModifier * element.x1,
                                                          page.actualHeightModifier * element.y1))
    
    return result_elements
    
def convert_to_datastructure(object_list: list, desired_object: object):
    result_obj_list = []
    for obj in object_list:
    	result_obj_list.append(desired_object(obj))
    	
    return result_obj_list


def Check_If_Line(x0, y0, x1, y1):
    is_It_Line = False
    x = abs(x1 - x0)
    y = abs(y1 - y0)
    threshold = 5 #I made this variable up, but it works

    if(y < threshold): #horizontal line
        is_It_Line = True
        return is_It_Line, 1

    if(x < threshold): #vertical line
        is_It_Line = True
        return is_It_Line, 2

    return is_It_Line, 0

def SaveFigure(lobj, page, figureIndex, args):
    file_stream = lobj.stream.get_rawdata()
    fileExtension = IO_handler.get_file_extension(file_stream[0:4])

    if(fileExtension != None):
        figureName = page.image_name.replace(".png", "") + str(figureIndex) + fileExtension

        file_obj = open(os.path.join(os.path.join(args.output, FIGURES), figureName), 'wb')
        file_obj.write(lobj.stream.get_rawdata())
        file_obj.close()

def Flip_Y_Coordinates(page):
    Flip_Y_Coordinate(page, page.LTImageList)
    Flip_Y_Coordinate(page, page.LTRectList)
    Flip_Y_Coordinate(page, page.LTRectLineList)
    Flip_Y_Coordinate(page, page.LTCurveList)
    Flip_Y_Coordinate(page, page.LTLineList)
    Flip_Y_Coordinate(page, page.LTTextLineList)

def Flip_Y_Coordinate(page, object_List):
    for element in object_List:
        element.y0 = page.PDFfile_height - element.y0
        element.y1 = page.PDFfile_height - element.y1

def PaintPNGs(page, args):

    thickness = -1
    lineThickness = 40
    image = cv2.rectangle(page.first_image, (0,0), (0,0), (255, 255, 255), 1)

    #LTRect:
    colorPink = (127,255,0)
    image = Paint(image, page, page.LTRectList, colorPink, thickness)    

    #LTImage:
    colorGreen = (0, 255, 0) #green - image
    image = Paint(image, page, page.LTImageList, colorGreen, thickness)    

    #LTCurve:
    colorBlue = (255, 0, 0) #blue - figure
    image = Paint(image, page, page.LTCurveList, colorBlue, lineThickness)    

    #LTLines:
    image = Paint(image, page, page.LTLineList, colorBlue, lineThickness)  
    #LTRectlines:
    color_Light_Blue = (255,191,0)
    image = Paint(image, page, page.LTRectLineList, color_Light_Blue, lineThickness) 

    #tables:
    colorRed = (0,0,255)
    image = Paint(image, page, page.TableCoordinates, colorRed, thickness)      

    #LTTextlines:
    colorBlack = (0, 0, 0) #black - text
    #colorWhite = (255, 255, 255) #white
    image = Paint(image, page, page.LTTextLineList, colorBlack, thickness)    
    print(page.image_name)

    cv2.imwrite(os.path.join(args.output, ANNOTATED, page.image_name, image)) #save picture

def Paint(image, page, objectList, color, thickness):
    for element in objectList:
        start_point = (round(element.x0*page.actualWidthModifier), round(element.y0*page.actualHeightModifier))
        end_point = (round(element.x1* page.actualWidthModifier), round(element.y1*page.actualHeightModifier))

        image = cv2.rectangle(image, start_point, end_point, color, thickness)
    
    return image

def LookThroughLineLists(page, args):
    # if(len(page.LTLineList) > 0):
    #     LookThroughLTLineList(page, args)
    # if(len(page.TableLines) > 0):
    #     for element in page.TableLines:
    #         page.LTRectLineList.append(element)
    LookThroughLTRectLineList(page, args)

# def LookThroughLTLineList(page, args):
#     #Divide into dictionary where key is the elements height.
#     Line_Dictionary = {}
#     for LT_Line_element in page.LTLineList:
#         if(round(LT_Line_element.y0) == round(LT_Line_element.y1)): #Only horizontal lines
#             if(round(LT_Line_element.x1) - round(LT_Line_element.x0) > 10): #Only lines longer than 10 (points)
#                 newHeightCoordinate = True
#                 for dicelement in Line_Dictionary.values():
#                     for Line_Dic_element in dicelement:
#                         if(round(LT_Line_element.y0, 2) == round(Line_Dic_element.y0, 2)):
#                             newHeightCoordinate = False
#                             key = str(round(LT_Line_element.y0, 2))
#                             if key in Line_Dictionary:
#                                 Line_Dictionary[key].append(LT_Line_element) 
#                             else:
#                                 Line_Dictionary[key] = [LT_Line_element]
#                             break
#                     if(newHeightCoordinate == False):
#                         break
#                 if(newHeightCoordinate == True):
#                     key = str(round(LT_Line_element.y0, 2))
#                     Line_Dictionary[key] = [LT_Line_element]
    
#     #delete those elements in the dictionaries groupings which are not connected:
#     dictionary_Values_Lengh = Count_Elements_In_Dictionary(Line_Dictionary)
#     new_Dictionary_Values_Lengh = 0
#     while(True):
#         Line_Dictionary = Clean_Up_Dictionary(Line_Dictionary)
#         new_Dictionary_Values_Lengh = Count_Elements_In_Dictionary(Line_Dictionary)
#         if(dictionary_Values_Lengh == new_Dictionary_Values_Lengh or new_Dictionary_Values_Lengh == 0):
#             break
#         else:
#             dictionary_Values_Lengh = new_Dictionary_Values_Lengh

#     #Prints dictionary info:
#     # print("Dic lengh:" + str(len(Line_Dictionary)))
#     # for LT_Line_element in Line_Dictionary.values():
#     #     print(str(len(LT_Line_element)))

#     # f = open(os.path.join(os.path.join(args.output, LINES), page.image_name.replace(".png", "")) + "-LTLines.txt", "w")
#     # f.write(str(len(Line_Dictionary)) + "\n")
#     # for dicelement in Line_Dictionary.values():
#     #     for element in dicelement:
#     #         f.write(element.To_String() + "\n")   
#     # for element in page.LTLineList:
#     #     f.write(element.To_String() + "\n")   
#     #f.close()

#     for dicelement in Line_Dictionary.values():
#         for element in dicelement:
#             page.TableLines.append(element)

# def Clean_Up_Dictionary(dictionary):
#     for key, value in dictionary.items():
#         if(len(value) > 0):
#             if(len(value) == 1):
#                 dictionary[key].pop()
#             else:
#                 connected = False
#                 for element in value:
#                     for element2 in value:
#                         if(round(element.x0, 2) == round(element2.x1, 2) or round(element.x1, 2) == round(element2.x0, 2)):
#                             connected = True
#                 if(connected == False):
#                     dictionary[key].pop()
#     return dictionary

# def Count_Elements_In_Dictionary(dictionary):
    # dictionary_Values_Lengh = 0
    # for LT_Line_element in dictionary.values():
    #     dictionary_Values_Lengh = dictionary_Values_Lengh + len(LT_Line_element)
    # return dictionary_Values_Lengh

def LookThroughLTRectLineList(page, args):
    Table_Dictionary = {}
    table_Index_key = 0
    line_list = page.LTRectLineList.copy()

    something_was_changed = False

    while(True):
        if(something_was_changed == True):
            something_was_changed = False
            for LT_Line_element in line_list:
                result = On_Segment(LT_Line_element, Table_Dictionary)
                if(result[0] == True):
                    key = result[1]
                    if key in Table_Dictionary:
                        Table_Dictionary[key].append(LT_Line_element) 
                        line_list.remove(LT_Line_element)
                        something_was_changed = True
        else:
            if(len(line_list) > 0):
                Table_Dictionary[table_Index_key] = [line_list[0]]
                line_list.remove(line_list[0])
                table_Index_key = table_Index_key + 1
                something_was_changed = True
            else:
                break

    #Prints dictionary info, for testing purposes:
    # print("Dic lengh:" + str(len(Table_Dictionary)))
    # for LT_Line_element in Table_Dictionary.values():
    #     print(str(len(LT_Line_element)))

    #Write to file, also for testing purposes.
    # f = open(os.path.join(os.path.join(args.output, LINES), page.image_name.replace(".png", "")) + "-LTLines.txt", "w")
    # f.write(str(len(Table_Dictionary)) + "\n")
    # for dicelement in Table_Dictionary.values():
    #     for element in dicelement:
    #         f.write(element.To_String() + "\n")   
    # for element in line_list:
    #     f.write(element.To_String() + "\n")    
    #f.close()

    #Delete single elements in the dictionary:
    Table_Dictionary = Remove_Single_Elements(Table_Dictionary)

    #find retangle coordinates for each grouping of table lines:
    for dicelement in Table_Dictionary.values():
        page.TableCoordinates.append(ReturnRetangleCoordinatesForTable(dicelement))

def On_Segment(Line_element, dictionary):
    offset = 1 #I made this up, but it works
    for key, value in dictionary.items():
        if(len(value) > 0):
            for element in value:  
                if (round(Line_element.x0) - offset <= max(round(element.x0), round(element.x1)) and round(Line_element.x0) + offset >= min(round(element.x0), round(element.x1)) and 
                    round(Line_element.y0) - offset <= max(round(element.y0), round(element.y1)) and round(Line_element.y0) + offset >= min(round(element.y0), round(element.y1))):
                    return True, key
                elif(round(Line_element.x1) - offset <= max(round(element.x0), round(element.x1)) and round(Line_element.x1) + offset >= min(round(element.x0), round(element.x1)) and 
                     round(Line_element.y1) - offset <= max(round(element.y0), round(element.y1)) and round(Line_element.y1) + offset >= min(round(element.y0), round(element.y1))):
                    return True, key
    return False, ""

def Remove_Single_Elements(dictionary):
    dictionary_Copy = dictionary.copy()
    for key, value in dictionary_Copy.items():
        if(len(value) == 1):
            dictionary_Copy[key].pop()
    return dictionary_Copy

def ReturnRetangleCoordinatesForTable(dicelement):
    lower_left_x0 = 0
    lower_left_y0 = 0
    upper_right_x1 = 0
    upper_right_y1 = 0

    index = 0
    for element in dicelement:
        if(index > 0):
            if(round(element.x0) <= round(lower_left_x0) and round(element.y0) >= round(lower_left_y0)):
                lower_left_x0 = round(element.x0)
                lower_left_y0 = round(element.y0)
            elif(round(element.x1) >= round(upper_right_x1) and round(element.y1) <= round(upper_right_y1)):
                upper_right_x1 = round(element.x1)
                upper_right_y1 = round(element.y1)
        else:
            lower_left_x0 = round(element.x0)
            lower_left_y0 = round(element.y0)
            upper_right_x1 = round(element.x1)
            upper_right_y1 = round(element.y1)
        index = index + 1
    
    table_coordinate = Coordinates(lower_left_x0, lower_left_y0, upper_right_x1, upper_right_y1)
    return table_coordinate

def Check_Text_Objects(page):
    if(len(page.LTTextLineList) > 0):
        if(len(page.LTImageList) > 0):
            Remove_Text_Within(page, page.LTImageList)
        if(len(page.LTRectList) > 0):
            Remove_Text_Within(page, page.LTRectList)
        if(len(page.TableCoordinates) > 0):
            Remove_Text_Within(page, page.TableCoordinates)

def Remove_Text_Within(page, object_List):
    text_Line_List = page.LTTextLineList.copy()
    for text_Element in text_Line_List:
        element_Found = False
        for object_Element in object_List:
            #If the whole text line is within the object, delete it:
            if((text_Element.x0 >= object_Element.x0 and text_Element.y0 <= object_Element.y0) and
               (text_Element.x1 <= object_Element.x1 and text_Element.y1 >= object_Element.y1)):
                page.LTTextLineList.remove(text_Element)
                element_Found = True
                break
            #If the text line starts within the object (per x-coordinates), also delete it:
            elif((text_Element.x0 <= object_Element.x1 and text_Element.x0 >= object_Element.x0) and 
                 (text_Element.y0 <= object_Element.y0 and text_Element.y1 >= object_Element.y1)):
                page.LTTextLineList.remove(text_Element)
                element_Found = True
                break
            #If the text line ends within the object (per x-coordinates), also delete it:
            elif((text_Element.x1 >= object_Element.x0 and text_Element.x1 <= object_Element.x1) and 
                 (text_Element.y0 <= object_Element.y0 and text_Element.y1 >= object_Element.y1)):
                page.LTTextLineList.remove(text_Element)
                element_Found = True
                break  
            #If the text lines bottom is partly within the object (per y-coordinates), also delete it:
            elif((text_Element.y0 >= object_Element.y1 and object_Element.y0 >= text_Element.y0) and 
                 (text_Element.x1 <= object_Element.x1 and text_Element.x0 >= object_Element.x0)):
                page.LTTextLineList.remove(text_Element)
                element_Found = True
                break
            #If the text lines top is partly within the object (per y-coordinates), also delete it:
            elif((text_Element.y1 <= object_Element.y0 and object_Element.y1 <= text_Element.y1) and 
                 (text_Element.x1 <= object_Element.x1 and text_Element.x0 >= object_Element.x0)):
                page.LTTextLineList.remove(text_Element)
                element_Found = True
                break
            #Should there be a check which also deletes it if it starts before and ends after the object (goes through)? -Mette #TODO
        if(element_Found == True):
            continue

if __name__ == '__main__':
    # Arguments
    argparser = argparse.ArgumentParser(description="WIP")
    argparser.add_argument("-i", "--input", action="store", default=os.path.join(os.getcwd(), 'src'), help="Path to input folder")
    argparser.add_argument("-o", "--output", action="store", default=os.path.join(os.getcwd(), 'out'), help="Path to output folder")
    argparser.add_argument("-c", "--clean", action="store", type=bool, default=False, help="Activate nice mode.")
    args = argparser.parse_args()

    main(args)