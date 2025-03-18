from PyQt6.QtWidgets import QMainWindow
from PyQt6 import QtWidgets, uic
from Data import database
import sys

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.errorLabel = None
        uic.loadUi("UI/loginScreen.ui", self)  # Ensure this path is correct
        print("The UI screen is loaded")
        self.pushButton.clicked.connect(self.onButtonClick)
        self.dbManager = database.DatabaseManager()

    def onButtonClick(self):
        usernameInput = self.usernameLine.text()
        passwordInput = self.passwordLine.text()
        dbUsers = self.dbManager.getUsers()
        if (usernameInput, passwordInput) in dbUsers:
            print("Login checks out, go to mainWindow")
        else:
            print("Login failed, write so out on the screen")
            self.errorLabel.setText("Neuspjesna prijava, probajte ponovno")



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
