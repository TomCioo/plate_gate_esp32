import config
import cv2 as cv
from detector.plateDetector import plateDetector
from tracker.plateTracker import plateTracker
import numpy as np
import time

def main():
    cap = cv.VideoCapture(config.VIDEO_SOURCE)

    if not cap.isOpened():
        print("Nie mozna otworzyc zrodla video")
        return
   
    detector = plateDetector(config.MODEL_PATH)
    tracker = plateTracker()

    openedIds = set()
    lastOpenTime = 0
    idFrameCounter = {} #jak dlugo jest widoczna tablica np 20 klatek

    while True:
        success,frame = cap.read()
        if not success:
            break
    
        detections = detector.detect(frame)
        trackedObjects = tracker.update(detections)
        currentIdsInFrame = set()

        for obj in trackedObjects:
            x1, y1, x2, y2, id = map(int, obj)
            idFrameCounter[id] = idFrameCounter.get(id,0) + 1
            currentIdsInFrame.add(id)
            if(id not in openedIds and idFrameCounter[id] >= config.MIN_FRAMES_FOR_OPEN and time.time() - lastOpenTime > config.GLOBAL_COOLDOWN):
                print("OTWIERANIE BRAMY", id)

                openedIds.add(id)
                lastOpenTime = time.time()

            cv.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2)
            cv.putText(frame,f'{id}',(x1,y1 - 10),cv.FONT_HERSHEY_PLAIN,1,(0,0,255),2)

        
        for id in list(idFrameCounter.keys()):
            if id not in currentIdsInFrame:
                del idFrameCounter[id]

        
        resizedFrame = cv.resize(frame, (1280, 720))
        cv.imshow("Frame",resizedFrame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

















if __name__ == "__main__":
    main()
