from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6 import QtWidgets, uic
from Data import database
from Data.Helpers import cryptoFunctions
import re

class RegistrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/registrationScreen.ui", self)

        #provjera lozinke, postoji li vec username
        print("The UI screen is loaded")
        self.infoLabel = self.findChild(QLabel, "infoLabel")
        self.infoLabel.setText("")
        self.infoLabel.setStyleSheet("color: red;")
        self.pushButton.clicked.connect(self.onButtonClick) #registracija
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
            else:
                self.infoLabel.setText("")

            storedId = cryptoFunctions.prepId(usernameInput)
            passwordHash = cryptoFunctions.encryptThenHash(passwordInput, usernameInput)
            def onUserInserted(_):
                print("Registracija korisnika je uspješna!")

            self.dbManager.insertNewUser(
                storedId, nameInput, surnameInput, dateInput, emailInput,
                usernameInput, passwordHash, roleInput, callback=onUserInserted
            )

        self.dbManager.getUsersInfo("username", callback=onUsersFetched)

    def isValidPassword(self, password, confirmPassword):
        pattern = r'^(?=.*[0-9])(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
        if re.match(pattern, password) and len(password) >= 8 and password == confirmPassword:
            return True
        return False
