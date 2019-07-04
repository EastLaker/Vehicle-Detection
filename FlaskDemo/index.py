# encoding:utf-8
# !/usr/bin/env python
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request, make_response, send_from_directory, abort, url_for, redirect
import time
import os
#from strUtil import Pic_str
from vehicleClassify import vehicleClassify
import base64
import urllib.parse
import urllib.request
import json
from flask_cors import CORS
from vehicle_license_plate import Vehicle_License_Plate
from VehicleDC import Car_DC


app = Flask(__name__)   # 路由匹配
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF', 'JPEG'])
CORS(app, resources=r'/*')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload')
def upload_test():
    return render_template('up.html')


@app.route('/Login')
def login():
    render_template('index.html')


@app.route('/userlogin',methods=['POST','GET'])
def userLogin():
    uname = request.form.get("uname")
    upsd = request.form.get("upsd")
    print(uname, upsd)
    return render_template('index.html')


# 上传文件
@app.route('/up_photo', methods=['POST','GET'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, 'static/vehicle')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['photo']
    if f and allowed_file(f.filename):
        fname = secure_filename(f.filename)
        print(fname)
        ext = fname.rsplit('.', 1)[1]
        # new_filename = Pic_str().create_uuid() + '.' + ext
        # new_filename = 'test.' + ext
        new_filename = 'test.jpg'
        f.save(os.path.join(file_dir, new_filename))
        # 本地模型的分类
        detector = vehicleClassify()
        carModel = detector.detect()
        # 向百度发送请求
        request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/car"
        # 二进制方式打开图片文件
        file_path = os.path.join(file_dir, new_filename)
        f = open(file_path, 'rb')
        img = base64.b64encode(f.read())
        params = {"image": img, "top_num": 5}
        params = urllib.parse.urlencode(params).encode(encoding='UTF8')
        access_token = "24.a68791b5a1673ff5e06335c409e34185.2592000.1564026900.282335-16630389"
        request_url = request_url + "?access_token=" + access_token
        request1 = urllib.request.Request(url=request_url, data=params)
        request1.add_header('Content-Type', 'application/x-www-form-urlencoded')
        print(request1)
        response = urllib.request.urlopen(request1)
        content = response.read()
        if content:
            res = json.loads(content, encoding='UTF8')
            print(res["result"][0])
        return json.dumps({"success": 0, "msg": "upload success", 'car info': res["result"][0], '车的种类:': carModel}, ensure_ascii=False)
    else:
        return json.dumps({"fail": 0, "msg": "upload fail"}, ensure_ascii=False)


# 车牌识别
@app.route('/up_license', methods=['POST', 'GET'], strict_slashes=False)
def api_license():
    file_dir = os.path.join(basedir, 'license_plate_recognition')  # 图像存储路径为license_plate_recognition文件夹中
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['photo']
    if f and allowed_file(f.filename):
        fname = secure_filename(f.filename)
        print(fname)
        ext = fname.rsplit('.', 1)[1]
        # new_filename = Pic_str().create_uuid() + '.' + ext
        new_filename = 'license.' + ext
        f.save(os.path.join(file_dir, new_filename))
        # TODO 识别车牌
        licensedetector = Vehicle_License_Plate(os.path.join(file_dir, new_filename))
        # print(licensedetector.vehicle_license_plate)
        return json.dumps({"success": 0, "msg": "upload success", "car_license:": licensedetector.vehicle_license_plate}, ensure_ascii=False)
    else:
        return json.dumps({"fail": 0, "msg": "upload fail"}, ensure_ascii=False)


@app.route('/up_vehicle', methods=['POST', 'GET'], strict_slashes=False)
def api_vehicle():
    file_dir = os.path.join(basedir, 'static/vehicle')  # 图像存储路径为license_plate_recognition文件夹中
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['photo']
    if f and allowed_file(f.filename):
        fname = secure_filename(f.filename)
        print(fname)
        ext = fname.rsplit('.', 1)[1]
        # new_filename = Pic_str().create_uuid() + '.' + ext
        new_filename = 'test.jpg'
        f.save(os.path.join(file_dir, new_filename))
        # TODO 检测图中的车辆
        DR_model = Car_DC(src_dir="static/vehicle/", dst_dir="vehicleResults/")
        DR_model.detect_classify()
        return json.dumps({"success": 0, "msg": "upload success"}, ensure_ascii=False)
    else:
        return json.dumps({"fail": 0, "msg": "upload fail"}, ensure_ascii=False)


@app.route('/download/<string:filename>', methods=['GET'])
def download(filename):
    if request.method == "GET":
        if os.path.isfile(os.path.join('upload', filename)):
            return send_from_directory('upload', filename, as_attachment=True)
        pass


# show photo
@app.route('/show/<string:filename>', methods=['GET'])
def show_photo(filename):
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            image_data = open(os.path.join(file_dir, '%s' % filename), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response
    else:
        pass


@app.route('/')
def index():
    # user_agent = request.headers.get('User-Agent')
    # print(user_agent)
    return render_template('index.html')


if __name__=='__main__':
    app.run(debug=True,host='0.0.0.0')