import csv
import os

def loadWhitelist(path=None):
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "whitelist.csv")
    
    whitelist = set()

    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            whitelist.add(row["plate"].strip().upper())

    return whitelist