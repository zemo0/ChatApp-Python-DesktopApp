import requests
from PyQt6.QtCore import QMetaObject, Qt, Q_ARG, pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QHeaderView, \
    QDialog, QInputDialog, QLabel, QMessageBox

from Data import database

class AdminWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Panel")
        self.resize(900, 400)

        layout = QVBoxLayout()
        self.dbManager = database.DatabaseManager.instance()
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

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Ime", "Prezime", "Datum rođenja", "Email", "Korisničko ime",
            "Lozinka", "Uloga", "Broj poruka"
        ])

        layout.addWidget(self.table)
        self.setLayout(layout)
        self.loadUsers()

    def loadUsers(self):
        self.dbManager.getAllUsersFullInfo(callback=self.populateTable)

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

            self.dbManager.getMessageCountByUserId(
                user_id,
                callback=lambda count, row=i: self.setMessageCount(row, count)
            )

    def setMessageCount(self, row, count):
        self.table.setItem(row, 8, QTableWidgetItem(str(count)))

    def getSelectedUserId(self):
        selected = self.table.currentRow()
        if selected >= 0:
            item = self.table.item(selected, 0)
            print(f"Trenutno odabrani korisnik je {selected}, imena {item.text()}")
            return item.text() if item else None
        return None

    def editSelectedUser(self):
        user_id = self.getSelectedUserId()
        if not user_id:
            QMessageBox.warning(self, "Upozorenje", "Niste odabrali korisnika.")
            return

        row = self.table.currentRow()
        current_data = {
            "name": self.table.item(row, 1).text(),
            "surname": self.table.item(row, 2).text(),
            "dateOfBirth": self.table.item(row, 3).text(),
            "email": self.table.item(row, 4).text(),
            "username": self.table.item(row, 5).text(),
            "password": self.table.item(row, 6).text(),
            "role": self.table.item(row, 7).text()
        }

        # poziva se iz glavnog threada
        QMetaObject.invokeMethod(
            self,
            "openEditDialog",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, user_id),
            Q_ARG(dict, current_data)
        )

    @pyqtSlot(str, dict)
    def openEditDialog(self, user_id, current_data):
        updated_data = {}
        for key, label in [
            ("name", "Ime"), ("surname", "Prezime"), ("dateOfBirth", "Datum rođenja"),
            ("email", "Email"), ("username", "Korisničko ime"),
            ("password", "Lozinka"), ("role", "Uloga")
        ]:
            value, ok = QInputDialog.getText(self, f"Uredi {label}", f"{label}:", text=current_data[key])
            print(f"Value za dodat je {value}")
            if not ok:
                return
            updated_data[key] = value

        try:
            print("Probaj poslat response za update")
            response = requests.put(f"http://localhost:5000/api/update_user/{user_id}", json=updated_data)
            if response.status_code == 200:
                QMessageBox.information(self, "Uspjeh", "Korisnik ažuriran.")
                self.loadUsers()
            else:
                QMessageBox.warning(self, "Greška", "Ažuriranje nije uspjelo.")
        except Exception as e:
            QMessageBox.critical(self, "Greška", f"Greška pri spajanju na server:\n{str(e)}")

    def deleteSelectedUser(self):
        user_id = self.getSelectedUserId()
        if not user_id:
            QMessageBox.warning(self, "Upozorenje", "Niste odabrali korisnika.")
            return

        def sendDeleteRequest(username):
            QMetaObject.invokeMethod(
                self,
                "confirmAndDeleteUser",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, user_id),
                Q_ARG(str, username)
            )
        #mali workaround, ovaj thread ne moze zvati sendDeleteReq jer funk radi UI promjene, zato ide invokeMethod
        self.dbManager.getUsernameById(user_id, callback=sendDeleteRequest)

    @pyqtSlot(str, str)
    def confirmAndDeleteUser(self, user_id, username):
        reply = QMessageBox.question(
            self,
            "Potvrda brisanja",
            f"Jeste li sigurni da želite obrisati korisnika '{username}'?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Ok:
            try:
                response = requests.delete(f"http://localhost:5000/api/delete_user/{user_id}")
                if response.status_code == 200:
                    QMessageBox.information(self, "Uspjeh", f"Korisnik '{username}' je obrisan.")
                    self.loadUsers()
                else:
                    QMessageBox.warning(self, "Greška", "Brisanje nije uspjelo.")
            except Exception as e:
                QMessageBox.critical(self, "Greška", f"Greška pri spajanju na server:\n{str(e)}")

    def generateReportForSelectedUser(self):
        user_id = self.getSelectedUserId()
        if user_id:
            print(f"Generiraj PDF izvještaj za korisnika {user_id}")