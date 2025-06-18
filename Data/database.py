from PyQt6.QtCore import QObject, QMutex, QThreadPool, QRunnable, pyqtSlot
import mysql.connector
import sys
from Data.user import User
from Data.message import Message
from Data.chat_group import Chat_group
from Data.Helpers import jsonLogger

sys.stdout.reconfigure(encoding='utf-8')

class DBTask(QRunnable):
    def __init__(self, fn, callback=None, mutex=None):
        super().__init__()
        self.fn = fn
        self.callback = callback
        self.mutex = mutex

    @pyqtSlot()
    def run(self):
        result = None
        if self.mutex:
            print("Mutex is locked")
            self.mutex.lock()
        try:
            result = self.fn()
        finally:
            if self.mutex:
                print("Mutex is unlocked")
                self.mutex.unlock()

        if self.callback:
            self.callback(result)

class DatabaseManager(QObject):
    _instance = None

    def __init__(self):
        super().__init__()
        if DatabaseManager._instance is not None:
            raise Exception("Use DatabaseManager.instance()")

        try:
            print("Connecting to database...")
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="pythonchatapp"
            )
            self.cursor = self.db.cursor()
            print("Database connection successful!")
            jsonLogger.write_log("Connection to database is successful!", "INFO")
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            sys.exit(1)

        self.mutex = QMutex()
        self.threadPool = QThreadPool()
        self.threadPool.setMaxThreadCount(4)
        DatabaseManager._instance = self

    @staticmethod
    def instance():
        if DatabaseManager._instance is None:
            DatabaseManager()
        return DatabaseManager._instance

    def runAsync(self, fn, callback=None):
        task = DBTask(fn=fn, callback=callback, mutex=self.mutex)
        self.threadPool.start(task)

    def getUsersInfo(self, var, callback):
        def query():
            self.cursor.execute("SELECT * FROM user")
            result = self.cursor.fetchall()
            if result:
                if var == "nameAndPassword":
                    return [User(*row).getNameAndPassword() for row in result]
                else:
                    return [User(*row).getUsername() for row in result]
            return None
        self.runAsync(query, callback)

    def getIdByUsername(self, username, callback):
        def query():
            self.cursor.execute("SELECT ID FROM user WHERE username = %s", (username,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        self.runAsync(query, callback)

    def getUsernameById(self, id, callback):
        def query():
            self.cursor.execute("SELECT username FROM user WHERE id = %s", (id,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        self.runAsync(query, callback)

    def insertNewUser(self, ID, name, surname, dateOfBirth, email, username, password, role, callback=None):
        def query():
            self.cursor.execute(
                """INSERT INTO user (ID, name, surname, dateOfBirth, email, username, password, role)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (ID, name, surname, dateOfBirth, email, username, password, role)
            )
            self.db.commit()
        self.runAsync(query, callback)

    def getAllUsers(self, currentUserId, callback):
        def query():
            self.cursor.execute("SELECT u.username, u.ID FROM user u WHERE u.ID != %s", (currentUserId,))
            result = self.cursor.fetchall()
            return [(row[0], row[1]) for row in result] if result else None
        self.runAsync(query, callback)

    def getAllContacts(self, currentUserId, callback):
        def query():
            self.cursor.execute("""
                SELECT DISTINCT contact_name,contact_id
                FROM (
                    SELECT u.ID AS contact_id, u.username AS contact_name
                    FROM user u
                    WHERE u.ID != %s
                    UNION
                    SELECT g.ID AS contact_id, g.name AS contact_name
                    FROM chat_group g
                ) AS contacts;
            """, (currentUserId,))
            result = self.cursor.fetchall()
            return [(row[0], row[1]) for row in result] if result else None
        self.runAsync(query, callback)

    def getContacts(self, userId, callback):
        def query():
            self.cursor.execute("""
                SELECT DISTINCT * FROM (
                    SELECT DISTINCT u.username, u.ID
                    FROM message m
                    JOIN user u ON (m.IDSender = u.ID AND m.IDReceiver = %s) OR (m.IDReceiver = u.ID AND m.IDSender = %s)
                    WHERE u.ID != %s
                    UNION
                    SELECT chat_group.name, chat_group.ID
                    FROM chat_group_members
                    JOIN chat_group ON chat_group_members.IDGroup = chat_group.ID
                    JOIN message ON chat_group.ID = message.GroupID
                    WHERE chat_group_members.IDUser = %s
                ) AS contacts;
            """, (userId, userId, userId, userId))
            result = self.cursor.fetchall()
            return [(row[0], row[1]) for row in result] if result else None
        self.runAsync(query, callback)

    def getChatMessages(self, currentUserId, receiverId, callback):
        def query():
            self.cursor.execute("""
                SELECT * FROM message
                WHERE (IDSender = %s AND IDReceiver = %s) OR (IDSender = %s AND IDReceiver = %s)
                ORDER BY timestamp ASC;
            """, (currentUserId, receiverId, receiverId, currentUserId))
            result = self.cursor.fetchall()
            return [Message(*row) for row in result] if result else None
        self.runAsync(query, callback)

    def getGroupMessages(self, groupId, callback):
        def query():
            self.cursor.execute("SELECT * FROM message WHERE GroupID = %s ORDER BY timestamp ASC;", (groupId,))
            result = self.cursor.fetchall()
            return [Message(*row) for row in result] if result else None
        self.runAsync(query, callback)

    def insertNewChatMessage(self, ID, content, IDSender, whichID, timestamp, callback=None):
        def query():
            if self.isGroup(whichID):
                self.insertNewGroupMessage(ID, content, IDSender, whichID, timestamp)
            else:
                self.insertNewDirectMessage(ID, content, IDSender, whichID, timestamp)
        self.runAsync(query, callback)

    def insertNewGroupMessage(self, ID, content, IDSender, GroupID, timestamp):
        self.cursor.execute("""
            INSERT INTO message (ID, content, IDSender, GroupId, IDReceiver, timestamp)
            VALUES (%s, %s, %s, %s, NULL, %s)
        """, (ID, content, IDSender, GroupID, timestamp))
        self.db.commit()

    def insertNewDirectMessage(self, ID, content, IDSender, IDReceiver, timestamp):
        self.cursor.execute("""
            INSERT INTO message (ID, content, IDSender, GroupId, IDReceiver, timestamp)
            VALUES (%s, %s, %s, NULL, %s, %s)
        """, (ID, content, IDSender, IDReceiver, timestamp))
        self.db.commit()

    def isGroup(self, groupID):
        groupIDsInDB = self.getGroupIdSync()
        return groupID in groupIDsInDB if groupIDsInDB else False

    def getGroupIdSync(self):
        self.cursor.execute("SELECT ID FROM chat_group")
        result = self.cursor.fetchall()
        return [row[0] for row in result] if result else None

    def insertNewGroup(self, id, name, callback=None):
        def query():
            self.cursor.execute("INSERT INTO chat_group (ID, name) VALUES (%s, %s)", (id, name))
            self.db.commit()
        self.runAsync(query, callback)

    def insertGroupMember(self, ID, IDGroup, IDUser, callback=None):
        def query():
            self.cursor.execute("INSERT INTO chat_group_members (ID, IDGroup, IDUser) VALUES (%s, %s, %s)", (ID, IDGroup, IDUser))
            self.db.commit()
        self.runAsync(query, callback)

    def close(self):
        self.cursor.close()
        self.db.close()
