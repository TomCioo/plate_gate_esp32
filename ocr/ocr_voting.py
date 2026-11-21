from collections import defaultdict,Counter, deque


class OcrVoting:
    def __init__(self,ocr_voting_min_ratio,ocr_voting_min_reads,ocr_history_size):
        if ocr_voting_min_reads < 1:
            raise ValueError("min_reads musi być większe lub równe 1")
        
        if ocr_history_size < 1:
            raise ValueError("history_size musi być większe lub równe 1")
        
        if ocr_voting_min_reads > ocr_history_size:
            raise ValueError("min_reads nie może być większe niż history_size")
        
        if not 0.5 < ocr_voting_min_ratio <= 1:
            raise ValueError("min_ratio musi być większe od 0.5 i mniejsze lub równe 1")
        
        self.ocr_voting_min_reads = ocr_voting_min_reads
        self.ocr_voting_min_ratio = ocr_voting_min_ratio
        self.ocr_history_size = ocr_history_size
        self.history = defaultdict(lambda: deque(maxlen=ocr_history_size))

    def add_reading(self,track_id,plate_text):
        if not plate_text:
            return
        
        self.history[track_id].append(plate_text)

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