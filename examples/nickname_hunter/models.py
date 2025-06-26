import json


with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

entertainers = [data["entertainers"]]
# data from accounts that should be occupied by nicknames.

trackeds = [data["trackeds"]]
# ids of users that should be occupied.
