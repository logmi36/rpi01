import time
import senders
import datetime
import os
import base64
import sqlite3



con1 = sqlite3.connect('local_db.sqlite')
cur1 = con1.cursor()


path='/home/pi/Documents/rpi1/images'


def write(txt):
    print('\n')
    print('='*40)
    print(txt,'='*10,'\n')


def show(list):
    dt=datetime.datetime.now()
    dtt=dt.strftime("%H%M%S")
    print(dtt,*list, sep='\t')
    
        
def upd(id, idv):
    dt=datetime.datetime.now()
    dtt=dt.strftime("%Y-%m-%d %H:%M:%S")
    sql="update positions set sn=1, dts='{dtt}', idv={idv} where id={id}".format(id=id, dtt=dtt, idv=idv)
    cur1.execute(sql)
    con1.commit()
    
def tobs64(uid):
    global path
    f2=uid+'.jpg'
    f3=os.path.join(path, f2)
    bs=''
    with open(f3, "rb") as image_file:
        bs64 = base64.b64encode(image_file.read())
        bs=bs64.decode('utf-8')    
    
    return bs    


def getP():
    sql="select id, uid, ch from positions where  en=1 and sn is NULL order by id ASC"
    cur1.execute(sql)
    rows=cur1.fetchall()
    
    res=False
    id=0
    ch=''
    uid=''
    
    for row in rows:
        res=True
        id=row[0]
        uid=row[1]
        ch=row[2]
    
    return res,id, ch, uid


def sendImage(id, pla, uid):

    v=senders.search(pla)

    for r  in v:

        print('')
        idv=r['f01']
        show([id, pla, uid[0:8], idv])

        bs=tobs64(uid)
            
        senders.sendImage(idv, bs)
        
        upd(id, idv)

def main():
    
    print('='*20)
    print('send image and notifications')
    print('='*20)
        
    while True:
        try:
            res,id, ch, uid=getP()
            
            if(res):
                
                #enviar imagen al servidor
                sendImage(id, ch, uid)
                
                #enviar notificaciones
                senders.main(ch)


            time.sleep(1)
            
        except KeyboardInterrupt:
            break
    
    write('eof')    
    


if __name__=='__main__':
    main()



