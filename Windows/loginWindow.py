import requests
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

        try:
            response = requests.post("http://localhost:5000/api/login", json={
                "username": usernameInput,
                "password": passwordInput
            })

            if response.status_code == 200:
                print("Login uspješan")
                self.dbManager.getIdByUsername(usernameInput, callback=lambda userId: self.finishLogin(usernameInput, userId))
            else:
                print("Login neuspješan")
                self.errorLabel.setText("Neuspješna prijava, probajte ponovno")

        except Exception as e:
            print("Greška pri spajanju na server:", e)

    def finishLogin(self, username, userId):
        self.loginSession.login(username, userId)
        self.loginSuccess.emit()