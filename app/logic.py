import json

from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
SESSIONS_FILE = DATA_DIR / "sleep_sessions.json"


class SleepSessionManager:
    def __init__(self):
        self.sessions = self.load_sessions()

    def get_sessions(self):
        return self.sessions
    
    def load_sessions(self):
        if not SESSIONS_FILE.exists():
            return []
        with open (SESSIONS_FILE, "r") as f:
            return json.load(f)
        
    def save_sessions(self):
        with open(SESSIONS_FILE, "w") as f:
            json.dump(self.sessions, f, indent=4)
    
    def add_session(self, start, end):
        self.sessions.append({"start": start % 24, "end": end % 24})
        self.save_sessions()

    def clear_sessions(self):
        self.sessions = []
        self.save_sessions()