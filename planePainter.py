# Python script to convert an image into lat lon coordinates and then ADS-B broadcasts

from tkinter.filedialog import askopenfilename # used for file select dialog
import tkinter as tk # needed for gui

import cv2 # needed for finding black pixels
import numpy as np # needed for pixel math
import random # needed for picking random pixels to paint

class PlanePainter:
    '''Class that handles painting planes'''

    def __init__(self, imgFile, lat, lon, radius, numTargets):
        
        self.centerLat = float(lat)
        self.centerLon = float(lon)
        self.radius = float(radius)

        # makes the list of points to paint
        pixelList = self.listBlack(imgFile)
        targetPixels = random.sample(pixelList, numTargets)

        print(str(targetPixels))




    def listBlack(self, imgFile):

        # loads the image and converts it into a grayscale one
        image = cv2.imread(imgFile)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # threshold of what counts as black
        threshold = 128

        # find coordinates of all pixels below threshold
        coords = np.column_stack(np.where(gray < threshold))
        #print(coords)

        
        # Sanitity check by redrawing the new image
        # Create mask of all pixels lower than threshold level
        #mask = gray < threshold
        # Color the pixels in the mask
        #image[mask] = (204, 119, 0)
        #cv2.imshow('image', image)
        #cv2.waitKey()

        return coords.tolist()


    

if __name__ == '__main__':
    
    root = tk.Tk()
    root.withdraw()
    imgFile = askopenfilename(title="select image to use", filetypes=(("PNG files", ".png"), ("JPEG files", ".jpg"), ("all files", ".")))

    planePainter = PlanePainter(imgFile, 0, 0, 1000, 20)