from tornado import web


class RequestValidationError(web.HTTPError):
    """Raised when a request fails validation."""

    def __init__(self, status_code: int) -> None:
        super().__init__(status_code)
