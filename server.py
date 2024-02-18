from flask import Flask, request, Response, send_file
from flask_cors import CORS, cross_origin

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
