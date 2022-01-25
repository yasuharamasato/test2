import csv
import datetime
import os
import pandas as pd

#生産進捗グラフの予定線のcsvを作成する
#input:ini.csv
#output:yotei.csv
def yotei():
    path=os.path.dirname(os.path.abspath(__file__))

    df = pd.read_csv(path+'/ini_time.csv', header=0, index_col=0)

    with open(path+'/yotei/yotei.csv', 'w',newline="", encoding="utf_8_sig") as csv_file:
        fieldnames = ['time', 'num']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        x=df.at['就業時間','値1']
        t=datetime.time( int(x.split(':')[0]),int(x.split(':')[1]))
        t=datetime.datetime.combine(datetime.date.today(), t)

        x=df.at['就業時間','値2']
        t_end=datetime.time( int(x.split(':')[0]),int(x.split(':')[1]))
        t_end=datetime.datetime.combine(datetime.date.today(), t_end)

        x=df.at['標準CT','値1']
        H_CT=int(x)

        kys=[]
        for ky in df.iloc[3:10,:].values.tolist():
            if not(pd.isnull(ky[0])):
                ky1=datetime.time( int(ky[0].split(':')[0]),int(ky[0].split(':')[1]))
                ky1=datetime.datetime.combine(datetime.date.today(), ky1)
                ky2=datetime.time( int(ky[1].split(':')[0]),int(ky[1].split(':')[1]))
                ky2=datetime.datetime.combine(datetime.date.today(), ky2)
                kys.append([ky1,ky2])
        print (kys)

        loop=0
        while t<t_end:
            for ky in kys:
                if t>ky[0] and t<ky[1]:
                    t=ky[1]
                    writer.writerow({'time': t, 'num': loop})

            writer.writerow({'time': t, 'num': loop})
            t = t + datetime.timedelta(seconds=H_CT)
            loop=loop+1
    return

if __name__ == '__main__':
    yotei()