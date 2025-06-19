from datetime import datetime
from PyQt6.QtCore import QModelIndex, pyqtSignal, Qt, QTimer, QMetaObject, Q_ARG, pyqtSlot
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic
from Data import database
from Data.Helpers import cryptoFunctions
from Data.userSession import UserSession
from Data.Helpers import XMLoutput

class ChatWindow(QMainWindow):
    newGroupSignal = pyqtSignal()
    openSettingsSignal = pyqtSignal()
    loginSession = UserSession()
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/chatScreen.ui", self)
        print("The UI screen is loaded")

        self.dbManager = database.DatabaseManager.instance() #db connector
        self.chatModel = QStandardItemModel()
        self.contactsModel = QStandardItemModel()
        self.chatView.setModel(self.chatModel)
        self.contactsView.setModel(self.contactsModel)
        self.contactsView.clicked.connect(self.onContactClicked)
        self.pushButton.clicked.connect(self.sendMessage)
        self.searchContacts.textChanged.connect(self.searchForUsers)
        self.openGroup.triggered.connect(self.openNewGroup)
        self.downloadConversation.triggered.connect(self.downloadConversationXML)
        self.openSettings.triggered.connect(self.openSettingsDialog)


    def loadContacts(self):
        print("Try to load the messages on startup")
        currentUserId = self.loginSession.getCurrentId()
        self.dbManager.getContacts(currentUserId, callback=self.fillContactView)

    def fillContactView(self, contacts):
        if contacts is not None:
            self.contacts = contacts
            for name, contact_id in contacts:
                item = QStandardItem(name)
                item.setData(contact_id, Qt.ItemDataRole.UserRole)
                self.contactsModel.appendRow(item)
            print(f"Kontakti su {contacts}")
        else:
            print("Nijedan kontakt nije nađen.")

    def onContactClicked(self, index: QModelIndex):
        selection, selectionId = self.getSelectedContact()
        print(f"seleciton is {selection} and id is {selectionId}")
        if self.dbManager.isGroup(selectionId):
            self.loadGroupChat(selectionId)
        else:
            print(f"The currently selected contact is {selection}")
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
            for message in messages:
                print(f"All messages to add are {messages}")
                userId = message.getSenderId()
                timestamp = message.getTimestamp()
                content = message.getContent()
                def handleUsername(username, ts=timestamp, text=content):
                    formatted_text = f"{username}   {ts}\n{text}\n"
                    item = QStandardItem(formatted_text)
                    self.chatModel.appendRow(item)
                self.dbManager.instance().getUsernameById(userId, callback=handleUsername)

    def sendMessage(self):
        message = self.messageLine.text()
        ID = cryptoFunctions.prepId(message)
        idSender = self.loginSession.getCurrentId()
        receiverUsername, idReceiver = self.getSelectedContact()
        timestamp = datetime.now()
        print("insertat message")
        def onMessageInserted(_):
            if self.dbManager.isGroup(idReceiver):
                QMetaObject.invokeMethod(
                    self,
                    "loadGroupChat",
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(str, idReceiver)
                )
            else:
                QMetaObject.invokeMethod(
                    self,
                    "loadChatsBetweenUsers",
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(str, idSender),
                    Q_ARG(str, idReceiver)
                )

        self.dbManager.insertNewChatMessage(ID, message, idSender, idReceiver, timestamp, callback=onMessageInserted)

    def searchForUsers(self):
        self.contactsModel.clear()
        inputUsername = self.searchContacts.text()
        self.dbManager.getAllContacts(
            self.loginSession.getCurrentId(),
            callback=lambda contacts: self.filterUsers(contacts, inputUsername)
        )

    def filterUsers(self, contacts, inputUsername):
        for username, user_id in contacts:
            if inputUsername.lower() in username.lower():
                item = QStandardItem(username)
                item.setData(user_id, Qt.ItemDataRole.UserRole)
                self.contactsModel.appendRow(item)

    def getSelectedContact(self):
        selection = self.contactsView.selectedIndexes()
        print(f"Selection is {selection}")
        if selection:
            item = self.contactsModel.itemFromIndex(selection[0])
            print(f"Item is {item}")
            contact_id = item.data(Qt.ItemDataRole.UserRole)
            print(f"The contact id is {contact_id}")
            return item.text(), contact_id
        return None  # No selection

    def downloadConversationXML(self):
        selection, selectionId = self.getSelectedContact()
        if self.dbManager.isGroup(selectionId):
            self.dbManager.getGroupMessages(selectionId, callback=self.onMessagesFetched)
        else:
            self.dbManager.getChatMessages(
                self.loginSession.getCurrentId(),
                selectionId,
                callback=self.onMessagesFetched
            )

    def onMessagesFetched(self, messages):
        self.downloadMessagesInXML(messages)
        print(f"The messages are {messages}")

    def downloadMessagesInXML(self, listOfMessages):
        formattedMessages = []
        remaining = len(listOfMessages)

        def onSingleMessageFormatted(msg_dict):
            nonlocal remaining
            formattedMessages.append(msg_dict)
            remaining -= 1
            print(f"Remaining je {remaining}")
            if remaining == 0:
                XMLoutput.save_chat_to_xml(formattedMessages)

        for message in listOfMessages:
            self.message_to_dict(message, callback=onSingleMessageFormatted)


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