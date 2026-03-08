import easyocr
import cv2 as cv
import numpy as np
from collections import defaultdict, Counter
import re


class plateOCR:

    def __init__(self):

        self.reader = easyocr.Reader(['en'], gpu=True)

        self.memory = defaultdict(list)


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

        if re.match(pattern, text):
            return True

        return False


    def read(self, plate_img, track_id):

        if plate_img.size == 0:
            return ""

        plate_img = cv.resize(plate_img, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)

        processed = self.preprocess(plate_img)

        results = self.reader.readtext(processed)

        texts = []

        for (_, text, score) in results:
            if score < 0.4:
                continue

            text = text.upper()
            text = ''.join(filter(str.isalnum, text))

            if self.plate_regex(text):
                texts.append(text)

        for t in texts:
            self.memory[track_id].append(t)
        
        self.memory[track_id] = self.memory[track_id][-20:]

        if len(self.memory[track_id]) >= 6:

            most_common = Counter(self.memory[track_id]).most_common(1)[0][0]

            return most_common

        return ""