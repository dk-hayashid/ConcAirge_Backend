from flask import Flask
from flask import request, make_response, jsonify, send_file
from flask_cors import CORS
import base64

from pmv import calc_comf_temp_p
from map import save_temperature_map
from sensor import return_measured_data

app = Flask(__name__)
CORS(app)


@app.route("/post", methods=['POST'])
def parse():

    user = request.get_json()
    user = user['post_text']
    age = int(user['age'])
    height = float(user['height'])
    weight = float(user['weight'])
    sex = user['sex']

    comf_temp, _, _ = calc_comf_temp_p(
        50, age, sex, height, weight)
    
    comf_temp = round(comf_temp, 1)
    data = return_measured_data()

    # TODO: 1月28日15時40分ぐらいの一番理想的なヒートマップを利用 
    save_temperature_map(data, comf_temp)
    with open('./map.png', "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')

    return {"ComfortTemperature": comf_temp, "Map": img_base64}


if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True)
