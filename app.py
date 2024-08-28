import time
import engine
import camera
import datetime
import uuid



def show(v):
    dt=datetime.datetime.now()
    dtt=dt.strftime("%H%M%S")
    l=str(dtt)
    for r in v:
        l=l+"\t"+str(r)
    print(l)

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


print("======================================")


engine.lcdMessage('initializaing...')


show(['init camera'])

#engine.initCamera()


show(['init position'])

engine.reset()

engine.lcdInfo()

show(['ready!'])
print("======================================")

try:

    while(True):
        
        print("")

        # x1=random.randrange(-10,10,1)
        # y1=random.randrange(-10,10,1)
        
        # input('CTRL + C')
        
        # print('')
        # x1=int(input('x1 : '))
        # y1=int(input('y1 : '))
        
        x1=0
        y1=0
        
        p1=P(x1,y1)
        
        engine.goto(p1)
        engine.takePicB(p1)
        
        camera.ocr(p1)
        
        #engine.takePic(p1)
        #OCR
        
        v=engine.getPoints(p1)
        
        print("")
        for p in v:
            
            #show([p.uid[0:8], p.x, p.y, p.ch])
            engine.goto(p)
            engine.updP(p1,p)
            engine.takePicB(p)
            camera.ocr(p)
            
            c=engine.getC(p)
            engine.updC(p, c)
            
            #take photo
            #ocr
            #reorder by radious
            time.sleep(1)
        
        engine.valP(p1)
        engine.lcdInfo()
        
        
    
except KeyboardInterrupt:
    print('You pressed ctrl+c')
    

print("======================================")
print("eof")
print("======================================")