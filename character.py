import cv2
import math

class character:

    def __init__(self, _num, _contour):

        self.i=_num
        self.j=0
        self.k=0
        self.n =len(_contour)
        
        self.c = _contour
        
        [x, y, w, h] = cv2.boundingRect(_contour)

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.s = w*h

        self.xc = x + w/2
        self.yc = y + h/2

        self.d = math.sqrt(w*w + h*h)

        self.r = float(w) / float(h)

        self.v=(180/math.pi)*math.atan(self.r)

        self.g=0

        self.m=1

        self.ch=''

