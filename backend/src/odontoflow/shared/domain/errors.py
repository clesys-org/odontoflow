"""Domain error types."""


class DomainError(Exception):
    """Base domain error."""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(DomainError):
    def __init__(self, entity: str, identifier: str):
        super().__init__(f"{entity} nao encontrado: {identifier}", "NOT_FOUND")


class ValidationError(DomainError):
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class ConflictError(DomainError):
    def __init__(self, message: str):
        super().__init__(message, "CONFLICT")


class AuthorizationError(DomainError):
    def __init__(self, message: str = "Permissao negada"):
        super().__init__(message, "UNAUTHORIZED")
