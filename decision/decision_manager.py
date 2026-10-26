import time


class DecisionManager:
    def __init__(self,open_cooldown,min_frames_for_open,retry_cooldown):
        self.open_cooldown = open_cooldown
        self.min_frames_for_open = min_frames_for_open
        self.retry_cooldown = retry_cooldown

        self.last_attempt_time = None
        
    def should_open_gate(self,track_id,text,id_frame_counter,opened_ids,last_open_time,whitelist):
        if self.last_attempt_time is not None and time.monotonic() - self.last_attempt_time < self.retry_cooldown:
            return False
            
        frames_ok = id_frame_counter.get(track_id, 0) >= self.min_frames_for_open
        plate_ok = text != "" and text in whitelist
        not_opened = track_id not in opened_ids
        if last_open_time is None:
            cooldown_ok = True
        else:
            cooldown_ok = time.monotonic() - last_open_time > self.open_cooldown

        return frames_ok and cooldown_ok and plate_ok and not_opened

    def mark_attempt(self):
        self.last_attempt_time = time.monotonic()