import time


class DecisionManager:
    def __init__(self,open_cooldown,retry_cooldown,whitelist):
        self.open_cooldown = open_cooldown
        self.retry_cooldown = retry_cooldown
        self.whitelist = whitelist

        self.last_attempt_time = None
        self.last_open_time = None

        self.opened_ids = set()
        self.pending_ids = set()
        
    def should_open_gate(self,track_id,text):
        current_time = time.monotonic()

        if track_id in self.pending_ids:
            return False
        
        if self.last_attempt_time is not None and current_time - self.last_attempt_time < self.retry_cooldown:
            return False

        if self.last_open_time is not None and current_time - self.last_open_time < self.open_cooldown:
            return False
    
        plate_ok = text is not None and text in self.whitelist
        not_opened = track_id not in self.opened_ids
     
        if plate_ok and not_opened:
            self.pending_ids.add(track_id)
            return True

        return False

    def report_attempt(self,track_id,success):
        if track_id not in self.pending_ids:
            return

        current_time = time.monotonic()

        self.last_attempt_time = current_time
        self.pending_ids.discard(track_id)
        
        if success:
            self.opened_ids.add(track_id)
            self.last_open_time = current_time
            

    def forget_track(self,track_id):
        self.opened_ids.discard(track_id)
        self.pending_ids.discard(track_id)