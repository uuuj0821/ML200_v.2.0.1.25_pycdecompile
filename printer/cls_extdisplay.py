# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Nov 16 2020, 22:23:17)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /home/dp110/carima/dp110server/printer/cls_extdisplay.py
# Compiled at: 2017-02-07 16:44:31
"""
Created on Jun 19, 2015

@author: cloud3
"""
import cv2, numpy as np
from PIL import Image
from printer.cls_display import cls_Display
from time import sleep
import os
from cv2 import cv

class cls_ExtDisplay(cls_Display):
    """
    classdocs
    """

    def __init__(self, imageRoot, fileType='gif', filter=False):
        """
        Constructor
        :param imageRoot: image folder path. no slash(/) at the end.
        :param fileType: gif, jpg, png, etc. no dot(.) at the beginning.
        """
        self.imageRoot = imageRoot
        self.fileType = fileType
        self.filter = filter
        self.imagesPath = os.environ.get('HOME', '/home/pi') + '/carima/dp110server/images'
        self.maskimagesPath = os.environ.get('HOME', '/home/pi') + '/carima/basic/DP845_basic'

    def getLayerPath(self, layer):
        return cls_Display.getLayerPath(self, layer)

    def getImagePath(self, baseName):
        return cls_Display.getImagePath(self, baseName)

    def loadGif(self, imagePath):
        pimg = Image.open(imagePath).convert('RGB')
        oimg = np.array(pimg)
        if self.filter:
            kernel = np.ones((3, 3), np.float32) / 2
            return cv2.filter2D(oimg, -1, kernel)
        else:
            return oimg

    def showImage(self, imagePath, msecs):
        self.image = cv2.imread(imagePath)
        cv2.imshow('dp110display', self.image)
        if msecs > 0:
            sleep(msecs / 1000.0)
        return True

    def showLayer(self, layer, msecs):
        return cls_Display.showLayer(self, layer, msecs)

    def showNewAlgo(self, finalImgpath, msecs):
        return cls_Display.showImage(self, finalImgpath, msecs)

    def clear(self):
        self.showImage(self.imagesPath + '/black1280.png', 0)
        return True

    def whiteclear(self):
        self.showImage(self.maskimagesPath + '/mask.png', 6000)
        self.showImage(self.maskimagesPath + '/black.png', 0)
        return True

    def setupGrids(self, xres, yres, xgrid, ygrid, line=5):
        self.xres = xres
        self.yres = yres
        self.xgrid = xgrid
        self.ygrid = ygrid
        self.line = line
        cv2.namedWindow('dp110display')
        cv2.cv.ResizeWindow('dp110display', xres, yres)
        cv2.cv.MoveWindow('dp110display', 1024, 0)
        self.grid = np.zeros((yres, xres, 4), np.uint8)
        self.white = (255, 255, 255, 255)
        self.black = (0, 0, 0, 255)
        self.xseg = xres / xgrid
        self.yseg = yres / ygrid
        return 1

    def showGrids(self, x, y, val, flag):
        color = (
         val, val, val, 255)
        cv2.rectangle(self.grid, (x * self.xseg, y * self.yseg), ((x + 1) * self.xseg, (y + 1) * self.yseg), color, -1)
        cv2.rectangle(self.grid, (x * self.xseg, y * self.yseg), ((x + 1) * self.xseg, (y + 1) * self.yseg), self.black, self.line)
        cv2.startWindowThread()
        cv2.imshow('dp110display', self.grid)
        return 1

    def clearGrids(self):
        self.showImage(self.maskimagesPath + '/black.png', 0)
        self.grid[:] = self.black = (0, 0, 0, 225)
        return 1