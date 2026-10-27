import io
import os
import urllib.request

import zstandard

url = "https://database.lichess.org/lichess_db_eval.jsonl.zst"
positions = 1000
os.makedirs("data", exist_ok=True)

with urllib.request.urlopen(url) as response:
    stream = zstandard.ZstdDecompressor().stream_reader(response)
    lines = io.TextIOWrapper(stream, encoding="utf-8")
    with open("data/sample.jsonl", "w") as out:
        for i, line in enumerate(lines):
            if i >= positions:
                break
            out.write(line)

print("Success!")