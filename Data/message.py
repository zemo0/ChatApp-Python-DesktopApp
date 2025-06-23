from datetime import datetime

class Message:
    def __init__(self, messageId: str, content: str, senderId: str,
                 groupId: str, receiverId: str, timestamp: datetime,
                 attachment: bytes = None, attachment_name: str = None):
        self._id = messageId
        self._content = content
        self._senderId = senderId
        self._groupId = groupId
        self._receiverId = receiverId
        self._timestamp = timestamp
        self._attachment = attachment
        self._attachment_name = attachment_name

    def setId(self, idMessage): self._id = idMessage
    def setContent(self, newContent): self._content = newContent
    def setSenderId(self, senderId): self._senderId = senderId
    def setGroupId(self, groupId): self._groupId = groupId
    def setReceiverId(self, receiverId): self._receiverId = receiverId
    def setTimestamp(self, timestamp): self._timestamp = timestamp
    def setAttachment(self, attachment): self._attachment = attachment
    def setAttachmentName(self, name): self._attachment_name = name

    def getId(self): return self._id
    def getContent(self): return self._content
    def getSenderId(self): return self._senderId
    def getGroupId(self): return self._groupId
    def getReceiverId(self): return self._receiverId
    def getTimestamp(self): return self._timestamp
    def getAttachment(self): return self._attachment
    def getAttachmentName(self): return self._attachment_name

    def displayMessage(self):
        if self._attachment_name:
            print(f"Attachment: {self._attachment_name} ({len(self._attachment)} bytes)")
        else:
            print("Attachment: nema")
