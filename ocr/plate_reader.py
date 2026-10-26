import re
from collections import Counter, defaultdict

import cv2 as cv
import easyocr


class PlateOCR:

    def __init__(self,ocr_use_gpu,ocr_confidence,ocr_history_size,ocr_voting_min_reads):
        self.ocr_use_gpu = ocr_use_gpu
        self.reader = easyocr.Reader(['en'], gpu=self.ocr_use_gpu)
        self.memory = defaultdict(list)
        self.ocr_confidence = ocr_confidence
        self.ocr_history_size = ocr_history_size
        self.ocr_voting_min_reads = ocr_voting_min_reads

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


    def read(self, plate_img, track_id):

        if plate_img.size == 0:
            return ""

        plate_img = cv.resize(plate_img, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)

        processed = self.preprocess(plate_img)

        results = self.reader.readtext(processed)

        texts = []

        for (_, text, score) in results:
            if score < self.ocr_confidence:
                continue

            text = text.upper()
            text = ''.join(filter(str.isalnum, text))

            if self.plate_regex(text):
                texts.append(text)

        for t in texts:
            self.memory[track_id].append(t)
        
        self.memory[track_id] = self.memory[track_id][-self.ocr_history_size:]

        if len(self.memory[track_id]) >= self.ocr_voting_min_reads:

            most_common = Counter(self.memory[track_id]).most_common(1)[0][0]

            return most_common

        return ""