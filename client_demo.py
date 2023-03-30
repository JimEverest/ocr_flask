import requests
import base64
import io
from PIL import Image
import os

# API_ENDPOINT = 'http://localhost:5000/image-big'

# API_ENDPOINT = 'http://120.48.71.76/image-big'
API_ENDPOINT = 'http://120.48.71.76/image-small'

def send_base64_encoded_image(image_path):
    with open(image_path, 'rb') as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        response = requests.post(API_ENDPOINT, data={'image_base64': img_base64})
        print(response.json())

def send_image_as_file(image_path):
    with open(image_path, 'rb') as img_file:
        files = {'image': img_file}
        response = requests.post(API_ENDPOINT, files=files)
        print(response.json())

def send_image_url(image_url):
    response = requests.post(API_ENDPOINT, data={'image_url': image_url})
    print(response.json())

# Modify this to the path of your image or image URL
image_path = 'test/capcha2.png'
image_url = 'https://pic1.zhimg.com/v2-2788902b8312ace667a5c002256a9401_1440w.jpg'
small_img = 'test/capcha4.png'

send_base64_encoded_image(small_img)
# send_image_as_file(image_path)
# send_image_url(image_url)