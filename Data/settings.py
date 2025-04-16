import configparser
import winreg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QComboBox, QSlider, QSpinBox, QPushButton, QVBoxLayout, QLabel, QHBoxLayout

INI_PATH = 'Data/Helpers/config.ini'
REG_PATH = r"SOFTWARE\ChatApp"
REG_NAME = "FontSize"


def read_font_size():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, REG_NAME)
        winreg.CloseKey(key)
        return int(value)  # Convert from string if needed
    except FileNotFoundError:
        return 12  # Default font size
    except Exception as e:
        print(f"Error reading registry: {e}")
        return 12


def write_font_size(font_size):
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        winreg.SetValueEx(key, REG_NAME, 0, winreg.REG_SZ, str(font_size))
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Error writing registry: {e}")


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chatWindow = None
        self.groupWindow = None
        self.width = None
        self.x = None
        self.font_size = None
        self.theme = None
        self.y = None
        self.height = None
        self.config = None
        # Create widgets for settings (theme, font size, position)
        self.theme_combo = QComboBox(self)
        self.theme_combo.addItems(["light", "dark"])

        self.font_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.font_slider.setMinimum(8)
        self.font_slider.setMaximum(30)
        self.font_slider.setValue(12)  # Default font size

        self.x_spinbox = QSpinBox(self)
        self.x_spinbox.setRange(0, 1920)  # Assume screen width is 1920
        self.x_spinbox.setValue(100)

        self.y_spinbox = QSpinBox(self)
        self.y_spinbox.setRange(0, 1080)  # Assume screen height is 1080
        self.y_spinbox.setValue(100)

        # Layout setup
        layout = QVBoxLayout()

        # Add settings to layout
        layout.addWidget(QLabel("Theme:"))
        layout.addWidget(self.theme_combo)

        layout.addWidget(QLabel("Font Size:"))
        layout.addWidget(self.font_slider)

        layout.addWidget(QLabel("X Position:"))
        layout.addWidget(self.x_spinbox)

        layout.addWidget(QLabel("Y Position:"))
        layout.addWidget(self.y_spinbox)

        # Apply/Cancel Buttons
        button_layout = QHBoxLayout()
        apply_button = QPushButton("Apply", self)
        apply_button.clicked.connect(self.apply_changes)
        button_layout.addWidget(apply_button)
        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def apply_changes(self):
        """Apply the selected settings and pass them to the parent window."""
        theme = self.theme_combo.currentText()
        font_size = self.font_slider.value()
        x_pos = self.x_spinbox.value()
        y_pos = self.y_spinbox.value()

        # Apply settings to the parent (ChatWindow)
        self.apply_settings(theme, font_size, x_pos, y_pos)
        print(f"The parent object is {self.parent()}")

        # Close the settings window
        self.accept()

    def load_settings(self, chatWindow, groupWindow):
        """Load settings from the INI file or default values."""
        self.config = configparser.ConfigParser()
        self.config.read(INI_PATH)

        # Load user preferences (theme, font size)
        self.theme = self.config.get('UserPreferences', 'theme', fallback='dark')
        self.font_size = read_font_size()

        # Load window position and size
        self.x = self.config.getint('WindowSettings', 'x_position', fallback=100)
        self.y = self.config.getint('WindowSettings', 'y_position', fallback=100)
        self.width = self.config.getint('WindowSettings', 'width', fallback=800)
        self.height = self.config.getint('WindowSettings', 'height', fallback=600)

        self.chatWindow = chatWindow
        self.groupWindow = groupWindow
        # Apply user preferences and window settings
        self.apply_user_preferences()
        self.apply_window_settings()

    def apply_user_preferences(self):
        """Apply user preferences such as theme and font size."""
        if self.theme == 'dark':
            self.setStyleSheet("background-color: #2e2e2e; color: white;")
            self.chatWindow.setStyleSheet("background-color: #2e2e2e; color: white;")
            self.groupWindow.setStyleSheet("background-color: #2e2e2e; color: white;")
        else:
            print("try to set stylesheet")
            self.setStyleSheet("background-color: white; color: black;")
            self.chatWindow.setStyleSheet("background-color: white; color: black;")
            self.groupWindow.setStyleSheet("background-color: white; color: black;")

        # Apply font size
        font = self.font()
        font.setPointSize(int(self.font_size))
        self.setFont(font)

    def apply_window_settings(self):
        """Apply the window position and size."""
        self.setGeometry(self.x, self.y, 100, 100)
        self.chatWindow.setGeometry(self.x, self.y, self.width, self.height)
        self.groupWindow.setGeometry(self.x, self.y, 200, 200)

    def apply_settings(self, theme, font_size, x, y):
        """Apply the updated settings."""
        # Update theme and font size
        self.theme = theme
        self.font_size = font_size
        self.x = x
        self.y = y

        # Apply settings to the window
        self.apply_user_preferences()
        self.apply_window_settings()

        # Save settings to the config file
        self.save_settings()

    def save_settings(self):
        """Save the updated settings to the INI file."""
        print("try save settings to file")
        for section in self.config.sections():
            print(f"[{section}]")
            for key, value in self.config.items(section):
                print(f"{key} = {value}")

        self.config.set('UserPreferences', 'theme', self.theme)
        write_font_size(str(self.font_size))
        self.config.set('WindowSettings', 'x_position', str(self.x))
        self.config.set('WindowSettings', 'y_position', str(self.y))
        self.config.set('WindowSettings', 'width', str(self.width))
        self.config.set('WindowSettings', 'height', str(self.height))

        with open(INI_PATH, 'w') as configfile:
            self.config.write(configfile)
        print("settings saved to file")

