class UserSession: #singleton klasa
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserSession, cls).__new__(cls)
            cls._instance.username = None
            cls._instance.user_id = None
            cls._instance.is_logged_in = False
        return cls._instance

    def login(self, username, user_id):
        self.username = username
        self.user_id = user_id
        self.is_logged_in = True

    def logout(self):
        self.username = None
        self.user_id = None
        self.is_logged_in = False