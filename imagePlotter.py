# Python script to convert an image into lat lon coordinates and then ADS-B broadcasts

from tkinter.filedialog import askopenfilename # used for file select dialog
import tkinter as tk # needed for gui

import cv2 # needed for finding black pixels
import numpy as np # needed for pixel math
import random # needed for picking random pixels to paint
import math # needed for coord calcs

class ImagePlotter:
    """
    Class that handles converting image points into lat lon coordinates
    """

    def __init__(self, imgFile, lat, lon, width):
        """
        Initalization method

        Args:
            imgFile (_type_): _description_
            lat (_type_): _description_
            lon (_type_): _description_
            width (_type_): _description_
        """
        
        self.centerLat = math.radians(float(lat))
        self.centerLon = math.radians(float(lon))
        self.width = float(width)

        # makes the list of points to paint
        self.pixelList = self.__listBlack(imgFile)
        
        #print(f"Center pixel: {str(self.centerWidth)}, {str(self.centerHeight)}")

    def updateLocation(self, lat, lon, width):
        """
        Updates the central location and width to be used in coordinate generation

        Args:
            lat (float): the center lat point in degrees
            lon (float): the center lon point in degrees
            width (float): the width in km of the image when painted
        """

        self.centerLat = math.radians(float(lat))
        self.centerLon = math.radians(float(lon))
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

        # gets the ratio of kilometers per pixel by dividing the max km width by total width in pixels
        kmPerPix = self.width / (self.centerWidth * 2)
        #print(f"km per pixel: {str(kmPerPix)}")

        # radius of the earth
        rEarth = 6371

        debugFile = open("test.txt", 'w')

        #print(targetPixels)
        for target in targetPixels:
            
            # get angle and distance of each target point from the center
            angle = math.atan2(target[0] - self.centerHeight, target[1] - self.centerWidth) * (180 / math.pi)
            distPix = math.sqrt(pow(target[1] - self.centerWidth, 2) + pow(target[0] - self.centerHeight, 2))

            # get bearing in rads and dist in km
            bearing = math.radians(90 + angle)
            distKM = distPix * kmPerPix
            #print(f"{str(bearing)} {str(distKM)}")

            # get the target lat lon
            targetLat = math.asin(math.sin(self.centerLat)*math.cos(distKM / rEarth) + math.cos(self.centerLat)*math.sin(distKM / rEarth)*math.cos(bearing))
            #print(str(targetLat))
            targetLon = self.centerLon + math.atan2(math.sin(bearing)*math.sin(distKM / rEarth)*math.cos(self.centerLat),math.cos(distKM / rEarth)-math.sin(self.centerLat)*math.sin(targetLat))
            #print(str(targetLon))
            targetLat = math.degrees(targetLat)
            targetLon = math.degrees(targetLon)

            #print(f"{str(targetLon)},{str(targetLat)}")
            debugFile.write(f"{str(format(targetLon, '.20f'))},{str(format(targetLat, '.20f'))}\n")
            


    def __listBlack(self, imgFile):
        """
        Returns a list of every black pixel in the provided image. 
        Also updates centerWidth and centerHeight to the new image.

        Args:
            imgFile (file): The image file to load and read

        Returns:
            list: list of pixel coordinates in the format of [Height, Width]
        """

        # loads the image and converts it into a grayscale one
        image = cv2.imread(imgFile, cv2.IMREAD_UNCHANGED) # grabs transparent pixels

        # converts transparent pixels to white
        alpha_channel = image[: ,: , 3]
        _, mask = cv2.threshold(alpha_channel, 254, 255, cv2.THRESH_BINARY) # binarize mask
        color = image[: ,: ,: 3]
        newImg = cv2.bitwise_not(cv2.bitwise_not(color, mask = mask))



        gray = cv2.cvtColor(newImg, cv2.COLOR_BGR2GRAY)

        # grab center
        height, width = gray.shape
        self.centerHeight = round(height / 2)
        self.centerWidth = round(width / 2)


        # threshold of what counts as black
        threshold = 128

        # find coordinates of all pixels below threshold
        coords = np.column_stack(np.where(gray < threshold))
        #print(coords)

        
        # Sanity check by redrawing the new image
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

    painter = ImagePlotter(imgFile, 33.0, -70.0, 1000)
    painter.getCoords(300)