from PyQt6.QtWidgets import QApplication, QMainWindow 
from PyQt6 import QtWidgets, uic
import sys
from Windows.groupWindow import GroupWindow
from Windows.loginWindow import LoginWindow
from Windows.registrationWindow import RegistrationWindow
from Windows.chatWindow import ChatWindow

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.groupWindow = None
        self.loginWindow = LoginWindow()
        self.registrationWindow = RegistrationWindow()
        self.chatWindow = ChatWindow()
        self.loginWindow.show()
        self.loginWindow.linkLabel.linkActivated.connect(self.showRegistration)
        self.loginWindow.loginSuccess.connect(self.showChatWindow)
        self.chatWindow.newGroupSignal.connect(self.showAddGroupWindow)

    def showRegistration(self):
        print("RegistrationScreen link clicked")
        self.registrationWindow.show()
        self.loginWindow.hide()

    def showChatWindow(self):
        print("ChatScreen showing")
        self.groupWindow = GroupWindow()
        self.chatWindow.show()
        self.chatWindow.loadContacts()
        self.loginWindow.hide()

    def showAddGroupWindow(self):
        print("Group window is now showing")
        self.groupWindow.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    sys.exit(app.exec())