# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Nov 16 2020, 22:23:17)
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-44)]
# Embedded file name: /home/dp110/carima/dp110server/printer/cls_displayIMJ.py
# Compiled at: 2017-02-07 16:44:31
"""
Created on Jun 19, 2015

@author: cloud3
"""

class cls_DisplayIMJ(object):
    """
    classdocs
    """

    def __init__(self, imageRoot, fileType):
        """
        Constructor
        :param imageRoot: image folder path. no slash(/) at the end.
        :param fileType: gif, jpg, png, etc. no dot(.) at the beginning.
        """
        self.imageRoot = imageRoot
        self.fileType = 'png'
        self.black = None
        return

    def getLayerPath(self, layer):
        return self.getImagePath('SEC_%04d.png' % layer)

    def getImagePath(self, baseName):
        return '%s/%s' % (self.imageRoot, baseName)

    def showImage(self, imagePath, msecs):
        return True

    def showLayer(self, layer, msecs):
        self.showImage(self.getLayerPath(layer), msecs)