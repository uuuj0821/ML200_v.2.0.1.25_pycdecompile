# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Nov 16 2020, 22:23:17)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /home/dp110/carima/dp110server/printer/cls_ML192v22.py
# Compiled at: 2019-04-10 12:43:29
"""
Created on Jun 18, 2015

@author: cloud3
"""
from lines.cls_controlpcb2 import cls_ControlPCB2
import logging
from printer.cls_extdisplayIMJ import cls_ExtDisplayIMJ
import os
from time import sleep
import time, sys, cv2, ConfigParser

class cls_ML192v22(object):
    """
    classdocs
    """
    Motor_STOP, Motor_UP, Motor_DOWN, Motor_Home = range(0, 4)
    Z_STOP, Z_UP, Z_DOWN, Z_HOME = range(0, 4)

    def readConfig(self, configPath):
        print configPath
        config = ConfigParser.ConfigParser()
        config.read(configPath)
        self.LightStep_Beginning = float(config.get('PARAMETER', 'LightStep_Beginning'))
        self.LightTime_Basic = float(config.get('PARAMETER', 'LightTime_Basic'))
        self.LightTime_Beginning = float(config.get('PARAMETER', 'LightTime_Beginning'))
        self.DivisionTime = float(config.get('PARAMETER', 'DivisionTime'))
        self.ZMotorEndUpDistance = int(config.get('MOTOR_SETUP', 'ZMotorEndUpDistance'))
        self.ZMotorAmount = float(config.get('MOTOR_SETUP', 'ZMotorAmount'))
        self.ZeroPoint = float(config.get('MOTOR_SETUP', 'ZeroPoint'))
        # self.WaitTime_Basic = float(config.get('PARAMETER', 'BasicWaitTime'))
        # self.WaitTime_Beginning = float(config.get('PARAMETER', 'InitWaitTime'))

    def writeConfig(self, configPath):
        print configPath
        config = ConfigParser()
        config.write(configPath)
        self.LightStep_Beginning = config.set('PARAMETER', 'LightStep_Beginning')
        self.LightTime_Basic = config.set('PARAMETER', 'LightTime_Basic')
        self.LightTime_Beginning = config.set('PARAMETER', 'LightTime_Beginning')
        self.DivisionTime = config.set('PARAMETER', 'DivisionTime')
        self.ZMotorEndUpDistance = config.set('MOTOR_SETUP', 'ZMotorEndUpDistance')
        self.ZMotorAmount = config.set('MOTOR_SETUP', 'ZMotorAmount')
        self.ZeroPoint = config.set('MOTOR_SETUP', 'ZeroPoint')

    def __init__(self, ImageRoot='./images', FileType='png'):
        """
        Constructor
        """
        self.readConfig(os.environ.get('HOME', '/home/dp110') + '/carima/system.cfg')
        self.display = cls_ExtDisplayIMJ(ImageRoot, 'png')
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
        self.board.ser.timeout = 0.3
        self.board.ser.writeTimeout = 0.3
        e = self.board.z_ledOn_fanOn(200)
        self.logger.debug('PCB_PAN ON: %s' % e)
        return 1

    def printConnect1(self):
        self.board.ser.timeout = 200
        self.board.ser.writeTimeout = 200
        return True

    def printConnect2(self):
        self.board.ser.timeout = 0.1
        self.board.ser.writeTimeout = 0.1
        return True

    def removeImageFile(self):
        os.system('sudo rm -r /home/dp110/carima/buffer/image')
        return True

    def zMotorPositionRead(self):
        self.board.readSignal('7E0D000000000000000000000000000A', 2000)
        return True

    def boardGo(self, value):
        self.logger.debug('Printing - Board_UP %f' % value)
        return self.board.z_AbsoluteMove(value, 30000)

    def boardHome(self):
        self.logger.debug('boardHome')
        return self.board.z_home(50000)

    def checkSensor(self):
        return self.board.checkSensor(2000)

    def changeTimer(self, lightTime):
        firstStep = round(lightTime / 60.0, 4)
        secondStep = round(firstStep / 0.0025, 4)
        setTime = int(round(15625.0 / secondStep, 4))
        self.logger.info('setTime = %d' % setTime)
        self.board.continuousTimer(setTime, 1)
        cv2.waitKey(250)
        return 1

    def orginalTimer(self):
        self.logger.debug('orginalTimer')
        self.board.orginalTimer(10000)
        cv2.waitKey(500)
        return 1

    def boardStop(self):
        self.logger.debug('boardStop')
        return self.board.z_MotorStop(1000)

    def boardUp(self, value):
        self.board.z_RelativeUp(value, 30000)
        self.logger.debug('Printing - Board_UP %f' % value)
        return 1

    def boardDown(self, value, lthick):
        self.board.z_RelativeDown(value - lthick, 30000)
        self.logger.debug('Printing - Board_Down %f-%f' % (value, lthick))
        return 1

    def shutdownbeep(self):
        self.board.shutdownbeep(1000)

    def led_fanOn(self):
        return self.board.z_ledOn_fanOn(1000)

    def ledOn_fanOff(self):
        return self.board.z_ledOn_fanOff(1000)

    def ledblink_fanOn(self):
        return self.board.z_ledBlink_fanOn(1000)

    def ledOff_fanOff(self):
        return self.board.z_ledOff_fanOff(1000)

    def engineOn(self, isOn):
        return 1

    def lightOn1(self, nowLayer, basicTime, beginningTime):
        try:
            imgPath = os.environ.get('HOME', '/home/pi') + '/carima/buffer/image/SEC_%04d.png' % nowLayer
            if nowLayer > self.LightStep_Beginning:
                lightOnTime = basicTime
            else:
                lightOnTime = beginningTime
            self.display.showSliceImage(imgPath, lightOnTime)
            return True
        except (IOError, ValueError) as e:
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
                showDividelightONtime = DividelightONtime + 200
                self.display.showSliceImage(imgPath, showDividelightONtime)
                lightOnTime -= DividelightONtime
                self.display.showSliceOffImage()
                sleep(0.1)
                if lightOnTime <= DividelightONtime:
                    self.display.showSliceImage(imgPath, lightOnTime)
                    self.display.showSliceOffImage()
                    lightOnTime = -200
                    return True

            self.display.showSliceImage(imgPath, lightOnTime + 100)
            self.logger.debug('--Light On--')
            return True
        except (IOError, ValueError) as e:
            self.logger.debug('Image Load failed : %s (%s)' % (imgPath, e))
            return False

    def BasicImageOn(self):
        imgPath = os.environ.get('HOME', '/home/dp110') + '/carima/dp110server/images/BasicImg.png'
        try:
            self.display.showSliceImage(imgPath, -1)
            return 1
        except (IOError, ValueError) as e:
            self.logger.debug('Image Load failed : %s (%s)' % (imgPath, e))
            return -1

    def BasicImageOff(self):
        self.display.showSliceOffImage()
        return 1

    def printingEndsqeunce(self, nowLayer, basicTime, beginningTime, DivideTime):
        if self.DivisionTime == 0:
            self.lightOn1(nowLayer, basicTime, beginningTime)
        else:
            self.lightOn(nowLayer, basicTime, beginningTime, DivideTime)
        self.display.showSliceOffImage()
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

    def timeprintingEndsqeunce(self):
        self.display.showSliceOffImage()
        self.led_fanOn()
        self.removeImageFile()
        self.printConnect2()
        return 1