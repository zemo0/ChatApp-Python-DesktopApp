from PyQt6.QtWidgets import QApplication, QMainWindow 
from PyQt6 import QtWidgets, uic
import sys

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/loginScreen.ui", self)

        self.pushButton.clicked.connect(self.onButtonClick)

    def onButtonClick(self):
        userInput = self.usernameLine.text()
        passInput = self.passwordLine.text()
        print(f"Button je stisnut, ispisujem user {userInput} i pass {passInput}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())