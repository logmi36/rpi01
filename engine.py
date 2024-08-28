import I2C_LCD_driver
import time
import datetime
import RPi.GPIO as GPIO
import sqlite3
import os
import shutil
import uuid
from difflib import SequenceMatcher


mylcd = I2C_LCD_driver.lcd()
con1 = sqlite3.connect('local_db.sqlite')
cur1 = con1.cursor()
path='/home/pi/Documents/rpi1/images'
home='/home/pi/Documents/rpi1'
txtf='/home/pi/Documents/rpi1/txt'

ic=True

mx=[32,40,36,38]
my=[12,18,16,22]

sx=[[False, False, False, True],[False, False, True, False],[False, True, False, False],[True, False, False, False]]
sy=[[False, False, True, True],[False, True, True, False],[True, True, False, False],[True, False, False, True]]


rx=[-92,85]
ry=[-22,67]



GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(mx[0], GPIO.OUT)
GPIO.setup(mx[1], GPIO.OUT)
GPIO.setup(mx[2], GPIO.OUT)
GPIO.setup(mx[3], GPIO.OUT)

GPIO.setup(my[0], GPIO.OUT)
GPIO.setup(my[1], GPIO.OUT)
GPIO.setup(my[2], GPIO.OUT)
GPIO.setup(my[3], GPIO.OUT)


#fin de carrera motor XY
GPIO.setup(13, GPIO.IN)
GPIO.setup(15, GPIO.IN)

#fin de carrera motor Z
GPIO.setup(7, GPIO.IN)
GPIO.setup(11, GPIO.IN)

#buttons up down
GPIO.setup(35, GPIO.IN)
GPIO.setup(37, GPIO.IN)


#leds:
#   [35]       [__] [33]
#   [37]       [29] [31]


GPIO.setup(33, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)
GPIO.setup(29, GPIO.OUT)




GPIO.output(33, False)
GPIO.output(31, False)
GPIO.output(29, False)


GPIO.output(my[0],False)
GPIO.output(my[1],False)
GPIO.output(my[2],False)
GPIO.output(my[3],False) 

GPIO.output(mx[0],False)
GPIO.output(mx[1],False)
GPIO.output(mx[2],False)
GPIO.output(mx[3],False) 


class P:
    uid=''
    x=0
    y=0
    ch=''
    def __init__(self, *args):
        if(len(args)==2):
            self.uid=str(uuid.uuid4())
            self.x=args[0]
            self.y=args[1]
        if(len(args)==3):
            self.uid=args[0]
            self.x=args[1]
            self.y=args[2]


def show(v):
    dt=datetime.datetime.now()
    dtt=dt.strftime("%H%M%S")
    l=str(dtt)
    for r in v:
        l=l+"\t"+str(r)
    
    print(l)

def save(a,b):
    
    # print('=========')
    # show([a.uid,a.x, a.y])
    show([b.uid[0:8],b.x, b.y, b.ch])
    # print('=========')
    
    sql="update positions set ps=0"
    cur1.execute(sql)
    con1.commit()
    
    dt=datetime.datetime.now()
    dtt=dt.strftime("%Y-%m-%d %H:%M:%S")
    sql="insert into positions(x0,y0,x1,y1,dtt,ps,uid) values({x0},{y0},{x1},{y1},'{dtt}',1,'{uid}');".format(x0=a.x,y0=a.y,x1=b.x,y1=b.y,dtt=dtt, uid=b.uid)
    cur1.execute(sql)
    con1.commit()


def updP(p1,p2):
    sql="update positions set rid='{rid}', ch='{ch}' where uid='{uid}'".format(rid=p1.uid, ch=p2.ch, uid=p2.uid)
    cur1.execute(sql)
    con1.commit()

def getP():
    sql="select uid,x1,y1,dtt from positions order by id desc limit 1;"
    cur1.execute(sql)
    row=cur1.fetchone()
    uid=row[0]
    x1=row[1]
    y1=row[2]
    p1=P(uid,x1,y1)
    return p1

def genT(uid):
    sql="select id, uid, ch from positions where uid='{uid}'".format(uid=uid)
    cur1.execute(sql)
    row=cur1.fetchone()
    
    id=str(row[0])
    uid=str(row[1])
    ch=str(row[2])
    
    lines=[id+'\n',uid+'\n',ch+'\n']
    
    f1=uid+'.txt'
    fn=os.path.join(txtf, f1)
    
    file=open(fn,'w')
    file.writelines(lines)
    file.close()
    

def valP(p):
    
    sql="update positions set en=0 where rid='{rid}'".format(rid=p.uid)
    cur1.execute(sql)
    con1.commit()
    
    sql="select uid, ch, nc from positions where rid='{rid}'".format(rid=p.uid)
    cur1.execute(sql)
    rows=cur1.fetchall()
    
    n=0
    for r in rows:
        uid=r[0]
        ch=r[1]
        nc=r[2]
        r=similar(ch, nc)
        sql="update positions set r={r} where uid='{uid}'".format(r=r, uid=uid)
        cur1.execute(sql)
        con1.commit()
        
        if(r>0.5):
            n=n+1
            sql="update positions set en=1 where uid='{uid}'".format(uid=uid)
            cur1.execute(sql)
            con1.commit()
            
            genT(uid)

    if(n>0):
        rerP()
    
def rerP():
    
    sql="update positions set ps=0"
    cur1.execute(sql)
    con1.commit()
    
    sql="select max(id) as id from positions where en=1"
    cur1.execute(sql)
    row=cur1.fetchone()
    id=row[0]
    
    sql="update positions set ps=1 where id={id}".format(id=id)
    cur1.execute(sql)
    con1.commit()
        
    
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()        

def getC(p):
    sql="select ch from plates where uid='{uid}' order by r ASC".format(uid=p.uid)
    cur1.execute(sql)
    row=cur1.fetchone()
    
    ch=''
    if(row):
        ch=row[0]
    
    return ch

def updC(p, ch):
    sql="update positions set nc='{nc}' where uid='{uid}'".format(nc=ch, uid=p.uid)
    cur1.execute(sql)
    con1.commit()

def getPoints(p):
    sql="select i, ch, uid, x1,  y1 from plates  where uid='{uid}' order by id asc".format(uid=p.uid)
    cur1.execute(sql)
    rows=cur1.fetchall()
    v=[]
    for r in rows:
        ch=r[1]
        x1=r[3]
        y1=r[4]
        q=P(x1, y1)
        q.ch=ch
        v.append(q)
    return v

def initCamera():
    
    global camera
    
    camera.resolution=(1280,720)
    camera.framerate=40
    #camera.sensor_mode=4
    camera.iso=300
    #camera.meter_mode='matrix'
    time.sleep(2)
    
def endCamera():
    global camera 
    camera.close()
    return True

def takePic(p):
    
    f1=p.uid+'.jpg'
    f2='car.jpg'

    f3=os.path.join(path, f1)
    f4=os.path.join(home, f2)
    
    camera.capture(f2)
    
    shutil.copyfile(f4,f3)
    
    return True


def takePicB(p):
    
    
    f1=p.uid+'.jpg'
    f2='car.jpg'

    f3=os.path.join(path, f1)
    f4=os.path.join(home, f2)
    
    # print(f4)
    # print('-->')
    # print(f3)
    
    shutil.copyfile(f4,f3)
    
    return True

    
def lcdMessage(l):
    mylcd.lcd_clear()
    mylcd.lcd_display_string("%s" %time.strftime("%Y-%m-%d"), 1)
    mylcd.lcd_display_string("%s" %time.strftime("%H:%M:%S"), 2)
    mylcd.lcd_display_string(l, 3)
    mylcd.lcd_display_string("", 4)
    time.sleep(1)


def getId():
    global con1

    sql="select ifnull(id,0) as id from positions where ps=1"
    cur1.execute(sql)
    row=cur1.fetchone()
    id=row[0]
    return id


def toDateTime(date_time):
    format = '%Y-%m-%d %H:%M:%S'
    datetime_str = datetime.datetime.strptime(date_time, format)
    return datetime_str



def lcdInfo():
    
    global con1
    global mylcd
    
    idn=getId()

    sql="select id, x1,y1, dtt, ch, sn from positions where id<={idn} and en=1 order by id DESC limit 4;".format(idn=idn)
    cur1.execute(sql)
    rows=cur1.fetchall()


    GPIO.output(31,True)
        
    mylcd.lcd_clear()
    ##print('==============================================')
    i=1
    for row in rows:
        p1=row[1]
        p2=row[2]
        dtt=toDateTime(row[3])
        p3=dtt.strftime('%H:%M:%S')
        p4=row[4]
        p6=row[5]
        p7=''
        if(p6==1):
            p7='OK'
        
        p5="{dtt} {ch}  {sn}".format(dtt=p3, ch=p4, sn=p7)
        
        #p4="{dtt} {x1},{y1}".format(dtt=p3, x1=p1, y1=p2)
        mylcd.lcd_display_string(p5, i)
        i=i+1
        #show([idn+i,p4])

    time.sleep(0.5)
    GPIO.output(31,False)
    

def sign(a,b):
    
    r=P(0,0)
    
    if (a.x<b.x):
        r.x=1
    if (a.x>b.x):
        r.x=-1
    
    if (a.y<b.y):
        r.y=1
    if (a.y>b.y):
        r.y=-1
        
    return r


def reset():
    
    x=0
    
    while(True):
        
        x+=1
        step(x,0)
        sns()
        if(GPIO.input(13)):
            break


    y=0
    
    while(True):
        
        y-=1
        step(0,y)
        sns()
        if(GPIO.input(11)):
            break
        
    a=getP()
    b=P(85,-22)
    save(a,b)
    
    b=P(0,0)
    c=goto(b)
    
    #show([c.uid, c.x, c.y])
    

def goto(*args):
    
    # a --> b
    
    a=getP()
    c=getP()
    b=args[0]
    
    if(len(args)==2):
        a=args[0]
        c=args[0]
        b=args[1]
        
    
    r=sign(a,b)
    
    while(True):
        
        sns()
        
        
        if(GPIO.input(13) and (r.x>0)):
            a.x=rx[1]
            b.x=rx[1]
        
        if(GPIO.input(15) and (r.x<0)):
            a.x=rx[0]
            b.x=rx[0]
        
        if(GPIO.input(11) and (r.y<0)):
            a.y=ry[0]
            b.y=ry[0]
            
        if(GPIO.input(7) and (r.y>0)):
            a.y=ry[1]
            b.y=ry[1]

                        
        r=sign(a,b)
        
        a.x+=r.x
        a.y+=r.y
        
        step(a.x, a.y)
        
        sns()
        
        if(r.x==0 and r.y==0):
            break
    
    
    save(c, b)
        
    return a                            

    
    
def step(n,m):
    
    i=n%4
    j=m%4
    
    GPIO.output(mx[0],sx[i][0])
    GPIO.output(mx[1],sx[i][1])
    GPIO.output(mx[2],sx[i][2])
    GPIO.output(mx[3],sx[i][3])
    
    GPIO.output(my[0],sy[j][0])
    GPIO.output(my[1],sy[j][1])
    GPIO.output(my[2],sy[j][2])
    GPIO.output(my[3],sy[j][3])
    
    time.sleep(0.05)
    
    
    
def sns():
    
    GPIO.output(29,False)
    
    #sensor X
    if (GPIO.input(15)):
        GPIO.output(29,True)
    
    if (GPIO.input(13)):
        GPIO.output(29,True)
    
    #sensor Y
    if (GPIO.input(11)):
        GPIO.output(29,True)
    
    if (GPIO.input(7)):
        GPIO.output(29,True)





if __name__=='__main__':
    show(['reset'])
    lcdMessage('reset')
    reset()
    lcdInfo()
    