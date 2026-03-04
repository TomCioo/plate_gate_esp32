from ultralytics import YOLO
import config

class plateDetector():
    def __init__(self,model_path):
        self.model = YOLO(model_path)

    def detect(self,frame):
        results = self.model(frame,stream=True)

        plates = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1,y1,x2,y2 = map(int,box.xyxy[0].tolist())
                conf = float(box.conf[0])
                if conf > config.DETECTION_CONFIDENCE:
                    plates.append((x1,y1,x2,y2,conf))

        return plates

       











