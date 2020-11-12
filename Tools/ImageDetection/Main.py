import numpy as np
import cv2
import os
import shutil

start_path = os.getcwd()
local_path_to_PreProcessedImages_folder = os.path.join(start_path, "Pre_Processed_Images")
local_path_to_processedImages_folder = os.path.join(start_path, "Processed_Images")
local_path_to_OriginalImages_folder = os.path.join(start_path,"Original_Images")

shutil.rmtree(local_path_to_processedImages_folder)
os.mkdir(local_path_to_processedImages_folder)

for root, dirs, files in os.walk(local_path_to_PreProcessedImages_folder):
    for file in files:
        if file.endswith(".png"):

            imageName = os.path.basename(file)
            
            # load the image
            image = cv2.imread(os.path.join(local_path_to_PreProcessedImages_folder, imageName))
            #original = image.copy()

            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            hsv_lower = np.array([110,50,50]) #[254,0,0] [0,0,254]
            hsv_upper = np.array([130,255,255]) #[255,1,1] [1,1,255]
            mask = cv2.inRange(hsv, hsv_lower, hsv_upper)

            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
            opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            close = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=1)

            cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            offset = 20
            ROI_number = 0
            for c in cnts:
                x,y,w,h = cv2.boundingRect(c)
                if(x != 0 and y != 0 and w != 0 and h != 0):
                    if not(w < 65 or h < 65): #Sort straight lines away
                        #firstCorner = (x - offset, y - offset)
                        #secondCorner = (x + w + offset, y + h + offset)

                        for root, dirs, files in os.walk(local_path_to_OriginalImages_folder):
                            for originalFile in files:
                                if originalFile.endswith(".png"):
                                    originalImageName = os.path.basename(originalFile)

                                    if(imageName == originalImageName): #check if it is the same file
                                        # load the original image
                                        originalImage = cv2.imread(os.path.join(local_path_to_OriginalImages_folder, originalImageName))
                                        #cv2.rectangle(image, firstCorner, secondCorner, (36,255,12), 2) #draw green boxes
                                        ROI = originalImage[y-offset:y+h+offset, x-offset:x+w+offset]

                                        cv2.imwrite(os.path.join(local_path_to_processedImages_folder, imageName.replace(".png", "") + '-{}.png'.format(ROI_number)), ROI)
                                        ROI_number += 1