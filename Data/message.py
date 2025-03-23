from datetime import datetime

class Message:
    def __init__(self, messageId:int, content:str, senderId:int, receiverId:int, timestamp:datetime):
        self._id = messageId
        self._content = content
        self._senderId = senderId
        self._receiverId = receiverId
        self._timestamp = timestamp if timestamp else datetime.now()

    def setId(self, idMessage):
        self._id = idMessage

    def setContent(self, newContent):
        self._content = newContent

    def setSenderId(self, senderId):
        self._senderId = senderId

    def setReceiverId(self, receiverId):
        self._receiverId = receiverId

    def setTimestamp(self, timestamp):
        self._timestamp = timestamp

    def getId(self):
        return self._id

    def getContent(self):
        return self._content

    def getSenderId(self):
        return self._senderId

    def getReceiverId(self):
        return self._receiverId

    def getTimestamp(self):
        return self._timestamp

    def displayMessage(self):
        """Display the message in a readable format"""
        print(f"Message ID: {self._id}")
        print(f"Sender ID: {self._senderId}")
        print(f"Receiver ID: {self._receiverId}")
        print(f"Timestamp: {self._timestamp}")
        print(f"Content: {self._content}")