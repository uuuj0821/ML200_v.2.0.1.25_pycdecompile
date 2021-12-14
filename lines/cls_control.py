# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Nov 16 2020, 22:23:17)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /home/dp110/carima/dp110server/lines/cls_control.py
# Compiled at: 2017-02-07 16:44:31
"""
Created on Jun 17, 2015

@author: Shocky Han <shockyhan@gmail.com>
core serial communication function for DP110 remote printing system
"""
import codecs, binascii, logging, os, serial
from serial.serialutil import SerialException
from serial import serialutil
if os.name == 'posix':

    class USBSerial(serial.PosixSerial, serial.serialutil.FileLike):
        """
           port: number of device; numbering starts at
                zero. if everything fails, the user can
                specify a device string, note that this
                isn't portable any more. /dev/ttyUSB0
           baudrate: baud rate
           bytesize: number of databits
           parity: enable parity checking
           stopbits: number of stopbits
           timeout: set a timeout (None for waiting forever)
           xonxoff: enable software flow control
           rtscts: enable RTS/CTS flow control
           retry: DOS retry mode
        """

        def open(self):
            """Open port with current settings. This may throw a SerialException
               if the port cannot be opened."""
            if self._port is None:
                raise SerialException('Port must be configured before it can be used.')
            if self._isOpen:
                raise SerialException('Port is already open.')
            self.fd = None
            try:
                mode = os.O_RDWR | os.O_NOCTTY | os.O_NDELAY
                mode &= ~os.O_NONBLOCK
                self.fd = os.open(self.portstr, mode)
            except Exception as msg:
                self.fd = None
                raise SerialException('could not open port %s: %s' % (self._port, msg))
            else:
                try:
                    pass
                except:
                    try:
                        os.close(self.fd)
                    except:
                        pass

                    self.fd = None
                    raise

                self._isOpen = True

            return

        def makeDeviceName(self, port):
            return '/dev/ttyUSB%d' % port


class cls_Control(object):
    """
    serial control class
    """

    def __init__(self, port, ser_newline='\r', spy=False):
        """
        Constructor
        """
        self.port = port
        self.ser_newline = ser_newline
        self.spy = spy
        self.logger = logging.getLogger('dp110server')

    def connect(self, port):
        self.ser = USBSerial(port)
        self.ser.port = port
        self.ser.baudrate = 9600
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.logger.info('port %s' % port)
        try:
            self.ser.open()
            return True
        except serial.SerialException as e:
            self.logger.error('Could not open serial port %s: %s' % (self.ser.port, e))
            return False

    def openSerialPort(self):
        try:
            try:
                if not self.ser.isOpen():
                    self.connect(self.port)
            except AttributeError as e:
                if os.name == 'posix':
                    self.ser = USBSerial(self.port)
                else:
                    self.ser = serial.Serial(port=self.port - 1, baudrate=9600, bytesize=serialutil.EIGHTBITS, parity=serialutil.PARITY_NONE, stopbits=serialutil.STOPBITS_ONE, timeout=None)

            return self.ser.isOpen()
        except serial.SerialException as e:
            self.logger.error('Could not open serial port %s: %s\n' % (self.port, e))
            return False

        return

    def closeSerialPort(self):
        try:
            self.stop()
            if self.ser.isOpen():
                self.ser.close()
            return True
        except serial.SerialException as e:
            self.logger.error('Could not open serial port %s: %s\n' % (self.ser.portstr, e))
            return False

    def HexStrToByteArray(self, data):
        return bytearray.fromhex(data)

    def ByteArrayToHexStr(self, byte):
        return binascii.hexlify(byte)

    def writeData(self, data):
        """ write hex string (data) to byte array to serial port """
        if not data:
            return False
        try:
            self.ser.write(bytearray.fromhex(data))
            if self.spy:
                self.logger.info(codecs.escape_encode(data)[0])
        except serial.SerialException as e:
            self.logger.error('%s' % e)

        return True

    def stop(self):
        """stop all actions"""
        pass

    def readData(self, msecs=2000):
        """derived classes should override this function"""
        self.ser.timeout = msecs / 1000
        return self.ser.read(1)

    def readSignal(self, data, msecs=2000):
        self.ser.writeTimeout = msecs / 1000
        self.ser.timeout = msecs / 1000
        self.writeData(data)
        s = self.readData(msecs)
        return s

    def sendCommand(self, data, msecs=2000):
        s = self.readSignal(data, msecs)
        if s == '' or s[0] not in 'PFO':
            return None
        e = s.startswith('P')
        if e:
            self.logger.debug('Success')
            return 1
        else:
            self.logger.debug('Fail')
            return -1
            return -1