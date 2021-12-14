# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Nov 16 2020, 22:23:17)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /home/dp110/carima/dp110server/printer/cls_CMv22.py
# Compiled at: 2017-02-07 16:44:31
"""
Created on Jun 18, 2015

@author: cloud3
"""
from lines.cls_controlpcb2 import cls_ControlPCB2
import logging
from printer.cls_extdisplay import cls_ExtDisplay
from ConfigParser import ConfigParser
import os
from time import sleep
import time, sys, cv2

class cls_CMV22(object):
    """
    classdocs
    """
    Motor_STOP, Motor_UP, Motor_DOWN, Motor_Home = range(0, 4)
    Z_STOP, Z_UP, Z_DOWN, Z_HOME = range(0, 4)

    def readConfig(self, configPath='system.cfg'):
        print configPath
        config = ConfigParser()
        config.read(configPath)
        self.LightStep_Beginning = float(config.get('PARAMETER', 'LightStep_Beginning'))
        self.LightTime_Basic = float(config.get('PARAMETER', 'LightTime_Basic'))
        self.LightTime_Beginning = float(config.get('PARAMETER', 'LightTime_Beginning'))
        self.DivisionTime = float(config.get('PARAMETER', 'DivisionTime'))
        self.MotorStep = float(config.get('MOTOR_SETUP', 'MotorStep'))
        self.ZMotorEndUpDistance = int(config.get('MOTOR_SETUP', 'ZMotorEndUpDistance'))
        self.ZMotorAmount = float(config.get('MOTOR_SETUP', 'ZMotorAmount'))
        self.ZeroPoint = float(config.get('MOTOR_SETUP', 'ZeroPoint'))

    def writeConfig(self, configPath='system.cfg'):
        print configPath
        config = ConfigParser()
        config.write(configPath)
        self.LightStep_Beginning = config.set('PARAMETER', 'LightStep_Beginning')
        self.LightTime_Basic = config.set('PARAMETER', 'LightTime_Basic')
        self.LightTime_Beginning = config.set('PARAMETER', 'LightTime_Beginning')
        self.DivisionTime = config.set('PARAMETER', 'DivisionTime')
        self.MotorStep = config.set('MOTOR_SETUP', 'MotorStep')
        self.ZMotorEndUpDistance = config.set('MOTOR_SETUP', 'ZMotorEndUpDistance')
        self.ZMotorAmount = config.set('MOTOR_SETUP', 'ZMotorAmount')
        self.ZeroPoint = config.set('MOTOR_SETUP', 'ZeroPoint')

    def __init__(self, ImageRoot='./images', FileType='png'):
        """
        Constructor
        """
        self.readConfig(os.environ.get('HOME', '/home/pi') + '/carima/system.cfg')
        self.display = cls_ExtDisplay(ImageRoot, 'png')
        self.logger = logging.getLogger('dp110server')
        self.board = cls_ControlPCB2(0)

    def printConnect(self):
        """
        serial = USBSerial(portEngine)
        serial.timeout = 0.1
        serial.writeTimeout = 0.1
        serial.write('
')
        r = serial.read(1)
        if r=='' or not r in 'PF':
            eport = portPcb
            bport = portEngine
            self.logger.error('port number changed!')
        else:
            eport = portEngine
            bport = portPcb
        """
        if not self.board.openSerialPort():
            self.logger.debug('PCB, Engine connect failed')
            return False
        self.board.ser.timeout = 0.1
        self.board.ser.writeTimeout = 0.1
        e = self.board.z_ledOn_fanOn(200)
        self.logger.debug('PCB_PAN ON: %s' % e)
        return 1

    def printConnect1(self):
        self.board.ser.timeout = 40
        self.board.ser.writeTimeout = 40
        return 1

    def printConnect2(self):
        self.board.ser.timeout = 0.1
        self.board.ser.writeTimeout = 0.1
        return 1

    def removeImageFile(self):
        os.system('sudo rm -r /home/pi/carima/buffer/image')
        return 1

    def boardHome(self):
        self.logger.debug('boardHome')
        return self.board.z_home(50000)

    def orginalTimer(self):
        self.logger.debug('orginalTimer')
        self.board.orginalTimer(10000)
        return 1

    def boardStop(self):
        self.logger.debug('boardStop')
        return self.board.z_MotorStop(1000)

    def boardUp(self, value):
        self.board.z_RelativeUp(value, 30000)
        self.logger.debug('Printing - Board_UP %d' % value)
        return 1

    def boardDown(self, value, lthick):
        self.board.z_RelativeDown(value - lthick, 30000)
        self.logger.debug('Printing - Board_Down %f-%f' % (value, lthick))
        return 1

    def shutterOpen(self):
        self.board.shutterOpen(1000)
        return 1

    def shutterClose(self):
        self.board.shutterClose(1000)
        return 1

    def shutdownbeep(self):
        self.board.shutdownbeep(1000)
        return 1

    def led_fanOn(self):
        self.logger.debug('led_fanOn')
        return self.board.z_ledOn_fanOn(1000)

    def ledOn_fanOff(self):
        self.logger.debug('ledOn_fanOff')
        return self.board.z_ledOn_fanOff(1000)

    def ledblink_fanOn(self):
        self.logger.debug('ledblink_fanOn')
        return self.board.z_ledBlink_fanOn(1000)

    def ledOff_fanOff(self):
        self.logger.debug('ledOn_fanOff')
        return self.board.z_ledOff_fanOff(1000)

    def engineOn(self, isOn):
        return 1

    def lightOn1(self, nowLayer, basicTime, beginningTime):
        try:
            imgPath = self.display.getLayerPath(nowLayer)
            self.logger.debug('Light Ready : %s' % imgPath)
            if nowLayer > self.LightStep_Beginning:
                lightOnTime = basicTime
            else:
                lightOnTime = beginningTime
            self.display.showImage(imgPath, lightOnTime - 100)
            self.logger.debug('--Light On--')
            return True
        except (IOError, ValueError) as e:
            self.logger.debug('Image Load failed : %s (%s)' % (imgPath, e))
            return False

    def lightOn(self, nowLayer, basicTime, beginningTime, DivideTime):
        try:
            imgPath = self.display.getLayerPath(nowLayer)
            self.logger.debug('Light Ready : %s' % imgPath)
            if nowLayer > self.LightStep_Beginning:
                lightOnTime = basicTime
                DividelightONtime = DivideTime
            else:
                lightOnTime = beginningTime
                DividelightONtime = DivideTime
            while lightOnTime > DividelightONtime:
                showDividelightONtime = DividelightONtime - 100
                self.display.showImage(imgPath, showDividelightONtime)
                lightOnTime -= DividelightONtime
                self.display.clear()
                sleep(1)
                if lightOnTime <= DividelightONtime:
                    self.display.showImage(imgPath, lightOnTime - 100)
                    self.display.clear()
                    lightOnTime = 100
                    return True

            self.display.showImage(imgPath, lightOnTime - 100)
            self.logger.debug('--Light On--')
            return True
        except (IOError, ValueError) as e:
            self.logger.debug('Image Load failed : %s (%s)' % (imgPath, e))
            return False

    def BasicImageOn(self):
        imgPath = os.environ.get('HOME', '/home/pi') + '/carima/dp110server/images/BasicImg1280.png'
        try:
            self.display.showImage(imgPath, -1)
            return 1
        except (IOError, ValueError) as e:
            self.logger.debug('Image Load failed : %s (%s)' % (imgPath, e))
            return -1

    def BasicImageOff(self):
        self.display.clear()
        return 1

    def printingEndsqeunce(self, nowLayer, basicTime, beginningTime, DivideTime):
        if self.DivisionTime == 0:
            self.lightOn1(nowLayer, basicTime, beginningTime)
        else:
            self.lightOn(nowLayer, basicTime, beginningTime, DivideTime)
        self.display.clear()
        self.led_fanOn()
        self.removeImageFile()
        self.printConnect2()
        return 1

    def printingsqeunce(self, nowLayer, basicTime, beginningTime, DivideTime, thickness):
        if self.DivisionTime == 0:
            self.lightOn1(nowLayer, basicTime, beginningTime)
        else:
            self.lightOn(nowLayer, basicTime, beginningTime, DivideTime)
        return 1