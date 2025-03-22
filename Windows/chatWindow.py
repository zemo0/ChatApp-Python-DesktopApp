from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QMainWindow, QListView
from PyQt6 import uic
from Data import database
from Windows.registrationWindow import RegistrationWindow

class ChatWindow(QMainWindow):
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

        # Format using HTML (with bold username, gray timestamp, and message on a new line)
        formatted_text = f"<b>{username}</b> <span style='color:gray;'>({timestamp})</span><br>{message}"

        # Create item and set the formatted HTML text using setData
        item = QStandardItem()
        item.setData(formatted_text, Qt.DisplayRole)  # Use Qt.DisplayRole for rich text rendering

        # Add the item to the model
        self.model.appendRow(item)

        # Add the item to the model
        self.model.appendRow(item)
