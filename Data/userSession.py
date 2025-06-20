class UserSession:  # singleton klasa
    _instance = None

    def __init__(self):
        self.user_id = None
        self.username = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserSession, cls).__new__(cls)
            cls._instance.username = None
            cls._instance.user_id = None
        return cls._instance

    def login(self, username, user_id):
        self.username = username
        self.user_id = user_id
        print(f"[SESSION] Logged in as {username} with ID {user_id}")

    def getCurrentId(self):
        if self.user_id is not None:
            print(f"[SESSION] Current user ID: {self.user_id}")
            return self.user_id
        else:
            print("[SESSION] No user is logged in.")

    def getCurrentUsername(self):
        if self.username is not None:
            print(f"[SESSION] Current username: {self.username}")
            return self.username
        else:
            print("[SESSION] No user is logged in.")
