import json, gzip
file = input("> ")

# Add encoding="utf-8" here:
with open(f"packs/{file}.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

with gzip.open(f"packs/{file}.json.gz", "wt", encoding="utf-8") as f:
    json.dump(data, f)