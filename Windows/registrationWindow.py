from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6 import QtWidgets, uic
from Data import database
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
        self.dbManager = database.DatabaseManager()

    def onButtonClick(self):
        #get frontend
        nameInput = self.nameLine.text()
        surnameInput = self.surnameLine.text()
        dateInput = self.dateEdit.date().toString("yyyy-MM-dd")
        emailInput = self.emailLine.text()
        usernameInput = self.usernameLine.text()
        passwordInput = self.passwordLine.text()
        confirmPasswordInput = self.confirmPasswordLine.text()
        roleInput = self.comboBox.currentText()

        #provjera pass i duplikata usernamea
        if self.doChecks(usernameInput, passwordInput, confirmPasswordInput):
            self.dbManager.insertNewUser(nameInput, surnameInput, dateInput, emailInput, usernameInput, passwordInput,
                                         roleInput)
            print("Registracija korisnika je uspješna!")
        else:
            print("Neuspješna registracija")

    def doChecks(self, usernameInput, passwordInput, confirmPasswordInput):
        dbUsernames = self.dbManager.getUsersInfo("username")
        print(dbUsernames)
        if usernameInput in dbUsernames:
            self.infoLabel.setText("to korisničko ime već postoji, probajte neko drugo")
            return False
        elif not self.isValidPassword(passwordInput, confirmPasswordInput):
            self.infoLabel.setText("lozinka nije dobra, mora imati barem 8 znakova, 1 broj i 1 specijalan znak")
            return False
        else:
            self.infoLabel.setText("")
            return True

    def isValidPassword(self, password, confirmPassword):
        pattern = r'^(?=.*[0-9])(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
        if re.match(pattern, password) and len(password) > 8 and password == confirmPassword:
            return True
        return False
