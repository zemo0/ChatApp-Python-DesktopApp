from PyQt6.QtCore import QObject, QMutex, QThreadPool, QRunnable, pyqtSlot
import mysql.connector
from mysql.connector import Binary
import sys
from Data.user import User
from Data.message import Message
from Data.chat_group import Chat_group
from Data.Helpers import jsonLogger, cryptoFunctions
import threading
import datetime
sys.stdout.reconfigure(encoding='utf-8')

class DBTask(QRunnable):
    def __init__(self, fn, callback=None, mutex=None):
        super().__init__()
        self.fn = fn
        self.callback = callback
        self.mutex = mutex

    @pyqtSlot()
    def run(self):
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{timestamp}] [DBTask] ID Threada: {threading.get_ident()} | Ime: {threading.current_thread().name}\n")

        result = None
        if self.mutex:
            self.mutex.lock()
        try:
            result = self.fn()
        finally:
            if self.mutex:
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
            print("Creating database connection pool...")
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=4,
                pool_reset_session=True,
                host="localhost",
                user="root",
                password="root",
                database="pythonchatapp"
            )
            print("Connection pool created successfully!")
            jsonLogger.write_log("Connection pool initialized successfully!", "INFO")
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

    def get_connection(self):
        return self.pool.get_connection()

    def runAsync(self, fn, callback=None, use_mutex=False):
        mutex = self.mutex if use_mutex else None
        task = DBTask(fn=fn, callback=callback, mutex=mutex)
        print(f"Thread pool probaj pokrenut task {task.fn}")
        self.threadPool.start(task)

    def getUsersInfo(self, var, callback):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM user")
                result = cursor.fetchall()
                if result:
                    decrypted_result = []
                    for row in result:
                        decrypted_row = list(row)
                        decrypted_row[1] = cryptoFunctions.decryptAES(row[1])  # name
                        decrypted_row[2] = cryptoFunctions.decryptAES(row[2])  # surname
                        decrypted_row[4] = cryptoFunctions.decryptAES(row[4])  # email
                        decrypted_row[5] = cryptoFunctions.decryptAES(row[5])  # username
                        decrypted_row[7] = cryptoFunctions.decryptAES(row[7])  # role
                        decrypted_result.append(tuple(decrypted_row))

                    if var == "nameAndPassword":
                        return [User(*row).getNameAndPassword() for row in decrypted_result]
                    else:
                        return [User(*row).getUsername() for row in decrypted_result]
                return None
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback)

    def getIdByUsername(self, username, callback):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                enc_username = cryptoFunctions.encryptAES(username)
                cursor.execute("SELECT ID FROM user WHERE username = %s", (enc_username,))
                result = cursor.fetchone()
                return result[0] if result else None
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback)

    def getUsernameById(self, id, callback):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT username FROM user WHERE id = %s", (id,))
                result = cursor.fetchone()
                if result:
                    return cryptoFunctions.decryptAES(result[0])
                return None
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback)


    def insertNewUser(self, ID, name, surname, dateOfBirth, email, username, password, role, callback=None):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """INSERT INTO user (ID, name, surname, dateOfBirth, email, username, password, role)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (ID, name, surname, dateOfBirth, email, username, password, role)
                )
                conn.commit()
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback)

    def getAllUsers(self, currentUserId, callback):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT u.username, u.ID FROM user u WHERE u.ID != %s", (currentUserId,))
                result = cursor.fetchall()
                return [(cryptoFunctions.decryptAES(row[0]), row[1]) for row in result] if result else None
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback)

    def getAllContacts(self, currentUserId, callback):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
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
                result = cursor.fetchall()
                print(f"Rezultat getallcontacts je {result}")
                final_result = []
                for row in result:
                    try:
                        decrypted = cryptoFunctions.decryptAES(row[0])
                    except:
                        decrypted = row[0]  # for group names (not encrypted)
                    final_result.append((decrypted, row[1]))
                return final_result if result else None
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback)

    def getContacts(self, userId, callback):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
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
                result = cursor.fetchall()

                final_result = []
                for name, contact_id in result:
                    try:
                        decrypted_name = cryptoFunctions.decryptAES(name)
                    except Exception:
                        decrypted_name = name
                    final_result.append((decrypted_name, contact_id))

                return final_result if final_result else None

            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback)


    def getChatMessages(self, currentUserId, receiverId, callback):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT * FROM message
                    WHERE (IDSender = %s AND IDReceiver = %s) OR (IDSender = %s AND IDReceiver = %s)
                    ORDER BY timestamp ASC;
                """, (currentUserId, receiverId, receiverId, currentUserId))
                result = cursor.fetchall()
                return [Message(*row) for row in result] if result else None
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback)

    def getGroupMessages(self, groupId, callback):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM message WHERE GroupID = %s ORDER BY timestamp ASC;", (groupId,))
                result = cursor.fetchall()
                return [Message(*row) for row in result] if result else None
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback)

    def insertNewChatMessage(self, ID, content, IDSender, whichID, timestamp, attachment=None, attachment_name=None, callback=None):
        def query():
            print("Unutar query za insert msg sam")
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                print("Provjeri je li grupa")
                if self.isGroup(whichID, conn, cursor):
                    print("Prije sendquery sam u grupi")
                    # Grupna poruka
                    sendQuery = """
                        INSERT INTO message
                        (ID, content, IDSender, GroupId, IDReceiver, timestamp, attachment, attachment_name)
                        VALUES (%s, %s, %s, %s, NULL, %s, %s, %s)
                    """
                    print("query unesen, provjeri blob")
                    blob_data = Binary(attachment) if attachment is not None else None
                    attachment_name_data = attachment_name if attachment is not None else None
                    values = (ID, content, IDSender, whichID, timestamp, blob_data, attachment_name_data)
                    print(f"Values is {values}")
                else:
                    # Direktna poruka
                    print("Prije sendquery sam u direktnoj")
                    sendQuery = """
                            INSERT INTO message
                            (ID, content, IDSender, GroupID, IDReceiver, timestamp, attachment, attachment_name)
                            VALUES (%s, %s, %s, NULL, %s, %s, %s, %s)
                        """
                    print("query setiran, probaj blob")
                    blob_data = Binary(attachment) if attachment is not None else None
                    attachment_name_data = attachment_name if attachment is not None else None
                    print("query unesen, provjeri blob")
                    values = (ID, content, IDSender, whichID, timestamp, blob_data, attachment_name_data)
                    print(f"Values is {values}")
                cursor.execute(sendQuery, values)
                conn.commit()
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback, use_mutex=True)

    def isGroup(self, groupID, conn=None, cursor=None):
        # Pošto se poziva na vise mjesta moguce je pozvat funk bez conn i cursora, u tom slucaju se uzima novi mysql conn thread
        own_conn = own_cursor = False
        if conn is None or cursor is None:
            conn = self.get_connection()
            cursor = conn.cursor()
            own_conn = own_cursor = True

        try:
            groupIDsInDB = self.getGroupIdSync(conn, cursor)
            return groupID in groupIDsInDB if groupIDsInDB else False
        finally:
            if own_cursor:
                cursor.close()
            if own_conn:
                conn.close()

    def getGroupIdSync(self, conn=None, cursor=None):
        own_conn = own_cursor = False
        if conn is None or cursor is None:
            conn = self.get_connection()
            cursor = conn.cursor()
            own_conn = own_cursor = True

        try:
            cursor.execute("SELECT ID FROM chat_group")
            result = cursor.fetchall()
            return [row[0] for row in result] if result else None
        finally:
            if own_cursor:
                cursor.close()
            if own_conn:
                conn.close()

    def insertNewGroup(self, id, name, callback=None):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM chat_group WHERE ID = %s", (id,))
                count = cursor.fetchone()[0]
                if count == 0:
                    cursor.execute("INSERT INTO chat_group (ID, name) VALUES (%s, %s)", (id, name))
                    conn.commit()
                else:
                    print(f"[DEBUG] Grupa {id} već postoji — preskačem unos.")
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback, use_mutex=True)

    def insertGroupMember(self, ID, IDGroup, IDUser, callback=None):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO chat_group_members (ID, IDGroup, IDUser) VALUES (%s, %s, %s)", (ID, IDGroup, IDUser))
                conn.commit()
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback, use_mutex=True)

    def getUserRoleById(self, user_id, callback):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT role FROM user WHERE ID = %s", (user_id,))
                result = cursor.fetchone()
                return cryptoFunctions.decryptAES(result[0]) if result else None
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback)

    def getAllUsersFullInfo(self, callback):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                SELECT ID, name, surname, dateOfBirth, email, username, password, role
                FROM user
            """)
                result = cursor.fetchall()
                return [
                    {
                        "ID": row[0],
                        "name": cryptoFunctions.decryptAES(row[1]),
                        "surname": cryptoFunctions.decryptAES(row[2]),
                        "dateOfBirth": row[3],
                        "email": cryptoFunctions.decryptAES(row[4]),
                        "username": cryptoFunctions.decryptAES(row[5]),
                        "password": row[6],
                        "role": cryptoFunctions.decryptAES(row[7])
                    }
                    for row in result
                ] if result else None
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback)

    def getMessageCountByUserId(self, user_id, callback):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM message WHERE IDSender = %s", (user_id,))
                result = cursor.fetchone()
                return result[0] if result else 0
            finally:
                cursor.close()
                conn.close()
        self.runAsync(query, callback)

    def updateUserById(self, user_id, data, callback=None):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            affected = -1
            try:
                fields = ['name', 'surname', 'dateOfBirth', 'email', 'username', 'password', 'role']
                encrypted_values = [
                    cryptoFunctions.encryptAES(data.get('name')),
                    cryptoFunctions.encryptAES(data.get('surname')),
                    data.get('dateOfBirth'),
                    cryptoFunctions.encryptAES(data.get('email')),
                    cryptoFunctions.encryptAES(data.get('username')),
                    data.get('password'),
                    cryptoFunctions.encryptAES(data.get('role'))
                ]
                sql = """
                    UPDATE user SET
                        name = %s,
                        surname = %s,
                        dateOfBirth = %s,
                        email = %s,
                        username = %s,
                        password = %s,
                        role = %s
                    WHERE ID = %s
                """
                cursor.execute(sql, (*encrypted_values, user_id))
                conn.commit()
                affected = cursor.rowcount
            except Exception as e:
                conn.rollback()
                print(f"[DB ERROR] updateUserById: {e}")
            finally:
                cursor.close()
                conn.close()
            return affected
        self.runAsync(query, callback, use_mutex=True)


    def deleteUserById(self, user_id, callback=None):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            affected = -1
            try:
                #mora ic delete poruka radi foreign key constrainta
                cursor.execute("DELETE FROM chat_group_members WHERE IDUser = %s", (user_id,))
                cursor.execute("DELETE FROM message WHERE IDSender = %s OR IDReceiver = %s", (user_id, user_id))
                cursor.execute("DELETE FROM user WHERE ID = %s", (user_id,))
                conn.commit()
                affected = cursor.rowcount
            except Exception as e:
                conn.rollback()
                print(f"[DB ERROR] deleteUserById: {e}")
            finally:
                cursor.close()
                conn.close()
            return affected
        self.runAsync(query, callback, use_mutex=True)

    def updateMessageById(self, message_id, new_content, callback=None):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            affected = -1
            try:
                sql = "UPDATE message SET content = %s WHERE ID = %s"
                cursor.execute(sql, (new_content, message_id))
                conn.commit()
                affected = cursor.rowcount
            except Exception as e:
                conn.rollback()
                print(f"[DB ERROR] updateMessageById: {e}")
            finally:
                cursor.close()
                conn.close()
            return affected
        self.runAsync(query, callback, use_mutex=True)


    def deleteMessageById(self, message_id, callback=None):
        def query():
            conn = self.get_connection()
            cursor = conn.cursor()
            affected = -1
            try:
                cursor.execute("DELETE FROM message WHERE ID = %s", (message_id,))
                conn.commit()
                affected = cursor.rowcount
            except Exception as e:
                conn.rollback()
                print(f"[DB ERROR] deleteMessageById: {e}")
            finally:
                cursor.close()
                conn.close()
            return affected
        self.runAsync(query, callback, use_mutex=True)


    def close(self):
        self.pool = None
        print("Connection pool cleared.")
