import serial
from datetime import datetime
import os
import csv
import CT_bunseki

path=os.path.dirname(os.path.abspath(__file__))

def loop():
    while (1):
        ser = serial.Serial("COM5",9600,timeout=None)
        line = ser.readline()
        print(line) 
        sensore()
        ser.close()     

def sensore():
    id=2

    now=datetime.now()
    log_name='{:%Y-%m-%d}_{}.csv'.format(now,id)
    #ログに追記
    if os.path.exists(path+'/log/'+log_name):
        with open(path+'/log/'+log_name, 'a',newline="", encoding="utf_8_sig") as f:
            writer = csv.writer(f)
            writer.writerow([id,now,1])
    #ログファイルを作成（ログファイルがない時）、ついでにCT_...も作成
    else:
        with open(path+'/log/'+log_name, 'w',newline="", encoding="utf_8_sig") as f:
            writer = csv.writer(f)
            writer.writerow(['id','time','X'])
            writer.writerow([id,now,1])
        with open(path+'/bunseki/CT_'+log_name, 'w',newline="", encoding="utf_8_sig") as f1:
            fieldnames = ['id', '開始','終了','CT','就業時間判定','休憩時間判定','実績数']
            writer = csv.DictWriter(f1, fieldnames=fieldnames)
            writer.writeheader()
    #ログ情報を元に、CTや休憩時間判定等行い、CT_...に出力する
    CT_bunseki.add(log_name)

if __name__ == "__main__":
    loop()