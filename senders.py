import requests
import sys
import datetime
import firebase_admin
from firebase_admin import credentials, messaging
from time import sleep


firebase_cred = credentials.Certificate("contransapp-c0837-firebase-adminsdk-wbd3o-b51a405ed9.json")
firebase_app = firebase_admin.initialize_app(firebase_cred)

base='http://192.168.0.6:8085/'
##base='http://192.168.0.101:8085/'
##base='http://192.168.128.26:8085/'
##base='https://ctrapi8-hxd5cqbxfuebabdv.mexicocentral-01.azurewebsites.net/'

rpi='rpi01@contrans.pe'

ubn='arribo'
url1=base+'api/notificacion/insertar'
url2=base+'api/cita/listar/matricula'
url3=base+'api/cita/mostrarxid'
url4=base+'api/cita/actualizararribo'
url5=base+'api/cita/actualizaringreso'
url6=base+'api/cita/actualizarsalida'
url7=base+'api/vehiculo/buscar'
url8=base+'api/vehiculo/imagenregistrar'


def write(txt):
    print('\n')
    print('='*90)
    print(txt,'='*20,'\n')


def show(list):
    dt=datetime.datetime.now()
    dtt=dt.strftime("%H%M%S")
    print(dtt,*list, sep='\t')
    
    
def listarCitas(id):
    
    url=url2+"/"+id
    res=requests.get(url) 
    return res.json()


def obtenerCita(id):
    im={"num":id,"ser":rpi,"des":"","tip":"","com":"","rem":""}
    res=requests.post(url3, json=im) 
    return res.json()

def insertar(im):
    res=requests.post(url1, json=im) 
    return res.json()

def actualizarA(im):
    res=requests.post(url4, json=im) 
    return res.json()


def notificar(title, body, tokens, data):
    message = messaging.MulticastMessage(notification=messaging.Notification(title=title,body=body), data=data,tokens=tokens)
    messaging.send_multicast(message)


def search(id):
    im={"num":id,"ser":"","des":"","tip":"","com":"","rem":""}
    res=requests.post(url7, json=im) 
    return res.json()

def sendImage(id, img):
    im={"num":id,"ser":img,"des":"","tip":"","com":"","rem":""}
    res=requests.post(url8, json=im) 
    return res.json()


def main(id):
    
    print('')
    show([id])
    
    items=listarCitas(id)
    
    for item in items:
        
        f01=item['f01']
        f02=item['f02']
        f03=item['f03']
        f04=item['f04']
        f05=item['f05']
        f06=item['f06']
        f07=item['f07']
        f08=item['f08']
        f09=item['f09']
        f10=item['f10']
        
        
        if(f08=="0"):
            
            show([f01, f03[0:16]])
            m=obtenerCita(f01)
            m01=m['f01']
            m02=m['f02']
            m03=m['f03']
            m04=m['f04']
            m05=m['f05']
            m06=m['f06']
            m07=m['f07']
            m08=m['f08']
            m09=m['f09']
            m10=m['f10']
            m11=m['f11']
            m12=m['f12']
            m13=m['f13']
            m14=m['f14']
            m15=m['f15']
            m16=m['f16']
            m17=m['f17']
            m18=m['f18']
            
    
            
            #actualiza cita - fecha de arribo
            im={"num":f01,"ser":rpi,"des":"","tip":"","com":"","rem":""}
            r=actualizarA(im)
            
            dt1=r['num']
            dt2=r['ser']
            
            
            p1=m13 + " " + m04 + "-" + m05
            p2=m10 + " | " + m11 + " : " + m12+ " | "+ubn+ " | " + dt2 + " "+ dt1
            p3={"idCita":m01}
            
            #notificar
            notificar(p1,p2,[f03],p3)
            
            #insertar notificacion
            im={"num":m01,"ser":f03,"des":f04,"tip":p1,"com":p2,"rem":rpi}
            insertar(im)
            
            print('')
            print(p1)
            print(p2)
            print('')

if __name__=='__main__':
    id=sys.argv[1]
    main(id)
    
