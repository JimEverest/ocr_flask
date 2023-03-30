from paddleocr import PaddleOCR, draw_ocr
import cv2
from PIL import Image
import time
import hashlib
import random
import string
import numpy as np


# define a ocr class:
class ppocr:
    def __init__(self):
        self.predictor = PaddleOCR(use_angle_cls=False, lang="ch",det_model_dir="models/ch_ppocr_server_v2.0_det_infer/",enable_mkldnn=True,det_db_box_thresh=0.5,det_db_thresh=0.26 )
        # self.predictor = PaddleOCR(use_angle_cls=False, lang="ch",enable_mkldnn=True,det_model_dir="models/ch_ppocr_server_v2.0_det_infer/",det_db_box_thresh=0.3,det_db_thresh=0.34 )
        #det_db_box_thresh=0.3,det_db_thresh=0.34,
        #det_db_score_mode="slow",det_db_box_thresh=0.7,det_limit_side_len=300)#,det_db_box_thresh=0.7,det_db_unclip_ratio=1.8)#,det_db_unclip_ratio=0.8,det_db_box_thresh=0.8,det_db_thresh=0.4)  # need to run only once to download and load model into memory

    def zoomin(self,img,scale=2):
        # img -- cv2 img
        height, width = img.shape[:2]
        resized_img = cv2.resize(img, (scale*width, scale*height), interpolation=cv2.INTER_CUBIC)
        return resized_img

    #no-use
    def generate_random_string(len=4):
        # Define the pool of characters to choose from
        chars = string.ascii_uppercase + string.digits
        # Generate a random 4-character string
        return ''.join(random.choices(chars, k=len))


    def process_image(self,image, output_path=None):
        output_path = "./temp/intermedia/"
        cv2.imwrite(output_path+"0_aaa.jpg", image)

        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define color ranges for black text and white border
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 10])
        lower_white = np.array([0, 0, 245])
        upper_white = np.array([180, 50, 255])

        # Create masks for black and white regions
        black_mask = cv2.inRange(hsv, lower_black, upper_black)
        kernel = np.ones((3, 3), np.uint8)
        black_mask = cv2.dilate(black_mask, kernel, iterations=2)
        cv2.imwrite(output_path+"0_black_mask.jpg", black_mask)


        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        cv2.imwrite(output_path+"0_white_mask.jpg", white_mask)

        # Dilate the white mask to cover more area around the text
        kernel = np.ones((3, 3), np.uint8)
        white_mask_dilated = cv2.dilate(white_mask, kernel, iterations=4)
        cv2.imwrite(output_path+"1_white_mask_dilated.jpg", white_mask_dilated)

        # Combine black and dilated white masks
        text_mask = cv2.bitwise_or(black_mask, white_mask_dilated)
        cv2.imwrite(output_path+"2_text_mask.jpg", text_mask)
        
        kernel = np.ones((3, 3), np.uint8)
        dilated_text_mask = cv2.dilate(text_mask, kernel, iterations=2)
        cv2.imwrite(output_path+"3_dilated.jpg", dilated_text_mask)

        # Invert the text mask to create a background mask
        background_mask = cv2.bitwise_not(dilated_text_mask)
        cv2.imwrite(output_path+"4_background_mask.jpg", background_mask)
        # Apply the text mask to the original image and the background mask to a white image
        text_only = cv2.bitwise_and(image, image, mask=dilated_text_mask)
        white_background = np.full_like(image, 255)
        background_only = cv2.bitwise_and(white_background, white_background, mask=background_mask)
        cv2.imwrite(output_path+"5_background_only.jpg", background_only)

        # Combine the text-only and background-only images
        result = cv2.add(text_only, background_only)
        cv2.imwrite(output_path+"6_result.jpg", result)

        # Convert the result to grayscale
        grayscale_result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(output_path+"7_grayscale_result.jpg", grayscale_result)

        # Set pixel brightness values between 30-255 to white
        _, threshold_result = cv2.threshold(grayscale_result, 30, 255, cv2.THRESH_BINARY)
        cv2.imwrite(output_path+"8_threshold_result.jpg", threshold_result)

        #todo
        res=self.denoise(threshold_result)
        res=self.denoise(res)
        cv2.imwrite(output_path+"10_result.jpg", res)

        res = cv2.cvtColor(res, cv2.COLOR_GRAY2BGR)
        return res


    def denoise(self,grayscale_image):
        # Apply a binary threshold to separate black text and noise from the white background
        _, threshold_image = cv2.threshold(grayscale_image, 127, 255, cv2.THRESH_BINARY_INV)

        # Define a kernel for morphological operations
        kernel = np.ones((3, 3), np.uint8)

        # Apply morphological opening (erosion followed by dilation) to remove noise
        opened_image = cv2.morphologyEx(threshold_image, cv2.MORPH_OPEN, kernel)

        # Apply morphological closing (dilation followed by erosion) to restore text shape
        cleaned_image = cv2.morphologyEx(opened_image, cv2.MORPH_CLOSE, kernel)

        # Invert the binary image to have black text on a white background
        result_image = cv2.bitwise_not(cleaned_image)
        return result_image


    def generate_timestamp_str(self,len=4):
        timestamp = str(time.time()) # 获取当前时间戳
        timestamp_bytes = timestamp.encode('utf-8') # 将时间戳转换为bytes
        md5 = hashlib.md5() 
        md5.update(timestamp_bytes) # 对时间戳进行哈希处理
        return md5.hexdigest()[:len] # 返回哈希结果的前8位字符


    def generate_timestamp_filename(self):
        timestamp = time.time() 
        filename = time.strftime("%Y%m%d%H%M%S_", time.localtime(timestamp))
        filename = filename.replace('/', '_').replace('-', '-')
        return filename + self.generate_timestamp_str()


    def ocr(self,image, zoomin=False, verbose=True):
        if zoomin:
            image = self.zoomin(image)
        image=self.process_image(image)
        result = self.predictor.ocr(image, cls=False)
        # for idx in range(len(result)):
        #     res = result[idx]
        #     for line in res:
        #         print(line)
        if verbose:
            result = result[0]
            # image = Image.open(img_path).convert('RGB')
            boxes = [line[0] for line in result]
            txts = [line[1][0] for line in result]
            scores = [line[1][1] for line in result]
            im_show = draw_ocr(image, boxes, txts, scores, font_path='./test/msyh.ttc')
            im_show = Image.fromarray(im_show)
            im_show.save("temp/results/"+self.generate_timestamp_filename()+'.jpg')
        return result


    # # Usage example
    # input_path = 'path/to/your/image.jpg'
    # output_path = 'path/to/output/image.jpg'
    # process_image(input_path, output_path)







