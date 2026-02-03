import json
from pathlib import Path

def load_json():
    path = Path("./sshinfo.json")

    if not path.exists():
        raise FileNotFoundError(f"JSON file not found")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)