class User:
    def __init__(self, user_id: int, username: str, name: str, surname: str, address: str, email: str, password: str):
        self.__user_id = user_id
        self.__username = username
        self.__name = name
        self.__surname = surname
        self.__address = address
        self.__email = email
        self.__password = password

    def set_user_id(self, user_id: int):
        self.__user_id = user_id

    def set_username(self, username: str):
        self.__username = username

    def set_name(self, name: str):
        self.__name = name

    def set_surname(self, surname: str):
        self.__surname = surname

    def set_address(self, address: str):
        self.__address = address

    def set_email(self, email: str):
        self.__email = email

    def set_password(self, password: str):
        self.__password = password


    def get_user_id(self) -> int:
        return self.__user_id

    def get_username(self) -> str:
        return self.__username

    def get_name(self) -> str:
        return self.__name

    def get_surname(self) -> str:
        return self.__surname

    def get_address(self) -> str:
        return self.__address

    def get_email(self) -> str:
        return self.__email

    def get_password(self) -> str:
        return self.__password
