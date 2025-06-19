from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from Data import database
from Data.userSession import UserSession
from Windows.registrationWindow import RegistrationWindow

class LoginWindow(QMainWindow):
    loginSuccess = pyqtSignal()
    loginSession = UserSession()
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
        self.dbManager = database.DatabaseManager.instance() #db connector

    def onButtonClick(self):
        usernameInput = self.usernameLine.text()
        passwordInput = self.passwordLine.text()
        self.dbManager.getUsersInfo("nameAndPassword", callback=lambda users: self.handleLogin(users, usernameInput, passwordInput))

    def handleLogin(self, dbUsers, usernameInput, passwordInput):
        print(f"korisnici su {dbUsers}")
        if (usernameInput, passwordInput) in dbUsers:
            print("Dobar login, ide u chat")
            self.dbManager.getIdByUsername(usernameInput, callback=lambda userId: self.finishLogin(usernameInput, userId))
        else:
            print("Loš login")
            self.errorLabel.setText("Neuspješna prijava, probajte ponovno")

    def finishLogin(self, username, userId):
        self.loginSession.login(username, userId)
        self.loginSuccess.emit()