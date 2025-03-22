class MessageModel(QStandardItemModel):
    def add_message(self, username, timestamp, message):
        """ Adds a message to the model """
        item = QStandardItem()
        item.setData({"username": username, "timestamp": timestamp, "message": message}, Qt.UserRole)
        self.appendRow(item)