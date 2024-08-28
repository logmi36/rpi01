import datetime
import sqlite3
import I2C_LCD_driver
import time
import RPi.GPIO as GPIO


mylcd = I2C_LCD_driver.lcd()
con1 = sqlite3.connect('local_db.sqlite')
cur1 = con1.cursor()

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(35, GPIO.IN)
GPIO.setup(37, GPIO.IN)
GPIO.setup(31, GPIO.OUT)


id=0
sup=0
inf=0

def showLcd(txt):
    global mylcd
    mylcd.lcd_clear()
    mylcd.lcd_display_string("Fecha: %s" %time.strftime("%Y-%m-%d"), 1)
    mylcd.lcd_display_string("Hora : %s" %time.strftime("%H:%M:%S"), 2)
    mylcd.lcd_display_string("",3)
    mylcd.lcd_display_string(txt,4)
    time.sleep(1)


def show(v):
    dt=datetime.datetime.now()
    dtt=dt.strftime("%H%M%S")
    l=str(dtt)
    for r in v:
        l=l+"\t"+str(r)
    print(l)



def reset():
    sql="select max(id) as id from positions where en=1"
    cur1.execute(sql)
    row=cur1.fetchone()
    id=row[0]
    update(id)

def getSup(id):
    sql="select min(id) as id from positions where en=1 and id>{id}".format(id=id)
    cur1.execute(sql)
    row=cur1.fetchone()
    id=-1
    if(row):
        id=row[0]
    return id


def getId():
    sql="select id from positions where en=1 and ps=1"
    cur1.execute(sql)
    row=cur1.fetchone()
    id=-1
    if(row):
        id=row[0]
    return id

def getInf(id):
    sql="select max(id) as id from positions where en=1 and id<{id}".format(id=id)
    cur1.execute(sql)
    row=cur1.fetchone()
    id=-1
    if(row):
        id=row[0]
    return id

def update(id):
    sql="update positions set ps=0 where en=1"
    cur1.execute(sql)
    con1.commit()
    sql="update positions set ps=1 where id={id}".format(id=id)
    cur1.execute(sql)
    con1.commit()
    
def toDateTime(date_time):
    format = '%Y-%m-%d %H:%M:%S'
    datetime_str = datetime.datetime.strptime(date_time, format)
    return datetime_str



def lcd(id):
    
    global con1
    global mylcd
    
    sql="select id, x1,y1, dtt, ch, sn from positions where id<={id} and en=1 order by id DESC limit 4;".format(id=id)
    cur1.execute(sql)
    rows=cur1.fetchall()


    GPIO.output(31,True)
        
    mylcd.lcd_clear()
    
    print('==============================================')
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

        mylcd.lcd_display_string(p5, i)
        
        show([i,dtt, p1, p2, p4, p7])
        
        i=i+1
        
        
    time.sleep(0.5)
    GPIO.output(31,False)
        
# ===========================================

def showP():
    global id
    global sup
    global inf
    show(['inf', 'id','sup'])
    show([inf, id, sup])


# ===========================================

print('==============================================')
print('up down screen script')
print('==============================================')


showLcd('reset')
reset()

id=getId()
sup=getSup(id)
inf=getInf(id)
showP()

showLcd('ready!')


while True:

    if GPIO.input(35):
        sup=getSup(id)
        if(sup !=-1):
            id=sup
            update(id)
            lcd(id) 
        else:
            time.sleep(1)    

    if GPIO.input(37):
        inf=getInf(id)
        if(inf !=-1):
            id=inf
            update(id)
            lcd(id) 
        else:
            time.sleep(1)       