import csv
import os
import pandas as pd
from csv import reader
from datetime import datetime
import datetime as dt
import shutil

path=os.path.dirname(os.path.abspath(__file__))

#グラフ表示とログ書き込みによるcsvへの同時アクセスを防ぐため、表示用CSVを複製
def csv_renew(file_name):
    shutil.copy(path+'/bunseki/CT_'+file_name,path+'/bunseki/renew_CT_'+file_name)

#サイクルタイムの信号を処理する
#input:log/Logfile
#output:bunseki/CT_...
def add(file_name):
    list_log=[]
    after_length=0
    with open(path+'/log/'+file_name, 'r',newline="", encoding="utf_8_sig") as csv_file:
        csv_reader = reader(csv_file)
        # Passing the cav_reader object to list() to get a list of lists
        list_log = list(csv_reader)
        after_length = len(list(list_log))
    if len(list_log)<2:
        return
        
    before_length=0
    with open(path+'/bunseki/CT_'+file_name, 'r',newline="", encoding="utf_8_sig") as csv_file:
        csv_reader = reader(csv_file)
        list_log2 = list(csv_reader)
        before_length = len(list(list_log2))
        
    with open(path+'/bunseki/CT_'+file_name, 'a',newline="", encoding="utf_8_sig") as f:
        writer = csv.writer(f)
        print (before_length)
        print (after_length)
        i=before_length
        for i in range(before_length,after_length-1,1):
            id=list_log[i+1][0]
            start=datetime.strptime(list_log[i][1], '%Y-%m-%d %H:%M:%S.%f')
            end=datetime.strptime(list_log[i+1][1], '%Y-%m-%d %H:%M:%S.%f')
            CT=(end-start).total_seconds()
            syugyou=syugyou_hantei(start,end)
            kyukei=kyukei_hantei(start,end)
            writer.writerow([id,start,end,CT,syugyou,kyukei,i])
    csv_renew(file_name)
    return

#サイクルタイムの信号を処理する（iniファイルが書き換えられた時に実行）
#input:log/Logfile
#output:bunseki/CT_...
def syoki(file_name):
    list_log=[]
    with open(path+'/log/'+file_name, 'r',newline="", encoding="utf_8_sig") as csv_file:
        csv_reader = reader(csv_file)
        # Passing the cav_reader object to list() to get a list of lists
        list_log = list(csv_reader)
    if len(list_log)<2:
        return
    with open(path+'/bunseki/CT_'+file_name, 'w',newline="", encoding="utf_8_sig") as f:
        fieldnames = ['id', '開始','終了','CT','就業時間判定','休憩時間判定','実績数']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer = csv.writer(f)
        for i in range(len(list_log)-2):
            id=list_log[i+1][0]
            start=datetime.strptime(list_log[i+1][1], '%Y-%m-%d %H:%M:%S.%f')
            end=datetime.strptime(list_log[i+2][1], '%Y-%m-%d %H:%M:%S.%f')
            CT=(end-start).total_seconds()
            syugyou=syugyou_hantei(start,end)
            kyukei=kyukei_hantei(start,end)
            writer.writerow([id,start,end,CT,syugyou,kyukei,i])
    csv_renew(file_name)
    return

#休憩時間判定
def kyukei_hantei(start,end):
    df = pd.read_csv(path+'/ini_time.csv', header=0, index_col=0)
    kys=[]
    for ky in df.iloc[3:10,:].values.tolist():
        if not(pd.isnull(ky[0])):
            ky1=dt.time( int(ky[0].split(':')[0]),int(ky[0].split(':')[1]))
            ky1=dt.datetime.combine(dt.date.today(), ky1)
            ky2=dt.time( int(ky[1].split(':')[0]),int(ky[1].split(':')[1]))
            ky2=dt.datetime.combine(dt.date.today(), ky2)
            kys.append([ky1,ky2])


    hantei=0
    for ky in kys:
        if not(ky[1]<start or ky[0]>end):
            hantei=1
    if hantei==1:
        return '休憩'
    else:
        return '休憩外'


#就業時間判定
def syugyou_hantei(start,end):
    df = pd.read_csv(path+'/ini_time.csv', header=0, index_col=0)
    x=df.at['就業時間','値1']
    t_start=dt.time( int(x.split(':')[0]),int(x.split(':')[1]))
    t_start=dt.datetime.combine(dt.date.today(), t_start)

    x=df.at['就業時間','値2']
    t_end=dt.time( int(x.split(':')[0]),int(x.split(':')[1]))
    t_end=dt.datetime.combine(dt.date.today(), t_end)

    if t_start<start and t_end>end:
        return '就業'
    else:
        return '時間外'


if __name__ == '__main__':
    add()