from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6 import QtWidgets, uic
from Data import database
import sys
from Windows.registrationWindow import RegistrationWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/loginScreen.ui", self)
        print("The UI screen is loaded")

        #spoji UI sa funkcijama
        self.registrationWindow = RegistrationWindow()
        self.linkLabel = self.findChild(QLabel, "linkLabel") #registrationScreen link
        self.linkLabel.setText('<a href="register">linku</a>')
        self.linkLabel.setOpenExternalLinks(False)
        self.errorLabel = self.findChild(QLabel, "errorLabel")
        self.pushButton.clicked.connect(self.onButtonClick) #provjera logina
        self.dbManager = database.DatabaseManager() #db connector

    def onButtonClick(self):
        usernameInput = self.usernameLine.text()
        passwordInput = self.passwordLine.text()
        dbUsers = self.dbManager.getUsersInfo("nameAndPassword")
        if (usernameInput, passwordInput) in dbUsers:
            print("Login checks out, go to mainWindow")
        else:
            print("Login failed, write so out on the screen")
            self.errorLabel.setText("Neuspjesna prijava, probajte ponovno")
