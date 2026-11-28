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
from tracker.vehicle_lifecycle import VehicleLifecycle


  
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
        lifecycle = VehicleLifecycle(config.MAX_MISSING_FRAMES)

        if config.USE_FAKE_GATE:
            gate = FakeGate(config.FAKE_GATE_SUCCESS)
        else:
            gate = GateController(config.ESP_IP)

        while True: 
            success,frame = cap.read()
            if not success:
                break

            detections = detector.detect(frame)
            tracked_objects = tracker.update(detections)

            for obj in tracked_objects:
                x1, y1, x2, y2, track_id = map(int, obj)
                bbox = (x1, y1, x2, y2)
                width = x2 - x1
                height = y2 - y1
                lifecycle.mark_seen_vehicle(track_id)
            
                has_valid_plate_size = is_valid_plate_size(width,height,config.MIN_PLATE_WIDTH,config.MIN_PLATE_HEIGHT)
                if has_valid_plate_size:
                    readable_frames = lifecycle.increment_readable_frame(track_id)
    
                    plate_crop = crop_plate(bbox,config.PLATE_CROP_PADDING,frame)
                    if readable_frames % config.OCR_INTERVAL_FRAMES == 0:
                        print(f"[OCR] ID: {track_id} | Odczyt nr: {readable_frames // config.OCR_INTERVAL_FRAMES}")
                        text = ocr.read(plate_crop)
                        ocr_voting.add_reading(track_id,text)

                confirmed_plate = ocr_voting.get_confirmed_plate(track_id)

                if has_valid_plate_size:
                    if decision.try_open_gate(track_id, confirmed_plate):
                        print(f"[GATE ATTEMPT] ID: {track_id} | Plate: {confirmed_plate}")
                        is_opened = gate.open_gate(confirmed_plate)
                        decision.report_attempt(track_id, is_opened)

                        print(f"[GATE RESULT] ID: {track_id} | Success: {is_opened}")

                        if not is_opened:
                            print("Failed to open")

                draw_plate_overlay(confirmed_plate,frame,bbox,track_id)

            expired_ids = lifecycle.frame_end()

            for track_id in expired_ids:
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
