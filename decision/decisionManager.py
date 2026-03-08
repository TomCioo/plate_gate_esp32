import config
import time

class decisionManager():
    def shouldOpenGate(self,id,text,idFrameCounter,openedIds,lastOpenTime,whitelist):
        frames_ok = idFrameCounter.get(id, 0) >= config.MIN_FRAMES_FOR_OPEN
        cooldown_ok = time.time() - lastOpenTime > config.GLOBAL_COOLDOWN
        plate_ok = text != "" and text in whitelist
        not_opened = id not in openedIds

        if frames_ok and cooldown_ok and plate_ok and not_opened:
            return True

        return False