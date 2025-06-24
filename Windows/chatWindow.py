import base64
import json
import os
import socket
import subprocess
import threading
from datetime import datetime
import requests
from PyQt6.QtCore import QModelIndex, pyqtSignal, Qt, QTimer, QMetaObject, Q_ARG, pyqtSlot, QUrl
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QDesktopServices, QAction
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QInputDialog, QMessageBox
from PyQt6 import uic
from Data import database
from Data.Helpers import cryptoFunctions, jsonLogger
from Data.userSession import UserSession
from Data.Helpers import XMLBlacklist
from Windows.adminWindow import AdminWindow

class ChatWindow(QMainWindow):
    newGroupSignal = pyqtSignal()
    openSettingsSignal = pyqtSignal()
    loginSession = UserSession.instance()
    def __init__(self):
        super().__init__()
        self.adminAction = None
        self.fileMenu = None
        self.menubar = None
        self.tcp_socket = None
        uic.loadUi("UI/chatScreen.ui", self)
        print("The UI screen is loaded")
        self.udp_port = 9030
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dbManager = database.DatabaseManager.instance() #db connector
        self.chatModel = QStandardItemModel()
        self.contactsModel = QStandardItemModel()
        self.selectedAttachment = None
        self.toolButton.clicked.connect(self.selectAttachment)
        self.chatView.setModel(self.chatModel)
        self.chatView.clicked.connect(self.onChatItemClicked)
        self.contactsView.setModel(self.contactsModel)
        self.contactsView.clicked.connect(self.onContactClicked)
        self.pushButton.clicked.connect(self.sendMessage)
        self.searchContacts.textChanged.connect(self.searchForUsers)
        self.openGroup.triggered.connect(self.openNewGroup)
        self.openSettings.triggered.connect(self.openSettingsDialog)
        self.chatView.doubleClicked.connect(self.onMessageDoubleClicked)

    ####################################
    ### TCP za poruke, UDP za status ###
    ####################################
    def connectToTCPServer(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect(("127.0.0.1", 9010))
        self.tcp_socket.sendall((
                json.dumps({
                    'type': 'register',
                    'user_id': self.loginSession.getCurrentId()
                }) + "\n"
        ).encode('utf-8'))

        threading.Thread(target=self.startTCPListener, daemon=True).start()

    def startTCPListener(self):
        while True:
            try:
                data = self.tcp_socket.recv(4096).decode('utf-8')
                if data:
                    msg = json.loads(data)
                    if msg['type'] == 'new_message':
                        sender_id = msg['from']
                        my_id = self.loginSession.getCurrentId()
                        _, selected_contact = self.getSelectedContact()
                        if selected_contact == sender_id:
                            QMetaObject.invokeMethod(
                                self,
                                "loadChatsBetweenUsers",
                                Qt.ConnectionType.QueuedConnection,
                                Q_ARG(str, my_id),
                                Q_ARG(str, sender_id)
                            )
            except Exception as e:
                print(f"[TCP Listener] Error je {e}")
                break

    def startUdpListener(self):
        def listen():
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            listen_socket.bind(("0.0.0.0", 0))
            self.udp_socket = listen_socket
            print(f"[UDP Listener] Klijent osluškuje na portu {listen_socket.getsockname()[1]}")
            self.notifyServerOnlineUDP()
            self.fetchOnlineUsersUDP()
            QMetaObject.invokeMethod(
                self,
                "loadContacts",
                Qt.ConnectionType.QueuedConnection
            )
            while True:
                try:
                    data, _ = listen_socket.recvfrom(1024)
                    msg = data.decode()
                    if msg.startswith("ONLINE:"):
                        user_id = msg.split(":", 1)[1]
                        print(f"[INFO] {user_id} je online")
                        self.onlineUsers.add(user_id)

                    elif msg.startswith("OFFLINE:"):
                        user_id = msg.split(":", 1)[1]
                        print(f"[INFO] {user_id} je offline")
                        self.onlineUsers.discard(user_id)

                    QMetaObject.invokeMethod(
                        self,
                        "loadContacts",
                        Qt.ConnectionType.QueuedConnection
                    )
                except socket.timeout:
                    # nije problem, nastavi dalje slušat
                    continue
                except Exception as e:
                    print(f"UDP listener baci exception: {e}")
                    continue
        threading.Thread(target=listen, daemon=True).start()

    def notifyServerOnlineUDP(self):
        user_id = self.loginSession.getCurrentId()
        message = f"ONLINE:{user_id}".encode()
        self.udp_socket.sendto(message, ("localhost", self.udp_port))

    def notifyServerOfflineUDP(self):
        user_id = self.loginSession.getCurrentId()
        message = f"OFFLINE:{user_id}".encode()
        self.udp_socket.sendto(message, ("localhost", self.udp_port))

    def fetchOnlineUsersUDP(self):
        try:
            self.udp_socket.sendto("LIST_ONLINE".encode(), ("localhost", self.udp_port))
            #ako ne dode odgovor za 2 sekunde timeout
            self.udp_socket.settimeout(2.0)
            data, _ = self.udp_socket.recvfrom(4096)
            user_list = data.decode().split(",") if data else []
            self.onlineUsers = set(user_list)
            print(f"[UDP Listener] Online korisnici: {self.onlineUsers}")
        except Exception as e:
            print(f"[UDP Listener] Greška kod dohvaćanja online korisnika: {e}")

    @pyqtSlot()
    def loadContacts(self):
        currentUserId = self.loginSession.getCurrentId()
        self.dbManager.getContacts(currentUserId, callback=self.fillContactView)

    def fillContactView(self, contacts):
        self.contactsModel.clear()
        if contacts is not None:
            self.contacts = contacts
            for name, contact_id in contacts:
                print(f"Svi online kontakti su {self.onlineUsers}")
                is_online = contact_id in self.onlineUsers
                display_name = f"{name} {'🟢' if is_online else '🔴'}"
                item = QStandardItem(display_name)
                item.setData(contact_id, Qt.ItemDataRole.UserRole)
                self.contactsModel.appendRow(item)
            print(f"Kontakti su {contacts}")
        else:
            print("Nijedan kontakt nije nađen.")

    def onContactClicked(self, index: QModelIndex):
        selection, selectionId = self.getSelectedContact()
        if self.dbManager.isGroup(selectionId):
            self.loadGroupChat(selectionId)
        else:
            self.loadChatsBetweenUsers(self.loginSession.getCurrentId(), selectionId)

    @pyqtSlot(str)
    def loadGroupChat(self, groupId):
        def onMessagesFetched(messages):
            if messages is not None:
                self.addMessageToChat(messages)
        self.dbManager.getGroupMessages(groupId, callback=onMessagesFetched)

    @pyqtSlot(str, str)
    def loadChatsBetweenUsers(self, currentUserId, receiverId):
        self.dbManager.instance().getChatMessages(currentUserId, receiverId, callback=self.addMessageToChat)

    def addMessageToChat(self, messages):
        if messages is not None:
            self.chatModel.clear()
            def onUsernamesFetched(user_map):
                messages.sort(key=lambda m: m.getTimestamp())

                for message in messages:
                    message_id = message.getId()
                    userId = message.getSenderId()
                    timestamp = message.getTimestamp()
                    content = message.getContent()
                    attachment = message.getAttachment()
                    attachment_name = message.getAttachmentName()
                    username = user_map.get(userId, "Nepoznat")

                    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    formatted_text = f"{username}   {formatted_time}\n{content}\n"

                    item = QStandardItem(formatted_text)
                    item.setData(message_id, Qt.ItemDataRole.UserRole)

                    if attachment and attachment_name:
                        os.makedirs("downloads", exist_ok=True)
                        save_path = os.path.join("downloads", attachment_name)
                        with open(save_path, 'wb') as f:
                            f.write(attachment)
                        formatted_text += f"[📎 {attachment_name}]\n"
                        item.setText(formatted_text)
                        item.setData(save_path, Qt.ItemDataRole.UserRole + 1)
                    self.chatModel.appendRow(item)
            self.dbManager.instance().getAllUsernames(callback=onUsernamesFetched)

    def sendMessage(self):
        message = self.messageLine.text()
        ID = cryptoFunctions.prepId(message)
        idSender = self.loginSession.getCurrentId()
        receiverUsername, idReceiver = self.getSelectedContact()
        timestamp = datetime.now()

        script_path = os.path.abspath(os.path.join("Data", "Helpers", "checkBlacklistedWordsProcess.py"))
        print("Pozovi blacklist za provjeru")
        command = f'python "{script_path}" "{message}"'

        check = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        if check.returncode != 0:
            QMessageBox.warning(self, "Upozorenje", "Poruka sadrži nedozvoljene riječi i nije poslana.")
            return

        print("Poruka nema blacklistanih rijeci, idi dalje")
        attachment_data = None
        attachment_name = None
        print("Unutar send messagea sam")
        if self.selectedAttachment:
            print("unutar if za attachement sam")
            path, name = self.selectedAttachment
            print(f"Path je {path} i ime je {name}")
            try:
                with open(path, 'rb') as f:
                    raw_attachment_data = f.read()
                    attachment_size = len(raw_attachment_data)
                    attachment_name = name
                    message = message.replace(f"📎 {name}", "").strip()
            except Exception as e:
                print(f"Ne mogu učitati privitak: {e}")
                self.selectedAttachment = None
        else:
            raw_attachment_data = False
            attachment_size = 0
            attachment_name = ""
        print(f"Dosao do payloada, attachementdata je {attachment_data} i ime je {attachment_name}")
        payload = {
            'type': 'chat_message',
            'message_id': ID,
            'from': idSender,
            'to': idReceiver,
            'content': message,
            'timestamp': timestamp.isoformat(),
            'has_attachment': bool(raw_attachment_data),
            'attachment_name': attachment_name,
            'attachment_size': attachment_size
        }
        print("Ovo je nakon payloda")
        try:
            print("Probaj poslat json")
            self.tcp_socket.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            print("Json poslan")
            if raw_attachment_data:
                print("Pouruka ima attachement, poslaji")
                self.tcp_socket.sendall(raw_attachment_data)
                print("Poslan je attachment")
            self.messageLine.clear()
            self.selectedAttachment = None
            QTimer.singleShot(1000, lambda: self.reloadChat())
        except Exception as e:
            print(f"greška kod slanja poruke, {e}")

    def searchForUsers(self):
        self.contactsModel.clear()
        inputUsername = self.searchContacts.text()
        self.dbManager.getAllContacts(
            self.loginSession.getCurrentId(),
            callback=lambda contacts: self.filterUsers(contacts, inputUsername)
        )

    def filterUsers(self, contacts, inputUsername):
        if inputUsername == "":
            self.loadContacts()
        else:
            for username, user_id in contacts:
                if inputUsername.lower() in username.lower():
                    item = QStandardItem(username)
                    item.setData(user_id, Qt.ItemDataRole.UserRole)
                    self.contactsModel.appendRow(item)

    def getSelectedContact(self):
        selection = self.contactsView.selectedIndexes()
        if selection:
            item = self.contactsModel.itemFromIndex(selection[0])
            contact_id = item.data(Qt.ItemDataRole.UserRole)
            return item.text(), contact_id
        return None

    def message_to_dict(self, messageObject, callback):
        def onUsernameReceived(username):
            result = {
                "sender": username,
                "timestamp": messageObject.getTimestamp().isoformat(),
                "content": messageObject.getContent()
            }
            callback(result)

        self.dbManager.getUsernameById(messageObject.getSenderId(), callback=onUsernameReceived)

    def openNewGroup(self):
        self.newGroupSignal.emit()

    def openSettingsDialog(self):
        self.openSettingsSignal.emit()

    def selectAttachment(self):
        print("priložen je attachement ")
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Odaberi datoteku")
        if file_path:
            self.selectedAttachment = (file_path, os.path.basename(file_path))
            existing = self.messageLine.text()
            self.messageLine.setText(f"{existing} 📎 {os.path.basename(file_path)}")
        else:
            self.selectedAttachment = None

    def onChatItemClicked(self, index):
        print("Stisnut je attachement u chatu")
        path = index.data(Qt.ItemDataRole.UserRole + 1)
        if path and os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def triggerAdminCheck(self):
        user_id = self.loginSession.getCurrentId()
        try:
            response = requests.get("http://localhost:5000/api/get_role", params={"user_id": user_id})
            if response.status_code == 200:
                role = response.json().get("role")
                self.handleRoleCheck(role)
            else:
                print("Greška kod provjere role:", response.text)
        except Exception as e:
            print("Pogreška pri spajanju na server:", e)

    def handleRoleCheck(self, role):
        if role == "Admin":
            self.adminMenu = self.menubar.addMenu("Admin")
            self.adminAction = QAction("Admin Panel", self)
            self.adminAction.triggered.connect(self.showAdminTab)
            self.adminMenu.addAction(self.adminAction)

    def showAdminTab(self):
        print("Admin tab bi se sada otvorio..")
        self.adminWindow = AdminWindow(self)
        self.adminWindow.show()

    def onMessageDoubleClicked(self, index: QModelIndex):
        item = self.chatModel.itemFromIndex(index)
        message_id = item.data(Qt.ItemDataRole.UserRole)
        parts = item.text().split("\n")
        if len(parts) < 2:
            return
        original_text = parts[1].strip()

        new_text, ok = QInputDialog.getText(
            self, "Uredi poruku", "Nova verzija poruke:", text=original_text
        )
        if not ok:
            return

        new_text = new_text.strip()
        if new_text == "":
            try:
                response = requests.delete(f"http://localhost:5000/api/delete_message/{message_id}")
                if response.status_code == 200:
                    print("obrisana je poruka")
                else:
                    print(f" Greška : {response.text}")
            except Exception as e:
                print(f"Greška kod pristupa TCP serveru: {e}")
        elif new_text != original_text:
            try:
                response = requests.put(
                    f"http://localhost:5000/api/update_message/{message_id}",
                    json={"content": new_text}
                )
                if response.status_code == 200:
                    print("editana je poruka")
                else:
                    print(f"Greška: {response.text}")
            except Exception as e:
                print(f" {e}")
        else:
            print("poruka ostala ista")
            return
        QTimer.singleShot(500, lambda: QMetaObject.invokeMethod(
            self, "reloadChat", Qt.ConnectionType.QueuedConnection
        ))

    @pyqtSlot()
    def reloadChat(self):
        selection, selectionId = self.getSelectedContact()
        if self.dbManager.isGroup(selectionId):
            self.loadGroupChat(selectionId)
        else:
            self.loadChatsBetweenUsers(self.loginSession.getCurrentId(), selectionId)

    def closeEvent(self, event):
        self.notifyServerOfflineUDP()
        super().closeEvent(event)