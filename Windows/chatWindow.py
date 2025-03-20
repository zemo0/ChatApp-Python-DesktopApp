from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6 import uic
from Data import database
from Windows.registrationWindow import RegistrationWindow

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/chatScreen.ui", self)
        print("The UI screen is loaded")