# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Nov 16 2020, 22:23:17)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /home/dp110/carima/dp110server/printer/cls_extdisplayIMJ.py
# Compiled at: 2019-08-07 14:00:24
"""
Created on Jun 19, 2015

@author: cloud3
"""
import cv2, numpy as np
from PIL import Image, ImageDraw
from printer.cls_displayIMJ import cls_DisplayIMJ
from time import sleep
import os, xmlrpclib
from docutils.nodes import target
from multiprocessing import Process
from ConfigParser import ConfigParser
import datetime, logging, logging.handlers
from logging.handlers import TimedRotatingFileHandler
import cv, threading

class cls_ExtDisplayIMJ(cls_DisplayIMJ):
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
        self.imagesPath = os.environ.get('HOME', '/home/dp110') + '/carima/dp110server/images'
        self.maskpath = os.environ.get('HOME', '/home/pi') + '/carima/basic/IM-J_basic/mask.png'
        self.gridpath = os.environ.get('HOME', '/home/pi') + '/carima/basic/IM-J_basic'

    def getLayerPath(self, layer):
        return cls_DisplayIMJ.getLayerPath(self, layer)

    def getImagePath(self, baseName):
        return cls_DisplayIMJ.getImagePath(self, baseName)

    def loadGif(self, imagePath):
        pimg = Image.open(imagePath).convert('RGB')
        oimg = np.array(pimg)
        if self.filter:
            kernel = np.ones((3, 3), np.float32) / 2
            return cv2.filter2D(oimg, -1, kernel)
        else:
            return oimg

    def xmlrpcclient(self):
        self.proxy = xmlrpclib.ServerProxy('http://127.0.0.1:8080')

    def showImgThread(self, imagePath):
        os.system('omxiv -d 5 ' + imagePath)
        return True

    def closeImgThread(self):
        os.system('sudo killall omxiv')
        return True

    def showSliceImage(self, imagePath, msecs):
        self.proxy.EngineOnCall()
        th = threading.Thread(target=self.showImgThread, args=[imagePath])
        th.start()
        if msecs > 0:
            cv2.waitKey(msecs)
        return True

    def showSliceOffImage(self):
        cv2.waitKey(170)
        self.closeImgThread()
        return True

    def clear(self):
        self.image = cv2.imread(self.imagesPath + '/black.png')
        cv2.imshow('dp110display', self.image)
        return True

    def MakeLineMask(self):
        image = Image.open(self.maskpath)
        LineImage = Image.open(os.environ.get('HOME', '/home/pi') + '/carima/dp110server/images' + '/maskLine.png')
        image_copy = image.copy()
        position = (0, 0)
        image_copy.paste(LineImage, position)
        image_copy.save(os.environ.get('HOME', '/home/pi') + '/carima/basic/IM-J_basic' + '/lineMask.png')
        return True

    def LinemaskImageOn(self):
        self.showSliceImage(os.environ.get('HOME', '/home/pi') + '/carima/basic/IM-J_basic/lineMask.png', -1)
        return True

    def maskImageOn(self):
        self.showSliceImage(os.environ.get('HOME', '/home/pi') + '/carima/basic/IM-J_basic/mask.png', -1)
        return True

    def whiteImageOn(self):
        self.showImage(os.environ.get('HOME', '/home/pi') + '/carima/basic/IM-J_basic/white.png', 0)
        return True

    def whiteImageOff(self):
        self.showSliceImage(self.imagesPath + '/black.png', 0)
        self.showSliceOffImage()
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
        self.showSliceImage(self.imagesPath + '/black.png', 0)
        self.grid[:] = self.black = (0, 0, 0, 225)
        return 1

    def Insertlog(self, logmsg):
        now = datetime.datetime.now()
        if self.logtime != now.strftime('%d-%H'):
            self.logbytime.removeHandler(self.logbytime.handlers[0])
            self.Initlog()
        self.logbytime.info(logmsg)

    def Initlog(self):
        now = datetime.datetime.now()
        nowDateYM = now.strftime(os.environ.get('HOME', '/home/pi') + '/SystemLog/%Y-%m')
        if not os.path.exists(nowDateYM):
            os.makedirs(nowDateYM)
        self.logtime = now.strftime('%d-%H')
        nowDateMDH = now.strftime(os.environ.get('HOME', '/home/pi') + '/SystemLog/%Y-%m/%m-%d-%H')
        self.logbytime = logging.getLogger('imjlog')
        hdlr = logging.handlers.TimedRotatingFileHandler(nowDateMDH)
        formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
        hdlr.setFormatter(formatter)
        self.logbytime.addHandler(hdlr)
        self.logbytime.setLevel(logging.INFO)