from flask import Flask, request, make_response, redirect, jsonify
from flask_cors import CORS, cross_origin
import flicker
from random import randint
app = Flask(__name__, static_url_path='/static')
#CORS(app, resources={r"/*": {"origins": "http://arwes.pogo-muenchen.de/*"}})
CORS(app, resources={r"/*": {"origins": "*"}})
security_code = "5fa2b894de9ddfe6cbbcc7696aa175101b707985c08d020e418d693154dbab7a"

def setup_app(app):
    global security_code
    security_code = str(randint(0, 99999)).zfill(5)
    print(security_code)
    mask = flicker.Two_Masks(flicker.Mask.ACCOUNT_NUMBER_OLD, '01337', flicker.Mask.ACCOUNT_NUMBER_IBAN, 'Congratz WP', security_code)
    code = flicker.generate_code(mask)
    #print(code)
    flicker.gif_flicker_custom(code, "static/flicker.gif")

setup_app(app)

def gen_tan():
    global security_code
    security_code = str(randint(0, 99999)).zfill(5)
    print(security_code)
    mask = flicker.Two_Masks(flicker.Mask.ACCOUNT_NUMBER_OLD, '01337', flicker.Mask.ACCOUNT_NUMBER_IBAN, 'Congratz WP', security_code)
    code = flicker.generate_code(mask)
    #print(code)
    flicker.gif_flicker_custom(code, "static/flicker.gif")

@app.route('/check_code', methods=['POST'])
def check_code():
    data = request.get_json()
    if "code" in data and len(data["code"]) > 0:
        if data["code"] == security_code:
            gen_tan()
            return jsonify({"resp":"ALLES{🟩🟧🟨🟥🟦⬛🟫🟪⬜}"})
        else:
            gen_tan()
            return jsonify({"resp":"Wrong security code!"})
    return jsonify({"resp":"No security code entered!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
