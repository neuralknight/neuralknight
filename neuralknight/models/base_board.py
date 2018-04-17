from uuid import uuid4


class BaseBoard:
    GAMES = {}

    @classmethod
    def get_game(cls, _id):
        """
        Provide game matching id.
        """
        return cls.GAMES[_id]

    def __init__(self, _id):
        if _id:
            self.id = _id
        else:
            self.id = str(uuid4())
        self.GAMES[self.id] = self

    def close(self):
        del self.GAMES[self.id]
