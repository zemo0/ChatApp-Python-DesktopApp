import configparser
import winreg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QComboBox, QSlider, QSpinBox, QPushButton, QVBoxLayout, QLabel, QHBoxLayout

from Data.Helpers import jsonLogger
from Data.userSession import UserSession
from Windows.groupWindow import loginSession

INI_PATH = 'Data/Helpers/config.ini'
REG_PATH = r"SOFTWARE\ChatApp"
REG_NAME = "FontSize"


def readFontSize():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, REG_NAME)
        winreg.CloseKey(key)
        return int(value)
    except FileNotFoundError:
        return 12
    except Exception as e:
        print(f"Greška s registrom: {e}")
        return 12


def writeFontSize(font_size):
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        winreg.SetValueEx(key, REG_NAME, 0, winreg.REG_SZ, str(font_size))
        winreg.CloseKey(key)
    except Exception as e:
        print(f"windows regitar greska: {e}")


class SettingsWindow(QDialog):
    loginSession = UserSession.instance()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.adminWindow = None
        self.chatWindow = None
        self.groupWindow = None
        self.width = None
        self.x = None
        self.font_size = None
        self.theme = None
        self.y = None
        self.height = None
        self.config = None
        self.theme_combo = QComboBox(self)
        self.theme_combo.addItems(["light", "dark"])

        self.font_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.font_slider.setMinimum(8)
        self.font_slider.setMaximum(30)
        self.font_slider.setValue(12)

        self.x_spinbox = QSpinBox(self)
        self.x_spinbox.setRange(0, 1920)
        self.x_spinbox.setValue(100)

        self.y_spinbox = QSpinBox(self)
        self.y_spinbox.setRange(0, 1080)
        self.y_spinbox.setValue(100)
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tema aplikacije:"))
        layout.addWidget(self.theme_combo)

        layout.addWidget(QLabel("Veličina fonta:"))
        layout.addWidget(self.font_slider)

        layout.addWidget(QLabel("X koordinata:"))
        layout.addWidget(self.x_spinbox)

        layout.addWidget(QLabel("Y koordinata:"))
        layout.addWidget(self.y_spinbox)

        button_layout = QHBoxLayout()
        apply_button = QPushButton("Primjeni", self)
        apply_button.clicked.connect(self.applyChanges)
        button_layout.addWidget(apply_button)
        cancel_button = QPushButton("Poništi", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def applyChanges(self):
        theme = self.theme_combo.currentText()
        font_size = self.font_slider.value()
        x_pos = self.x_spinbox.value()
        y_pos = self.y_spinbox.value()

        self.apply_settings(theme, font_size, x_pos, y_pos)

        self.accept()

    def loadSettings(self, chatWindow, groupWindow):
        self.config = configparser.ConfigParser()
        self.config.read(INI_PATH)

        self.theme = self.config.get('UserPreferences', 'theme', fallback='dark')
        self.font_size = readFontSize()

        self.x = self.config.getint('WindowSettings', 'x_position', fallback=100)
        self.y = self.config.getint('WindowSettings', 'y_position', fallback=100)
        self.width = self.config.getint('WindowSettings', 'width', fallback=800)
        self.height = self.config.getint('WindowSettings', 'height', fallback=600)

        self.chatWindow = chatWindow
        self.groupWindow = groupWindow
        self.applyUserSettings()
        self.applyWindowSettings()

    def applyUserSettings(self):
        if self.theme == 'dark':
            self.setStyleSheet("background-color: #2e2e2e; color: white;")
            self.chatWindow.setStyleSheet("background-color: #2e2e2e; color: white;")
            self.groupWindow.setStyleSheet("background-color: #2e2e2e; color: white;")
        else:
            self.setStyleSheet("background-color: white; color: black;")
            self.chatWindow.setStyleSheet("background-color: white; color: black;")
            self.groupWindow.setStyleSheet("background-color: white; color: black;")

        font = self.font()
        font.setPointSize(int(self.font_size))
        self.setFont(font)

    def applyWindowSettings(self):
        self.setGeometry(self.x, self.y, 100, 100)
        self.chatWindow.setGeometry(self.x, self.y, self.width, self.height)
        self.groupWindow.setGeometry(self.x, self.y, 200, 200)

    def apply_settings(self, theme, font_size, x, y):
        self.theme = theme
        self.font_size = font_size
        self.x = x
        self.y = y

        self.applyUserSettings()
        self.applyWindowSettings()

        self.saveToFile()

    def saveToFile(self):
        jsonLogger.writeLog(self.loginSession.getCurrentUsername(), "Promjenjene postavke u aplikaciji")
        self.config.set('UserPreferences', 'theme', self.theme)
        writeFontSize(str(self.font_size))
        self.config.set('WindowSettings', 'x_position', str(self.x))
        self.config.set('WindowSettings', 'y_position', str(self.y))
        self.config.set('WindowSettings', 'width', str(self.width))
        self.config.set('WindowSettings', 'height', str(self.height))

        with open(INI_PATH, 'w') as configfile:
            self.config.write(configfile)

