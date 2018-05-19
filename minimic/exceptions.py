
class MinimicException(Exception):
    pass


class LoginError(MinimicException):
    pass


class ParseError(MinimicException):
    pass


class SkippedAlbum(MinimicException):
    pass

