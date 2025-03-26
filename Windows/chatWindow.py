from datetime import datetime
from PyQt6.QtCore import QModelIndex, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic
from Data import database
from Data.userSession import UserSession

class ChatWindow(QMainWindow):
    newGroupSignal = pyqtSignal()
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
        self.addGroup.triggered.connect(self.addNewGroup)


    def loadContacts(self):
        print("Try to load the messages on startup")
        self.contacts = self.dbManager.getContacts(self.loginSession.user_id)
        if self.loginSession.user_id is not None:
            for contact in self.contacts:
                item = QStandardItem(contact)
                self.contactsModel.appendRow(item)
            print(f"The contacts are {self.contacts}")

    def onContactClicked(self, index: QModelIndex):
        """Handle item click event"""
        selection = self.getSelectedContact()
        print(f"The currently selected contact is {selection}")
        self.loadChatsBetweenUsers(self.loginSession.user_id, self.dbManager.getIdByUsername(selection))

    def loadChatsBetweenUsers(self, currentUserId, receiverId):
        messages = self.dbManager.getChatMessages(currentUserId, receiverId)
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
        idSender = self.loginSession.user_id
        receiverUsername = self.getSelectedContact()
        idReceiver = self.dbManager.getIdByUsername(receiverUsername)
        timestamp = datetime.now()
        print(f"The full data sent to the database is {message}, {idSender}, {idReceiver}, {timestamp}")
        self.dbManager.insertNewMessage(message, idSender, idReceiver, timestamp)

    def searchForUsers(self):
        self.contactsModel.clear()
        inputUsername = self.searchContacts.text()
        self.contacts = self.dbManager.getContacts(self.loginSession.user_id)
        for contact in self.contacts:
            if inputUsername in contact:
                item = QStandardItem(contact)
                self.contactsModel.appendRow(item)

    def getSelectedContact(self):
        selection = self.contactsView.selectedIndexes()
        if selection:
            item = self.contactsModel.itemFromIndex(selection[0])
            return item.text()
        return None  # No selection

    def addNewGroup(self):
        self.newGroupSignal.emit()
