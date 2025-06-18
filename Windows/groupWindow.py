from PyQt6 import uic
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QComboBox, QPushButton, QWidget, QLabel, QLineEdit, QSizePolicy
from Data import database
from Data.Helpers import cryptoFunctions
from Data.userSession import UserSession

dbManager = database.DatabaseManager.instance() #zasto je db connector van group windowa? nije li ovo
class MultiSelectDropdown(QWidget):
    loginSession = UserSession()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.comboBox = QComboBox(self)
        self.comboBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.comboBox.setEditable(False)
        self.comboBox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        # model for checkable items
        self.model = QStandardItemModel()
        self.comboBox.setModel(self.model)

        # Add checkable items
        dbManager.getAllUsers(self.loginSession.getCurrentId(), callback=self.populateUserList)


        # event filter to catch clicks on checkboxes
        self.comboBox.view().viewport().installEventFilter(self)

    def populateUserList(self, users):
        if users is not None:
            for username, ids in users:
                item = QStandardItem(username)
                item.setCheckable(True)
                item.setCheckState(Qt.CheckState.Unchecked)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                self.model.appendRow(item)
        else:
            print("No users in database")


    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonRelease:
            index = self.comboBox.view().indexAt(event.position().toPoint())
            if index.isValid():
                item = self.model.item(index.row())
                item.setCheckState(Qt.CheckState.Checked if item.checkState() == Qt.CheckState.Unchecked else Qt.CheckState.Unchecked)
                self.updateSelection()
                return True
        return super().eventFilter(obj, event)

    def updateSelection(self):
        selected_items = [
            self.model.item(i).text() for i in range(self.model.rowCount())
            if self.model.item(i).checkState() == Qt.CheckState.Checked
        ]
        self.comboBox.setCurrentText(", ".join(selected_items) if selected_items else "Select items")

    def getSelectedItems(self):
        return [
            self.model.item(i).text() for i in range(self.model.rowCount())
            if self.model.item(i).checkState() == Qt.CheckState.Checked
        ]

class GroupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 500, 250
        self.setMinimumSize(self.window_width, self.window_height)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.groupName = QLineEdit()
        self.groupName.setPlaceholderText("Ime grupe...")
        self.layout.addWidget(self.groupName)

        self.groupName.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.dropdown = MultiSelectDropdown()
        self.layout.addWidget(self.dropdown)

        self.button = QPushButton("Retrieve")
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.buttonIsClicked)

    def buttonIsClicked(self):
        groupname = self.groupName.text()
        members = self.dropdown.getSelectedItems()
        groupId = cryptoFunctions.prepId(groupname)
        dbManager.insertNewGroup(groupId, groupname)
        for member in members:
            idUser = dbManager.getIdByUsername(member)
            idInDb = cryptoFunctions.prepId(groupId)
            dbManager.insertGroupMember(idInDb, groupId, idUser)