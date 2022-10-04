# Python script to convert an image into lat lon coordinates and then ADS-B broadcasts

from tkinter.filedialog import askopenfilename # used for file select dialog
import tkinter as tk # needed for gui

import cv2 # needed for finding black pixels
import numpy as np # needed for pixel math
import random # needed for picking random pixels to paint

class ImagePlotter:
    '''Class that handles painting planes'''

    def __init__(self, imgFile, lat, lon, width):
        
        self.centerLat = float(lat)
        self.centerLon = float(lon)
        self.width = float(width)

        # makes the list of points to paint
        self.pixelList = self.__listBlack(imgFile)
        

        #print(str(targetPixels))
        #print(f"Center pixel: {str(self.centerWidth)}, {str(self.centerHeight)}")

    def updateLocation(self, lat, lon, width):
        """
        Updates the central location and width to be used in coordinate generation

        Args:
            lat (float): the center lat point
            lon (float): the center lon point
            width (float): the width in km of the image when painted
        """

        self.centerLat = float(lat)
        self.centerLon = float(lon)
        self.width = float(width)

    def updateImage(self, imgFile):
        """
        updates all of the pixel maps with the new image

        Args:
            imgFile (file): the new image file to use
        """

        # makes the list of points to paint
        self.pixelList = self.__listBlack(imgFile)

    def getCoords(self, numTargets):
        '''
        Pulls a user given number of lat lon coordinates from the loaded image and returns them
        '''

        targetPixels = random.sample(self.pixelList, numTargets)

        return self.__pixelsToCoords(targetPixels)


    def __pixelsToCoords(self, targetPixels):
        '''
        Takes a list of pixels and returns a list of coordinates
        '''

        print(targetPixels)
        # TODO: fix this


    def __listBlack(self, imgFile):
        """
        Returns a list of every black pixel in the provided image. 
        Also updates centerWidth and centerHeight to the new image.

        Args:
            imgFile (file): The image file to load and read

        Returns:
            list: list of XY coordinates
        """

        # loads the image and converts it into a grayscale one
        image = cv2.imread(imgFile)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # grab center
        height, width = gray.shape
        self.centerHeight = round(height / 2)
        self.centerWidth = round(width / 2)


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

    painter = ImagePlotter(imgFile, 0, 0, 1000)