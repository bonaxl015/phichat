class AppException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DatabaseException(AppException):
    pass


class UnauthorizedException(AppException):
    pass
