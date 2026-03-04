from .sort import Sort, KalmanBoxTracker
import numpy as np

class plateTracker():
    def __init__(self):
        self.tracker = Sort(max_age=10,min_hits=3,iou_threshold=0.3)


    def update(self,detections):
        if len(detections) > 0:
            dets = np.array(detections, dtype=float)
        else:
            dets = np.empty((0, 5))
        
        out = self.tracker.update(dets)
        
        return out