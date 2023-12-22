import math
import random
import numpy as np
import cv2
import os
from matplotlib import pyplot as plt
import sys

def showRGBImg(img):
    imgShow = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.figure(num='fg1',figsize=(6,6))
    plt.imshow(imgShow)
    plt.show()

def convertStringToBinaryCode(message:str,img_height:int,img_width:int):
    ans=[]
    for word in message:
        str=format(ord(word),'08b')
        for binary in str:
            ans.append(int(binary))

    if len(ans)>img_width*img_height*3:
        print('Message is too long')
        return None
    
    random.seed(None)
    while len(ans)<img_width*img_height*3:
        ans.append(int(math.floor(random.random()*2)))
        # print(int(math.floor(random.random()*2)))
    return ans

def LSB_encode(img:np.ndarray, message:str):
    img_height=img.shape[0]
    img_width =img.shape[1]
    
    img_written=img.copy()

    writtenData=convertStringToBinaryCode(message,img_height,img_width)
    
    index=0
    for k in range(0,3):
        for i in range(img_height):
            for j in range(img_width):
                if writtenData[index]==1:
                    img_written[i,j,k]=img_written[i,j,k] | 1
                else:
                    img_written[i,j,k]=img_written[i,j,k] & ~1
                index+=1

    return img_written

img = cv2.imread('../web_frontend/static/images/userUpload.jpg', cv2.IMREAD_COLOR)
IMG_WIDTH = img.shape[1]
IMG_HEIGHT = img.shape[0]

# 在主程式中處理使用者輸入
if len(sys.argv) < 2:
    print("錯誤：請提供要隱藏的訊息")
    sys.exit(1)

written_msg = sys.argv[1]  # 取得傳入的參數 (欲隱藏的文字)
encoded_img = LSB_encode(img, written_msg)

if encoded_img is None:
    print("錯誤：無法產生隱藏訊息的圖片")
    sys.exit(1)

cv2.imwrite('../web_frontend/static/images/result.jpg', encoded_img, [cv2.IMWRITE_PNG_COMPRESSION, 1])

print("done normally", end="")
