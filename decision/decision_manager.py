import time

import config


class DecisionManager:
    def should_open_gate(self,track_id,text,id_frame_counter,opened_ids,last_open_time,whitelist):
        frames_ok = id_frame_counter.get(track_id, 0) >= config.MIN_FRAMES_FOR_OPEN
        cooldown_ok = time.time() - last_open_time > config.GLOBAL_COOLDOWN
        plate_ok = text != "" and text in whitelist
        not_opened = track_id not in opened_ids

        return frames_ok and cooldown_ok and plate_ok and not_opened