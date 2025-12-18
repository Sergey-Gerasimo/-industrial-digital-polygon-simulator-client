import asyncio
import grpc
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
import logging
from contextlib import asynccontextmanager

from .exceptions import ConnectionError, TimeoutError
from .utils import ExponentialBackoff, AsyncRateLimiter, retry_async

logger = logging.getLogger(__name__)


class AsyncBaseClient(ABC):
    """
    Базовый абстрактный класс для асинхронных gRPC клиентов.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 50051,
        max_retries: int = 3,
        timeout: float = 30.0,
        rate_limit: Optional[float] = None,
        enable_logging: bool = True,
    ):
        """
        Инициализация базового клиента.

        Args:
            host: Хост сервера
            port: Порт сервера
            max_retries: Максимальное количество повторных попыток
            timeout: Таймаут операций в секундах
            rate_limit: Ограничение запросов в секунду
            enable_logging: Включить логирование
        """
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.timeout = timeout
        self.channel = None
        self.stub = None
        self.backoff = ExponentialBackoff(max_retries=max_retries)
        self.rate_limiter = AsyncRateLimiter(rate_limit, 1.0) if rate_limit else None

        if enable_logging:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )

    @abstractmethod
    def _create_stub(self, channel: grpc.aio.Channel):
        """
        Создать stub для gRPC сервиса.

        Args:
            channel: gRPC канал

        Returns:
            Stub объект для конкретного сервиса
        """
        pass

    @abstractmethod
    def _get_service_name(self) -> str:
        """
        Получить имя сервиса для логирования.

        Returns:
            str: Имя сервиса
        """
        pass

    @abstractmethod
    def _parse_ping_response(self, response) -> bool:
        """
        Парсить ответ ping для получения статуса.

        Args:
            response: Ответ от ping метода

        Returns:
            bool: True если сервер доступен
        """
        pass

    async def connect(self):
        """
        Подключиться к серверу.

        Создает канал, stub и проверяет соединение через ping.
        Использует wait_for_ready=True для ожидания готовности сервера.
        """
        try:
            # Создаем канал
            logger.info(
                f"Creating channel to {self._get_service_name()} at {self.host}:{self.port}..."
            )
            self.channel = await self._create_channel()
            self.stub = self._create_stub(self.channel)

            # Проверяем соединение через ping с wait_for_ready
            # wait_for_ready=True позволяет клиенту ждать готовности сервера
            logger.info(
                f"Checking connection to {self._get_service_name()} via ping..."
            )
            if await self.ping():
                logger.info(
                    f"✅ Connected to {self._get_service_name()} at {self.host}:{self.port}"
                )
            else:
                raise ConnectionError(
                    f"Cannot connect to {self._get_service_name()} at {self.host}:{self.port}"
                )

        except grpc.RpcError as e:
            error_msg = f"gRPC error connecting to {self._get_service_name()}: {e.code()} - {e.details()}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
        except asyncio.TimeoutError as e:
            error_msg = f"Timeout connecting to {self._get_service_name()} at {self.host}:{self.port}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
        except ConnectionError:
            # Пробрасываем ConnectionError как есть
            raise
        except Exception as e:
            error_msg = f"Failed to connect to {self._get_service_name()}: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

    async def close(self):
        """Закрыть соединение."""
        if self.channel:
            await self.channel.close()
            self.stub = None
            logger.info(f"Disconnected from {self._get_service_name()}")

    async def ping(self) -> bool:
        """
        Проверить доступность сервера.

        Использует wait_for_ready=True для ожидания готовности сервера
        перед выполнением ping запроса.

        Returns:
            bool: True если сервер доступен
        """
        if self.stub is None:
            logger.warning(f"{self._get_service_name()} client not connected")
            return False

        try:
            await self._rate_limit()
            # Импортируем protobuf модуль для PingRequest
            from .proto import simulator_pb2

            # Используем wait_for_ready=True и timeout согласно best practices
            # Это позволяет клиенту ждать готовности сервера вместо немедленного отказа
            response = await self.stub.ping(
                simulator_pb2.PingRequest(),
                wait_for_ready=True,
                timeout=10.0,  # Таймаут для ping запроса
            )
            return self._parse_ping_response(response)
        except grpc.RpcError as e:
            # Логируем детали gRPC ошибки
            error_code = e.code()
            error_details = e.details()
            logger.warning(
                f"Ping to {self._get_service_name()} failed: {error_code} - {error_details}"
            )
            return False
        except asyncio.TimeoutError:
            logger.warning(
                f"Ping to {self._get_service_name()} timed out after 10 seconds"
            )
            return False
        except Exception as e:
            logger.warning(f"Ping to {self._get_service_name()} failed: {e}")
            return False

    def _ensure_connected(self):
        """Проверить, что клиент подключен."""
        if self.stub is None:
            raise ConnectionError(
                f"Client not connected to {self.host}:{self.port}. Call connect() first."
            )

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _rate_limit(self):
        """Применить ограничение скорости."""
        if self.rate_limiter:
            await self.rate_limiter.wait()

    async def _with_retry(self, func, *args, **kwargs):
        """Выполнить функцию с повторными попытками."""
        return await retry_async(
            func,
            *args,
            max_retries=self.max_retries,
            base_delay=1.0,
            retry_exceptions=(grpc.RpcError, ConnectionError, TimeoutError),
            **kwargs,
        )

    async def _create_channel(self, options: Optional[list] = None) -> grpc.aio.Channel:
        """
        Создать асинхронный канал.

        Args:
            options: Дополнительные опции канала

        Returns:
            grpc.aio.Channel: Асинхронный канал
        """
        default_options = [
            ("grpc.keepalive_time_ms", 10000),
            ("grpc.keepalive_timeout_ms", 5000),
            ("grpc.keepalive_permit_without_calls", True),
            ("grpc.max_reconnect_backoff_ms", 10000),
        ]

        if options:
            default_options.extend(options)

        return grpc.aio.insecure_channel(
            f"{self.host}:{self.port}", options=default_options
        )

    @asynccontextmanager
    async def _timeout_context(self, custom_timeout: Optional[float] = None):
        """
        Контекстный менеджер для таймаута.

        Args:
            custom_timeout: Кастомный таймаут (по умолчанию используется self.timeout)
        """
        timeout = custom_timeout or self.timeout

        try:
            await asyncio.wait_for(asyncio.sleep(0), timeout=timeout)
            yield
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout}s")

    def _handle_grpc_error(self, e: grpc.RpcError, operation: str) -> None:
        """
        Обработать gRPC ошибку.

        Args:
            e: Исключение gRPC
            operation: Название операции
        """
        from .exceptions import (
            NotFoundError,
            AuthenticationError,
            ResourceExhaustedError,
            ValidationError,
        )

        error_map = {
            grpc.StatusCode.NOT_FOUND: NotFoundError,
            grpc.StatusCode.UNAUTHENTICATED: AuthenticationError,
            grpc.StatusCode.PERMISSION_DENIED: AuthenticationError,
            grpc.StatusCode.RESOURCE_EXHAUSTED: ResourceExhaustedError,
            grpc.StatusCode.INVALID_ARGUMENT: ValidationError,
            grpc.StatusCode.FAILED_PRECONDITION: ValidationError,
        }

        exception_class = error_map.get(e.code())
        if exception_class:
            raise exception_class(f"{operation} failed: {e.details()}")

        from .exceptions import SimulationError

        raise SimulationError(f"{operation} failed: {e.details()}")
