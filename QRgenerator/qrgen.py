import qrcode
import uuid


def genQRcode():
    string = str(uuid.uuid4())
    image = qrcode.make(string, box_size=1, border=1)
    image.save("../QRcode/QRcode.png", "PNG")
    return image


if __name__ == "__main__":
    genQRcode()
