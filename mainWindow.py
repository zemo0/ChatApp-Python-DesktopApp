import traceback

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow
from PyQt6 import QtWidgets
import sys
from Windows.settingsWindow import SettingsWindow
from Windows.groupWindow import GroupWindow
from Windows.loginWindow import LoginWindow
from Windows.registrationWindow import RegistrationWindow
from Windows.chatWindow import ChatWindow

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settingsWindow = None
        self.groupWindow = None
        self.loginWindow = LoginWindow()
        self.registrationWindow = RegistrationWindow()
        self.chatWindow = ChatWindow()
        self.loginWindow.show()
        self.loginWindow.linkLabel.linkActivated.connect(self.showRegistration)
        self.loginWindow.loginSuccess.connect(self.showChatWindow)
        self.chatWindow.newGroupSignal.connect(self.showAddGroupWindow)
        self.chatWindow.openSettingsSignal.connect(self.openSettingsDialog)

    def showRegistration(self):
        self.registrationWindow.show()
        self.loginWindow.hide()

    def showChatWindow(self):
        self.chatWindow.startUdpListener()
        self.chatWindow.connectToTCPServer()
        print("ChatScreen showing")
        self.groupWindow = GroupWindow(chatWindow=self.chatWindow)
        self.settingsWindow = SettingsWindow()
        self.chatWindow.show()
        self.chatWindow.loadContacts()
        self.settingsWindow.load_settings(self.chatWindow, self.groupWindow)
        self.loginWindow.hide()
        self.chatWindow.triggerAdminCheck()

    def showAddGroupWindow(self):
        print("Group window is now showing")
        self.groupWindow.show()

    def openSettingsDialog(self):
        self.settingsWindow.show()


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("Neočekivana greška u aplikaciji:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

sys.excepthook = handle_exception

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    sys.exit(app.exec())