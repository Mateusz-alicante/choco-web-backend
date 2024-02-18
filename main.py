from multiprocessing import Process
import numpy as np
import cv2
import requests
import serial
from flask import Flask, request, Response, send_file
from flask_cors import CORS, cross_origin
from multiprocessing import Process

BLUETOOTH = False
WebServer = False


def FlaskAppSetup():
    app = Flask(__name__)

    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    @app.route('/api/test', methods=['GET'])
    @cross_origin()
    def test():
        response = "Hello World!"
        return Response(response=response, status=200, mimetype="application/json")

    @app.route('/api/get_image', methods=['GET'])
    @cross_origin()
    def get_image():
        filename = 'frame.jpg'
        return send_file(filename, mimetype='image/gif')

    app.run(host="0.0.0.0", port=4000)


if __name__ == '__main__' and WebServer:
    p = Process(target=FlaskAppSetup)
    p.start()

'''
INFO SECTION
- if you want to monitor raw parameters of ESP32CAM, open the browser and go to http://192.168.x.x/status
- command can be sent through an HTTP get composed in the following way http://192.168.x.x/control?var=VARIABLE_NAME&val=VALUE (check varname and value in status)
'''

# Change your port name COM... and your baudrate
if (BLUETOOTH):
    ser = serial.Serial("COM9", 9600, timeout=1)


# ESP32 URL
URL = "http://172.20.10.12"
AWB = True

# Face recognition and opencv setup
cap = cv2.VideoCapture(URL + ":81/stream")
# insert the full path to haarcascade file if you encounter any problem
face_classifier = cv2.CascadeClassifier(
    'haarcascade_frontalface_alt.xml')


def set_resolution(url: str, index: int = 1, verbose: bool = False):
    try:
        if verbose:
            resolutions = "10: UXGA(1600x1200)\n9: SXGA(1280x1024)\n8: XGA(1024x768)\n7: SVGA(800x600)\n6: VGA(640x480)\n5: CIF(400x296)\n4: QVGA(320x240)\n3: HQVGA(240x176)\n0: QQVGA(160x120)"
            print("available resolutions\n{}".format(resolutions))

        if index in [10, 9, 8, 7, 6, 5, 4, 3, 0]:
            requests.get(url + "/control?var=framesize&val={}".format(index))
        else:
            print("Wrong index")
    except:
        print("SET_RESOLUTION: something went wrong")


def set_quality(url: str, value: int = 1, verbose: bool = False):
    try:
        if value >= 10 and value <= 63:
            requests.get(url + "/control?var=quality&val={}".format(value))
    except:
        print("SET_QUALITY: something went wrong")


def set_awb(url: str, awb: int = 1):
    try:
        awb = not awb
        requests.get(url + "/control?var=awb&val={}".format(1 if awb else 0))
    except:
        print("SET_QUALITY: something went wrong")
    return awb


if __name__ == '__main__':
    set_resolution(URL, index=8)

    while True:
        if cap.isOpened():
            ret, frame = cap.read()

            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)

                faces = face_classifier.detectMultiScale(gray)
                for (x, y, w, h) in faces:
                    center = (x + w//2, y + h//2)
                    frame = cv2.rectangle(
                        frame, (x, y), (x + w, y + h), (255, 255, 0), 4)
                    dist = (x + w//2, y + h//2)
                    print(dist)

                    if (BLUETOOTH):
                        ser.write(b'L')
                        ser.write(bytes(str(h), 'utf-8'))
                        ser.write(b'X')
                        ser.write(bytes(str(dist[0]), 'utf-8'))
                        ser.write(b'Y')
                        ser.write(bytes(str(dist[1]), 'utf-8'))

            cv2.imshow("frame", frame)
            cv2.imwrite("frame.jpg", frame)

            key = cv2.waitKey(1)

            if key == ord('r'):
                idx = int(input("Select resolution index: "))
                set_resolution(URL, index=idx, verbose=True)

            elif key == ord('q'):
                val = int(input("Set quality (10 - 63): "))
                set_quality(URL, value=val)

            elif key == ord('a'):
                AWB = set_awb(URL, AWB)

            elif key == 27:
                break

    cv2.destroyAllWindows()
    cap.release()
