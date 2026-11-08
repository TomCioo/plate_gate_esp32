from ocr_voting import OcrVoting


# Test 1 - za mało odczytów
voting = OcrVoting(0.6, 6, 20)

for _ in range(5):
    voting.add_reading(1, "KRA12345")

assert voting.get_confirmed_plate(1) is None


# Test 2 - wyraźny zwycięzca
voting = OcrVoting(0.6, 6, 20)

for _ in range(6):
    voting.add_reading(1, "KRA12345")

for _ in range(2):
    voting.add_reading(1, "KNT123456")

assert voting.get_confirmed_plate(1) == "KRA12345"


# Test 3 - brak wyraźnego zwycięzcy (3 / 3 / 2)
voting = OcrVoting(0.6, 6, 20)

for plate in ["KRA12345"] * 3 + ["KNT123456"] * 3 + ["KWA12345"] * 2:
    voting.add_reading(1, plate)

assert voting.get_confirmed_plate(1) is None


# Test 4 - forget_track usuwa potwierdzony numer
voting = OcrVoting(0.6, 6, 20)

for _ in range(6):
    voting.add_reading(1, "KRA12345")

assert voting.get_confirmed_plate(1) == "KRA12345"

voting.forget_track(1)

assert voting.get_confirmed_plate(1) is None


# Test 5 - forget_track dla nieznanego ID
voting = OcrVoting(0.6, 6, 20)

voting.forget_track(2)

assert voting.get_confirmed_plate(2) is None


# Test 6 - puste odczyty i None są ignorowane
voting = OcrVoting(0.6, 6, 20)

for plate in [None, "", "", "", "", "", None]:
    voting.add_reading(1, plate)

assert voting.get_confirmed_plate(1) is None


# Test 7 - limit historii deque
voting = OcrVoting(0.6, 1, 3)

for plate in ["KRA11111", "KRA22222", "KRA33333", "KRA44444"]:
    voting.add_reading(1, plate)

assert len(voting.history[1]) == 3
assert "KRA11111" not in voting.history[1]


# Test 8 - usunięcie jednego tracka nie usuwa drugiego
voting = OcrVoting(0.6, 2, 20)

voting.add_reading(1, "KRA12345")
voting.add_reading(1, "KRA12345")

voting.add_reading(2, "KNT12345")
voting.add_reading(2, "KNT12345")

voting.forget_track(1)

assert voting.get_confirmed_plate(1) is None
assert voting.get_confirmed_plate(2) == "KNT12345"


# Test 9 - dokładnie 60% zgodności
voting = OcrVoting(0.6, 5, 20)

for plate in ["KRA12345"] * 3 + ["KNT12345"] * 2:
    voting.add_reading(1, plate)

assert voting.get_confirmed_plate(1) == "KRA12345"


# Test 10 - poniżej progu 60%
voting = OcrVoting(0.6, 5, 20)

for plate in ["KRA12345"] * 4 + ["KNT12345"] * 3:
    voting.add_reading(1, plate)

assert voting.get_confirmed_plate(1) is None


# Test 11 - min_reads = 0
try:
    OcrVoting(0.6, 0, 20)
    assert False, "Powinien wystąpić ValueError"
except ValueError:
    pass


# Test 12 - min_ratio = 0
try:
    OcrVoting(0, 6, 20)
    assert False, "Powinien wystąpić ValueError"
except ValueError:
    pass


# Test 13 - min_ratio = 0.5
try:
    OcrVoting(0.5, 6, 20)
    assert False, "Powinien wystąpić ValueError"
except ValueError:
    pass


# Test 14 - min_ratio = 1.5
try:
    OcrVoting(1.5, 6, 20)
    assert False, "Powinien wystąpić ValueError"
except ValueError:
    pass


# Test 15 - min_reads > history_size
try:
    OcrVoting(0.6, 10, 5)
    assert False, "Powinien wystąpić ValueError"
except ValueError:
    pass


print("Wszystkie testy zakończone poprawnie!")