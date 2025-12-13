"""
Unit tests for AsyncDatabaseClient.

Проверяем только клиентскую логику:
- Корректность конвертации Pydantic -> protobuf
- Корректность конвертации protobuf -> Pydantic
- Корректность вызовов методов stub'ов
- Обработку ошибок
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import grpc

from src.simulation_client import AsyncDatabaseClient
from src.simulation_client.models import (
    CreateWorkerRequest,
    CreateSupplierRequest,
    CreateWorkplaceRequest,
    CreateLeanImprovementRequest,
    CreateEquipmentRequest,
    GetAllWorkersResponse,
    GetAllSuppliersResponse,
    GetAllWorkplacesResponse,
    GetAllLeanImprovementsResponse,
    Worker,
    Supplier,
    Workplace,
    LeanImprovement,
    Equipment,
)
from src.simulation_client.proto import simulator_pb2


class TestAsyncDatabaseClient:
    """Тесты для AsyncDatabaseClient."""

    @pytest.fixture
    def client(self):
        """Создать клиент для тестирования."""
        return AsyncDatabaseClient("localhost", 50052)

    @pytest.fixture
    def mock_stub(self):
        """Создать мок stub'а."""
        return AsyncMock()

    @pytest.fixture
    def mock_internal_methods(self, client):
        """Мокировать внутренние методы клиента."""
        with patch.object(client, '_with_retry', new_callable=AsyncMock) as mock_retry:
            with patch.object(client, '_rate_limit', new_callable=AsyncMock) as mock_rate:
                with patch.object(client, '_timeout_context', new_callable=MagicMock) as mock_timeout:
                    with patch.object(client, '_ensure_connected') as mock_ensure:
                        mock_timeout.return_value.__aenter__ = AsyncMock(return_value=None)
                        mock_timeout.return_value.__aexit__ = AsyncMock(return_value=None)
                        yield {
                            'retry': mock_retry,
                            'rate': mock_rate,
                            'timeout': mock_timeout,
                            'ensure': mock_ensure,
                        }

    @pytest.mark.asyncio
    async def test_create_worker(self, client, mock_stub, mock_internal_methods):
        """Тест создания работника."""
        # Настраиваем мок ответа
        mock_response = MagicMock()
        mock_response.worker_id = "worker-1"
        mock_response.name = "Иван"
        mock_response.qualification = 5
        mock_response.specialty = "Сборка"
        mock_response.salary = 50000
        
        mock_internal_methods['retry'].return_value = mock_response

        with patch.object(client, '_create_stub', return_value=mock_stub):
            with patch.object(client, 'stub', mock_stub, create=True):
                request = CreateWorkerRequest(
                    name="Иван",
                    qualification=5,
                    specialty="Сборка",
                    salary=50000,
                )
                result = await client.create_worker(request)

                # Проверяем вызов
                mock_internal_methods['retry'].assert_called_once()
                call_args = mock_internal_methods['retry'].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.CreateWorkerRequest)
                assert call_args.name == "Иван"
                assert call_args.qualification == 5
                assert call_args.specialty == "Сборка"
                assert call_args.salary == 50000

                # Проверяем результат
                assert isinstance(result, Worker)
                assert result.worker_id == "worker-1"
                assert result.name == "Иван"

    @pytest.mark.asyncio
    async def test_create_supplier(self, client, mock_stub, mock_internal_methods):
        """Тест создания поставщика."""
        mock_response = MagicMock()
        mock_response.supplier_id = "supplier-1"
        mock_response.name = "Поставщик"
        mock_response.product_name = "Продукт"
        mock_response.material_type = "Металл"
        mock_response.delivery_period = 30
        mock_response.special_delivery_period = 10
        mock_response.reliability = 0.95
        mock_response.product_quality = 0.9
        mock_response.cost = 1000
        mock_response.special_delivery_cost = 1500
        
        mock_internal_methods['retry'].return_value = mock_response

        with patch.object(client, '_create_stub', return_value=mock_stub):
            with patch.object(client, 'stub', mock_stub, create=True):
                request = CreateSupplierRequest(
                    name="Поставщик",
                    product_name="Продукт",
                    material_type="Металл",
                    delivery_period=30,
                    special_delivery_period=10,
                    reliability=0.95,
                    product_quality=0.9,
                    cost=1000,
                    special_delivery_cost=1500,
                )
                result = await client.create_supplier(request)

                # Проверяем вызов
                mock_internal_methods['retry'].assert_called_once()
                call_args = mock_internal_methods['retry'].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.CreateSupplierRequest)
                assert call_args.name == "Поставщик"
                assert call_args.material_type == "Металл"

                # Проверяем результат
                assert isinstance(result, Supplier)
                assert result.supplier_id == "supplier-1"
                assert result.material_type == "Металл"

    @pytest.mark.asyncio
    async def test_create_workplace_with_required_equipment(self, client, mock_stub, mock_internal_methods):
        """Тест создания рабочего места с required_equipment."""
        mock_response = MagicMock()
        mock_response.workplace_id = "wp-1"
        mock_response.workplace_name = "Рабочее место"
        mock_response.required_speciality = "Сборка"
        mock_response.required_qualification = 5
        mock_response.required_equipment = "Станок"  # Важное поле!
        mock_response.required_stages = ["Сборка", "Проверка"]
        mock_response.is_start_node = False
        mock_response.is_end_node = False
        mock_response.next_workplace_ids = []
        # worker и equipment должны быть None или falsy, чтобы не вызывать _proto_to_worker
        # Используем специальный класс, который возвращает False при проверке if
        class FalsyMock:
            def __bool__(self):
                return False
            def __len__(self):
                return 0
        
        mock_response.worker = FalsyMock()
        mock_response.equipment = FalsyMock()
        
        mock_internal_methods['retry'].return_value = mock_response

        with patch.object(client, '_create_stub', return_value=mock_stub):
            with patch.object(client, 'stub', mock_stub, create=True):
                request = CreateWorkplaceRequest(
                    workplace_name="Рабочее место",
                    required_speciality="Сборка",
                    required_qualification=5,
                    required_equipment="Станок",  # Проверяем это поле
                    required_stages=["Сборка", "Проверка"],
                )
                result = await client.create_workplace(request)

                # Проверяем вызов
                mock_internal_methods['retry'].assert_called_once()
                call_args = mock_internal_methods['retry'].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.CreateWorkplaceRequest)
                assert call_args.workplace_name == "Рабочее место"
                assert call_args.required_equipment == "Станок"  # Проверяем правильное поле
                # worker_id не должно быть в proto
                assert not hasattr(call_args, 'worker_id') or getattr(call_args, 'worker_id', '') == ''

                # Проверяем результат
                assert isinstance(result, Workplace)
                assert result.workplace_id == "wp-1"
                assert result.required_equipment == "Станок"

    @pytest.mark.asyncio
    async def test_create_lean_improvement(self, client, mock_stub, mock_internal_methods):
        """Тест создания Lean улучшения."""
        mock_response = MagicMock()
        mock_response.improvement_id = "improvement-1"
        mock_response.name = "Улучшение"
        mock_response.is_implemented = False
        mock_response.implementation_cost = 100000
        mock_response.efficiency_gain = 0.15
        
        mock_internal_methods['retry'].return_value = mock_response

        with patch.object(client, '_create_stub', return_value=mock_stub):
            with patch.object(client, 'stub', mock_stub, create=True):
                request = CreateLeanImprovementRequest(
                    name="Улучшение",
                    is_implemented=False,
                    implementation_cost=100000,
                    efficiency_gain=0.15,
                )
                result = await client.create_lean_improvement(request)

                # Проверяем вызов
                mock_internal_methods['retry'].assert_called_once()
                call_args = mock_internal_methods['retry'].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.CreateLeanImprovementRequest)
                assert call_args.name == "Улучшение"
                assert call_args.is_implemented is False

                # Проверяем результат
                assert isinstance(result, LeanImprovement)
                assert result.improvement_id == "improvement-1"

    @pytest.mark.asyncio
    async def test_create_equipment(self, client, mock_stub, mock_internal_methods):
        """Тест создания оборудования."""
        mock_response = MagicMock()
        mock_response.equipment_id = "eq-1"
        mock_response.name = "Станок"
        mock_response.equipment_type = "Токарный"  # Важное поле!
        mock_response.reliability = 0.95
        mock_response.maintenance_period = 30
        mock_response.maintenance_cost = 5000
        mock_response.cost = 100000
        mock_response.repair_cost = 10000
        mock_response.repair_time = 2
        
        mock_internal_methods['retry'].return_value = mock_response

        with patch.object(client, '_create_stub', return_value=mock_stub):
            with patch.object(client, 'stub', mock_stub, create=True):
                request = CreateEquipmentRequest(
                    name="Станок",
                    equipment_type="Токарный",
                    reliability=0.95,
                    maintenance_period=30,
                    maintenance_cost=5000,
                    cost=100000,
                    repair_cost=10000,
                    repair_time=2,
                )
                result = await client.create_equipment(request)

                # Проверяем вызов
                mock_internal_methods['retry'].assert_called_once()
                call_args = mock_internal_methods['retry'].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.CreateEquipmentRequest)
                assert call_args.name == "Станок"
                assert call_args.equipment_type == "Токарный"

                # Проверяем результат
                assert isinstance(result, Equipment)
                assert result.equipment_id == "eq-1"
                assert result.equipment_type == "Токарный"

    @pytest.mark.asyncio
    async def test_get_all_workers(self, client, mock_stub, mock_internal_methods):
        """Тест получения всех работников."""
        mock_response = MagicMock()
        mock_worker1 = MagicMock()
        mock_worker1.worker_id = "worker-1"
        mock_worker1.name = "Иван"
        mock_worker1.qualification = 5
        mock_worker1.specialty = "Сборка"
        mock_worker1.salary = 50000
        mock_response.workers = [mock_worker1]
        mock_response.total_count = 1
        
        mock_internal_methods['retry'].return_value = mock_response

        with patch.object(client, '_create_stub', return_value=mock_stub):
            with patch.object(client, 'stub', mock_stub, create=True):
                result = await client.get_all_workers()

                # Проверяем вызов
                mock_internal_methods['retry'].assert_called_once()
                call_args = mock_internal_methods['retry'].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.GetAllWorkersRequest)

                # Проверяем результат
                assert isinstance(result, GetAllWorkersResponse)
                assert result.total_count == 1
                assert len(result.workers) == 1
                assert result.workers[0].worker_id == "worker-1"

    @pytest.mark.asyncio
    async def test_get_all_lean_improvements_without_request(self, client, mock_stub, mock_internal_methods):
        """Тест получения всех Lean улучшений без request."""
        mock_response = MagicMock()
        mock_improvement = MagicMock()
        mock_improvement.improvement_id = "improvement-1"
        mock_improvement.name = "Улучшение"
        mock_improvement.is_implemented = False
        mock_improvement.implementation_cost = 100000
        mock_improvement.efficiency_gain = 0.15
        mock_response.improvements = [mock_improvement]
        mock_response.total_count = 1
        
        mock_internal_methods['retry'].return_value = mock_response

        with patch.object(client, '_create_stub', return_value=mock_stub):
            with patch.object(client, 'stub', mock_stub, create=True):
                result = await client.get_all_lean_improvements()

                # Проверяем вызов
                mock_internal_methods['retry'].assert_called_once()
                call_args = mock_internal_methods['retry'].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.GetAllLeanImprovementsRequest)

                # Проверяем результат
                assert isinstance(result, GetAllLeanImprovementsResponse)
                assert result.total_count == 1

    @pytest.mark.asyncio
    async def test_get_available_lean_improvements_without_request(self, client, mock_stub, mock_internal_methods):
        """Тест получения доступных Lean улучшений без request."""
        mock_response = MagicMock()
        mock_improvement = MagicMock()
        mock_improvement.improvement_id = "improvement-1"
        mock_improvement.name = "Улучшение"
        mock_response.improvements = [mock_improvement]
        mock_response.timestamp = "2024-01-01T00:00:00"
        
        mock_internal_methods['retry'].return_value = mock_response

        with patch.object(client, '_create_stub', return_value=mock_stub):
            with patch.object(client, 'stub', mock_stub, create=True):
                result = await client.get_available_lean_improvements()

                # Проверяем вызов
                mock_internal_methods['retry'].assert_called_once()
                call_args = mock_internal_methods['retry'].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.GetAvailableLeanImprovementsRequest)

                # Проверяем результат
                assert len(result.improvements) == 1

    @pytest.mark.asyncio
    async def test_get_available_material_types(self, client, mock_stub, mock_internal_methods):
        """Тест получения доступных типов материалов."""
        mock_response = MagicMock()
        mock_response.material_types = ["Металл", "Пластик"]
        mock_response.timestamp = "2024-01-01T00:00:00"
        
        mock_internal_methods['retry'].return_value = mock_response

        with patch.object(client, '_create_stub', return_value=mock_stub):
            with patch.object(client, 'stub', mock_stub, create=True):
                result = await client.get_available_material_types()

                # Проверяем вызов
                mock_internal_methods['retry'].assert_called_once()
                call_args = mock_internal_methods['retry'].call_args[0][1]
                assert isinstance(call_args, simulator_pb2.GetMaterialTypesRequest)

                # Проверяем результат
                assert len(result.material_types) == 2
                assert "Металл" in result.material_types

    @pytest.mark.asyncio
    async def test_error_handling(self, client, mock_stub, mock_internal_methods):
        """Тест обработки ошибок gRPC."""
        error = grpc.RpcError()
        error.code = lambda: grpc.StatusCode.NOT_FOUND
        error.details = lambda: "Worker not found"
        mock_internal_methods['retry'].side_effect = error

        with patch.object(client, '_create_stub', return_value=mock_stub):
            with patch.object(client, 'stub', mock_stub, create=True):
                with pytest.raises(Exception):
                    await client.get_all_workers()

                # Проверяем, что _with_retry был вызван
                mock_internal_methods['retry'].assert_called_once()

