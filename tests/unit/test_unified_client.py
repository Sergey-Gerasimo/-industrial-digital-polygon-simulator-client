"""
Unit tests for AsyncUnifiedClient.

Проверяем только клиентскую логику:
- Корректность проксирования вызовов к соответствующим клиентам
- Корректность обработки данных
- Обработку ошибок
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.simulation_client import AsyncUnifiedClient
from src.simulation_client.models import (
    SimulationConfig,
    SimulationResponse,
    GetAllWorkersResponse,
    GetAllSuppliersResponse,
    GetAllWorkplacesResponse,
    GetAllEquipmentResponse,
    GetAllTendersResponse,
)


class TestAsyncUnifiedClient:
    """Тесты для AsyncUnifiedClient."""

    @pytest.fixture
    def mock_sim_client(self):
        """Создать мок SimulationClient."""
        return AsyncMock()

    @pytest.fixture
    def mock_db_client(self):
        """Создать мок DatabaseClient."""
        return AsyncMock()

    @pytest.fixture
    def client(self, mock_sim_client, mock_db_client):
        """Создать UnifiedClient с моками."""
        with patch(
            "src.simulation_client.unified_client.AsyncSimulationClient",
            return_value=mock_sim_client,
        ):
            with patch(
                "src.simulation_client.unified_client.AsyncDatabaseClient",
                return_value=mock_db_client,
            ):
                client = AsyncUnifiedClient()
                client.sim_client = mock_sim_client
                client.db_client = mock_db_client
                return client

    @pytest.mark.asyncio
    async def test_create_simulation(self, client, mock_sim_client):
        """Тест создания симуляции через UnifiedClient."""
        mock_config = SimulationConfig(simulation_id="test-id", capital=10000000)
        mock_sim_client.create_simulation = AsyncMock(return_value=mock_config)

        result = await client.create_simulation()

        # Проверяем, что вызов был проксирован в sim_client
        mock_sim_client.create_simulation.assert_called_once()
        assert isinstance(result, SimulationConfig)
        assert result.simulation_id == "test-id"

    @pytest.mark.asyncio
    async def test_get_simulation(self, client, mock_sim_client):
        """Тест получения симуляции через UnifiedClient."""
        mock_response = MagicMock(spec=SimulationResponse)
        mock_sim_client.get_simulation = AsyncMock(return_value=mock_response)

        result = await client.get_simulation("test-id")

        # Проверяем проксирование
        mock_sim_client.get_simulation.assert_called_once_with("test-id")
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_get_all_workers(self, client, mock_db_client):
        """Тест получения всех работников через UnifiedClient."""
        mock_response = GetAllWorkersResponse(workers=[], total_count=0)
        mock_db_client.get_all_workers = AsyncMock(return_value=mock_response)

        result = await client.get_all_workers()

        # Проверяем проксирование
        mock_db_client.get_all_workers.assert_called_once()
        assert isinstance(result, GetAllWorkersResponse)

    @pytest.mark.asyncio
    async def test_get_all_suppliers(self, client, mock_db_client):
        """Тест получения всех поставщиков через UnifiedClient."""
        mock_response = GetAllSuppliersResponse(suppliers=[], total_count=0)
        mock_db_client.get_all_suppliers = AsyncMock(return_value=mock_response)

        result = await client.get_all_suppliers()

        # Проверяем проксирование
        mock_db_client.get_all_suppliers.assert_called_once()
        assert isinstance(result, GetAllSuppliersResponse)

    @pytest.mark.asyncio
    async def test_get_all_workplaces(self, client, mock_db_client):
        """Тест получения всех рабочих мест через UnifiedClient."""
        mock_response = GetAllWorkplacesResponse(workplaces=[], total_count=0)
        mock_db_client.get_all_workplaces = AsyncMock(return_value=mock_response)

        result = await client.get_all_workplaces()

        # Проверяем проксирование
        mock_db_client.get_all_workplaces.assert_called_once()
        assert isinstance(result, GetAllWorkplacesResponse)

    @pytest.mark.asyncio
    async def test_get_all_equipment(self, client, mock_db_client):
        """Тест получения всего оборудования через UnifiedClient."""
        mock_response = GetAllEquipmentResponse(equipments=[], total_count=0)
        mock_db_client.get_all_equipment = AsyncMock(return_value=mock_response)

        result = await client.get_all_equipment()

        # Проверяем проксирование
        mock_db_client.get_all_equipment.assert_called_once()
        assert isinstance(result, GetAllEquipmentResponse)

    @pytest.mark.asyncio
    async def test_get_all_tenders(self, client, mock_db_client):
        """Тест получения всех тендеров через UnifiedClient."""
        mock_response = GetAllTendersResponse(tenders=[], total_count=0)
        mock_db_client.get_all_tenders = AsyncMock(return_value=mock_response)

        result = await client.get_all_tenders()

        # Проверяем проксирование
        mock_db_client.get_all_tenders.assert_called_once()
        assert isinstance(result, GetAllTendersResponse)

    @pytest.mark.asyncio
    async def test_configure_simulation(self, client, mock_sim_client):
        """Тест настройки симуляции через UnifiedClient."""
        mock_response = MagicMock(spec=SimulationResponse)
        mock_sim_client.set_dealing_with_defects = AsyncMock(return_value=mock_response)
        mock_sim_client.set_sales_strategy = AsyncMock(return_value=mock_response)

        results = await client.configure_simulation(
            simulation_id="test-id",
            dealing_with_defects="Отбраковка",
            sales_strategy="standard",
        )

        # Проверяем, что методы были вызваны
        mock_sim_client.set_dealing_with_defects.assert_called_once_with(
            "test-id", "Отбраковка"
        )
        mock_sim_client.set_sales_strategy.assert_called_once_with(
            "test-id", "standard"
        )
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_get_factory_metrics(self, client, mock_sim_client):
        """Тест получения метрик завода через UnifiedClient."""
        mock_response = MagicMock()
        mock_sim_client.get_factory_metrics = AsyncMock(return_value=mock_response)

        result = await client.get_factory_metrics("test-id")

        # Проверяем проксирование
        mock_sim_client.get_factory_metrics.assert_called_once_with("test-id", 1)
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_get_factory_metrics_with_step(self, client, mock_sim_client):
        """Тест получения метрик завода с step через UnifiedClient."""
        mock_response = MagicMock()
        mock_sim_client.get_factory_metrics = AsyncMock(return_value=mock_response)

        result = await client.get_factory_metrics("test-id", step=5)

        # Проверяем проксирование с правильным step
        mock_sim_client.get_factory_metrics.assert_called_once_with("test-id", 5)
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_get_production_schedule(self, client, mock_sim_client):
        """Тест получения производственного плана через UnifiedClient."""
        mock_response = MagicMock()
        mock_sim_client.get_production_schedule = AsyncMock(return_value=mock_response)

        result = await client.get_production_schedule("test-id")

        # Проверяем проксирование
        mock_sim_client.get_production_schedule.assert_called_once_with("test-id")
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_get_workshop_plan(self, client, mock_sim_client):
        """Тест получения плана цеха через UnifiedClient."""
        mock_response = MagicMock()
        mock_sim_client.get_workshop_plan = AsyncMock(return_value=mock_response)

        result = await client.get_workshop_plan("test-id")

        # Проверяем проксирование
        mock_sim_client.get_workshop_plan.assert_called_once_with("test-id")
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_get_available_lean_improvements(self, client, mock_db_client):
        """Тест получения доступных Lean улучшений через UnifiedClient."""
        mock_response = MagicMock()
        mock_response.improvements = []
        mock_db_client.get_available_lean_improvements = AsyncMock(
            return_value=mock_response
        )

        result = await client.get_available_lean_improvements()

        # Проверяем проксирование без request
        mock_db_client.get_available_lean_improvements.assert_called_once_with(None)
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_ping(self, client, mock_sim_client, mock_db_client):
        """Тест ping через UnifiedClient."""
        mock_sim_client.ping = AsyncMock(return_value=True)
        mock_db_client.ping = AsyncMock(return_value=True)

        result = await client.ping()

        # Проверяем, что оба клиента были вызваны
        mock_sim_client.ping.assert_called_once()
        mock_db_client.ping.assert_called_once()
        assert result == {"simulation_service": True, "database_service": True}
