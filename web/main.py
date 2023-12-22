from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import keras
from keras.models import load_model
import tensorflow #載入tensor模組
from tensorflow import keras #從tensor模組中載入高階API keras
from keras import layers #從tensoe的keras高階API中載入layers用於建立模型
from matplotlib import pyplot as plt #載入matplotlib用來繪圖
import pandas as pd

upload_folder = '/upload'
dir_path = os.path.dirname(os.path.abspath(__file__))
allowed_extensions = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def convertStringToBinaryCode(message, IMG_WIDTH=512, IMG_HEIGHT=512):
    ans=[]
    for word in message:
        str=format(ord(word),'08b')
        for binary in str:
            ans.append(int(binary))

    if len(ans)>IMG_WIDTH*IMG_HEIGHT*3:
        print('Message is too long')
        return None
    
    while len(ans)<IMG_WIDTH*IMG_HEIGHT*3:
        ans.append(0)

    return ans

def LSB_encode(filename):
    img = cv2.imread(dir_path + app.config['UPLOAD_FOLDER'] + '/' + filename)
    writtenData = convertStringToBinaryCode(filename, img.shape[1], img.shape[0])
    img_written = img.copy()
    index = 0

    for k in range(0,3):
        for i in range(0, img.shape[0]):
            for j in range(0, img.shape[1]):
                if writtenData[index] == 1:
                    img_written[i,j,k] = img_written[i,j,k] | 1
                else:
                    img_written[i,j,k] = img_written[i,j,k] & ~1
                index+=1
    # write image
    cv2.imwrite(dir_path + '/result/result.png', img_written, [cv2.IMWRITE_PNG_COMPRESSION, 1])


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(dir_path + app.config['UPLOAD_FOLDER'], filename))
            LSB_encode(filename)
            return redirect(url_for('result', filename=filename))
    else:
        return render_template('index.html')

# detect 是壞的，因為 model 大小為 24x24x3，所以只能辨識 24x24 的圖片，但是我們的圖片是 512x512 的，所以會出錯
@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(dir_path + app.config['UPLOAD_FOLDER'], filename))
            model = keras.models.load_model(dir_path + '/model/LSB_model.h5')
            # guess if the image is stego or not

            img = cv2.imread(dir_path + app.config['UPLOAD_FOLDER'] + '/' + filename)
            img = cv2.resize(img, (24, 24)) # resize to 24x24
            img = img.reshape((1,) + img.shape) # reshape to (1, 24, 24, 3)
            # only store the last bit of each pixel
            img = img & 1
            # predict
            pred = model.predict(img)
            print(pred)
            return render_template('detect_result.html', filename="/getImg?folder=upload&filename=" + filename, pred=("該圖片未被隱寫" if pred[0][0] > 0.5 else "該圖片已被隱寫"))

    else:
        return render_template('detect.html')
    
@app.route('/detect_result', methods=['GET'])
def detect_result():
    return render_template('detect_result.html')

@app.route('/result', methods=['GET'])
def result():
    return render_template('result.html',
        origin_filename = "/getImg?folder=upload&filename=" + request.args.get('filename'),
        filename = "/getImg?folder=result&filename=result.png")

@app.route('/getImg', methods=['GET'])
def getImg():
    return send_from_directory(dir_path + '/' + request.args.get('folder'), request.args.get('filename'))

@app.route('/download', methods=['POST'])
def download():
    return send_from_directory(dir_path + '/result', 'result.png', as_attachment=True)

if __name__ == '__main__':
    app.run()