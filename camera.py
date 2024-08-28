import uuid
import sys
import math
import cv2
import numpy as np
import sqlite3
import pandas as pd
import character
import word
import os
import time
import datetime



BLANCO=(255.0,255.0,255.0)
AMARILLO=(0.0,255.0,255.0)
VERDE=(0.0,255.0,0.0)
ROJO=(0.0,0.0,255.0)

fuente = cv2.FONT_HERSHEY_SIMPLEX 

con2=sqlite3.connect('local_db.sqlite')
cur2 = con2.cursor()

# =======================================

sql="select * from images"
df1=pd.read_sql(sql,con2).astype('float32')

df2=df1.drop(columns=['n','c'])
df3=df1['c']

words_id=df3.to_numpy()
words_im=df2.to_numpy()

words_id = words_id.reshape((words_id.size, 1))       

kNearest = cv2.ml.KNearest_create()
kNearest.setDefaultK(1)
kNearest.train(words_im, cv2.ml.ROW_SAMPLE, words_id)


f1="/home/pi/Documents/rpi1/images"
f2="/home/pi/Documents/rpi1/result"


# =======================================

def isGroup(c1, c2):
    dx = float(abs(c1.x - c2.x))
    dy = float(abs(c1.y - c2.y))
    dd=math.sqrt((dx*dx) + (dy*dy))
    v = math.pi/2
    if dx != 0.0:
        v = math.atan(dy / dx)      
    dv = (180.0 / math.pi)*v
    ds = float(abs(c1.s - c2.s)) / float(c1.s)
    dw = float(abs(c1.w - c2.w)) / float(c1.w)
    dh = float(abs(c1.h - c2.h)) / float(c1.h)
    ans=False
    if (dd < (c1.d * 5) and
        dv < 12 and
        ds < 0.5 and
        dw < 0.8 and
        dh < 0.2):
        ans=True
    return ans   

# =======================================

def show(v):
    dt=datetime.datetime.now()
    dtt=dt.strftime("%H%M%S")
    l=str(dtt)
    for r in v:
        l=l+"\t"+str(r)
    print(l)
    

# =======================================


def save(p, po):
    sql="insert into plates(uid, i, l, xc, yc, v, dx, dy, x0, y0, lx, ly, ch, w, width, height,r, hx, hy, x1, y1) values('{uid}', {i}, {l}, {xc}, {yc}, {v}, {dx}, {dy}, {x0}, {y0}, {lx}, {ly}, '{ch}', {w},{width}, {height},{r},{hx},{hy},{x1},{y1})".format(uid=po.uid, i=p.i, l=p.l, xc=p.xc, yc=p.yc, v=p.v, dx=p.dx, dy=p.dy, x0=p.x0, y0=p.y0, lx=p.lx, ly=p.ly, ch=p.ch, w=p.w, width=p.width, height=p.height, r=p.r, hx=p.hx, hy=p.hy, x1=p.x1,y1=p.y1)
    cur2.execute(sql)
    con2.commit()
    
# =======================================


def ocr(po):

    imgOriginal  = cv2.imread('car.jpg')

    imgHSV = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2HSV)

    imgHue, imgSaturation, imgGrayscale = cv2.split(imgHSV)

    # maximizar contraste

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    imgTopHat   = cv2.morphologyEx(imgGrayscale, cv2.MORPH_TOPHAT, kernel)
    imgBlackHat = cv2.morphologyEx(imgGrayscale, cv2.MORPH_BLACKHAT, kernel)

    imgGrayscalePlusTopHat = cv2.add(imgGrayscale, imgTopHat)

    imgGrayscale2 = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)

    imgBlurred = cv2.GaussianBlur(imgGrayscale2, (5,5), 0)
    imgThresh  = cv2.adaptiveThreshold(imgBlurred, 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 19, 9)

    #imgGrayscale22 = cv2.cvtColor(imgGrayscale2,cv2.COLOR_GRAY2RGB)

    # encontrar todos los contornos
    #imgContours, contours,npaHierarchy = cv2.findContours(imgThresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)   
    
    contours, npaHierarchy = cv2.findContours(imgThresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)   
        
    n=len(contours)
    
    height0, width0 = imgThresh.shape
    imgLienzo = np.zeros((height0, width0, 3), np.uint8)

    posiblescharacteres = []  
    contador = 0
    
    for i in range(0, n):
        contour=contours[i]
        c = character.character(i,contour)
        if ((80<c.s) and (2<c.w) and (8<c.h) and (0.25<c.r) and (c.r < 1.0)):  
            contador = contador + 1           
            posiblescharacteres.append(c)                   

    grupocharacteres = []

    for c1 in posiblescharacteres:
        v=[]
        for c2 in posiblescharacteres:
            if(c2.g==0):
                if(isGroup(c1, c2)):
                    c2.g=c1.i
                    v.append(c2)
        if(len(v)>3):
            c1.g=c1.i
            v.append(c1)
            grupocharacteres.append(v)

    # rotacion de characteres

    grupowords=[]

    i=0
    for r1 in grupocharacteres:
        
        p=word.word(i,r1, width0, height0)
        rm = cv2.getRotationMatrix2D(p.pc, p.w, 1.0)
        h, w, nc = imgOriginal.shape 
        imgRotated = cv2.warpAffine(imgOriginal, rm, (w, h))
        imgCropped = cv2.getRectSubPix(imgRotated, p.pl, p.pc)
        p.img=imgCropped
        grupowords.append(p)
        i=i+1

    #redimensionar
        

    for q in grupowords:


        if(q.img is None):
            continue

        h, w, nc = q.img.shape
        imgHSV = cv2.cvtColor(q.img, cv2.COLOR_BGR2HSV)
        imgHue, imgSaturation, imgGray = cv2.split(imgHSV)

        imgTopHat = cv2.morphologyEx(imgGray, cv2.MORPH_TOPHAT, kernel)
        imgBlackHat = cv2.morphologyEx(imgGray, cv2.MORPH_BLACKHAT, kernel)

        imgAdd = cv2.add(imgGray, imgTopHat)
        imgSub = cv2.subtract(imgAdd, imgBlackHat)

        imgBlurred = cv2.GaussianBlur(imgSub, (5,5), 0)

        imgThresh = cv2.adaptiveThreshold(imgBlurred, 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 19, 9)

        imgThresh = cv2.resize(imgThresh, (0, 0), fx = 1.6, fy = 1.6)
        threshold, imgThresh = cv2.threshold(imgThresh, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        height, width = imgThresh.shape
        

        posiblescharacteres = []
        contours = []

        ##imgContours, contours, npaHierarchy = cv2.findContours(imgThresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours, npaHierarchy = cv2.findContours(imgThresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        n=len(contours)
        
        imgLienzo = np.zeros((height, width, 3), np.uint8)

        for j in range(0, n):
            contour=contours[j]
            c = character.character(j,contour)
            c.j=i
            c.m=0
            
            cv2.drawContours(imgLienzo, c.c, -1, BLANCO)
            ##cv2.rectangle(imgLienzo,c ,p2,(0,255,0),1)
            ##cv2.putText(imgLienzo, str(c.i), 1, fuente, 0.5, BLANCO, 1, cv2.LINE_AA) 
            
            if ((80<c.s) and (2<c.w) and (8<c.h) and (0.25<c.r) and (c.r < 1)):  
                contador = contador + 1           
                posiblescharacteres.append(c)      
                c.m=1                  

        # f5='imgLienzo.jpg'
        # cv2.imwrite(f5, imgLienzo)
        
        w = []
        
        for p1 in posiblescharacteres:
            v=[]
            for p2 in posiblescharacteres:
                if(p2.g==0):
                    if(isGroup(p1, p2)):
                        p2.g=p1.i
                        v.append(p2)
            if(len(v)>3):
                p1.g=p1.i
                v.append(p1)
                w.append(v)

        n2=len(w)
        
        if n2>0:
            posiblescharacteres=w[0]
        else:
            continue
        
        # si el character esta dentro de otro character

        for c1 in posiblescharacteres:
            for c2 in posiblescharacteres:
                if(c1!=c2):
                    if( (c1.x<c2.x) and (c2.x+c2.w<c1.x+c1.w)):
                        if( (c1.y<c2.y) and (c2.y+c2.h<c1.y+c1.h)):
                            c2.m=0
        
        # aplicando un ordenamiento de los characteres
        posiblescharacteres.sort(key = lambda p: p.x)  

        strChars=''

        for c in posiblescharacteres:
            if(c.m==1):
                imgROI = imgThresh[c.y : c.y + c.h,c.x : c.x + c.w]
                imgROIResized = cv2.resize(imgROI, (20, 30))           
                npaROIResized = imgROIResized.reshape((1, 20 * 30))
                npaROIResized = np.float32(npaROIResized)
                retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized, k = 1)   
                strChar = str(chr(int(npaResults[0][0]))) 
                c.ch=strChar
                strChars=strChars+strChar

        q.ch=strChars

        p1=(q.x0, q.y0)
        p2=(q.x0+q.lx, q.y0+q.ly)

        imgOriginal2=imgOriginal.copy()


        cv2.rectangle(imgOriginal2,p1,p2,(0,255,0),1)
        cv2.putText(imgOriginal2, strChars, p1, fuente, 1, ROJO, 2, cv2.LINE_AA)    

        f3=po.uid+'_{:02}.jpg'.format(q.i)
        
        #f3=po.uid+'_'+str(q.i)+'.jpg'
        
        f4=os.path.join(f2, f3)
        cv2.imwrite(f4, imgOriginal2)
        
        ##show([po.uid[0:8], q.i, strChars])
        save(q,po)

    
if __name__ == "__main__":
    uid=uuid.uuid4()
    show([uid])
    ocr(uid)
