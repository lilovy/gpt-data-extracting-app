

class BingError(Exception):
    pass

class DayLimit(Exception):
    def __init__(self):
        self.message = "You used the daily limit!"
        super().__init__(self.message)