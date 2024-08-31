import pandas as pd
import sqlite3
import datetime
import pandas as pd

con1 = sqlite3.connect('local_db.sqlite')
cur1 = con1.cursor()


def write(cad):
    dt=datetime.datetime.now()
    dtt=dt.strftime("%H%M%S")
    print('\n')
    print('='*80)
    print(dtt,'\t',cad,' ======')
    print('\n')


def show(list):
    dt=datetime.datetime.now()
    dtt=dt.strftime("%H%M%S")
    # print(dtt,*list, sep='\t')
    print(dtt,'\t'.join([str(x) for x in list]))



def toDateTime(date_time):
    format = '%Y-%m-%d %H:%M:%S'
    datetime_str = datetime.datetime.strptime(date_time, format)
    return datetime_str


# ============================================================

write('init')


def cat(m):
    
    d=''
    if(0<=m and m<15):
        d='De 0 a 15'
    
    if(15<=m and m<30):
        d='De 15 a 30'
    
    if(30<=m and m<45):
        d='De 30 a 45'
    
    if(45<=m and m<60):
        d='De 45 a 60'
    
    if(60<=m and m<75):
        d='De 60 a 75'
    
    if(75<=m and m<90):
        d='De 75 a 90'
    
    if(90<=m and m<105):
        d='De 90 a 105'
    
    if(105<=m and m<120):
        d='De 105 a 120'
    
    if(120<=m):
        d='Mas de 2 horas'
        
    return d



def main():
    sql="select FechaArribo from data_balanza where Operacion='Gate In Dry' order by FechaArribo asc"
    df=pd.read_sql(sql,con1)
    df['FechaArribo'] = df['FechaArribo'].astype('datetime64[ns]')
    
    
    df1=pd.DataFrame()
    df2=pd.DataFrame()
    
    df1['FechaArribo1']=df['FechaArribo'].copy()
    df2['FechaArribo2']=df['FechaArribo'].copy()
    
    df2.index-=1
    
    df3=pd.concat([df1, df2], axis=1)
    
    df3['min']=(df3['FechaArribo2']-df3['FechaArribo1'])/pd.Timedelta(minutes=1)
    df3['hrs']=(df3['FechaArribo2']-df3['FechaArribo1'])/pd.Timedelta(hours=1)
    
    df3['cat']=df3['min'].map(cat)
    
    # print(df3)
    # print("")
    # print(df3['min'].max())
    # print("")
    print(df3['cat'].value_counts(sort=True))
    
    # n,m=df.shape
    
    # for i in range(0,n-1):
    #     FechaArribo1=df.loc[i,'FechaArribo']
    #     FechaArribo2=df.loc[i+1,'FechaArribo']
        
    #     minutes_diff = (FechaArribo2 - FechaArribo1).total_seconds() / 60.0
        
    #     show([i, FechaArribo1, FechaArribo2, minutes_diff])


main()

write('end')
