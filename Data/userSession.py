import os
import pickle
import multiprocessing

class UserSession:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserSession, cls).__new__(cls)
            cls._instance._init_session()
        return cls._instance

    def _init_session(self):
        self.user_id = None
        self.username = None
        self.session_dir = os.path.join(os.path.dirname(__file__), "Helpers/SessionData")
        os.makedirs(self.session_dir, exist_ok=True)
        self.session_file = os.path.join(self.session_dir, f"session_{os.getpid()}.bin")
        self._load_session_from_file()

    def login(self, username, user_id):
        self.username = username
        self.user_id = user_id
        self._save_session_to_file()
        print(f"[SESSION] Logged in as {username} with ID {user_id}")

    def getCurrentId(self):
        self._load_session_from_file()
        if self.user_id is not None:
            print(f"[SESSION] Current user ID: {self.user_id}")
            return str(self.user_id)
        else:
            print("[SESSION] No user is logged in.")
            return None

    def getCurrentUsername(self):
        self._load_session_from_file()
        if self.username is not None:
            print(f"[SESSION] Current username: {self.username}")
            return str(self.username)
        else:
            print("[SESSION] No user is logged in.")
            return None

    def _save_session_to_file(self):
        try:
            with open(self.session_file, "wb") as f:
                pickle.dump({"user_id": self.user_id, "username": self.username}, f)
            print(f"[SESSION] Podaci zapisani u {self.session_file}")
        except Exception as e:
            print(f"[SESSION] Greška kod zapisivanja u datoteku: {e}")

    def _load_session_from_file(self):
        if not os.path.exists(self.session_file):
            return
        try:
            with open(self.session_file, "rb") as f:
                data = pickle.load(f)
                self.user_id = data.get("user_id")
                self.username = data.get("username")
        except Exception as e:
            print(f"[SESSION] Greška kod učitavanja iz datoteke: {e}")