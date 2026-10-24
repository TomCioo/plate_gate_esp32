import numpy as np

from .sort import Sort
import config

class PlateTracker:
    def __init__(self):
        self.tracker = Sort(max_age=config.TRACKER_MAX_AGE,min_hits=config.TRACKER_MIN_HITS,iou_threshold=config.TRACKER_IOU_THRESHOLD)


    def update(self,detections):
        if len(detections) > 0:
            dets = np.array(detections, dtype=float)
        else:
            dets = np.empty((0, 5))
        
        out = self.tracker.update(dets)
        
        return out