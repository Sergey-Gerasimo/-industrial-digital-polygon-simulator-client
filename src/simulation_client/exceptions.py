from typing import Dict, Optional


class SimulationError(Exception):
    """Базовое исключение для симуляции."""

    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConnectionError(SimulationError):
    """Ошибка подключения к серверу."""

    pass


class AuthenticationError(SimulationError):
    """Ошибка аутентификации."""

    pass


class NotFoundError(SimulationError):
    """Ресурс не найден."""

    pass


class ValidationError(SimulationError):
    """Ошибка валидации данных."""

    pass


class SimulationNotConfiguredError(SimulationError):
    """Симуляция не настроена."""

    pass


class SimulationRunError(SimulationError):
    """Ошибка запуска симуляции."""

    pass


class ResourceExhaustedError(SimulationError):
    """Ресурсы исчерпаны."""

    pass


class TimeoutError(SimulationError):
    """Таймаут операции."""

    pass


class RetryableError(SimulationError):
    """Ошибка, после которой можно повторить операцию."""

    pass
