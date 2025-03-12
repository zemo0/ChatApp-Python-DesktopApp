from PyQt6 import QtWidgets, uic

if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    uic.loadUi('UI/loginScreen.ui', window)
    window.show()
    sys.exit(app.exec())