# ŹRÓDŁO WIDEO
VIDEO_SOURCE = "data/test_videos/test.mp4"  # później RTSP

# MODEL
MODEL_PATH = "models/license_plate_detector.pt"

# DETEKCJA
DETECTION_CONFIDENCE = 0.5

# OCR
OCR_CONFIDENCE = 0.5

# ROI (x1, y1, x2, y2) – na razie cały obraz
ROI = None

# COOLDOWN
GLOBAL_COOLDOWN = 10
MIN_FRAMES_FOR_OPEN = 5

# ESP
ESP_IP = "192.168.1.50"

# LOGI
LOG_FILE = "logs/system.log"