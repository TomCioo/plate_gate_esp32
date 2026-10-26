import numpy as np

from .sort import Sort


class PlateTracker:
    def __init__(self,max_age,min_hits,iou_threshold):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.tracker = Sort(max_age=self.max_age,min_hits=self.min_hits,iou_threshold=self.iou_threshold)


    def update(self,detections):
        if len(detections) > 0:
            dets = np.array(detections, dtype=float)
        else:
            dets = np.empty((0, 5))
        
        out = self.tracker.update(dets)
        
        return out