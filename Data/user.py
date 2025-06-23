from datetime import date
class User:
    def __init__(self, user_id: str, name: str, surname: str, dateOfBirth: date, email: str, username: str, password: str, role: str):
        self._user_id = user_id
        self._username = username
        self._name = name
        self._surname = surname
        self._dateOfBirth = dateOfBirth
        self._email = email
        self._password = password
        self._role = role

    def setUserId(self, userId): self._user_id = userId
    def setUsername(self, username): self._username = username
    def setName(self, name): self._name = name
    def setSurname(self, surname): self._surname = surname
    def setDateOfBirth(self, dateOfBirth): self._dateOfBirth = dateOfBirth
    def setEmail(self, email): self._email = email
    def setPassword(self, password): self._password = password
    def setRole(self, role): self._role = role

    def getUserId(self): return self._user_id
    def getUsername(self): return self._username
    def getName(self): return self._name
    def getSurname(self): return self._surname
    def getDateOfBirth(self): return self._dateOfBirth
    def getEmail(self): return self._email
    def getPassword(self): return self._password
    def getRole(self): return self._role
    def getNameAndPassword(self): return self._username, self._password

    def __repr__(self):
        return f"User({self._user_id}, {self._username}, {self._name}, {self._surname}, {self.__address}, {self._email}, {self._password})"

    def __str__(self):
        return (f"User ID: {self.user_id}, "
                f"Username: {self.username}, "
                f"Name: {self.name} {self.surname}, "
                f"Address: {self.address}, "
                f"Email: {self.email}")
