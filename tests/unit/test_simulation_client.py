"""
Unit tests for AsyncSimulationClient.

Проверяем только клиентскую логику:
- Корректность конвертации Pydantic -> protobuf
- Корректность конвертации protobuf -> Pydantic
- Корректность вызовов методов stub'ов
- Обработку ошибок
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import grpc

from src.simulation_client import AsyncSimulationClient
from src.simulation_client.models import (
    SimulationConfig,
    SimulationResponse,
    Simulation,
    SimulationParameters,
    SimulationResults,
    FactoryMetricsResponse,
    ProductionScheduleResponse,
    ValidationResponse,
    MaterialTypesResponse,
)
from src.simulation_client.proto import simulator_pb2


class TestAsyncSimulationClient:
    """Тесты для AsyncSimulationClient."""

    @pytest.fixture
    def client(self):
        """Создать клиент для тестирования."""
        return AsyncSimulationClient("localhost", 50051)

    @pytest.fixture
    def mock_stub(self):
        """Создать мок stub'а."""
        return AsyncMock()

    @pytest.fixture
    def mock_internal_methods(self, client):
        """Мокировать внутренние методы клиента."""
        with patch.object(client, "_with_retry", new_callable=AsyncMock) as mock_retry:
            with patch.object(
                client, "_rate_limit", new_callable=AsyncMock
            ) as mock_rate:
                with patch.object(
                    client, "_timeout_context", new_callable=MagicMock
                ) as mock_timeout:
                    mock_timeout.return_value.__aenter__ = AsyncMock(return_value=None)
                    mock_timeout.return_value.__aexit__ = AsyncMock(return_value=None)
                    yield {
                        "retry": mock_retry,
                        "rate": mock_rate,
                        "timeout": mock_timeout,
                    }

    @pytest.mark.asyncio
    async def test_create_simulation(self, client, mock_stub, mock_internal_methods):
        """Тест создания симуляции."""
        # Настраиваем мок ответа
        mock_response = MagicMock()
        mock_simulation = MagicMock()
        mock_simulation.simulation_id = "test-sim-id"
        mock_simulation.capital = 10000000
        mock_response.simulations = (
            mock_simulation  # В proto это объект Simulation, не список
        )
        mock_response.timestamp = "2024-01-01T00:00:00"

        # Настраиваем _with_retry для возврата нашего мок-ответа
        mock_internal_methods["retry"].return_value = mock_response

        # Мокируем создание stub'а
        with patch.object(client, "_create_stub", return_value=mock_stub):
            with patch.object(client, "stub", mock_stub, create=True):
                # Вызываем метод
                result = await client.create_simulation()

                # Проверяем, что _with_retry был вызван
                mock_internal_methods["retry"].assert_called_once()
                # Проверяем аргументы вызова _with_retry
                call_args = mock_internal_methods["retry"].call_args[0]
                assert call_args[0] == mock_stub.create_simulation
                assert isinstance(call_args[1], simulator_pb2.CreateSimulationRquest)

                # Проверяем результат
                assert isinstance(result, SimulationConfig)
                assert result.simulation_id == "test-sim-id"

    @pytest.mark.asyncio
    async def test_get_simulation(self, client, mock_stub, mock_internal_methods):
        """Тест получения симуляции."""
        # Настраиваем мок ответа
        mock_response = MagicMock()
        mock_simulation = MagicMock()
        mock_simulation.simulation_id = "test-sim-id"
        mock_simulation.capital = 10000000
        mock_simulation.step = 0
        mock_simulation.parameters = []
        mock_simulation.results = []
        mock_simulation.room_id = "room-1"
        mock_simulation.is_completed = False
        mock_response.simulations = mock_simulation
        mock_response.timestamp = "2024-01-01T00:00:00"

        mock_internal_methods["retry"].return_value = mock_response

        with patch.object(client, "_create_stub", return_value=mock_stub):
            with patch.object(client, "stub", mock_stub, create=True):
                result = await client.get_simulation("test-sim-id")

                # Проверяем вызов
                mock_internal_methods["retry"].assert_called_once()
                call_args = mock_internal_methods["retry"].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.GetSimulationRequest)
                assert call_args.simulation_id == "test-sim-id"

                # Проверяем результат
                assert isinstance(result, SimulationResponse)
                assert result.simulation.simulation_id == "test-sim-id"

    @pytest.mark.asyncio
    async def test_set_sales_strategy(self, client, mock_stub, mock_internal_methods):
        """Тест установки стратегии продаж."""
        mock_response = MagicMock()
        mock_simulation = MagicMock()
        mock_simulation.simulation_id = "test-sim-id"
        mock_simulation.capital = 10000000
        mock_simulation.step = 0
        mock_simulation.room_id = "room-1"
        mock_simulation.is_completed = False
        # parameters и results должны быть пустыми списками, чтобы не вызывать _proto_to_simulation_parameters
        # Если parameters пустой, то _proto_to_simulation_parameters не вызовется
        mock_simulation.parameters = []
        mock_simulation.results = []
        mock_response.simulations = mock_simulation
        mock_response.timestamp = "2024-01-01T00:00:00"

        mock_internal_methods["retry"].return_value = mock_response

        with patch.object(client, "_create_stub", return_value=mock_stub):
            with patch.object(client, "stub", mock_stub, create=True):
                result = await client.set_sales_strategy("test-sim-id", "standard")

                # Проверяем вызов
                mock_internal_methods["retry"].assert_called_once()
                call_args = mock_internal_methods["retry"].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.SetSalesStrategyRequest)
                assert call_args.simulation_id == "test-sim-id"
                assert call_args.strategy == "standard"  # Проверяем правильное поле

                assert isinstance(result, SimulationResponse)

    @pytest.mark.asyncio
    async def test_set_dealing_with_defects(
        self, client, mock_stub, mock_internal_methods
    ):
        """Тест установки политики работы с браком."""
        mock_response = MagicMock()
        mock_simulation = MagicMock()
        mock_simulation.simulation_id = "test-sim-id"
        mock_simulation.capital = 10000000
        mock_simulation.step = 0
        mock_simulation.room_id = "room-1"
        mock_simulation.is_completed = False
        mock_simulation.parameters = []
        mock_simulation.results = []
        mock_response.simulations = mock_simulation
        mock_response.timestamp = "2024-01-01T00:00:00"

        mock_internal_methods["retry"].return_value = mock_response

        with patch.object(client, "_create_stub", return_value=mock_stub):
            with patch.object(client, "stub", mock_stub, create=True):
                result = await client.set_dealing_with_defects(
                    "test-sim-id", "Отбраковка"
                )

                # Проверяем вызов
                mock_internal_methods["retry"].assert_called_once()
                call_args = mock_internal_methods["retry"].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.SetDealingWithDefectsRequest)
                assert call_args.simulation_id == "test-sim-id"
                assert call_args.dealing_with_defects == "Отбраковка"

                assert isinstance(result, SimulationResponse)

    @pytest.mark.asyncio
    async def test_set_certification_status(
        self, client, mock_stub, mock_internal_methods
    ):
        """Тест установки статуса сертификации."""
        mock_response = MagicMock()
        mock_simulation = MagicMock()
        mock_simulation.simulation_id = "test-sim-id"
        mock_simulation.capital = 10000000
        mock_simulation.step = 0
        mock_simulation.room_id = "room-1"
        mock_simulation.is_completed = False
        mock_simulation.parameters = []
        mock_simulation.results = []
        mock_response.simulations = mock_simulation
        mock_response.timestamp = "2024-01-01T00:00:00"

        mock_internal_methods["retry"].return_value = mock_response

        with patch.object(client, "_create_stub", return_value=mock_stub):
            with patch.object(client, "stub", mock_stub, create=True):
                result = await client.set_certification_status(
                    "test-sim-id", "ISO9001", True
                )

                # Проверяем вызов
                mock_internal_methods["retry"].assert_called_once()
                call_args = mock_internal_methods["retry"].call_args[0][1]
                assert isinstance(
                    call_args, simulator_pb2.SetCertificationStatusRequest
                )
                assert call_args.simulation_id == "test-sim-id"
                assert call_args.certificate_type == "ISO9001"
                assert call_args.is_obtained is True

                assert isinstance(result, SimulationResponse)

    @pytest.mark.asyncio
    async def test_set_lean_improvement_status(
        self, client, mock_stub, mock_internal_methods
    ):
        """Тест установки статуса Lean улучшения."""
        mock_response = MagicMock()
        mock_simulation = MagicMock()
        mock_simulation.simulation_id = "test-sim-id"
        mock_simulation.capital = 10000000
        mock_simulation.step = 0
        mock_simulation.room_id = "room-1"
        mock_simulation.is_completed = False
        mock_simulation.parameters = []
        mock_simulation.results = []
        mock_response.simulations = mock_simulation
        mock_response.timestamp = "2024-01-01T00:00:00"

        mock_internal_methods["retry"].return_value = mock_response

        with patch.object(client, "_create_stub", return_value=mock_stub):
            with patch.object(client, "stub", mock_stub, create=True):
                result = await client.set_lean_improvement_status(
                    "test-sim-id", "Улучшение", True
                )

                # Проверяем вызов
                mock_internal_methods["retry"].assert_called_once()
                call_args = mock_internal_methods["retry"].call_args[0][1]
                assert isinstance(
                    call_args, simulator_pb2.SetLeanImprovementStatusRequest
                )
                assert call_args.simulation_id == "test-sim-id"
                assert call_args.name == "Улучшение"
                assert call_args.is_implemented is True

                assert isinstance(result, SimulationResponse)

    @pytest.mark.asyncio
    async def test_get_factory_metrics_without_step(
        self, client, mock_stub, mock_internal_methods
    ):
        """Тест получения метрик завода без указания step (используется значение по умолчанию step=1)."""
        mock_metrics_response = MagicMock()
        mock_metrics = MagicMock()
        mock_metrics.profitability = 0.15
        mock_metrics_response.metrics = mock_metrics
        mock_metrics_response.timestamp = "2024-01-01T00:00:00"

        mock_internal_methods["retry"].return_value = mock_metrics_response

        with patch.object(client, "_create_stub", return_value=mock_stub):
            with patch.object(client, "stub", mock_stub, create=True):
                # Вызываем без указания step - должен использоваться step=1 по умолчанию
                result = await client.get_factory_metrics("test-sim-id")

                # Проверяем вызов get_factory_metrics
                mock_internal_methods["retry"].assert_called_once()

                # Проверяем параметры запроса
                call_args = mock_internal_methods["retry"].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.GetMetricsRequest)
                assert call_args.simulation_id == "test-sim-id"
                assert call_args.step == 1  # step должен быть 1 по умолчанию

                assert isinstance(result, FactoryMetricsResponse)

    @pytest.mark.asyncio
    async def test_get_factory_metrics_with_step(
        self, client, mock_stub, mock_internal_methods
    ):
        """Тест получения метрик завода с указанием step."""
        mock_response = MagicMock()
        mock_metrics = MagicMock()
        mock_metrics.profitability = 0.15
        mock_response.metrics = mock_metrics
        mock_response.timestamp = "2024-01-01T00:00:00"

        mock_internal_methods["retry"].return_value = mock_response

        with patch.object(client, "_create_stub", return_value=mock_stub):
            with patch.object(client, "stub", mock_stub, create=True):
                result = await client.get_factory_metrics("test-sim-id", step=5)

                # Проверяем вызов
                mock_internal_methods["retry"].assert_called_once()
                call_args = mock_internal_methods["retry"].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.GetMetricsRequest)
                assert call_args.simulation_id == "test-sim-id"
                assert call_args.step == 5

                assert isinstance(result, FactoryMetricsResponse)

    @pytest.mark.asyncio
    async def test_get_production_schedule(
        self, client, mock_stub, mock_internal_methods
    ):
        """Тест получения производственного плана."""
        mock_response = MagicMock()
        mock_schedule = MagicMock()
        mock_schedule.rows = []
        mock_response.schedule = mock_schedule
        mock_response.timestamp = "2024-01-01T00:00:00"

        mock_internal_methods["retry"].return_value = mock_response

        with patch.object(client, "_create_stub", return_value=mock_stub):
            with patch.object(client, "stub", mock_stub, create=True):
                result = await client.get_production_schedule("test-sim-id")

                # Проверяем вызов
                mock_internal_methods["retry"].assert_called_once()
                call_args = mock_internal_methods["retry"].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.GetProductionScheduleRequest)
                assert call_args.simulation_id == "test-sim-id"

                assert isinstance(result, ProductionScheduleResponse)

    @pytest.mark.asyncio
    async def test_validate_configuration(
        self, client, mock_stub, mock_internal_methods
    ):
        """Тест валидации конфигурации."""
        mock_response = MagicMock()
        mock_response.is_valid = True
        mock_response.errors = []
        mock_response.warnings = []
        mock_response.timestamp = "2024-01-01T00:00:00"

        mock_internal_methods["retry"].return_value = mock_response

        with patch.object(client, "_create_stub", return_value=mock_stub):
            with patch.object(client, "stub", mock_stub, create=True):
                result = await client.validate_configuration("test-sim-id")

                # Проверяем вызов
                mock_internal_methods["retry"].assert_called_once()
                call_args = mock_internal_methods["retry"].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.ValidateConfigurationRequest)
                assert call_args.simulation_id == "test-sim-id"

                assert isinstance(result, ValidationResponse)
                assert result.is_valid is True

    @pytest.mark.asyncio
    async def test_get_material_types(self, client, mock_stub, mock_internal_methods):
        """Тест получения типов материалов."""
        mock_response = MagicMock()
        mock_response.material_types = ["Тип1", "Тип2"]
        mock_response.timestamp = "2024-01-01T00:00:00"

        mock_internal_methods["retry"].return_value = mock_response

        with patch.object(client, "_create_stub", return_value=mock_stub):
            with patch.object(client, "stub", mock_stub, create=True):
                result = await client.get_material_types()

                # Проверяем вызов
                mock_internal_methods["retry"].assert_called_once()
                call_args = mock_internal_methods["retry"].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.GetMaterialTypesRequest)

                assert isinstance(result, MaterialTypesResponse)
                assert len(result.material_types) == 2

    @pytest.mark.asyncio
    async def test_error_handling(self, client, mock_stub, mock_internal_methods):
        """Тест обработки ошибок gRPC."""
        # Настраиваем мок для выброса ошибки
        error = grpc.RpcError()
        error.code = lambda: grpc.StatusCode.NOT_FOUND
        error.details = lambda: "Simulation not found"
        mock_internal_methods["retry"].side_effect = error

        with patch.object(client, "_create_stub", return_value=mock_stub):
            with patch.object(client, "stub", mock_stub, create=True):
                # Проверяем, что ошибка обрабатывается
                with pytest.raises(
                    Exception
                ):  # Клиент должен обработать и преобразовать ошибку
                    await client.get_simulation("non-existent-id")

                # Проверяем, что _with_retry был вызван
                mock_internal_methods["retry"].assert_called_once()
