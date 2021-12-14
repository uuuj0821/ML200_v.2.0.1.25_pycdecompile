# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Nov 16 2020, 22:23:17)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /home/dp110/carima/dp110server/printer/cls_IM131.py
# Compiled at: 2017-05-15 13:42:51
"""
Created on Jun 18, 2015

@author: cloud3
"""
from lines.cls_controlpcb3 import cls_ControlPCB3
import logging
from printer.cls_extdisplayIMJ import cls_ExtDisplayIMJ
from ConfigParser import ConfigParser
import os
from time import sleep
import time, sys, cv2

class cls_IM131(object):
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
        self.readConfig(os.environ.get('HOME', '/home/dp110') + '/carima/system.cfg')
        self.display = cls_ExtDisplayIMJ(ImageRoot, 'png')
        self.logger = logging.getLogger('dp110server')
        self.board = cls_ControlPCB3(0)

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
        self.board.UpTray(20, 3000)
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

    def changeTimer(self):
        self.board.continuousTimer(1000)
        cv2.waitKey(250)
        return 1

    def orginalTimer(self):
        self.logger.debug('orginalTimer')
        self.board.orginalTimer(1000)
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

    def TrayUp(self, value):
        self.board.UpTray(value, 30000)
        return 1

    def TrayDown(self, value):
        self.board.DownTray(value, 30000)
        return 1

    def TraySlowDown(self, value):
        self.board.SlowDownTray(value, 30000)
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
            imgPath = self.display.getLayerPath(nowLayer)
            self.logger.debug('Light Ready : %s' % imgPath)
            if nowLayer > self.LightStep_Beginning:
                lightOnTime = basicTime + 100
            else:
                lightOnTime = beginningTime + 100
            self.display.showSliceImage(imgPath, lightOnTime)
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
                showDividelightONtime = DividelightONtime + 200
                self.display.showSliceImage(imgPath, showDividelightONtime)
                lightOnTime -= DividelightONtime
                self.display.showSliceOffImage()
                cv2.waitKey(100)
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

    def timeprintingEndsqeunce(self):
        self.display.clear()
        self.led_fanOn()
        self.removeImageFile()
        self.printConnect2()
        return 1