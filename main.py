import cv2 as cv

import config
from database.database import load_whitelist
from decision.decision_manager import DecisionManager
from detector.plate_detector import PlateDetector
from gate.fake_gate import FakeGate
from gate.gate_controller import GateController
from ocr.plate_reader import PlateOCR
from ocr.ocr_voting import OcrVoting
from tracker.plate_tracker import PlateTracker


def main():
    cap = cv.VideoCapture(config.VIDEO_SOURCE)
    try:
        if not cap.isOpened():
            print("Nie mozna otworzyc zrodla video")
            return

        decision = DecisionManager(open_cooldown=config.OPEN_COOLDOWN,retry_cooldown=config.RETRY_COOLDOWN,whitelist=load_whitelist())
        detector = PlateDetector(model_path=config.MODEL_PATH,detection_confidence=config.DETECTION_CONFIDENCE)
        tracker = PlateTracker(max_age=config.TRACKER_MAX_AGE,min_hits=config.TRACKER_MIN_HITS,iou_threshold=config.TRACKER_IOU_THRESHOLD)
        ocr = PlateOCR(ocr_use_gpu=config.OCR_USE_GPU,ocr_confidence=config.OCR_CONFIDENCE)
        ocr_voting = OcrVoting(ocr_voting_min_ratio=config.OCR_VOTING_MIN_RATIO,ocr_voting_min_reads=config.OCR_VOTING_MIN_READS,ocr_history_size=config.OCR_HISTORY_SIZE)

        if config.USE_FAKE_GATE:
            gate = FakeGate(config.FAKE_GATE_SUCCESS)
        else:
            gate = GateController(config.ESP_IP)
        id_frame_counter = {} #klatki w ktorych tablica jest czytelna
        tracked_ids = {}  #id samochodu : missing frames

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
                tracked_ids[track_id] = 0
                current_ids_in_frame.add(track_id)
            
                
                if width >= config.MIN_PLATE_WIDTH and height >= config.MIN_PLATE_HEIGHT:
                    id_frame_counter[track_id] = id_frame_counter.get(track_id,0) + 1
                    pad = config.PLATE_CROP_PADDING
                    x1p = max(0, x1-pad)
                    y1p = max(0, y1-pad)
                    x2p = min(frame.shape[1], x2+pad)
                    y2p = min(frame.shape[0], y2+pad)
    
                    plate_crop = frame[y1p:y2p, x1p:x2p]
                    if id_frame_counter[track_id] % config.OCR_INTERVAL_FRAMES == 0:
                        text = ocr.read(plate_crop)
                        ocr_voting.add_reading(track_id,text)

                confirmed_plate = ocr_voting.get_confirmed_plate(track_id)

                if width >= config.MIN_PLATE_WIDTH and height >= config.MIN_PLATE_HEIGHT:
                    if decision.try_open_gate(track_id, confirmed_plate):
                        isOpened = gate.open_gate(confirmed_plate)
                        decision.report_attempt(track_id, isOpened)

                        if not isOpened:
                            print("Failed to open")

                display_text = confirmed_plate if confirmed_plate is not None else "?"
                cv.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),2)
                cv.putText(frame,f'ID:{track_id} {display_text}',(x1,y1 - 10),cv.FONT_HERSHEY_PLAIN,1,(0,255,0),2)
            
            for track_id in list(tracked_ids.keys()):
                if track_id not in current_ids_in_frame:
                    tracked_ids[track_id] += 1

                    if tracked_ids[track_id] >= config.MAX_MISSING_FRAMES:
                        del tracked_ids[track_id]
                        id_frame_counter.pop(track_id, None)
                        ocr_voting.forget_track(track_id)
                        decision.forget_track(track_id)
            
            resized_frame = cv.resize(frame, (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT))
            cv.imshow("Frame",resized_frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv.destroyAllWindows()

if __name__ == "__main__":
    main()
