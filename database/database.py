import csv

def loadWhitelist(path="whitelist.csv"):
    whitelist = set()

    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            whitelist.add(row["plate"].strip())

    return whitelist