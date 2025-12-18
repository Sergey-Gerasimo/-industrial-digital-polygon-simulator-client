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
from simulation_client.models import WarehouseType, GetProcessGraphRequest


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


async def ensure_full_simulation_configuration(
    client: AsyncUnifiedClient, simulation_id: str
) -> None:
    """
    Configure simulation with all required parameters so it can be started.
    """
    (
        suppliers,
        workers,
        logists,
        workplaces,
        tenders,
        defect_policies,
        lean_improvements,
        sales_strategies,
        certifications,
    ) = await asyncio.gather(
        client.get_all_suppliers(),
        client.get_all_workers(),
        client.get_all_logists(),
        client.get_all_workplaces(),
        client.get_all_tenders(),
        client.get_available_defect_policies(),
        client.get_all_lean_improvements(),
        client.get_available_sales_strategies(),
        client.get_available_certifications(),
    )

    assert suppliers.suppliers, "No suppliers available for configuration"
    assert workers.workers, "No workers available for configuration"
    assert workplaces.workplaces, "No workplaces available for configuration"

    # Logist
    if logists.logists:
        await client.set_logist(simulation_id, logists.logists[0].worker_id)
    else:
        await client.set_logist(simulation_id, workers.workers[0].worker_id)

    # Suppliers
    await client.add_supplier(
        simulation_id, suppliers.suppliers[0].supplier_id, is_backup=False
    )
    if len(suppliers.suppliers) > 1:
        await client.add_supplier(
            simulation_id, suppliers.suppliers[1].supplier_id, is_backup=True
        )

    # Warehouse workers
    await client.set_warehouse_worker(
        simulation_id,
        workers.workers[0].worker_id,
        WarehouseType.WAREHOUSE_TYPE_MATERIALS,
    )
    target_worker = (
        workers.workers[1] if len(workers.workers) > 1 else workers.workers[0]
    )
    await client.set_warehouse_worker(
        simulation_id,
        target_worker.worker_id,
        WarehouseType.WAREHOUSE_TYPE_PRODUCTS,
    )

    # Process graph
    process_graph = await client.get_process_graph(
        GetProcessGraphRequest(simulation_id=simulation_id, step=1)
    )
    await client.update_process_graph(simulation_id, process_graph)

    # Tender
    if tenders.tenders:
        await client.add_tender(simulation_id, tenders.tenders[0].tender_id)

    # Defect policy
    if getattr(defect_policies, "policies", None):
        policy = defect_policies.policies[0]
        policy_value = (
            getattr(policy, "id", None) or getattr(policy, "name", None) or policy
        )
        await client.set_dealing_with_defects(simulation_id, policy_value)

    # Lean improvements
    for improvement in lean_improvements.improvements:
        await client.set_lean_improvement_status(simulation_id, improvement.name, True)

    # Sales strategy
    if getattr(sales_strategies, "strategies", None):
        strategy = sales_strategies.strategies[0]
        strategy_value = (
            getattr(strategy, "id", None) or getattr(strategy, "name", None) or strategy
        )
        await client.set_sales_strategy(simulation_id, strategy_value)

    # Certification
    if getattr(certifications, "certifications", None):
        cert = certifications.certifications[0]
        cert_value = getattr(cert, "id", None) or getattr(cert, "name", None) or cert
        await client.set_certification_status(simulation_id, cert_value, True)


@pytest_asyncio.fixture
async def configured_simulation(unified_client) -> AsyncGenerator:
    """Создать и полностью настроить симуляцию, вернуть конфигурацию."""
    config = await unified_client.create_simulation()
    await ensure_full_simulation_configuration(unified_client, config.simulation_id)
    yield config


@pytest_asyncio.fixture
async def configured_simulation_id(configured_simulation) -> AsyncGenerator:
    """Упрощенный доступ только к simulation_id полностью настроенной симуляции."""
    yield configured_simulation.simulation_id


@pytest_asyncio.fixture
async def configure_simulation(unified_client):
    """Возвращает helper для настройки созданной симуляции."""

    async def _configure(simulation_id: str) -> None:
        await ensure_full_simulation_configuration(unified_client, simulation_id)

    return _configure


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
