from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMainWindow, QListView
from PyQt6 import uic
from Data import database
from Data.userSession import UserSession
from Windows.registrationWindow import RegistrationWindow

class ChatWindow(QMainWindow):
    loginSession = UserSession()
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/chatScreen.ui", self)
        print("The UI screen is loaded")

        self.model = QStandardItemModel()
        self.chatView.setModel(self.model)
        self.pushButton.clicked.connect(self.add_item)


    def add_item(self):
        """Adds a new item to the QListView"""
        username = "JohnDoe"
        timestamp = "10:30 AM"
        message = "This is a sample message."
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        formatted_text = f"{username}   {timestamp}\n{message}"
        item = QStandardItem(formatted_text)
        self.model.appendRow(item)

        print(f"Session is {self.loginSession.user_id} and {self.loginSession.username}")
