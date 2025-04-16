class Chat_group:
    def __init__(self, ID:int, name:str):
        self._groupId = ID
        self._name = name

    def getGroupId(self) -> int:
            return self._groupId

    def setGroupId(self, ID: int):
        self._groupId = ID

    def getGroupName(self) -> str:
        return self._groupName

    def setGroupName(self, name: str):
        self._groupName = name