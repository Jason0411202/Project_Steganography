import os
import tensorflow as tf

os.environ['TF_CPP_MIN_LOG_LEVEL'] = "3"

from tensorflow import keras  # 從tensor模組中載入高階API keras
import numpy as np
import cv2


# 謝,龍哥函式支援
def preprocess_image(img: np.ndarray, maxHeight: int, maxWidth: int):
    target_size = (maxHeight, maxWidth, img.shape[2])
    padded_img = np.zeros(target_size, dtype=np.uint8)
    padded_img[:min(maxHeight, img.shape[0]), :min(maxWidth, img.shape[1]), :] = img[:min(maxHeight, img.shape[0]), :min(maxWidth, img.shape[1]), :]
    return padded_img


model = keras.models.load_model('../models/LSB_model.h5')

img = cv2.imread("../web_frontend/static/images/userUpload.jpg")
img = img & 1

maxHeight = 96
maxWidth = 96

datas = []
img = preprocess_image(img, maxHeight, maxWidth)
datas.append(img)
datas = np.array(datas, dtype=np.uint8)
datas = datas.reshape(len(datas), maxHeight, maxWidth, 3).astype("float32")
datas = datas / 255.0

predition = model.predict(datas)
print(predition)
print("$" + str(round(predition[0][1] * 100, 5)) + "$")
