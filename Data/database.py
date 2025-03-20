import mysql.connector
import sys
from Data.user import User
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

    def insertNewUser(self, name, surname, dateOfBirth, email, username, password, role):
        query = """INSERT INTO user (name, surname, dateOfBirth, email, username, password, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (name, surname, dateOfBirth, email, username, password, role)
        self.cursor.execute(query, values)
        self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()