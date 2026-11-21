class VehicleLifecycle:
    def __init__(self,max_missing_frames):
        if max_missing_frames <= 0:
            raise ValueError("Max Missing Frames musi byc wieksze od 0")
        self.max_missing_frames = max_missing_frames
        self.id_frame_counter = {}  #klatki w ktorych tablica jest czytelna
        self.vehicles_with_missing_frames = {}  #id samochodu : missing frames
        self.current_ids_in_frame = set()
        

    def mark_seen_car(self,track_id):
        self.vehicles_with_missing_frames[track_id] = 0
        self.current_ids_in_frame.add(track_id)


    def frame_end(self):
        expired_ids = []

        for track_id in list(self.vehicles_with_missing_frames.keys()):
            if track_id not in self.current_ids_in_frame:
                self.vehicles_with_missing_frames[track_id] += 1

                if self.vehicles_with_missing_frames[track_id] >= self.max_missing_frames:
                    expired_ids.append(track_id)
                    del self.vehicles_with_missing_frames[track_id]
                    self.id_frame_counter.pop(track_id, None)

        self.current_ids_in_frame.clear()

        return expired_ids



    def increment_readable_frame(self,track_id):
        self.id_frame_counter[track_id] = self.id_frame_counter.get(track_id,0) + 1
        return self.id_frame_counter[track_id]

