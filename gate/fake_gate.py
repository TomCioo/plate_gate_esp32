

class FakeGate:
    def __init__(self,should_succeed):
        self.should_succeed = should_succeed

    def open_gate(self, plate):
        if self.should_succeed:
            print("[FAKE] BRAMA OTWARTA DLA: ", plate)
            return True

        print("[FAKE] BRAMA NIE ODPOWIADA")
        return False