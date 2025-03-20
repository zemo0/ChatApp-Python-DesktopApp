from PyQt6.QtWidgets import QApplication, QMainWindow 
from PyQt6 import QtWidgets, uic
import sys
from Windows.loginWindow import LoginWindow
from Windows.registrationWindow import RegistrationWindow
from Windows.chatWindow import ChatWindow

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loginWindow = LoginWindow()
        self.registrationWindow = RegistrationWindow()
        self.chatWindow = ChatWindow()
        self.loginWindow.show()
        self.loginWindow.linkLabel.linkActivated.connect(self.showRegistration)
        self.loginWindow.loginSuccess.connect(self.showChatWindow)

    def showRegistration(self):
        print("RegistrationScreen link clicked")
        self.registrationWindow.show()
        self.loginWindow.hide()

    def showChatWindow(self):
        print("ChatScreen showing")
        self.chatWindow.show()
        self.loginWindow.hide()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    sys.exit(app.exec())