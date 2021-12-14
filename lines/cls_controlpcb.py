#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jun 18, 2015

@author: cloud3
'''
from lines.cls_control import cls_Control
from _socket import htonl
from string import hexdigits

class cls_ControlPCB(cls_Control):  
    '''
    derived borad control class 
    '''

    def __init__(self, port=0, ser_newline='\r', spy=False):
        '''
        Constructor
        '''
        cls_Control.__init__(self, port=port, ser_newline=ser_newline, spy=spy)
        
    def connect_PCBCom(self):
        return self.connect(self, self.port)
    
    def readData(self, msecs=2000):
        self.ser.timeout = msecs/1000/3
        ntry = 0;
        e = ''        
        while True:
            if ntry > 3:
                break
            c = self.ser.read(1)
            e += c;
            if c=='P' or c=='F':
                break            
            ntry += 1                      
        return e
    
    def sendCommand(self, data, msecs=2000):
        if len(self.HexStrToByteArray(data)) != 8:
            self.logger.error("check data format:%s" % data)            
        return cls_Control.sendCommand(self, data, msecs=msecs) 
    
    def z_home(self, msecs=70000):
        return self.sendCommand("0205002000000000", msecs)

    def convertMoveValue(self, value):
        lvalue = int(value/0.0025)  # mm_per_step = 2.0 / 200 / 4 = 0.0025 (lead_screw_pitch: 2.0 mm/rot, motor: 200 steps / (1/4 microsteps) / rot)   
        nethex = htonl(lvalue)
        return '{:08X}'.format(nethex)
    
    def z_RelativeUp(self, value, msecs=30000):
        sdata = "02050007%s" % self.convertMoveValue(value)        
        return self.sendCommand(sdata, msecs)
       
    def z_RelativeDown(self, value, msecs=20000):
        sdata = "02050006%s" % self.convertMoveValue(value)        
        return self.sendCommand(sdata, msecs)
    
    def z_AbsoluteMove(self, value, msecs=100000):
        sdata = "02050004%s" % self.convertMoveValue(value)        
        return self.sendCommand(sdata, msecs)
    
    def z_MotorStop(self, msecs = 200):
        return self.sendCommand("0205000900000000", msecs)
    
    def read_version(self, msecs = 200):
        return self.readSignal("0205000B00000000", msecs)

    def pcb_SignalCheck(self):
        self.logger.error('not impl')       
        return False
