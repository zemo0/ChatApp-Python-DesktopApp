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
        self.dbManager = database.DatabaseManager() #db connector

    def onButtonClick(self):
        usernameInput = self.usernameLine.text()
        passwordInput = self.passwordLine.text()
        dbUsers = self.dbManager.getUsersInfo("nameAndPassword")
        print(f"dbusers are {dbUsers}")
        if (usernameInput, passwordInput) in dbUsers:
            print("Login checks out, go to mainWindow")
            self.loginSession.username = usernameInput
            self.loginSession.user_id = self.dbManager.getIdByUsername(usernameInput)
            print(f"Session values are {self.loginSession.username} and {self.loginSession.user_id}")
            self.loginSuccess.emit()
        else:
            print("Login failed, write so out on the screen")
            self.errorLabel.setText("Neuspjesna prijava, probajte ponovno")
