# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Nov 16 2020, 22:23:17)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /home/dp110/carima/dp110server/cls_rpcprintCM.py
# Compiled at: 2017-02-07 16:44:31
"""
Created on Jun 19, 2015

@author: cloud3
"""
from printer.cls_CMv22 import cls_CMV22
import os, logging, threading, zipfile, ConfigParser, xmlrpclib
from time import sleep
import sys, cv2, datetime, logging, logging.handlers
from logging.handlers import TimedRotatingFileHandler
from ConfigParser import ConfigParser
from time import time
from cv2 import WINDOW_NORMAL, CV_WINDOW_AUTOSIZE
from cv2 import cv
logger = logging.getLogger('dp110server')

class printThread(threading.Thread):

    def setPrint(self, parent, printer, rpcprinter, totalLayer, baseNumber, ZMotorAmount, thickness, ZeroPoint, ZMotorEndUpDistance, ifolder):
        self.parent = parent
        self.printer = printer
        self.rpcprinter = rpcprinter
        self.totalLayer = totalLayer
        self.baseNumber = baseNumber
        CMIDXpath = os.environ.get('HOME', '/home/pi') + '/carima/buffer/CMSection.idx'
        if os.path.exists(CMIDXpath) == True:
            self.nowLayer = 0
            self.totalLayer = totalLayer - 1
        else:
            self.nowLayer = 1
            self.totalLayer = totalLayer
        self.nowLayer = 1
        self.ZMotorAmount = ZMotorAmount
        self.thickness = thickness
        self.ZeroPoint = ZeroPoint
        self.ZMotorEndUpDistance = ZMotorEndUpDistance
        self.ifolder = ifolder
        self.pause = False
        self.stop = False
        self.interim = False
        self.interims = False
        self.interimcheck = False
        self.basicTime = int(self.printer.LightTime_Basic * 1000)
        self.beginningTime = int(self.printer.LightTime_Beginning * 1000)
        self.DivideTime = int(self.printer.DivisionTime * 1000)
        self.subtime = 0
        self.LightStep_Beginning = int(self.printer.LightStep_Beginning)
        self.shutterState = 0

    def run(self):
        self.printer.printConnect1()
        if self.printer.boardHome() != '4f0b0000000000000000500a' and self.parent.is_printing == 1:
            self.printer.boardHome()
        if self.stop == True:
            return 1
        self.printer.boardUp(self.printer.ZeroPoint)
        if self.stop == True:
            return 1
        if self.beginningTime != self.basicTime and self.beginningTime > self.basicTime:
            Minus_beginningTime = int((self.beginningTime - self.basicTime) / self.LightStep_Beginning)
        else:
            Minus_beginningTime = 0
        while self.nowLayer < self.totalLayer:
            if self.pause == True:
                if self.stop == True:
                    return 1
                if self.interim == True:
                    self.printer.boardUp(int(self.printer.ZMotorEndUpDistance))
                    self.interim = False
                    self.interimcheck = True
                    continue
                elif self.stop == True:
                    return 1
                else:
                    continue

            elif self.interims == True & self.interimcheck == True:
                self.printer.boardDown(int(self.printer.ZMotorEndUpDistance), 0)
                self.interims = False
                self.interimcheck = False
            else:
                sleep(1)
                self.printer.shutterOpen()
                self.shutterState = 1
                self.printer.printingsqeunce(self.nowLayer, self.basicTime, self.beginningTime, self.DivideTime, self.thickness)
                self.nowLayer += 1
                if self.stop == True:
                    self.printer.display.clear()
                    return 1
                self.printer.shutterClose()
                self.shutterState = 0
                self.printer.display.clear()
                if self.nowLayer <= self.LightStep_Beginning:
                    self.beginningTime = self.beginningTime - Minus_beginningTime
                sleep(0.5)
                self.printer.boardUp(self.printer.ZMotorAmount)
                if self.stop == True:
                    return 1
                self.printer.boardDown(self.printer.ZMotorAmount, self.thickness)
                if self.stop == True:
                    return 1
                if self.nowLayer >= self.totalLayer:
                    self.printer.printingEndsqeunce(self.nowLayer, self.basicTime, self.beginningTime, self.DivideTime)
                    self.printer.boardUp(int(self.printer.ZMotorEndUpDistance))
                    self.parent.is_printing = -1
                    return 1


class cls_RpcPrintCM(object):
    """
    classdocs
    """

    def __init__(self, params):
        """
        Constructor
        """
        self.printer = cls_CMV22()
        self.rpcprinter = cls_RpcPrintCM
        self.is_open = -1
        self.is_printing = 2
        self.new_img = 0
        self.is_light_on = False
        self.Initlog()
        self.Insertlog('system on')
        print 'CM'
        cv.NamedWindow('dp110display')
        cv.ResizeWindow('dp110display', 1280, 800)
        cv.MoveWindow('dp110display', 1024, 0)
        self.logger = logging.getLogger('dp110server')
        cv.StartWindowThread()
        self.printer.display.clear()
        self.engineUSEStartTime = 0
        if os.name == 'posix':
            self.configPath = os.environ.get('HOME', '/home/pi') + '/carima/system.cfg'
        else:
            self.configPath = 'System.cfg'

    def isOpenPorts(self):
        return self.is_open

    def openPorts(self):
        self.Insertlog('open port')
        return self.printer.printConnect()

    def closePorts(self):
        self.printer.board.closeSerialPort()
        self.is_open = -1
        return 1

    def isPrinting(self):
        return self.is_printing

    def printStart(self, FileType, totalLayer, thickness, totalTime):
        self.printer.readConfig(self.configPath)
        ifolder = os.environ.get('HOME', '/home/pi') + '/carima/buffer/image'
        if not os.path.exists(ifolder):
            self.logger.error('path not exists: %s' % ifolder)
            return False
        base_index = 1
        self.printer.display.imageRoot = ifolder
        self.printer.display.fileType = 'png'
        self.pthread = printThread()
        self.pthread.setPrint(self, self.printer, self.rpcprinter, totalLayer, base_index, self.printer.ZMotorAmount, thickness, self.printer.ZeroPoint, self.printer.ZMotorEndUpDistance, ifolder)
        self.printer.ledblink_fanOn()
        self.printer.printConnect1()
        self.pthread.start()
        self.Insertlog('printing start - %d - %d' % (totalTime, totalLayer))
        self.is_printing = 1
        return 1

    def uploadFile(self, fileName, fileData):
        if os.path.isdir('/home/pi/carima/buffer/image'):
            self.printer.removeImageFile()
        fileNames = os.environ.get('HOME', '/home/pi') + '/carima/buffer/' + fileName
        with open(fileNames, 'wb') as (handle):
            handle.write(fileData.data)
        fzip = zipfile.ZipFile(fileNames)
        fzip.extractall(os.environ.get('HOME', '/home/pi') + '/carima/buffer/image')
        fzip.close()
        return 1

    def sliceUpload(self, fileName, fileData):
        fileNames = os.environ.get('HOME', '/home/pi') + '/carima/data/' + fileName
        with open(fileNames, 'wb') as (handle):
            handle.write(fileData.data)
        return 1

    def sliceDownload(self):
        with open(os.environ.get('HOME', '/home/pi') + '/carima/system.cfg', 'rb') as (handle):
            return xmlrpclib.Binary(handle.read())
        handle.close()

    def getCurrentLayer(self):
        return self.pthread.nowLayer

    def printStop(self, nowLayer, remainTime):
        nowLayers = int(nowLayer)
        remainTimes = int(remainTime)
        self.is_printing = -1
        self.pthread.stop = True
        if self.pthread.shutterState == 1:
            self.printer.shutterClose()
        self.printer.printConnect2()
        self.printer.boardStop()
        self.printer.boardUp(self.printer.ZMotorEndUpDistance)
        self.printer.display.clear()
        self.printer.led_fanOn()
        self.Insertlog('printing stop - %d - %d' % (remainTimes, nowLayers))
        self.printer.removeImageFile()
        return 1

    def isPause(self):
        return self.pthread.pause

    def printPause(self, pauseinterim):
        if pauseinterim == True:
            self.pthread.pause = True
            self.pthread.interim = True
            self.Insertlog('printing pause_interim')
        else:
            self.pthread.pause = True
            self.Insertlog('printing pause')
        return 1

    def printResume(self, pauseinterim):
        if pauseinterim == True:
            self.pthread.interims = True
            self.pthread.pause = False
        else:
            self.pthread.pause = False
        self.Insertlog('printing resume')
        return 1

    def isEngineOn(self):
        return 1

    def enginePower(self, isOn):
        return 1

    def isLightOn(self):
        return 1

    def engineLightOn(self):
        self.Insertlog('engine_on')
        self.engineUSEStartTime = datetime.datetime.now().replace(microsecond=0)
        return 1

    def engineLightOff(self):
        self.Insertlog('engine_off')
        Config = ConfigParser()
        Config.optionxform = str
        engine_EndTime = datetime.datetime.now().replace(microsecond=0)
        engine_CurUseTime = engine_EndTime - self.engineUSEStartTime
        Config.read(os.environ.get('HOME', '/home/pi') + '/carima/system.cfg')
        pre_Engine_USETime = Config.get('SYSTEM', 'Engine_TotalTime')
        dtime = datetime.datetime.strptime(pre_Engine_USETime, '%H:%M:%S')
        TotalTime = dtime + engine_CurUseTime
        convert = TotalTime.strftime('%H:%M:%S')
        filepath = os.environ.get('HOME', '/home/pi') + '/carima/system.cfg'
        Config.set('SYSTEM', 'Engine_TotalTime', convert)
        with open(filepath, 'wb') as (configfile):
            Config.write(configfile)
        return 1

    def boardHome(self):
        return self.printer.boardHome()

    def led_fanOn(self):
        return self.printer.led_fanOn()

    def ledOn_fanOff(self):
        return self.printer.ledOn_fanOff()

    def ledblink_fanOn(self):
        return self.printer.ledblink_fanOn()

    def shutdown(self):
        self.printer.ledOff_fanOff()
        self.printer.shutdownbeep()
        self.Insertlog('system off')
        os.system('sudo shutdown -h 0')
        return 1

    def zMotorPosition(self):
        return self.printer.zMotorPosition()

    def boardStop(self):
        self.Insertlog('motor control - stop')
        return self.printer.boardStop()

    def Block_Stop(self):
        return self.printer.boardStop()

    def boardUp(self, ZMotorAmount):
        self.printer.boardStop()
        self.printer.boardUp(ZMotorAmount)
        self.Insertlog('motor control - up')
        return 1

    def boardDown(self, ZMotorAmount, thickness):
        self.printer.boardStop()
        self.printer.boardDown(ZMotorAmount, thickness)
        self.Insertlog('motor control - down')
        return 1

    def zeropointUp(self, ZMotorAmount):
        self.printer.printConnect1()
        self.printer.boardUp(ZMotorAmount)
        return self.printer.printConnect2()

    def zeropointDown(self, ZMotorAmount, thickness):
        self.printer.printConnect1()
        self.printer.boardDown(ZMotorAmount, thickness)
        return self.printer.printConnect2()

    def boardGo(self, ZMotorAmount):
        return self.printer.boardGo(ZMotorAmount)

    def pcb_sendCommand(self, data, msecs):
        return self.printer.board.sendCommand(data, msecs)

    def engine_sendCommand(self, data, msecs):
        return self.printer.engine.sendCommand(data, msecs)

    def BasicImageOff(self):
        self.printer.BasicImageOff()
        self.Insertlog('basicimage_off')
        return 1

    def BasicImageOn(self):
        self.printer.BasicImageOn()
        self.Insertlog('basicimage_on')
        return 1

    def whiteImageOn(self):
        self.printer.display.whiteclear()
        return 1

    def setupGrid(self, xres, yres, xgrid, ygrid, line):
        return self.printer.display.setupGrids(xres, yres, xgrid, ygrid, line)

    def showGrid(self, x, y, val, flag):
        self.printer.display.showGrids(x, y, val, flag)
        return 1

    def clearGrid(self):
        self.printer.display.clearGrids()
        return 1

    def adminSet(self):
        self.Insertlog('admin set')

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
        hdlr = logging.handlers.TimedRotatingFileHandler(nowDateMDH, when='d', interval=90, backupCount=3)
        formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
        hdlr.setFormatter(formatter)
        self.logbytime.addHandler(hdlr)
        self.logbytime.setLevel(logging.INFO)