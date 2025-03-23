from datetime import datetime
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
        self.pushButton.clicked.connect(self.add_item)

        self.loadMessages()


    def loadMessages(self):
        print("Try to load the messages on startup")
        self.messages = self.dbManager.getMessages(self.loginSession.user_id)
        for message in self.messages:
            item = QStandardItem(message)
            self.contactsModel.appendRow(item)
        print(f"The messages are {self.messages}")

    def add_item(self):
        """Adds a new item to the QListView"""
        username = "JohnDoe"
        timestamp = "10:30 AM"
        message = "This is a sample message."
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        formatted_text = f"{username}   {timestamp}\n{message}"
        item = QStandardItem(formatted_text)
        self.chatModel.appendRow(item)

        print(f"Session is {self.loginSession.user_id} and {self.loginSession.username}")
