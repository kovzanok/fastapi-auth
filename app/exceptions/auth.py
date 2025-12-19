class AuthException(Exception):
    pass

class UserAlreadyExists(AuthException):
    pass

class InvalidToken(AuthException):
    pass

class ExpiredToken(AuthException):
    pass

class UserNotFound(AuthException):
    pass

class AlreadyVerifiedUser(AuthException):
    pass

class InvalidCredentials(AuthException):
    pass

class UserNotVerified(AuthException):
    pass