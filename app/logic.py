import json

from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
SESSIONS_FILE = DATA_DIR / "sleep_sessions.json"


class SleepSessionManager:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        self.sessions = self.load_sessions()

    def get_sessions(self):
        return self.sessions
    
    def load_sessions(self):
        if not SESSIONS_FILE.exists():
            return []
        with open (SESSIONS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
        
    def save_sessions(self):
        with open(SESSIONS_FILE, "w") as f:
            json.dump(self.sessions, f, indent=4)
    
    def add_session(self, start, end):
        if not (0 <= start < 24 and 0 <= end < 24):
            raise ValueError("start and end value must be between 0 and 23")
        self.sessions.append({"start": start, "end": end})
        self.save_sessions()

    def edit_session(self, index, start, end):
        if not (0 <= start < 24 and 0 <= end < 24):
            raise ValueError("start and end value must be between 0 and 23")
        if 0 <= index < len(self.sessions):
            self.sessions[index] = {"start": start, "end": end}
            self.save_sessions()
        else:
            raise IndexError("Session index out of range")

    def delete_session(self, index):
        if 0 <= index < len(self.sessions):
            self.sessions.pop(index)
            self.save_sessions()
        else:
            raise IndexError("Session index out of range")

    def clear_sessions(self):
        self.sessions = []
        self.save_sessions()