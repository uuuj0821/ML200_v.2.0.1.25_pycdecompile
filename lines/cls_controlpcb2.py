# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Nov 16 2020, 22:23:17)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /home/dp110/carima/dp110server/lines/cls_controlpcb2.py
# Compiled at: 2017-12-21 10:53:32
"""
Created on Jun 18, 2015

@author: cloud3
"""
from _socket import htonl
import serial, logging, binascii
from serial import serialutil
import os
from time import sleep
if os.name == 'posix':
    from lines.cls_control import USBSerial

class cls_ControlPCB2:
    """    derived borad control class
    """

    def __init__(self, port=15, ser_newline='\r', spy=False):
        self.logger = logging.getLogger('dp110server')
        self.port = port
        self.zeroStop = 0
        try:
            if os.name == 'posix':
                self.ser = USBSerial(self.port)
            else:
                self.ser = serial.Serial(port=self.port - 1, baudrate=9600, bytesize=serialutil.EIGHTBITS, parity=serialutil.PARITY_NONE, stopbits=serialutil.STOPBITS_ONE, timeout=None)
                if not self.ser.isOpen():
                    self.ser.open()
        except serial.SerialException as e:
            self.logger.error('Could not connect serial port %s: %s\n' % (self.port, e))

        return

    def openSerialPort(self):
        try:
            if not self.ser.isOpen():
                self.ser.open()
            return self.ser.isOpen()
        except serial.SerialException as e:
            self.logger.error('Could not open serial port %s: %s\n' % (self.port, e))
            return False

    def closeSerialPort(self):
        try:
            if self.ser.isOpen():
                self.ser.close()
            return True
        except serial.SerialException as e:
            self.logger.error('Could not open serial port %s: %s\n' % (self.ser.portstr, e))
            return False

    def connect_PCBCom(self):
        return self.ser.open()

    def HexStrToByteArray(self, data, size=16):
        bstr = bytearray.fromhex(data)
        if len(bstr) != size:
            return False
        return bstr

    def ByteArrayToHexStr(self, byte):
        return binascii.hexlify(byte)

    def readData(self, msecs):
        if msecs == 50000:
            sleep(0.2)
        ret = self.ser.read(12)
        self.ser.flushOutput()
        return ret

    def writeData(self, data, msecs):
        self.ser.write(data)

    def readSignal(self, shex, msecs):
        global hx
        if len(self.HexStrToByteArray(shex, 16)) != 16:
            return
        else:
            try:
                data = self.HexStrToByteArray(shex, 16)
                self.writeData(data, msecs)
                s = self.readData(msecs)
                hx = self.ByteArrayToHexStr(s)
                return hx
            except:
                self.logger.error('sendSignal exception:%d' % hx)
                return True

            return

    def sendCommand(self, shex, msecs):
        ret = self.readSignal(shex, msecs)
        return ret

    def convertMoveValue(self, value):
        lvalue = value / 0.0025
        lvalues = round(lvalue, 1)
        llvalues = int(lvalues)
        nethex = htonl(llvalues)
        hexdata = ('{:08X}').format(nethex)
        return hexdata

    def convertValue(self, lightTime):
        lightvalue = int(lightTime)
        hexval = htonl(lightvalue)
        return ('{:08X}').format(hexval)

    def z_RelativeDown(self, value, msecs=20000):
        sdata = '7E0200000000%s00000000000A' % self.convertMoveValue(value)
        return self.sendCommand(sdata, msecs)

    def z_RelativeUp(self, value, msecs=30000):
        sdata = '7E0300000000%s00000000000A' % self.convertMoveValue(value)
        return self.sendCommand(sdata, msecs)

    def shutterOpen(self, msecs=1000):
        return self.sendCommand('7E19000000000000000000000000000A', msecs)

    def shutterClose(self, msecs=1000):
        return self.sendCommand('7E20000000000000000000000000000A', msecs)

    def shutdownbeep(self, msecs):
        return self.sendCommand('7E18000000000000000000000000000A', msecs)

    def z_MotorStop(self, msecs=200):
        return self.sendCommand('7E04000000000000000000000000000A', msecs)

    def z_read_version(self, msecs=200):
        return self.sendCommand('7E05000000000000000000000000000A', msecs)

    def z_ledOn_fanOn(self, msecs=200):
        return self.sendCommand('7E06000000000000000000000000000A', msecs)

    def z_ledOn_fanOff(self, msecs=200):
        return self.sendCommand('7E07000000000000000000000000000A', msecs)

    def z_ledOff_fanOff(self, msecs=200):
        return self.sendCommand('7E09000000000000000000000000000A', msecs)

    def z_ledBlink_fanOn(self, msecs=200):
        return self.sendCommand('7E08000000000000000000000000000A', msecs)

    def checkSensor(self, msecs=200):
        return self.sendCommand('7E13000000000000000000000000000A', msecs)

    def z_home(self, msecs):
        sdata = '7E0B000000000000000000000000000A'
        self.logger.info('home = %s' % sdata)
        return self.sendCommand('7E0B000000000000000000000000000A', msecs)

    def continuousTimer(self, lightTime, msecs=1):
        sdata = '7E1400000000%s00000000000A' % self.convertValue(lightTime)
        return self.sendCommand(sdata, msecs)

    def orginalTimer(self, lighttime, msecs=10000):
        return self.sendCommand('7E15000000000000000000000000000A', msecs)