import json, os, time, datetime
from pathlib import Path
from collections import defaultdict

TELEMETRY_FILE = Path.home() / "Bridge_GAD_Telemetry.json"

class Telemetry:
    def __init__(self):
        self.start_time = time.time()
        # Use a regular dict instead of defaultdict to avoid type issues
        self.data = {}
        self.data["last_session"] = str(datetime.datetime.now())
        self.load()

    def load(self):
        if TELEMETRY_FILE.exists():
            try:
                with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    # Merge loaded data with existing data
                    self.data.update(loaded_data)
            except Exception:
                pass

    def event(self, name: str):
        # Initialize the counter if it doesn't exist
        if name not in self.data:
            self.data[name] = 0
        self.data[name] += 1
        self.save()

    def save(self):
        # Calculate and store total runtime
        current_runtime = time.time() - self.start_time
        self.data["total_runtime_sec"] = self.data.get("total_runtime_sec", 0) + current_runtime
        # Reset start_time for next save
        self.start_time = time.time()
        
        with open(TELEMETRY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def summarize(self):
        runtime_hr = self.data.get("total_runtime_sec", 0) / 3600
        return (
            f"Sessions: {self.data.get('sessions', 0)}\n"
            f"Total runtime: {runtime_hr:.2f} hours\n"
            f"Feature uses: {dict(self.data)}"
        )

telemetry = Telemetry()