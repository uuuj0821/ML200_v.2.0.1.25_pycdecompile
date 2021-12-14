import glob
from ConfigParser import ConfigParser
import cv2
from time import sleep

File_List=glob.glob('/home/dp110/carima/buffer/image/*.idx')
# idxpath = str(File_List)

# print File_List
# 
ConfigParser = ConfigParser()
ConfigParser.read(File_List)
try: 
    test = int(ConfigParser.get('PixelData', 'SEC_%04d.gif' % 100000))
except :
    sleep(1)
    test = 0
    pass
print test
# 
# print test

# f = open(idxpath, 'r')

# l=f.readlines()
# print(idxpath)
