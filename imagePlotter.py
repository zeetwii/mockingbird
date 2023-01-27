# Python script to convert an image into lat lon coordinates and then ADS-B broadcasts

from tkinter.filedialog import askopenfilename # used for file select dialog
import tkinter as tk # needed for gui
import cv2 # needed for finding black pixels
import numpy as np # needed for pixel math
import random # needed for picking random pixels to paint
import math # needed for coord calcs

from sklearn.cluster import DBSCAN # needed for DBSCAN clustering
from sklearn.neighbors import NearestNeighbors # needed for helping find epsilon
from kneed import KneeLocator # needed for helping to find epsilon

from PIL import Image # needed for debugging
import pandas as pd # debugging
import matplotlib.pyplot as plt # needed for visualization

class ImagePlotter:
    """
    Class that handles converting image points into lat lon coordinates
    """

    def __init__(self, imgFile, lat, lon, width):
        """
        Initialization method

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

        # TODO: Make this update picture coords

    def updateImage(self, imgFile):
        """
        updates all of the pixel maps with the new image

        Args:
            imgFile (file): the new image file to use
        """

        # makes the list of points to paint
        self.pixelList = self.__listBlack(imgFile)

        # TODO: Have this update the rest of the image stuff

    def getCoords(self, numTargets):
        '''
        Pulls a user given number of lat lon coordinates from the loaded image and returns them
        '''

        clusterPoints = self.__clusterData(self.pixelList)
        targetPixels = [] # the eventual list of pixels to paint

        # gets the number of targets that will be pulled from each cluster
        targetsPerCluster = round(numTargets / len(clusterPoints)) 

        for i in range(len(clusterPoints)):

            # calculate the spacing to even distrubute the target pixels within the cluster
            gap = math.floor(len(clusterPoints[i]) / targetsPerCluster)
            val = 0 # variable to move through cluster list

            # collect targets from cluster
            while val < len(clusterPoints[i]):
                targetPixels.append(clusterPoints[i][val])
                val = val + gap # increment value to next point to add

        #targetPixels = random.sample(self.pixelList, numTargets)
        #print(str(len(targetPixels)))

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

        # empty target list
        targetList = []

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
            targetList.append([targetLat, targetLon])
            #print(f"{str(targetLon)},{str(targetLat)}")

        return targetList

    def __clusterData(self, pixelList):
        '''
        Given a list of pixels, performs a clustering algorithm to look for points
        '''

        # gets distance from all neighbours
        neighbors = NearestNeighbors(n_neighbors=11).fit(np.asarray(pixelList))
        distances, indices = neighbors.kneighbors(np.asarray(pixelList))
        distances = np.sort(distances[:,10], axis=0)

        # find knee point
        knee = KneeLocator(np.arange(len(distances)), distances, S=1, curve='convex', direction='increasing', interp_method='polynomial')
        
        # use knee point to calculate clusters
        dbClusters = DBSCAN(eps=distances[knee.knee], min_samples=8).fit(np.asarray(pixelList))

        # Number of Clusters
        nClusters=len(set(dbClusters.labels_))-(1 if -1 in dbClusters.labels_ else 0)
        #print(str(nClusters))
        
        # creates a list of lists to hold each point in its cluster
        clusterPoints = []
        for i in range(nClusters):
            clusterPoints.append([])

        #print(str(clusterPoints))

        # put each pixel in the cluster list its a part of
        for i in range(len(pixelList)):
            if dbClusters.labels_[i] != -1: # if not a un-clustered point, add to list
                clusterPoints[dbClusters.labels_[i]].append(pixelList[i])
         
        # print method for debugging
        #for i in range(len(clusterPoints)):
            #print(str(len(clusterPoints[i])))

        return clusterPoints


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
        image = cv2.imread(imgFile) # grabs transparent pixels

        # convert to grayscale
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

    painter = ImagePlotter(imgFile, 38.6001, -77.1622, 10000)

    coords = painter.getCoords(200)

    debug = open('test.txt', 'w')
    
    for target in coords:
        # for use with: https://dwtkns.com/pointplotter/
        debug.write(f"{str(format(target[1], '.20f'))}, {str(format(target[0], '.20f'))}\n")
    debug.close()