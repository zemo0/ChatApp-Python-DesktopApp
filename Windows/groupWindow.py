from PyQt6 import uic
from PyQt6.QtCore import QEvent, Qt, QTimer
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QComboBox, QPushButton, QWidget, QLabel, QLineEdit, QSizePolicy, \
    QMessageBox, QInputDialog
from Data import database
from Data.Helpers import cryptoFunctions
from Data.userSession import UserSession

dbManager = database.DatabaseManager.instance() #zasto je db connector van group windowa? nije li ovo
loginSession = UserSession()
class MultiSelectDropdown(QWidget):
    def __init__(self, chatWindow=None):
        super().__init__()
        self.chatWindow = chatWindow
        self.comboBox = QComboBox(self)
        self.comboBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.comboBox.setEditable(False)
        self.comboBox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.model = QStandardItemModel()
        self.comboBox.setModel(self.model)
        dbManager.instance().getAllUsers(loginSession.getCurrentId(), callback=self.populateUserList)
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
    def __init__(self, chatWindow=None):
        super().__init__()
        self.chatWindow = chatWindow
        self.window_width, self.window_height = 500, 250
        self.setMinimumSize(self.window_width, self.window_height)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.groupName = QLineEdit()
        self.groupName.setPlaceholderText("Ime grupe...")
        self.layout.addWidget(self.groupName)

        self.groupName.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.dropdownUsers = MultiSelectDropdown()
        self.layout.addWidget(self.dropdownUsers)

        self.createGroupButton = QPushButton("Napravi")
        self.layout.addWidget(self.createGroupButton)

        self.groupDropdown = QComboBox()
        self.layout.addWidget(QLabel("Odaberi grupu:"))
        self.layout.addWidget(self.groupDropdown)

        self.editGroupButton = QPushButton("Izmjeni")
        self.layout.addWidget(self.editGroupButton)

        self.deleteGroupButton = QPushButton("Izbriši")
        self.layout.addWidget(self.deleteGroupButton)

        #popuna liste grupa
        dbManager.getGroupsByUserId(loginSession.getCurrentId(), callback=self.onGroupsFetched)

        self.createGroupButton.clicked.connect(self.buttonIsClicked)
        self.editGroupButton.clicked.connect(self.editGroup)
        self.deleteGroupButton.clicked.connect(self.deleteGroup)

    def buttonIsClicked(self):
        groupname = self.groupName.text()
        members = self.dropdownUsers.getSelectedItems()
        groupId = cryptoFunctions.prepId(groupname)

        current_username = loginSession.getCurrentUsername()
        if current_username not in members:
            members.append(current_username)

        print(f"[DEBUG] Insert group called with ID: {groupId}")
        def onGroupCreated(_):
            self.insertNextMember(members, groupId, 0)
        print("Pozvana insert new grupu")
        dbManager.instance().insertNewGroup(groupId, groupname, callback=onGroupCreated)

    def insertNextMember(self, members, groupId, index):
        if index >= len(members):
            print("Svi članovi grupe su dodani.")
            return

        member = members[index]

        def onUserIdReceived(userId):
            idInDb = cryptoFunctions.prepId(groupId)
            def onMemberInserted(_):
                self.insertNextMember(members, groupId, index + 1)
            dbManager.instance().insertGroupMember(idInDb, groupId, userId, callback=onMemberInserted)

        dbManager.instance().getIdByUsername(member, callback=onUserIdReceived)

    def editGroup(self):
        index = self.groupDropdown.currentIndex()
        if index == -1:
            QMessageBox.warning(self, "Upozorenje", "Odaberite grupu.")
            return

        current_name = self.groupDropdown.currentText()
        group_id = self.groupDropdown.currentData()

        new_name, ok = QInputDialog.getText(self, "Preimenuj grupu", f"Novo ime za grupu '{current_name}':")
        if ok and new_name.strip():
            dbManager.updateGroupName(group_id, new_name.strip(), callback=lambda _: self.loadUserGroups())
            QTimer.singleShot(1000, self.chatWindow.loadContacts)


    def deleteGroup(self):
        index = self.groupDropdown.currentIndex()
        if index == -1:
            QMessageBox.warning(self, "Upozorenje", "Odaberite grupu.")
            return

        group_name = self.groupDropdown.currentText()
        group_id = self.groupDropdown.currentData()

        reply = QMessageBox.question(
            self,
            "Potvrda brisanja",
            f"Jeste li sigurni da želite izbrisati grupu '{group_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            dbManager.deleteGroupById(group_id, callback=lambda _: self.loadUserGroups())
            QTimer.singleShot(1000, self.chatWindow.loadContacts)

    def loadUserGroups(self):
        user_id = loginSession.getCurrentId()

        def onGroupsFetched(groups):
            self.groupDropdown.clear()
            if groups:
                for name, group_id in groups:
                    self.groupDropdown.addItem(name, userData=group_id)

        dbManager.getGroupsByUserId(user_id, callback=onGroupsFetched)

    def onGroupsFetched(self, groups):
        self.groupDropdown.clear()
        if groups:
            for name, group_id in groups:
                self.groupDropdown.addItem(name, userData=group_id)
