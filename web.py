from flask import Flask, request, jsonify, render_template
from PIL import Image
import base64
import io
import requests
# from ocr.ocr import ppocr
from ocr.dddd import ddocr
import numpy as np
import cv2

# precdictor=ppocr()

app = Flask(__name__)

oc=ddocr()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


def log_file(text):
    with open('log.txt', mode='a', encoding='utf-8') as f:
        f.write(text)

#  convert a bytes buffer object returned by io.BytesIO() into a cv image
def bytes_to_cv_image(bytes_buffer):
    bytes_as_np_array = np.frombuffer(bytes_buffer.getvalue(), dtype=np.uint8)
    return cv2.imdecode(bytes_as_np_array, flags=1)

# def text_ocr(img):
#     image = bytes_to_cv_image(img)
#     info= precdictor.ocr(image,zoomin=True) 
#     result={"TextBlocks":[]} 
#     for textblocks in info: 
#         textBlock={"Points":[],"Text":""} 
#         for tk in textblocks[0]: 
#               point={"x":str(tk[0]),"y":str(tk[1])} 
#               textBlock["Points"].append(point)  
#         textBlock["Text"]=textblocks[1][0] 
#         print(textblocks[1][0] )
#         result["TextBlocks"].append(textBlock) 
#     print(result) 
#     return jsonify(result) 


@app.route('/image-big', methods=['POST'])
def image_big():
    if 'image' in request.files:
        image = request.files['image']
        image = oc.convert_to_bytes(image)
        # width, height = get_image_size(image)
    elif 'image_base64' in request.form:
        image_base64 = request.form['image_base64']
        # log_file(image_base64)
        image_data = base64.b64decode(image_base64)

        image = oc.convert_to_bytes(image_data)
        # image = io.BytesIO(image_data)

        # width, height = get_image_size(image)
    elif 'image_url' in request.form:
        image_url = request.form['image_url']
        image = oc.convert_to_bytes(image_url)
        # image = io.BytesIO(image_data)

        # width, height = get_image_size(image)
    else:
        return jsonify({'error': 'No image provided.'}), 400
    
    res=oc.OCR(image)
    return jsonify(res)


@app.route('/image-small', methods=['POST'])
def image_small():
    if 'image' in request.files:
        image = request.files['image']

        # width, height = get_image_size(image)
    elif 'image_base64' in request.form:
        image_base64 = request.form['image_base64']
        # log_file(image_base64)
        image_data = base64.b64decode(image_base64)
        image = io.BytesIO(image_data)

        # width, height = get_image_size(image)
    elif 'image_url' in request.form:
        image_url = request.form['image_url']
        response = requests.get(image_url)
        image_data = response.content
        image = io.BytesIO(image_data)

        # width, height = get_image_size(image)
    else:
        return jsonify({'error': 'No image provided.'}), 400
    
    res=oc.small_ocr(image)
    return jsonify(res)


if __name__ == '__main__':
    app.run(debug=True)