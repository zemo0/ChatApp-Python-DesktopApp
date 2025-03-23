from datetime import datetime

from PyQt6.QtCore import QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic
from Data import database
from Data.userSession import UserSession

class ChatWindow(QMainWindow):
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
        self.pushButton.clicked.connect(self.addMessage)

        self.loadContacts()


    def loadContacts(self):
        print("Try to load the messages on startup")
        self.contacts = self.dbManager.getContacts(self.loginSession.user_id)
        for contact in self.contacts:
            item = QStandardItem(contact)
            self.contactsModel.appendRow(item)
        print(f"The contacts are {self.contacts}")

    def addMessage(self, messages):
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

    def onContactClicked(self, index: QModelIndex):
        """Handle item click event"""
        item = self.contactsModel.itemFromIndex(index)
        print(f"Clicked on: {item.text()}")
        receiverId = self.dbManager.getIdByUsername(item.text())
        print(f"Receiver id is {receiverId}, current user is {self.loginSession.user_id}")
        self.loadChatsBetweenUsers(self.loginSession.user_id, receiverId)

    def loadChatsBetweenUsers(self, currentUserId, receiverId):
        messages = self.dbManager.getChatMessages(currentUserId, receiverId)
        self.addMessage(messages)
