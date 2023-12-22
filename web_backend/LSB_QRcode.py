import cv2
import numpy as np
import os
import random
import qrcode
import uuid

QRcode_size = 31

def genQRcode(id = 0):
    string = str(uuid.uuid4())
    # 35x35 QRcode
    img = qrcode.make(string, box_size=1, border=1)

    img.save('QRcode.png')
    img = cv2.imread('QRcode.png')
    img = cv2.resize(img, (QRcode_size, QRcode_size))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img.astype(np.uint8)
    # cv2.imshow("fuck you", img)
    # cv2.waitKey(0)
    os.remove('QRcode.png')
    return img

def LSBQRcode(target_img_path: str, QRcode: np.ndarray, if_random: bool = False, which_channel: int = 0) -> np.ndarray:
    global select_channel
    img = cv2.imread(target_img_path)
    # cv2.imshow('test',QRcode)

    # get blue channel
    img_b = img[:,:,0]
    # get green channel
    img_g = img[:,:,1]
    # get red channel
    img_r = img[:,:,2]

    # if which_channel == 0:
    #     img[:,:,0] &= 0b11111110
    # elif which_channel == 1:
    #     select_channel = img_g
    # elif which_channel == 2:
    #     select_channel = img_r
    #
    # select_channel &= 0b11111110

    img[:, :, which_channel] &= 0b11111110

    start_point = [0, 0]
    if if_random:
        start_point = [random.randint(0, img.shape[0] - QRcode_size - 1), random.randint(0, img.shape[1] - QRcode_size - 1)]

    for i in range(QRcode.shape[0]):
        for j in range(QRcode.shape[1]):
            if QRcode[i][j] >= 127:
                img[start_point[0] + i][start_point[1] + j][which_channel] +=1
    
    return img

index = 0
qr = genQRcode()
cv2.imwrite('../web_frontend/static/images/userUpload_QRcode.png', qr)

try:
    img = cv2.imread('../web_frontend/static/images/userUpload.png', cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError("無法讀取圖片！")

    if img.shape[0] > QRcode_size and img.shape[1] > QRcode_size:
        QRcode = cv2.imread('../web_frontend/static/images/userUpload_QRcode.png', cv2.IMREAD_GRAYSCALE)
        if QRcode is None:
            raise FileNotFoundError("無法讀取 QR code 圖片！")

        img = LSBQRcode('../web_frontend/static/images/userUpload.png', QRcode, if_random=True, which_channel=0)
        if img is None:
            raise ValueError("處理 LSBQRcode 出錯！")

        print(img.shape)
        cv2.imwrite('../web_frontend/static/images/result.png',img)
        index += 1

except FileNotFoundError as e:
    print(f"錯誤：{e}")

except ValueError as e:
    print(f"錯誤：{e}")

except Exception as e:
    print(f"其他錯誤：{e}")

print("done")
