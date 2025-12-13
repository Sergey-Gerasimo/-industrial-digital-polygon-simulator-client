"""
Configuration for integration tests using Docker Compose.
"""

import asyncio
import sys
import time
import pytest
import pytest_asyncio
import grpc
from testcontainers.compose import DockerCompose
from typing import Generator, AsyncGenerator
from pathlib import Path

# Configure pytest-asyncio for integration tests
pytest.register_assert_rewrite("pytest_asyncio")

from simulation_client import (
    AsyncUnifiedClient,
    AsyncSimulationClient,
    AsyncDatabaseClient,
)
from simulation_client.proto.simulator_pb2 import PingRequest
from simulation_client.proto.simulator_pb2_grpc import (
    SimulationServiceStub,
    SimulationDatabaseManagerStub,
)


# Удалены неиспользуемые фикстуры docker_client и docker_compose_file
# так как теперь используется testcontainers


@pytest.fixture(scope="session")
def simulation_service_port():
    """Port for SimulationService."""
    return 50051


@pytest.fixture(scope="session")
def database_service_port():
    """Port for SimulationDatabaseManager."""
    return 50052


PROJECT_ROOT = Path(__file__).parent.parent.parent

# Добавляем корень проекта в sys.path для импорта модулей
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session", autouse=True)
def docker_compose():
    """Фикстура для управления Docker Compose окружением."""
    compose = DockerCompose(
        str(PROJECT_ROOT),
        compose_file_name="docker-compose.yaml",
        pull=False,
        build=True,  # Собираем образ
    )

    with compose:
        # Ждем готовности PostgreSQL
        max_retries = 60
        for i in range(max_retries):
            try:
                stdout, stderr, exit_code = compose.exec_in_container(
                    service_name="db",
                    command=["pg_isready", "-U", "user"],
                )
                if exit_code == 0:
                    break
            except Exception as e:
                if i == max_retries - 1:
                    raise RuntimeError(f"PostgreSQL не готов после ожидания: {e}")
            if i == max_retries - 1:
                raise RuntimeError("PostgreSQL не готов после ожидания")
            time.sleep(1)

        # Ждем запуска сервиса - проверяем логи
        print("Ожидание запуска simulation_service...")
        max_retries = 120  # Увеличиваем время ожидания
        service_ready = False
        for i in range(max_retries):
            try:
                # Проверяем что контейнер запущен
                stdout, stderr, exit_code = compose.exec_in_container(
                    service_name="simulation_service",
                    command=["python", "-c", "import sys; sys.exit(0)"],
                )
                # Проверяем gRPC порты для обоих сервисов
                channel_db = grpc.insecure_channel("localhost:50052")
                channel_sim = grpc.insecure_channel("localhost:50051")
                try:
                    grpc.channel_ready_future(channel_db).result(timeout=2)
                    grpc.channel_ready_future(channel_sim).result(timeout=2)
                    channel_db.close()
                    channel_sim.close()
                    service_ready = True
                    print("gRPC сервисы готовы!")
                    break
                except Exception:
                    channel_db.close()
                    channel_sim.close()
            except Exception as e:
                if i % 10 == 0:  # Логируем каждые 10 попыток
                    print(f"Ожидание gRPC сервиса... попытка {i}/{max_retries}")
            if not service_ready:
                time.sleep(2)

        if not service_ready:
            # Пробуем получить логи сервиса для отладки
            try:
                stdout, stderr = compose.get_logs("simulation_service")
                print("Логи simulation_service:")
                print(stdout[:2000] if stdout else "Нет логов")
                if stderr:
                    print("Ошибки:")
                    print(stderr[:2000])
            except:
                pass
            raise RuntimeError("gRPC сервис не готов после ожидания")

        yield compose

        # Cleanup happens automatically when exiting context manager


@pytest_asyncio.fixture
async def unified_client(simulation_service_port, database_service_port):
    """Unified client for testing both services."""
    # Create and connect client
    client = AsyncUnifiedClient(
        sim_host="localhost",
        sim_port=simulation_service_port,
        db_host="localhost",
        db_port=database_service_port,
        timeout=10.0,  # Shorter timeout for tests
    )
    await client.connect()
    try:
        yield client
    finally:
        await client.close()


@pytest.fixture
def simulation_client(simulation_service_port):
    """Simulation client for testing SimulationService."""
    client = AsyncSimulationClient(
        host="localhost", port=simulation_service_port, timeout=10.0
    )
    return client


@pytest.fixture
def database_client(database_service_port):
    """Database client for testing SimulationDatabaseManager."""
    client = AsyncDatabaseClient(
        host="localhost", port=database_service_port, timeout=10.0
    )
    return client
