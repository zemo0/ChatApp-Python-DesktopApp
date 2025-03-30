import mysql.connector
import sys
from Data.user import User
from Data.message import Message
from Data.chat_group import Chat_group
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

    def getIdByUsername(self, username: str) -> str | None:
        query = "SELECT ID FROM user WHERE username = %s"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()

        if result:
            print(f"Result inside getID is {result}")
            return result[0]
        else:
            return None

    def getUsernameById(self, id: str) -> str | None:
        query = "SELECT username FROM user WHERE id = %s"
        self.cursor.execute(query, (id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def insertNewUser(self, ID, name, surname, dateOfBirth, email, username, password, role):
        query = """INSERT INTO user (ID, name, surname, dateOfBirth, email, username, password, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (ID, name, surname, dateOfBirth, email, username, password, role)
        self.cursor.execute(query, values)
        self.db.commit()

    def getAllContacts(self, currentUserId):
        query = """
            SELECT DISTINCT contact_name,contact_id
            FROM (
                -- Get all users except the current user
                SELECT u.ID AS contact_id, u.username AS contact_name
                FROM user u
                WHERE u.ID != %s
            
                UNION
            
                -- Get all groups
                SELECT g.ID AS contact_id, g.name AS contact_name
                FROM chat_group g
            ) AS contacts;
        """
        self.cursor.execute(query, (currentUserId,))
        result = self.cursor.fetchall()

        if result:
            contacts = [(row[0], row[1]) for row in result]  # Returns a list of tuples (ID, Name)
            print(f"All contacts (users & groups): {contacts}")
            return contacts
        else:
            return None


    def getContacts(self, userId):
        query = """
            SELECT DISTINCT contact_name, contact_id 
            FROM (
                -- Get direct user contacts
                SELECT u.ID AS contact_id, u.username AS contact_name
                FROM message m
                JOIN user u ON (m.IDSender = u.ID AND m.IDReceiver = %s) 
                   OR (m.IDReceiver = u.ID AND m.IDSender = %s)
                WHERE u.ID != %s
        
                UNION
        
                -- Get group chats the user is a part of and has messages
                SELECT g.ID AS contact_id, g.name AS contact_name
                FROM chat_group_members gm
                JOIN chat_group g ON gm.IDGroup = g.ID
                JOIN message m ON m.GroupID = g.ID
                WHERE gm.IDUser = %s
            ) AS contacts;
        """
        self.cursor.execute(query, (userId, userId, userId, userId))
        result = self.cursor.fetchall()

        if result:
            contacts = [(row[0], row[1]) for row in result]  # Returning a list of tuples (ID, Name)
            print(f"Contacts: {contacts}")
            return contacts
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

    def insertNewChatMessage(self, ID, content, IDSender, whichID, timestamp):
        if self.isGroup(whichID):
            self.insertNewGroupMessage(ID, content, IDSender, whichID, timestamp)
        else:
            self.insertNewDirectMessage(ID, content, IDSender, whichID, timestamp)

    def insertNewGroupMessage(self, ID, content, IDSender, GroupID, timestamp):
        query = """
            INSERT INTO message (ID, content, IDSender, GroupId, IDReceiver, timestamp)
            VALUES (%s, %s, %s, %s, NULL, %s)
        """
        values = (ID, content, IDSender, GroupID, timestamp)
        self.cursor.execute(query, values)
        self.db.commit()

    def insertNewDirectMessage(self, ID, content, IDSender, IDReceiver, timestamp):
        query = """
            INSERT INTO message (ID, content, IDSender, GroupId, IDReceiver, timestamp)
            VALUES (%s, %s, %s, NULL, %s, %s)
        """
        values = (ID, content, IDSender, IDReceiver, timestamp)
        print(f"the values to be inserted are {values}")
        self.cursor.execute(query, values)
        self.db.commit()

    def getGroupIds(self):
        query = """
            SELECT ID FROM chat_group
        """
        self.cursor.execute(query)
        result = self.cursor.fetchall()

        if result:
            groups = [Chat_group(*row).getGroupName() for row in result]
            return groups
        else:
            return None

    def isGroup(self, groupID):
        groupIDsInDB = self.getGroupIds()
        if groupIDsInDB is not None and groupID in groupIDsInDB:
            return True
        return False

    def close(self):
        self.cursor.close()
        self.db.close()