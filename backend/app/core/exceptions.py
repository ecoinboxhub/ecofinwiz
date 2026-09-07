from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: list | None = None):
        self.code = code
        self.details = details or []
        super().__init__(status_code=status_code, detail={"code": code, "message": message, "details": self.details})


class NotFoundException(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictException(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            code="RESOURCE_CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
        )


class UnauthorizedException(AppException):
    def __init__(self, code: str = "AUTH_INVALID_CREDENTIALS", message: str = "Invalid credentials"):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class RateLimitedException(AppException):
    def __init__(self):
        super().__init__(
            code="RATE_LIMITED",
            message="Too many requests",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )
