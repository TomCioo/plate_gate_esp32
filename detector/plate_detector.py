from ultralytics import YOLO


class PlateDetector:
    def __init__(self,model_path,detection_confidence):
        self.model = YOLO(model_path)
        self.detection_confidence = detection_confidence

    def detect(self,frame):
        results = self.model(frame,stream=True)

        plates = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1,y1,x2,y2 = map(int,box.xyxy[0].tolist())
                conf = float(box.conf[0])
                if conf > self.detection_confidence:
                    plates.append((x1,y1,x2,y2,conf))

        return plates

       











