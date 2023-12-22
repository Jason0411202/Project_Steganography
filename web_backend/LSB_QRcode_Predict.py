import os
import tensorflow as tf

os.environ['TF_CPP_MIN_LOG_LEVEL'] = "3"

from tensorflow import keras  # 從tensor模組中載入高階API keras
import numpy as np
import cv2

maxHeight = 256
maxWidth = 256


# 謝,龍哥函式支援
def preprocess_image(img):
    target_size = (maxHeight, maxWidth, img.shape[2])
    padded_img = np.zeros(target_size, dtype=np.uint8)
    padded_img[:min(maxHeight,img.shape[0]), :min(maxWidth,img.shape[1]), 0] = img[:min(maxHeight,img.shape[0]), :min(maxWidth,img.shape[1]), 0]
    return padded_img


model = keras.models.load_model('../models/LSB_QR_model.h5')

img = cv2.imread("../web_frontend/static/images/userUpload.png", cv2.IMREAD_COLOR)
# cv2.imshow('qrcode', (img[:, :, 0]&1) * 255)
img[:, :, 0] = (img[:, :, 0]&1) * 255
img = preprocess_image(img)
# cv2.imshow("fuck you", img)
# cv2.waitKey(0)

datas = []

datas.append(img)
datas = np.array(datas, dtype=np.uint8)
datas = datas.reshape(-1, maxHeight, maxWidth, 3).astype("float32")
datas = datas / 255.0

predition = model.predict(datas)
print(predition)
print("$" + str(round(predition[0][1] * 100, 5)) + "$")
