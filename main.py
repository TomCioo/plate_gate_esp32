import config
import cv2 as cv
from detector.plateDetector import plateDetector
from tracker.plateTracker import plateTracker
from ocr.plateReader import plateOCR
import numpy as np
import time

def main():
    cap = cv.VideoCapture(config.VIDEO_SOURCE)

    if not cap.isOpened():
        print("Nie mozna otworzyc zrodla video")
        return
   
    detector = plateDetector(config.MODEL_PATH)
    tracker = plateTracker()
    ocr = plateOCR()
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
            width = x2 - x1
            height = y2 - y1

            if width < config.MIN_PLATE_WIDTH or height < config.MIN_PLATE_HEIGHT:
                continue

            pad = 10
            x1p = max(0, x1-pad)
            y1p = max(0, y1-pad)
            x2p = min(frame.shape[1], x2+pad)
            y2p = min(frame.shape[0], y2+pad)

            plate_crop = frame[y1p:y2p, x1p:x2p]
            #if plate_crop.size != 0:
                #cv.imshow("plate", plate_crop)
            
            if idFrameCounter[id] % 3 == 0:
                text = ocr.read(plate_crop,id)
            idFrameCounter[id] = idFrameCounter.get(id,0) + 1
            currentIdsInFrame.add(id)
            if(id not in openedIds and idFrameCounter[id] >= config.MIN_FRAMES_FOR_OPEN and time.time() - lastOpenTime > config.GLOBAL_COOLDOWN):
                print("OTWIERANIE BRAMY", id)

                openedIds.add(id)
                lastOpenTime = time.time()

            cv.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2)
            cv.putText(frame,f'ID:{id} {text}',(x1,y1 - 10),cv.FONT_HERSHEY_PLAIN,1,(0,255,0),2)
            #cv.putText(frame,f'{id}',(x1,y1 - 10),cv.FONT_HERSHEY_PLAIN,1,(0,0,255),2)
            

        
        for id in list(idFrameCounter.keys()):
            if id not in currentIdsInFrame:
                del idFrameCounter[id]
                if id in ocr.memory:
                    del ocr.memory[id]

        
        resizedFrame = cv.resize(frame, (1280, 720))
        cv.imshow("Frame",resizedFrame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

















if __name__ == "__main__":
    main()
