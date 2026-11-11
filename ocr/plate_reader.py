import re

import cv2 as cv
import easyocr


class PlateOCR:

    def __init__(self,ocr_use_gpu,ocr_confidence):
        self.ocr_use_gpu = ocr_use_gpu
        self.reader = easyocr.Reader(['en'], gpu=self.ocr_use_gpu)
        self.ocr_confidence = ocr_confidence

    def preprocess(self, img):

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        gray = cv.bilateralFilter(gray, 11, 17, 17)

        gray = cv.equalizeHist(gray)

        thresh = cv.adaptiveThreshold(
            gray,
            255,
            cv.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv.THRESH_BINARY,
            11,
            2
        )

        return thresh
    
    def plate_regex(self, text):

        pattern = r'^[A-Z]{2,3}[A-Z0-9]{4,5}$'

        return re.match(pattern,text) is not None


    def read(self, plate_img):

        if plate_img.size == 0:
            return None

        plate_img = cv.resize(plate_img, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)

        #processed = self.preprocess(plate_img)

        results = self.reader.readtext(plate_img)
        best_result = None
        best_score = 0

        for _,text,score in results:
            text = text.upper()
            text = ''.join(filter(str.isalnum, text))

            if score >= self.ocr_confidence and self.plate_regex(text):
                if score > best_score:
                    best_score = score
                    best_result = text

        return best_result


        