from flask import Flask
from flask import request, make_response, jsonify, send_file
from flask_cors import CORS
import base64

from pmv import calc_comf_temp_p
from map import save_temperature_map
from sensor import return_measured_data

app = Flask(__name__)
CORS(app)

#グローバル変数の宣言
age=20
height=170.0
weight=60.0
sex=None
count=3 #何回まで要望を聞くか
before=None #直前のフィードバックがHotだったのかColdだったのか
comf_temp=25

@app.route("/postfeed", methods=['POST'])
def parsefeed():
    #global変数の取得
    global age,height,weight,sex,count,before,comf_temp
    
    #POST内容の読み込み
    feed = request.get_json()
    feed = feed['post_text']

    #要望聞き取り回数が0じゃないなら快適温度を修正
    if(count>0):
        if (feed=="Hot"):
            if(before=="Hot"):
                count=count+1
            comf_temp=comf_temp-0.1*count
            before="Hot"
            count=count-1
        elif(feed=="Cold"):
            if(before=="Cold"):
                count=count+1
            comf_temp=comf_temp+0.1*count
            before="Cold"
            count=count-1
        else:
            count=0
            
    return {"ComfortTemperature": comf_temp,"Number of requests allowed":count}
    


@app.route("/post", methods=['POST'])
def parse():

    global age,height,weight,sex,comf_temp
    user = request.get_json()
    user = user['post_text']
    age = int(user['age'])
    height = float(user['height'])
    weight = float(user['weight'])
    sex = user['sex']

    # TODO: 湿度をリアルタイムで受け取る(現在50%固定)
    comf_temp, _, _ = calc_comf_temp_p(
        50, age, sex, height, weight)
    
    comf_temp = round(comf_temp, 1)
    data = return_measured_data()
    save_temperature_map(data, comf_temp)
    with open('./map.png', "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')

    return {"ComfortTemperature": comf_temp, "Map": img_base64}


if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
