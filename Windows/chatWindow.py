from datetime import datetime
from PyQt6.QtCore import QModelIndex, pyqtSignal, Qt
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

        self.dbManager = database.DatabaseManager() #db connector
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
        self.contacts = self.dbManager.getContacts(self.loginSession.user_id)
        print(f"current user is {self.loginSession.user_id} and {self.loginSession.username}")
        if self.contacts is not None:
            for contact in self.contacts:
                name, contact_id = contact
                item = QStandardItem(name)
                item.setData(contact_id, Qt.ItemDataRole.UserRole)
                self.contactsModel.appendRow(item)
            print(f"The contacts are {self.contacts}")

    def onContactClicked(self, index: QModelIndex):
        """Handle item click event"""
        selection, selectionId = self.getSelectedContact()
        print(f"seleciton is {selection} and id is {selectionId}")
        if self.dbManager.isGroup(selectionId):
            self.loadGroupChat(selectionId)
        else:
            print(f"The currently selected contact is {selection}")
            self.loadChatsBetweenUsers(self.loginSession.user_id, selectionId)

    def loadGroupChat(self, groupId):
        messages = self.dbManager.getGroupMessages(groupId)
        if messages is not None:
            self.addMessageToChat(messages)

    def loadChatsBetweenUsers(self, currentUserId, receiverId):
        messages = self.dbManager.getChatMessages(currentUserId, receiverId)
        if messages is not None:
            self.addMessageToChat(messages)

    def addMessageToChat(self, messages):
        """Adds a new item to the QListView"""
        self.chatModel.clear()
        for message in messages:
            userId = message.getSenderId()
            username = self.dbManager.getUsernameById(userId)
            timestamp = message.getTimestamp()
            content = message.getContent()
            formatted_text = f"{username}   {timestamp}\n{content}\n"
            item = QStandardItem(formatted_text)
            self.chatModel.appendRow(item)

    def sendMessage(self):
        message = self.messageLine.text()
        ID = cryptoFunctions.prepId(message)
        idSender = self.loginSession.user_id
        receiverUsername, idReceiver = self.getSelectedContact()
        timestamp = datetime.now()
        self.dbManager.insertNewChatMessage(ID, message, idSender, idReceiver, timestamp)
        self.loadChatsBetweenUsers(self.loginSession.user_id, idReceiver)
        print(f"The full data sent to the database is {message}, {idSender}, {idReceiver}, {timestamp}")


    def searchForUsers(self):
        self.contactsModel.clear()
        inputUsername = self.searchContacts.text()
        self.contacts = self.dbManager.getAllContacts(self.loginSession.user_id)
        for contact in self.contacts:
            username, user_id = contact
            if inputUsername in username:
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
            messages = self.dbManager.getGroupMessages(selectionId)
            self.downloadMessagesInXML(messages)
            print(f"The messages are {messages}")
        else:
            messages = self.dbManager.getChatMessages(self.loginSession.user_id, selectionId)
            self.downloadMessagesInXML(messages)
            print(f"The messages are {messages}")

    def downloadMessagesInXML(self, listOfMessages):
        formattedMessages = []
        for message in listOfMessages:
            formattedMessages.append(self.message_to_dict(message))
        XMLoutput.save_chat_to_xml(formattedMessages)

    def message_to_dict(self, messageObject):
        return {
            "sender": self.dbManager.getUsernameById(messageObject.getSenderId()),
            "timestamp": messageObject.getTimestamp().isoformat(),
            "content": messageObject.getContent()
        }

    def openNewGroup(self):
        self.newGroupSignal.emit()

    def openSettingsDialog(self):
        self.openSettingsSignal.emit()