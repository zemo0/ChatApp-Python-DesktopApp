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
        dateInput = self.dateEdit.date().toString("dd-MM-yyyy")
        usernameInput = self.usernameLine.text()
        passwordInput = self.passwordLine.text()
        confirmPasswordInput = self.confirmPasswordLine.text()
        roleInput = self.comboBox.currentText()

        #provjera pass i duplikata usernamea
        self.doChecks(nameInput, surnameInput, dateInput, usernameInput, passwordInput, confirmPasswordInput, roleInput)

    def doChecks(self, nameInput, surnameInput, dateInput, usernameInput, passwordInput, confirmPasswordInput, roleInput):
        dbUsernames = self.dbManager.getUsersInfo("username")
        print(dbUsernames)
        if usernameInput in dbUsernames:
            self.infoLabel.setText("to korisničko ime već postoji, probajte neko drugo")
        elif not self.isValidPassword(passwordInput, confirmPasswordInput):
            self.infoLabel.setText("lozinka nije dobra, mora imati barem 8 znakova, 1 broj i 1 specijalan znak")
        else:
            self.infoLabel.setText("")

    def isValidPassword(self, password, confirmPassword):
        pattern = r'^(?=.*[0-9])(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
        if re.match(pattern, password) and len(password) > 8 and password == confirmPassword:
            return True
        return False
