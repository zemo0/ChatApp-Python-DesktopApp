from datetime import date
class User:
    def __init__(self, user_id: int, name: str, surname: str, dateOfBirth: date, email: str, username: str, password: str, role: str):
        self.__user_id = user_id
        self.__username = username
        self.__name = name
        self.__surname = surname
        self.__dateOfBirth = dateOfBirth
        self.__email = email
        self.__password = password
        self.__role = role

    def setUserId(self, userId: int):
        self.__userId = userId

    def setUsername(self, username: str):
        self.__username = username

    def setName(self, name: str):
        self.__name = name

    def setSurname(self, surname: str):
        self.__surname = surname

    def setDateOfBirth(self, dateOfBirth: date):
        self.__dateOfBirth = dateOfBirth

    def setEmail(self, email: str):
        self.__email = email

    def setPassword(self, password: str):
        self.__password = password

    def setRole(self, role: str):
        self.__role = role


    def getUserId(self) -> int:
        return self.__userId

    def getUsername(self) -> str:
        return self.__username

    def getName(self) -> str:
        return self.__name

    def getSurname(self) -> str:
        return self.__surname

    def getDateOfBirth(self) -> date:
        return self.__dateOfBirth

    def getEmail(self) -> str:
        return self.__email

    def getPassword(self) -> str:
        return self.__password

    def getRole(self) -> str:
        return self.__role

    def getNameAndPassword(self):
        return self.getUsername(), self.getPassword()

    def __repr__(self):  # For debugging
        return f"User({self.__user_id}, {self.__username}, {self.__name}, {self.__surname}, {self.__address}, {self.__email}, {self.__password})"

    def __str__(self):
        return (f"User ID: {self.user_id}, "
                f"Username: {self.username}, "
                f"Name: {self.name} {self.surname}, "
                f"Address: {self.address}, "
                f"Email: {self.email}")
