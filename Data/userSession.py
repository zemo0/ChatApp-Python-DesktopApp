import os
import pickle #za binary zapis/ispis

class UserSession: #singleton klasa
    _instance = None
    filePath = "Data/Helpers/data.bin"
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserSession, cls).__new__(cls)
            cls._instance.username = None
            cls._instance.user_id = None
        return cls._instance

    def login(self, username, user_id):
            with open(self.filePath, 'wb') as f:
                pickle.dump({
                    'username': username,
                    'user_id': user_id
                }, f)

    def getCurrentId(self):
        if os.path.exists(self.filePath):
            with open(self.filePath, 'rb') as f:
                data = pickle.load(f)
                user_id = data.get('user_id')
                print(f"id is {user_id}")
                return user_id
        else:
            print("No session file found.")

    def getCurrentUsername(self):
        if os.path.exists(self.filePath):
            with open(self.filePath, 'rb') as f:
                data = pickle.load(f)
                username = data.get('username')
                print(f"username is {username}")
                return username
        else:
            print("No session file found.")