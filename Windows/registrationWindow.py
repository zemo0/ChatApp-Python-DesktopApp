import requests
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6 import QtWidgets, uic

import config
from Data import database
from Data.Helpers import cryptoFunctions
import re


class RegistrationWindow(QMainWindow):
    backToLogin = pyqtSignal()
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/registrationScreen.ui", self)

        #provjera lozinke, postoji li vec username
        self.infoLabel = self.findChild(QLabel, "infoLabel")
        self.infoLabel.setText("")
        self.infoLabel.setStyleSheet("color: red;")
        self.pushButton.clicked.connect(self.onButtonClick) #registracija
        self.navigationButton.clicked.connect(self.onGoBackToLogin)
        self.dbManager = database.DatabaseManager.instance()

    def onButtonClick(self):
        nameInput = self.nameLine.text()
        surnameInput = self.surnameLine.text()
        dateInput = self.dateEdit.date().toString("yyyy-MM-dd")
        emailInput = self.emailLine.text()
        usernameInput = self.usernameLine.text()
        passwordInput = self.passwordLine.text()
        confirmPasswordInput = self.confirmPasswordLine.text()
        roleInput = self.comboBox.currentText()

        def onUsersFetched(usernames):
            if usernames is None:
                usernames = []

            if usernameInput in usernames:
                self.infoLabel.setText("To korisničko ime već postoji, probajte neko drugo")
                print("Korisničko ime već postoji.")
                return
            elif not self.isValidPassword(passwordInput, confirmPasswordInput):
                self.infoLabel.setText("Lozinka nije dobra, mora imati barem 8 znakova, 1 broj i 1 specijalan znak")
                print("Lozinka nije validna.")
                return
            elif not isValidMail(emailInput):
                self.infoLabel.setText("Vaš mail nije validan, unesite neki drugi")
                print("Mail nije validan.")
                return
            else:
                self.infoLabel.setText("")

            storedId = cryptoFunctions.prepId(usernameInput)
            passwordHash = cryptoFunctions.encryptThenHash(passwordInput, usernameInput)

            encryptedName = cryptoFunctions.encryptAES(nameInput)
            encryptedSurname = cryptoFunctions.encryptAES(surnameInput)
            encryptedDate = cryptoFunctions.encryptAES(dateInput)
            encryptedEmail = cryptoFunctions.encryptAES(emailInput)
            encryptedUsername = cryptoFunctions.encryptAES(usernameInput)
            encryptedRole = cryptoFunctions.encryptAES(roleInput)
            def onUserInserted(_):
                print("Registracija korisnika je uspješna!")
                self.nameLine.clear()
                self.surnameLine.clear()
                self.emailLine.clear()
                self.usernameLine.clear()
                self.passwordLine.clear()
                self.confirmPasswordLine.clear()
                self.infoLabel.setText("Registracija korisnika je uspješna, sad se možete ulogirati")
            self.dbManager.insertNewUser(
                storedId,
                encryptedName,
                encryptedSurname,
                encryptedDate,
                encryptedEmail,
                encryptedUsername,
                passwordHash,
                encryptedRole,
                callback=onUserInserted
            )

        self.dbManager.getUsersInfo("username", callback=onUsersFetched)

    def isValidPassword(self, password, confirmPassword):
        pattern = r'^(?=.*[0-9])(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
        if re.match(pattern, password) and len(password) >= 8 and password == confirmPassword:
            return True
        return False

    def onGoBackToLogin(self):
        self.backToLogin.emit()

def isValidMail(mail):
    url = "https://neutrinoapi.net/email-verify"
    data = {
        "user-id": config.NEUTRINO_API_USER_ID,
        "api-key": config.NEUTRINO_API_KEY,
        "email": mail
    }

    try:
        response = requests.post(url, data=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"call proso, rezultat je {result}")
            return result.get("valid", False)
        else:
            print(f"res los response: {response.status_code}")
            return False
    except Exception as e:
        print(f"rest call probo {e}")
        return False

