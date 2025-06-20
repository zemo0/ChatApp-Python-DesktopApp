from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QHeaderView, \
    QMessageBox, QDialog
from Data.database import DatabaseManager

class AdminWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Panel")
        self.resize(900, 400)

        layout = QVBoxLayout()

        #gumbi
        self.btnEdit = QPushButton("Uredi")
        self.btnDelete = QPushButton("Izbriši")
        self.btnReport = QPushButton("Izvještaj")

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btnEdit)
        btnLayout.addWidget(self.btnDelete)
        btnLayout.addWidget(self.btnReport)
        layout.addLayout(btnLayout)

        self.btnEdit.clicked.connect(self.editSelectedUser)
        self.btnDelete.clicked.connect(self.deleteSelectedUser)
        self.btnReport.clicked.connect(self.generateReportForSelectedUser)

        # tablica postavljenje korisnika
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Ime", "Prezime", "Datum rođenja", "Email", "Korisničko ime",
            "Lozinka", "Uloga", "Broj poruka"
        ])

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.db = DatabaseManager.instance()
        self.loadUsers()

    def loadUsers(self):
        self.db.getAllUsersFullInfo(callback=self.populateTable)

    def populateTable(self, users):
        if not users:
            QMessageBox.warning(self, "Greška", "Nema korisnika u sustavu.")
            return

        self.table.setRowCount(len(users))
        for i, user in enumerate(users):
            user_id = user["ID"]
            values = [
                user["ID"], user["name"], user["surname"], user["dateOfBirth"],
                user["email"], user["username"], user["password"], user["role"]
            ]

            for j, value in enumerate(values):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

            self.db.getMessageCountByUserId(
                user_id,
                callback=lambda count, row=i: self.setMessageCount(row, count)
            )

    def setMessageCount(self, row, count):
        self.table.setItem(row, 8, QTableWidgetItem(str(count)))

    def getSelectedUserId(self):
        selected = self.table.currentRow()
        if selected >= 0:
            item = self.table.item(selected, 0)
            return item.text() if item else None
        return None

    def editSelectedUser(self):
        user_id = self.getSelectedUserId()
        if user_id:
            print(f"Uredi korisnika {user_id}")

    def deleteSelectedUser(self):
        user_id = self.getSelectedUserId()
        if user_id:
            print(f"Izbriši korisnika {user_id}")

    def generateReportForSelectedUser(self):
        user_id = self.getSelectedUserId()
        if user_id:
            print(f"Generiraj PDF izvještaj za korisnika {user_id}")