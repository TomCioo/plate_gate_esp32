from collections import defaultdict, Counter


class OcrVoting:
    def __init__(self,ocr_voting_min_ratio,ocr_voting_min_reads,ocr_history_size):
        self.ocr_voting_min_reads = ocr_voting_min_reads
        self.ocr_voting_min_ratio = ocr_voting_min_ratio
        self.ocr_history_size = ocr_history_size
        self.history = defaultdict(list)
        if ocr_voting_min_reads > ocr_history_size:
            raise ValueError("voting min reads must be lower or equal to history size")

        if ocr_voting_min_ratio <= 0 or ocr_voting_min_ratio > 1:
            raise ValueError("voting min ratio must be in range of 0-1")

    def add_reading(self,track_id,plate_text):
        if not plate_text:
            return
        
        self.history[track_id].append(plate_text)
        self.history[track_id] = self.history[track_id][-self.ocr_history_size:]

    def get_confirmed_plate(self,track_id):
        plate_counter = Counter(self.history.get(track_id, []))
        total_readings = sum(plate_counter.values())
        if total_readings < self.ocr_voting_min_reads:
            return None
        
        required_votes = self.ocr_voting_min_ratio * total_readings
        most_common_plate,most_common_votes = plate_counter.most_common(1)[0]

        if most_common_votes >= required_votes:
            return most_common_plate
        else:
            return None

    def forget_track(self,track_id):
        self.history.pop(track_id,None)