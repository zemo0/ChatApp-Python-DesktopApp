import os
import pickle
import sys

class UserSession:
    _instance = None

    def __init__(self):
        if UserSession._instance is not None:
            raise Exception("Use UserSession.instance() to get the singleton instance.")
        self.user_id = None
        self.username = None
        self.session_dir = os.path.join(os.path.dirname(__file__), "Helpers", "SessionData")
        #svaki proces ima vlastitu sesiju i vlastite "sessiondata"
        self.session_file = os.path.join(self.session_dir, f"session_{os.getpid()}.bin")
        self.loadSessionData()

        UserSession._instance = self

    @staticmethod
    def instance():
        if UserSession._instance is None:
            UserSession()
        return UserSession._instance

    def setUserID(self, _user_id): self.user_id = _user_id
    def setUsername(self, _username): self.username = _username

    def getUserID(self): return self.user_id
    def getUsername(self): return self.username

    def login(self, username, user_id):
        self.setUsername(username)
        self.setUserID(user_id)
        self.saveSessionData()

    def getCurrentId(self):
        self.loadSessionData()
        return str(self.getUserID()) if self.getUserID() is not None else None

    def getCurrentUsername(self):
        self.loadSessionData()
        return str(self.getUsername()) if self.getUsername() is not None else None

    def saveSessionData(self):
        try:
            with open(self.session_file, "wb") as f:
                pickle.dump({"user_id": self.getUserID(), "username": self.getUsername()}, f)
        except Exception as e:
            print(f"Greška kod zapisivanja usera u datoteku: {e}")

    def loadSessionData(self):
        if not os.path.exists(self.session_file):
            return
        try:
            with open(self.session_file, "rb") as f:
                data = pickle.load(f)
                self.setUserID(data.get("user_id"))
                self.setUsername(data.get("username"))
        except Exception as e:
            print(f"Greška kod učitavanja iz user datoteke: {e}")
