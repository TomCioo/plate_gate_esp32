import time

import cv2 as cv

import config
from database.database import load_whitelist
from decision.decision_manager import DecisionManager
from detector.plate_detector import PlateDetector
from gate.gate_controller import GateController
from ocr.plate_reader import PlateOCR
from tracker.plate_tracker import PlateTracker


def main():
    cap = cv.VideoCapture(config.VIDEO_SOURCE)

    if not cap.isOpened():
        print("Nie mozna otworzyc zrodla video")
        return
    
    decision = DecisionManager()
    detector = PlateDetector(config.MODEL_PATH)
    tracker = PlateTracker()
    ocr = PlateOCR()
    gate = GateController(config.ESP_IP)
    whitelist = load_whitelist()
    opened_ids = set()
    last_open_time = 0
    id_frame_counter = {} #jak dlugo jest widoczna tablica np 20 klatek

    while True:
        success,frame = cap.read()
        if not success:
            break
    
        detections = detector.detect(frame)
        tracked_objects = tracker.update(detections)
        current_ids_in_frame = set()

        for obj in tracked_objects:
            x1, y1, x2, y2, track_id = map(int, obj)
            width = x2 - x1
            height = y2 - y1
            memory_list = ocr.memory.get(track_id, [])
            text = memory_list[-1] if memory_list else ""

            if width < config.MIN_PLATE_WIDTH or height < config.MIN_PLATE_HEIGHT:
                continue

            pad = config.PLATE_CROP_PADDING
            x1p = max(0, x1-pad)
            y1p = max(0, y1-pad)
            x2p = min(frame.shape[1], x2+pad)
            y2p = min(frame.shape[0], y2+pad)

            plate_crop = frame[y1p:y2p, x1p:x2p]
            #if plate_crop.size != 0:
                #cv.imshow("plate", plate_crop)
            
            id_frame_counter[track_id] = id_frame_counter.get(track_id,0) + 1
            if id_frame_counter[track_id] % config.OCR_INTERVAL_FRAMES == 0:
                text = ocr.read(plate_crop,track_id)
            current_ids_in_frame.add(track_id)
            if decision.should_open_gate(track_id, text, id_frame_counter, opened_ids, last_open_time,whitelist):
                gate.open_gate(text)
                #print("otwirranie bramy")
                opened_ids.add(track_id)
                last_open_time = time.time()

            cv.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2)
            cv.putText(frame,f'ID:{track_id} {text}',(x1,y1 - 10),cv.FONT_HERSHEY_PLAIN,1,(0,255,0),2)
            #cv.putText(frame,f'{id}',(x1,y1 - 10),cv.FONT_HERSHEY_PLAIN,1,(0,0,255),2)
            

        
        for track_id in list(id_frame_counter.keys()):
            if id not in current_ids_in_frame:
                del id_frame_counter[track_id]
                if track_id in ocr.memory:
                    del ocr.memory[track_id]

        
        resized_frame = cv.resize(frame, (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT))
        cv.imshow("Frame",resized_frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
