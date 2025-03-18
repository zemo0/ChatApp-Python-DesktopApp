from PyQt6.QtWidgets import QApplication, QMainWindow 
from PyQt6 import QtWidgets, uic
import sys
from Windows.loginWindow import LoginWindow

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loginWindow = LoginWindow()
        self.loginWindow.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    sys.exit(app.exec())