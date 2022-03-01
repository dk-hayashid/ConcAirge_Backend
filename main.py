from flask import Flask
from flask import request, make_response, jsonify, send_file
from flask_cors import CORS
import base64

from numpy import TooHardError

from pmv import calc_comf_temp_p
from map import save_temperature_map
from sensor import return_measured_data
from form import return_age

import pandas as pd
import requests

app = Flask(__name__)
CORS(app)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

#グローバル変数の宣言
age=20
height=170.0
weight=60.0
sex=None
comf_temp=25
email="jiro.ueda@docomo.co.jp"





@app.route("/postfeed", methods=['POST'])
def parsefeed():
    #global変数の取得
    global comf_temp,email
    
    #POST内容の読み込み
    feed = request.get_json()
    feed = feed['post_text']
    email=feed['email']
    comf_temp=feed['comtem']
    feedback=feed['feedback']


    #ゲストユーザーでないなら、フィードバック情報をDBにポスト
    if email:
        id=1
        post_data={
            "users" :[{
                "email":email,
                "comtem":comf_temp,
                "feedback":feedback
            }]
            
        }
        res=requests.post("http://ec2-35-77-188-73.ap-northeast-1.compute.amazonaws.com/"+"user?id={}".format(id),json=post_data)

                
    return {"ComfortTemperature": comf_temp,"feedback":feedback}
    
"""
# データの受け渡し方法

 - POST

     - 日付(2021/02/21 10:10:33, datetime)

     - 個別情報 (メアド) (daisaku.hayashi@daiki.co.jp, string)

     - その時の快適温度 (22.34, float)

     - フィードバック (３段階) (1,0,-1, int)


#要望聞き取り回数が0じゃないなら快適温度を修正
    if(count>0):
        if (feed==1):
            if(before==1):
                count=count+1
            comf_temp=comf_temp-0.1*count
            before=1
            count=count-1
        elif(feed==-1):
            if(before==-1):
                count=count+1
            comf_temp=comf_temp+0.1*count
            before=-1
            count=count-1
        else:
            count=0
"""  


@app.route("/post", methods=['POST'])
def parse():

    global age,height,weight,sex,comf_temp,email
    user = request.get_json()
    user = user['post_text']
    age = return_age(user['birthday'])
    print(age)
    height = float(user['height'])
    weight = float(user['weight'])
    sex = user['sex']
    clo = float(user['fashion'])
    email= user['email']

    comf_temp, _, _ = calc_comf_temp_p(
        50, age, sex, height, weight, clo)

    #ゲストユーザーでないなら、DBの情報を元に快適温度を補正
    if email:
        #ユーザーデータDBからのデータ読み取り
        res=requests.get("http://ec2-35-77-188-73.ap-northeast-1.compute.amazonaws.com/user?email="+email)
        if res.status_code==200:
            userdata=res.json()['users']
            userdata_df=pd.DataFrame(userdata)

            #過去のフィードバック結果の合計値
            feed_history=userdata_df["feedback"].sum()
            comf_temp=comf_temp-0.1*feed_history

    
    comf_temp = round(comf_temp, 1)
    data = return_measured_data()

    # TODO: 1月28日15時40分ぐらいの一番理想的なヒートマップを利用 
    save_temperature_map(data, comf_temp)
    with open('./map.png', "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')

    return {"ComfortTemperature": comf_temp, "Map": img_base64}


if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
