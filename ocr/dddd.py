import ddddocr
import cv2
from PIL import Image
import numpy as np
import os
import base64
import io
import json
import time
import requests
from werkzeug.datastructures import FileStorage

# define a ocr class:
class ddocr:
    def __init__(self):
        self.ocr = ddddocr.DdddOcr()
        # self.ocr = ddddocr.DdddOcr(beta=True)
        self.det = ddddocr.DdddOcr(det=True)
        # self.predictor = PaddleOCR(use_angle_cls=False, lang="ch",enable_mkldnn=True,det_model_dir="models/ch_ppocr_server_v2.0_det_infer/",det_db_box_thresh=0.3,det_db_thresh=0.34 )
        #det_db_box_thresh=0.3,det_db_thresh=0.34,
        #det_db_score_mode="slow",det_db_box_thresh=0.7,det_limit_side_len=300)#,det_db_box_thresh=0.7,det_db_unclip_ratio=1.8)#,det_db_unclip_ratio=0.8,det_db_box_thresh=0.8,det_db_thresh=0.4)  # need to run only once to download and load model into memory

    def base64_to_opencv_image(self,base64_str):
        # 移除可能存在的base64:前缀
        if base64_str.startswith('base64:'):
            base64_str = base64_str[7:]
        # 将base64字符串解码为二进制数据
        img_data = base64.b64decode(base64_str)
        # 将二进制数据解码为OpenCV图像
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    def convert_to_cv2(self,image_input):
        # Check if the input is a local file path
        if isinstance(image_input, str) and os.path.isfile(image_input):
            # Read the image from the file path
            image = cv2.imread(image_input)

        elif isinstance(image_input, bytes):
            # Read the image from bytes
            image = cv2.imdecode(np.frombuffer(image_input, np.uint8), cv2.IMREAD_COLOR)

        elif isinstance(image_input, Image.Image):
            # Read the image from a PIL.Image instance
            image = cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)

        elif isinstance(image_input, np.ndarray):
            # Read the image from a cv2 image (numpy array)
            image = image_input

        # Check if the input is a base64 string
        elif isinstance(image_input, str):
            try:
                # Remove 'base64:' prefix if it exists
                if image_input.startswith('base64:'):
                    image_input = image_input[7:]
                elif image_input.startswith("data:"):
                    image_input = image_input.split(",")[1]

                # Check if the input is a valid base64 string
                image=self.base64_to_opencv_image(image_input)
            except Exception:
                raise ValueError('Unsupported image_input format.')
        else:
            raise ValueError('Unsupported image_input format.')
        
        return image

    def convert_to_bytes(self,image_input):

        print("image_input")
        print(image_input)
        print("=======================================================================")
        # Check if the input is a local file path
        if isinstance(image_input, str) and os.path.isfile(image_input):
            # Read the image from the file path
            with open(image_input, 'rb') as f:
                image_bytes = f.read()

        elif isinstance(image_input, bytes):
            # Keep the image bytes as is
            image_bytes = image_input

        elif isinstance(image_input, Image.Image):
            # Read the image from a PIL.Image instance
            with io.BytesIO() as output:
                image_input.save(output, format='PNG')
                image_bytes = output.getvalue()

        elif isinstance(image_input, np.ndarray):
            # Read the image from a cv2 image (numpy array)
            _, buffer = cv2.imencode('.png', image_input)
            image_bytes = buffer.tobytes()

        elif isinstance(image_input, str) and (image_input.startswith('http://') or image_input.startswith('https://')):
            # Read the image from a URL
            response = requests.get(image_input)
            image_bytes = response.content
        elif isinstance(image_input, FileStorage):
            # Read the image from Flask's request.files['image']
            image_bytes = image_input.read()

        # Check if the input is a base64 string
        elif isinstance(image_input, str):
            try:
                # Remove 'base64:' prefix if it exists
                if image_input.startswith('base64:'):
                    image_input = image_input[7:]
                elif image_input.startswith("data:"):
                    image_input = image_input.split(",")[1]

                # Check if the input is a valid base64 string
                image_bytes = base64.b64decode(image_input)
            except Exception:
                raise ValueError('Unsupported image_input format.')
        else:
            raise ValueError('Unsupported image_input format.')

        return image_bytes

    def generate_timestamp_filename(self):
        timestamp = time.time() 
        filename = time.strftime("%Y%m%d%H%M%S_", time.localtime(timestamp))
        filename = filename.replace('/', '_').replace('-', '-')
        return filename



    def crop_boxes(self,image_input, boxes, expand=1):
        image=self.convert_to_cv2(image_input)
        # Convert the image to PIL.Image format
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        cropped_images = []
        center_points = []
        text=[]
        # Iterate over the boxes
        for box in boxes:
            x1, y1, x2, y2 = box

            # Expand the box
            x1 = max(0, x1 - expand)
            y1 = max(0, y1 - expand)
            x2 = min(pil_image.width, x2 + expand)
            y2 = min(pil_image.height, y2 + expand)

            # Calculate the center point
            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
            center_points.append((cx, cy))

            # Crop the image
            cropped_image = pil_image.crop((x1, y1, x2, y2))
            # print("type: ============ ",type(cropped_image))
            # print(isinstance(cropped_image,  Image.Image))
            if not isinstance(cropped_image, (bytes, str,  Image.Image)):
                print("未知图片类型..............................")
            # print(cropped_image)
            
            if self.ocr:
                res = self.ocr.classification(cropped_image)
                # print(res)
                text.append(res)
                
            # Append the cropped image to the list
            cropped_images.append(cropped_image)

            # Draw a red point on the image according to the center point coordinates
            cv2.circle(image, (cx, cy), 3, (0, 0, 255), -1)

        # Convert the result back to PIL.Image format
        result_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        return cropped_images, center_points,text, result_image

    def consolidate_lists(self, texts, centers):
        result = []
        for text, center in zip(texts, centers):
            result.append({"text": text, "center": center})
        return result
    
    def OCR(self,image_input):
        img_bytes=self.convert_to_bytes(image_input)
        poses = self.det.detection(img_bytes) #bytes
        # print(poses) #[[23, 116, 54, 146], [35, 26, 66, 56], [45, 154, 76, 184], [96, 6, 126, 35], [94, 87, 124, 118], [232, 48, 261, 77], [254, 134, 281, 162]]
        cropped_images, center_points,text, result_image = self.crop_boxes(image_input, poses, expand=1)
        result_image.save("temp/results/result_"+self.generate_timestamp_filename()+".jpg")
        consolidated_json = self.consolidate_lists(text, center_points)
        return consolidated_json
        # [{'text': '却', 'center': (38, 131)}, {'text': '厦', 'center': (50, 41)}, {'text': '线', 'center': (60, 169)}, {'text': '大', 'center': (111, 20)}, {'text': '帝', 'center': (109, 102)}, {'text': '国', 'center': (246, 62)}, {'text': '示', 'center': (267, 148)}]

        # print(text)
        # print(center_points)

        # for crop in poses:
        #     # crop.save("_crop.jpg")
        #     res = ocr.classification(crop)  # bytes,   str,   pathlib.PurePath,   Image.Image
        #     print(res)

            
        # cropped_images[0].show()

        # To show the image with the red points
        # result_image.show()

    def small_ocr(self,image_input):
        image = self.convert_to_bytes(image_input)
        res = self.ocr.classification(image)#bytes, str, pathlib.PurePath, Image.Image
        print(res)


if __name__ == '__main__':
    oc=ddocr()
    data_json=oc.OCR("../test/capcha2.png")
    print(data_json)


