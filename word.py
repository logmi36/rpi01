import math

class word:

    def __init__(self, i, c, width,	height):
        
        hxi=177.0
        hyi=89.0
        
        c.sort(key = lambda d: d.x)

        self.c=c

        l=len(c)

        self.i=i
        self.l=l
        
        self.dx=1.0*(c[l-1].xc - c[0].xc)
        self.dy=1.0*(c[l-1].yc - c[0].yc)
        
        self.yc=(c[l-1].yc + c[0].yc)/2
        self.xc=(c[l-1].xc + c[0].xc)/2

        self.lx=int(abs(c[l-1].xc-c[0].xc+c[l-1].w)*1.2)
        self.ly=int(abs(c[l-1].yc-c[0].yc+c[l-1].h)*1.7)

        self.pl=(self.lx,self.ly)


        self.v=math.atan(self.dy / self.dx)
        self.w=(180.0 / math.pi)*self.v

        self.pc=(self.xc,self.yc)

        self.x0=c[0].x
        self.y0=c[0].y

        self.ch=''
        self.img=None
        
        self.width=width
        self.height=height
        
        self.r=((self.xc-(self.width/2.0))**2+(self.yc-(self.height/2.0))**2)**0.5
        
        self.hx=(self.xc-(self.width/2.0))*(hxi/self.width)
        self.hy=(self.yc-(self.height/2.0))*(hyi/self.height)
        
        self.x1=int(round(self.hx))
        self.y1=int(round(-1*self.hy))

        

