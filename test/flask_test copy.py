
from bokeh.models import Range1d
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.resources import INLINE
from flask import Flask, render_template, request,send_from_directory
import csv
import os
import pandas as pd
import make_yotei
from datetime import datetime
import CT_bunseki
import math
import glob

app = Flask(__name__)
path=os.path.dirname(os.path.abspath(__file__))
Process_graph_height=0
Process_graph_width=0
CT_graph_height=0
CT_graph_width=0
CT_graph_scalemax=0

#初期値の設定画面
@app.route('/ini_time', methods = ["GET", "POST"])
def ini():
   #設定更新時に 更新情報をini.csvに登録
   if request.method == 'POST':
      with open(path+'/ini_time.csv','w',newline="", encoding="utf_8_sig") as f:
         writer = csv.writer(f)
         writer.writerow(['項目','値1','値2'])
         writer.writerow(['標準CT',request.form.get('H_CT')])
         writer.writerow(['閾値CT',request.form.get('S_CT')])
         writer.writerow(['就業時間',request.form.get('worktime_start'),request.form.get('worktime_end')])
         for i in range(9):
            writer.writerow(['休憩時間'+str(i+1),request.form.get('kyukeiS_'+str(i+1)),request.form.get('kyukeiE_'+str(i+1))])
      make_yotei.yotei()
      now=datetime.now()
      log_name='{:%Y-%m-%d}_{}.csv'.format(now,2)
      CT_bunseki.syoki(log_name)
   
   #設定画面表示
   df = pd.read_csv(path+'/ini_time.csv', header=0, index_col=0)
   print (df)
   print (df.iloc[3:10,:])
   html = render_template(
      'ini_time.html',
      H_CT=df.loc['標準CT','値1'],
      S_CT=df.loc['閾値CT','値1'],
      worktime_start=df.loc['就業時間','値1'],
      worktime_end=df.loc['就業時間','値2'],
      kyukei=df.iloc[3:10,:].values.tolist()
   )
   return (html)

#初期値の設定画面
@app.route('/ini_graph', methods = ["GET", "POST"])
def ini_graph():
   #設定更新時に 更新情報をini.csvに登録
   if request.method == 'POST':
      with open(path+'/ini_graph.csv','w',newline="", encoding="utf_8_sig") as f:
         writer = csv.writer(f)
         global Process_graph_height,Process_graph_width,CT_graph_height,CT_graph_width,CT_graph_scalemax
         Process_graph_height=int(float(request.form.get('process_graph_height')))
         Process_graph_width=int(float(request.form.get('process_graph_width')))
         CT_graph_height=int(float(request.form.get('CT_graph_height')))
         CT_graph_width=int(float(request.form.get('CT_graph_width')))
         CT_graph_scalemax=int(float(request.form.get('CT_graph_scalemax')))
         writer.writerow(['項目','値1','値2'])
         writer.writerow(['進捗グラフ大きさ',Process_graph_height,Process_graph_width])
         writer.writerow(['CTグラフ大きさ',CT_graph_height,CT_graph_width])
         writer.writerow(['CTグラフ最大値',CT_graph_scalemax])
   
   #設定画面表示
   df = pd.read_csv(path+'/ini_graph.csv', header=0, index_col=0)
   html = render_template(
      'ini_graph.html',
      process_graph_height=df.loc['進捗グラフ大きさ','値1'],
      process_graph_width=df.loc['進捗グラフ大きさ','値2'],
      CT_graph_height=df.loc['CTグラフ大きさ','値1'],
      CT_graph_width=df.loc['CTグラフ大きさ','値2'],
      CT_graph_scalemax=df.loc['CTグラフ最大値','値1'],
   )
   return (html)

   
#進捗グラフ表示
@app.route('/process_graph')
def bokeh():
   
   p=process_graph()

   # grab the static resources
   js_resources = INLINE.render_js()
   css_resources = INLINE.render_css()

   # render template
   script, div = components(p)
   html = render_template(
      'process_graph.html',
      title='進捗グラフ',
      plot_script=script,
      plot_div=div,
      js_resources=js_resources,
      css_resources=css_resources,
   )
   return (html)




#サイクルタイムグラフ表示
@app.route('/CT_graph')
def bokeh2():

   p=CT_graph()

   # grab the static resources
   js_resources = INLINE.render_js()
   css_resources = INLINE.render_css()

   # render template
   script, div = components(p)
   html = render_template(
      'CT_graph.html',
      title='サイクルタイムグラフ',
      plot_script=script,
      plot_div=div,
      js_resources=js_resources,
      css_resources=css_resources,
   )
   return (html)
   
#進捗・サイクルタイムグラフ表示
@app.route('/process_CT_graph')
def prcess_CT_graph():
   p_process=process_graph()
   p_CT=CT_graph()

   # grab the static resources
   js_resources = INLINE.render_js()
   css_resources = INLINE.render_css()

   # render template
   script_process, div_process = components(p_process)
   script_CT, div_CT = components(p_CT)
   html = render_template(
      'process_CT_graph.html',
      title_process='進捗グラフ',
      title_CT='サイクルタイムグラフ',
      plot_script_process=script_process,
      plot_div_process=div_process,
      plot_script_CT=script_CT,
      plot_div_CT=div_CT,
      js_resources=js_resources,
      css_resources=css_resources,
   )
   return (html)


#センサー情報を取得し、logに保存する
#id：センサーが複数の時に識別する用　　現状はその機能はなし
@app.route('/sensore', methods = ["GET", "POST"])
def sensore():
   if request.method == 'POST':
      id = request.form.get("id")
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
   
   html = render_template(
      'sensore.html',
   )
   return (html)

#eps32からのgetを受け取る
@app.route('/esp32', methods = ["GET"])
def sensore_esp32():
   if request.method == 'GET':
      id=2
      now=datetime.now()
      log_name='{:%Y-%m-%d}_{}.csv'.format(now,id)
      if os.path.exists(path+'/log/'+log_name):
         with open(path+'/log/'+log_name, 'a',newline="", encoding="utf_8_sig") as f:
            writer = csv.writer(f)
            writer.writerow([id,now,1])
      else:
         with open(path+'/log/'+log_name, 'w',newline="", encoding="utf_8_sig") as f:
            writer = csv.writer(f)
            writer.writerow(['id','time','X'])
            writer.writerow([id,now,1])
         with open(path+'/bunseki/CT_'+log_name, 'w',newline="", encoding="utf_8_sig") as f1:
            fieldnames = ['id', '開始','終了','CT','就業時間判定','休憩時間判定','実績数']
            writer = csv.DictWriter(f1, fieldnames=fieldnames)
            writer.wri5teheader()
      CT_bunseki.add(log_name)
   
   html = render_template(
      'sensore.html',
   )
   return (html)

#サイトマップ
@app.route('/sitemap')
def sitemape():   
   html = render_template(
      'sitemap.html')
   return (html)


#進捗グラフ作成
def process_graph():
   path=os.path.dirname(os.path.abspath(__file__))
   #予定進捗グラフ作成
   df = pd.read_csv(path+'/yotei/yotei.csv')
   # datetime に変換する
   df["time"] = pd.to_datetime(df["time"])
   # time を index として設定する 
   df.index = df["time"]
   p = figure(plot_width=Process_graph_width, plot_height=Process_graph_height, x_axis_type="datetime") 
   # add a line renderer
   p.line(df.index,df["num"], line_width=3,legend='num', color="green")

   #実績進捗グラフ作成
   now=datetime.now()
   log_name='{:%Y-%m-%d}_{}.csv'.format(now,2)
   path2=path+'/bunseki/CT_'+log_name
   if os.path.exists(path+'/bunseki/renew_CT_'+log_name):
      df2 = pd.read_csv(path2)
      # datetime に変換する
      df2["開始"] = pd.to_datetime(df2["開始"])
      # ga:date を index として設定する 
      df2.index = df2["開始"]
      p.line(df2.index,df2["実績数"], line_width=3,legend='実績数', color="blue")
   return p

#ダウンロード
@app.route('/download', methods = ["GET", "POST"])
def download():
   target_path_2 = os.path.join(os.path.dirname(__file__), './bunseki')
   target_path_2=os.path.normpath(target_path_2)

   if request.method == 'POST':
      filename=request.form.get("filename")
      print (filename)
      buf=target_path_2
      return send_from_directory(target_path_2, filename, \
        as_attachment = True, attachment_filename = filename)

   files=glob.glob(target_path_2 + "/*")

   filenames=[]
   for file in files:
      filename=os.path.split(file)[1]
      if filename.startswith("C"):    
         filenames.append(os.path.split(file)[1])
   filenames.sort()
   print (filenames)

   html = render_template(
      'download.html',
      kyukei=filenames
   )
   return (html)

#サイクルタイムグラフ作成
def CT_graph():
   #実績サイクルグラフ作成
   path=os.path.dirname(os.path.abspath(__file__))
#   p = figure(plot_width=1200, plot_height=300, x_axis_type="datetime") 
   now=datetime.now()
   log_name='{:%Y-%m-%d}_{}.csv'.format(now,2)
   path2=path+'/bunseki/renew_CT_'+log_name
   if os.path.exists(path+'/bunseki/renew_CT_'+log_name):
      df2 = pd.read_csv(path2)
      df2=(df2[(df2['就業時間判定'] =='就業') & (df2['休憩時間判定'] =='休憩外')])
      
      #y軸の範囲を設定
      yrange = Range1d(0,CT_graph_scalemax)
      #実績CTのグラフを作成
      x=df2["開始"].str.split(' ', expand=True)[1].str[:10].astype(str)
      p = figure(x_range=x,plot_width=CT_graph_width, plot_height=CT_graph_height,y_range = yrange) 
      
      #実績CTのグラフを作成
      p.vbar(x=x,top=df2["CT"],legend='CT', color="green")

      #閾値グラフ作成
      df = pd.read_csv(path+'/ini_time.csv', header=0, index_col=0)
      H_CT=int(df.at['閾値CT','値1'])
      p.line(x=x, y=H_CT,color="red")
      

      # x軸を縦書きにする
      p.xaxis.major_label_orientation = "vertical"
   return p

if __name__ == "__main__":
   df = pd.read_csv(path+'/ini_graph.csv', header=0, index_col=0)
   Process_graph_height=int(df.at['進捗グラフ大きさ','値1'])
   Process_graph_width=int(df.at['進捗グラフ大きさ','値2'])
   CT_graph_height=int(df.at['CTグラフ大きさ','値1'])
   CT_graph_width=int(df.at['CTグラフ大きさ','値2'])
   CT_graph_scalemax=int(df.at['CTグラフ最大値','値1'])

   make_yotei.yotei()
   
   app.run(host='0.0.0.0', port=8080, debug=True)