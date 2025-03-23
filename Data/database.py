import mysql.connector
import sys
from Data.user import User
from Data.message import Message
sys.stdout.reconfigure(encoding='utf-8')

class DatabaseManager:
    def __init__(self):
        try:
            print("Connecting to database...")
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="pythonchatapp"
            )
            print("Try to set the cursor")
            self.cursor = self.db.cursor()
            print("Database connection successful!")

        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            sys.exit(1)

    ###
    ### User functions
    ###
    def getUsersInfo(self, var) -> list[User] | None:
        query = "SELECT * FROM user"
        self.cursor.execute(query)
        result = self.cursor.fetchall()

        if result:
            if var == "nameAndPassword":
                users = [User(*row).getNameAndPassword() for row in result]
            else:
                users = [User(*row).getUsername() for row in result]
            return users
        else:
            return None

    def getUserById(self, user_id: int) -> User | None:
        query = "SELECT ID, username, name, surname, address, email, password FROM user WHERE ID = %s"
        self.cursor.execute(query, (user_id,))
        result = self.cursor.fetchone()

        if result:
            return User(*result).__str__()
        else:
            return None

    def getIdByUsername(self, username: str) -> int | None:
        query = "SELECT ID FROM user WHERE username = %s"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()

        if result:
            print(f"Result inside getID is {result}")
            return result[0]
        else:
            return None

    def getUsernameById(self, id: int) -> str | None:
        query = "SELECT username FROM user WHERE id = %s"
        self.cursor.execute(query, (id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def insertNewUser(self, name, surname, dateOfBirth, email, username, password, role):
        query = """INSERT INTO user (name, surname, dateOfBirth, email, username, password, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (name, surname, dateOfBirth, email, username, password, role)
        self.cursor.execute(query, values)
        self.db.commit()

    def getContacts(self, userId):
        query = """
            SELECT DISTINCT u.username
            FROM message m
            JOIN user u ON (m.IDSender = u.ID AND m.IDReceiver = %s) 
               OR (m.IDReceiver = u.ID AND m.IDSender = %s)
            WHERE u.ID != %s;
        """

        self.cursor.execute(query, (userId, userId, userId))
        result = self.cursor.fetchall()

        if result:
            usernames = [row[0] for row in result]
            print(f"Usernames are {usernames}")
            return usernames
        else:
            return None

    def getChatMessages(self, currentUserId, receiverId):
        query = """
            SELECT *
            FROM message
            WHERE (IDSender = %s AND IDReceiver = %s) 
                OR (IDSender = %s AND IDReceiver = %s)
            ORDER BY timestamp ASC;
        """

        self.cursor.execute(query, (currentUserId, receiverId, receiverId, currentUserId))
        result = self.cursor.fetchall()

        if result:
            messages = [Message(*row) for row in result]
            print(f"messages is {messages}")
            return messages
        else:
            return None

    def close(self):
        self.cursor.close()
        self.db.close()