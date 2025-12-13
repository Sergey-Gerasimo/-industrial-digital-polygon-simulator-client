import asyncio
import logging
from typing import Any, Dict, List, Optional, TypeVar, Callable
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import json

T = TypeVar("T")

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO"):
    """Настройка логирования."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


class ExponentialBackoff:
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    async def __aiter__(self):
        for retry in range(self.max_retries):
            delay = min(self.base_delay * (2**retry), self.max_delay)

            if self.jitter:
                # Добавляем случайность для предотвращения thundering herd
                delay *= 0.5 + (hash(str(retry)) % 100) / 200

            yield delay

    def get_delay(self, retry: int) -> float:
        """Получить задержку для конкретной попытки."""
        delay = min(self.base_delay * (2**retry), self.max_delay)
        if self.jitter:
            delay *= 0.5 + (hash(str(retry)) % 100) / 200
        return delay


async def retry_async(
    func: Callable[..., Any],
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    retry_exceptions: tuple = (Exception,),
    **kwargs,
) -> Any:
    """
    Повторить асинхронную функцию с экспоненциальной задержкой.

    Args:
        func: Асинхронная функция
        max_retries: Максимальное количество попыток
        base_delay: Базовая задержка
        retry_exceptions: Исключения, при которых нужно повторять
        *args, **kwargs: Аргументы функции

    Returns:
        Результат функции
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except retry_exceptions as e:
            last_exception = e

            if attempt == max_retries:
                logger.error(f"Failed after {max_retries + 1} attempts: {e}")
                raise

            delay = base_delay * (2**attempt)
            logger.warning(
                f"Attempt {attempt + 1} failed: {e}. " f"Retrying in {delay:.2f}s..."
            )

            await asyncio.sleep(delay)

    raise last_exception


class AsyncRateLimiter:
    def __init__(self, rate: float, period: float = 1.0):
        """
        Args:
            rate: Количество запросов в период
            period: Период в секундах
        """
        self.rate = rate
        self.period = period
        self.tokens = rate
        self.updated_at = asyncio.get_event_loop().time()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: float = 1.0) -> float:
        """
        Получить токены для запроса.

        Args:
            tokens: Количество необходимых токенов

        Returns:
            Время ожидания в секундах
        """
        async with self._lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self.updated_at

            # Восстанавливаем токены
            self.tokens = min(
                self.rate, self.tokens + elapsed * (self.rate / self.period)
            )
            self.updated_at = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return 0.0

            # Нужно подождать
            deficit = tokens - self.tokens
            wait_time = deficit * (self.period / self.rate)
            self.tokens = 0
            return wait_time

    async def wait(self, tokens: float = 1.0):
        """Подождать пока не будет доступно достаточно токенов."""
        wait_time = await self.acquire(tokens)
        if wait_time > 0:
            await asyncio.sleep(wait_time)


@asynccontextmanager
async def timeout_context(timeout: float):
    """Контекстный менеджер для таймаута."""
    try:
        await asyncio.wait_for(asyncio.sleep(0), timeout=timeout)
        yield
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout}s")


def dict_to_proto(data: Dict, proto_class) -> Any:
    """Конвертировать словарь в protobuf сообщение."""
    from .proto import simulator_pb2

    if proto_class is None:
        raise ValueError("proto_class must be specified")

    proto = proto_class()

    for key, value in data.items():
        if value is not None:
            if isinstance(value, dict):
                # Рекурсивно конвертируем вложенные словари
                nested_proto = getattr(proto, key)
                dict_to_proto(value, type(nested_proto))
            elif isinstance(value, list):
                # Обрабатываем списки
                if value and isinstance(value[0], dict):
                    # Список словарей
                    for item in value:
                        getattr(proto, key).add().CopyFrom(
                            dict_to_proto(
                                item, getattr(simulator_pb2, key[:-1].title())
                            )
                        )
                else:
                    # Простой список
                    getattr(proto, key).extend(value)
            else:
                setattr(proto, key, value)

    return proto


def proto_to_dict(proto) -> Dict:
    """Конвертировать protobuf сообщение в словарь."""
    if proto is None:
        return {}

    from google.protobuf.descriptor import FieldDescriptor

    result = {}

    for field in proto.DESCRIPTOR.fields:
        field_name = field.name
        value = getattr(proto, field_name)

        # Проверяем тип поля
        if field.is_repeated:
            if field.message_type:
                # Список сообщений
                result[field_name] = [proto_to_dict(item) for item in value]
            else:
                # Простой список
                result[field_name] = list(value)
        elif field.message_type:
            # Вложенное сообщение
            if value:
                result[field_name] = proto_to_dict(value)
        elif field.type == FieldDescriptor.TYPE_MESSAGE and hasattr(
            field, "message_type"
        ):
            # Map поле (в protobuf 3+ map представлены как сообщения)
            if hasattr(value, "items"):
                result[field_name] = dict(value)
            else:
                # Обычное вложенное сообщение
                result[field_name] = proto_to_dict(value)
        else:
            # Простое поле
            if value is not None and value != "":
                # Конвертируем специальные типы
                if field.type == FieldDescriptor.TYPE_ENUM:
                    result[field_name] = field.enum_type.values_by_number[value].name
                else:
                    result[field_name] = value

    return result
