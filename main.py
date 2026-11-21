import cv2 as cv

import config
from database.database import load_whitelist
from decision.decision_manager import DecisionManager
from detector.plate_detector import PlateDetector
from frame_utils import crop_plate, draw_plate_overlay, is_valid_plate_size
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
        vehicles_with_missing_frames = {}  #id samochodu : missing frames

        while True: 
            success,frame = cap.read()
            if not success:
                break

            detections = detector.detect(frame)
            tracked_objects = tracker.update(detections)
            current_ids_in_frame = set()

            for obj in tracked_objects:
                x1, y1, x2, y2, track_id = map(int, obj)
                bbox = (x1, y1, x2, y2)
                width = x2 - x1
                height = y2 - y1
                vehicles_with_missing_frames[track_id] = 0
                current_ids_in_frame.add(track_id)
            
                has_valid_plate_size = is_valid_plate_size(width,height,config.MIN_PLATE_WIDTH,config.MIN_PLATE_HEIGHT)
                if has_valid_plate_size:
                    id_frame_counter[track_id] = id_frame_counter.get(track_id,0) + 1
    
                    plate_crop = crop_plate(bbox,config.PLATE_CROP_PADDING,frame)
                    if id_frame_counter[track_id] % config.OCR_INTERVAL_FRAMES == 0:
                        text = ocr.read(plate_crop)
                        ocr_voting.add_reading(track_id,text)

                confirmed_plate = ocr_voting.get_confirmed_plate(track_id)

                if has_valid_plate_size:
                    if decision.try_open_gate(track_id, confirmed_plate):
                        is_opened = gate.open_gate(confirmed_plate)
                        decision.report_attempt(track_id, is_opened)

                        if not is_opened:
                            print("Failed to open")

                draw_plate_overlay(confirmed_plate,frame,bbox,track_id)
            
            for track_id in list(vehicles_with_missing_frames.keys()):
                if track_id not in current_ids_in_frame:
                    vehicles_with_missing_frames[track_id] += 1

                    if vehicles_with_missing_frames[track_id] >= config.MAX_MISSING_FRAMES:
                        del vehicles_with_missing_frames[track_id]
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
