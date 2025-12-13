import asyncio
import grpc
from typing import Optional, List, Dict, Any
import logging

from .base_client import AsyncBaseClient
from .proto import simulator_pb2
from .proto import simulator_pb2_grpc
from .models import *
from .exceptions import *

logger = logging.getLogger(__name__)


class AsyncDatabaseClient(AsyncBaseClient):
    """
    Асинхронный клиент для SimulationDatabaseManager.

    Работает на порту 50052 (или другом указанном порту).

    Пример использования:
    ```python
    async with AsyncDatabaseClient("localhost", 50052) as client:
        suppliers = await client.get_all_suppliers()
        workers = await client.get_all_workers()
        equipment = await client.get_all_equipment()
    ```
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 50052,  # 👈 Порт для DatabaseManager (отличается!)
        max_retries: int = 3,
        timeout: float = 30.0,
        rate_limit: Optional[float] = None,
        enable_logging: bool = True,
    ):
        super().__init__(host, port, max_retries, timeout, rate_limit, enable_logging)

    def _create_stub(self, channel: grpc.aio.Channel):
        """Создать stub для SimulationDatabaseManager."""
        return simulator_pb2_grpc.SimulationDatabaseManagerStub(channel)

    def _get_service_name(self) -> str:
        """Получить имя сервиса для логирования."""
        return "DatabaseManager"

    def _parse_ping_response(self, response) -> bool:
        """Парсить ответ ping для DatabaseManager."""
        return response.success

    # ==================== Управление поставщиками ====================

    async def get_all_suppliers(self) -> GetAllSuppliersResponse:
        """
        Получить всех поставщиков.

        Returns:
            GetAllSuppliersResponse: Ответ со всеми поставщиками
        """
        self._ensure_connected()
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_all_suppliers, simulator_pb2.GetAllSuppliersRequest()
                )
                return GetAllSuppliersResponse(
                    suppliers=[self._proto_to_supplier(s) for s in response.suppliers],
                    total_count=response.total_count,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get all suppliers")

    async def create_supplier(self, request: CreateSupplierRequest) -> Supplier:
        """
        Создать нового поставщика.

        Args:
            request: Запрос создания поставщика

        Returns:
            Supplier: Созданный поставщик
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.CreateSupplierRequest(
                    name=request.name,
                    product_name=request.product_name,
                    material_type=request.material_type,
                    delivery_period=request.delivery_period,
                    special_delivery_period=request.special_delivery_period,
                    reliability=request.reliability,
                    product_quality=request.product_quality,
                    cost=request.cost,
                    special_delivery_cost=request.special_delivery_cost,
                )

                response = await self._with_retry(
                    self.stub.create_supplier, proto_request
                )

                return self._proto_to_supplier(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Create supplier")

    async def update_supplier(self, request: UpdateSupplierRequest) -> Supplier:
        """
        Обновить поставщика.

        Args:
            request: Запрос обновления поставщика

        Returns:
            Supplier: Обновленный поставщик
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.UpdateSupplierRequest(
                    supplier_id=request.supplier_id,
                    name=request.name,
                    product_name=request.product_name,
                    material_type=request.material_type,
                    delivery_period=request.delivery_period,
                    special_delivery_period=request.special_delivery_period,
                    reliability=request.reliability,
                    product_quality=request.product_quality,
                    cost=request.cost,
                    special_delivery_cost=request.special_delivery_cost,
                )

                response = await self._with_retry(
                    self.stub.update_supplier, proto_request
                )

                return self._proto_to_supplier(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Update supplier")

    async def delete_supplier(self, request: DeleteSupplierRequest) -> SuccessResponse:
        """
        Удалить поставщика.

        Args:
            request: Запрос удаления поставщика

        Returns:
            SuccessResponse: Результат удаления
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                # Для DatabaseManager simulation_id может быть опциональным
                proto_request = simulator_pb2.DeleteSupplierRequest(
                    supplier_id=request.supplier_id,
                    simulation_id=getattr(
                        request, "simulation_id", ""
                    ),  # Опционально для DatabaseManager
                )

                response = await self._with_retry(
                    self.stub.delete_supplier, proto_request
                )

                return SuccessResponse(
                    success=response.success,
                    message=response.message,
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Delete supplier")

    # ==================== Управление работниками ====================

    async def get_all_workers(self) -> GetAllWorkersResponse:
        """
        Получить всех работников.

        Returns:
            GetAllWorkersResponse: Ответ со всеми работниками
        """
        self._ensure_connected()
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_all_workers, simulator_pb2.GetAllWorkersRequest()
                )

                return GetAllWorkersResponse(
                    workers=[self._proto_to_worker(w) for w in response.workers],
                    total_count=response.total_count,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get all workers")

    async def create_worker(self, request: CreateWorkerRequest) -> Worker:
        """
        Создать нового работника.

        Args:
            request: Запрос создания работника

        Returns:
            Worker: Созданный работник
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.CreateWorkerRequest(
                    name=request.name,
                    qualification=request.qualification,
                    specialty=request.specialty,
                    salary=request.salary,
                )

                response = await self._with_retry(
                    self.stub.create_worker, proto_request
                )

                return self._proto_to_worker(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Create worker")

    async def update_worker(self, request: UpdateWorkerRequest) -> Worker:
        """
        Обновить работника.

        Args:
            request: Запрос обновления работника

        Returns:
            Worker: Обновленный работник
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.UpdateWorkerRequest(
                    worker_id=request.worker_id,
                    name=request.name,
                    qualification=request.qualification,
                    specialty=request.specialty,
                    salary=request.salary,
                )

                response = await self._with_retry(
                    self.stub.update_worker, proto_request
                )

                return self._proto_to_worker(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Update worker")

    async def delete_worker(self, request: DeleteWorkerRequest) -> SuccessResponse:
        """
        Удалить работника.

        Args:
            request: Запрос удаления работника

        Returns:
            SuccessResponse: Результат удаления
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.DeleteWorkerRequest(
                    worker_id=request.worker_id
                )

                response = await self._with_retry(
                    self.stub.delete_worker, proto_request
                )

                return SuccessResponse(
                    success=response.success,
                    message=response.message,
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Delete worker")

    # ==================== Управление логистами ====================

    async def get_all_logists(self) -> GetAllLogistsResponse:
        """
        Получить всех логистов.

        Returns:
            GetAllLogistsResponse: Ответ со всеми логистами
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_all_logists, simulator_pb2.GetAllLogistsRequest()
                )

                return GetAllLogistsResponse(
                    logists=[self._proto_to_logist(l) for l in response.logists],
                    total_count=response.total_count,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get all logists")

    async def create_logist(self, request: CreateLogistRequest) -> Logist:
        """
        Создать нового логиста.

        Args:
            request: Запрос создания логиста

        Returns:
            Logist: Созданный логист
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.CreateLogistRequest(
                    name=request.name,
                    qualification=request.qualification,
                    specialty=request.specialty,
                    salary=request.salary,
                    speed=request.speed,
                    vehicle_type=request.vehicle_type,
                )

                response = await self._with_retry(
                    self.stub.create_logist, proto_request
                )

                return self._proto_to_logist(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Create logist")

    async def update_logist(self, request: UpdateLogistRequest) -> Logist:
        """
        Обновить логиста.

        Args:
            request: Запрос обновления логиста

        Returns:
            Logist: Обновленный логист
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.UpdateLogistRequest(
                    worker_id=request.worker_id,
                    name=request.name,
                    qualification=request.qualification,
                    specialty=request.specialty,
                    salary=request.salary,
                    speed=request.speed,
                    vehicle_type=request.vehicle_type,
                )

                response = await self._with_retry(
                    self.stub.update_logist, proto_request
                )

                return self._proto_to_logist(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Update logist")

    async def delete_logist(self, request: DeleteLogistRequest) -> SuccessResponse:
        """
        Удалить логиста.

        Args:
            request: Запрос удаления логиста

        Returns:
            SuccessResponse: Результат удаления
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.DeleteLogistRequest(
                    worker_id=request.worker_id
                )

                response = await self._with_retry(
                    self.stub.delete_logist, proto_request
                )

                return SuccessResponse(
                    success=response.success,
                    message=response.message,
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Delete logist")

    # ==================== Управление оборудованием ====================

    async def get_all_equipment(self) -> GetAllEquipmentResponse:
        """
        Получить всё оборудование.

        Returns:
            GetAllEquipmentResponse: Ответ со всем оборудованием
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_all_equipment, simulator_pb2.GetAllEquipmentRequest()
                )

                return GetAllEquipmentResponse(
                    equipments=[
                        self._proto_to_equipment(e) for e in response.equipments
                    ],
                    total_count=response.total_count,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get all equipment")

    async def create_equipment(self, request: CreateEquipmentRequest) -> Equipment:
        """
        Создать новое оборудование.

        Args:
            request: Запрос создания оборудования

        Returns:
            Equipment: Созданное оборудование
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.CreateEquipmentRequest(
                    name=request.name,
                    equipment_type=request.equipment_type,
                    reliability=request.reliability,
                    maintenance_period=request.maintenance_period,
                    maintenance_cost=request.maintenance_cost,
                    cost=request.cost,
                    repair_cost=request.repair_cost,
                    repair_time=request.repair_time,
                )

                response = await self._with_retry(
                    self.stub.create_equipment, proto_request
                )

                return self._proto_to_equipment(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Create equipment")

    async def update_equipment(self, request: UpdateEquipmentRequest) -> Equipment:
        """
        Обновить оборудование.

        Args:
            request: Запрос обновления оборудования

        Returns:
            Equipment: Обновленное оборудование
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.UpdateEquipmentRequest(
                    equipment_id=request.equipment_id,
                    name=request.name,
                    equipment_type=request.equipment_type,
                    reliability=request.reliability,
                    maintenance_period=request.maintenance_period,
                    maintenance_cost=request.maintenance_cost,
                    cost=request.cost,
                    repair_cost=request.repair_cost,
                    repair_time=request.repair_time,
                )

                response = await self._with_retry(
                    self.stub.update_equipment, proto_request
                )

                return self._proto_to_equipment(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Update equipment")

    async def delete_equipment(
        self, request: DeleteEquipmentRequest
    ) -> simulator_pb2.SuccessResponse:
        """
        Удалить оборудование.

        Args:
            request: Запрос удаления оборудования

        Returns:
            SuccessResponse: Результат удаления
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.DeleteEquipmentRequest(
                    equipment_id=request.equipment_id
                )

                response = await self._with_retry(
                    self.stub.delete_equipment, proto_request
                )

                return SuccessResponse(
                    success=response.success,
                    message=response.message,
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Delete equipment")

    # ==================== Управление тендерами ====================

    async def get_all_tenders(self) -> GetAllTendersResponse:
        """
        Получить все тендеры.

        Returns:
            GetAllTendersResponse: Ответ со всеми тендерами
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_all_tenders, simulator_pb2.GetAllTendersRequest()
                )

                return GetAllTendersResponse(
                    tenders=[self._proto_to_tender(t) for t in response.tenders],
                    total_count=response.total_count,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get all tenders")

    async def create_tender(self, request: CreateTenderRequest) -> Tender:
        """
        Создать новый тендер.

        Args:
            request: Запрос создания тендера

        Returns:
            Tender: Созданный тендер
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.CreateTenderRequest(
                    consumer_id=request.consumer_id,
                    cost=request.cost,
                    quantity_of_products=request.quantity_of_products,
                    penalty_per_day=request.penalty_per_day,
                    warranty_years=request.warranty_years,
                    payment_form=request.payment_form,
                )

                response = await self._with_retry(
                    self.stub.create_tender, proto_request
                )

                return self._proto_to_tender(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Create tender")

    async def update_tender(self, request: UpdateTenderRequest) -> Tender:
        """
        Обновить тендер.

        Args:
            request: Запрос обновления тендера

        Returns:
            Tender: Обновленный тендер
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.UpdateTenderRequest(
                    tender_id=request.tender_id,
                    consumer_id=request.consumer_id,
                    cost=request.cost,
                    quantity_of_products=request.quantity_of_products,
                    penalty_per_day=request.penalty_per_day,
                    warranty_years=request.warranty_years,
                    payment_form=request.payment_form,
                )

                response = await self._with_retry(
                    self.stub.update_tender, proto_request
                )

                return self._proto_to_tender(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Update tender")

    async def delete_tender(self, request: DeleteTenderRequest) -> SuccessResponse:
        """
        Удалить тендер.

        Args:
            request: Запрос удаления тендера

        Returns:
            SuccessResponse: Результат удаления
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.DeleteTenderRequest(
                    tender_id=request.tender_id
                )

                response = await self._with_retry(
                    self.stub.delete_tender, proto_request
                )

                return SuccessResponse(
                    success=response.success,
                    message=response.message,
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Delete tender")

    # ==================== Управление складами ====================

    async def get_warehouse(self, request: GetWarehouseRequest) -> Warehouse:
        """
        Получить информацию о складе.

        Args:
            request: Запрос получения склада

        Returns:
            Warehouse: Модель склада
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.GetWarehouseRequest(
                    warehouse_id=request.warehouse_id
                )

                response = await self._with_retry(
                    self.stub.get_warehouse, proto_request
                )

                return self._proto_to_warehouse(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get warehouse")

    # ==================== Управление заказчиками ====================

    async def get_all_consumers(self) -> GetAllConsumersResponse:
        """
        Получить всех заказчиков.

        Returns:
            GetAllConsumersResponse: Ответ со всеми заказчиками
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_all_consumers, simulator_pb2.GetAllConsumersRequest()
                )

                return GetAllConsumersResponse(
                    consumers=[self._proto_to_consumer(c) for c in response.consumers],
                    total_count=response.total_count,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get all consumers")

    async def create_consumer(self, request: CreateConsumerRequest) -> Consumer:
        """
        Создать нового заказчика.

        Args:
            request: Запрос создания заказчика

        Returns:
            Consumer: Созданный заказчик
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.CreateConsumerRequest(
                    name=request.name, type=request.type
                )

                response = await self._with_retry(
                    self.stub.create_consumer, proto_request
                )

                return self._proto_to_consumer(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Create consumer")

    async def update_consumer(self, request: UpdateConsumerRequest) -> Consumer:
        """
        Обновить заказчика.

        Args:
            request: Запрос обновления заказчика

        Returns:
            Consumer: Обновленный заказчик
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.UpdateConsumerRequest(
                    consumer_id=request.consumer_id,
                    name=request.name,
                    type=request.type,
                )

                response = await self._with_retry(
                    self.stub.update_consumer, proto_request
                )

                return self._proto_to_consumer(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Update consumer")

    async def delete_consumer(self, request: DeleteConsumerRequest) -> SuccessResponse:
        """
        Удалить заказчика.

        Args:
            request: Запрос удаления заказчика

        Returns:
            SuccessResponse: Результат удаления
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.DeleteConsumerRequest(
                    consumer_id=request.consumer_id
                )

                response = await self._with_retry(
                    self.stub.delete_consumer, proto_request
                )

                return SuccessResponse(
                    success=response.success,
                    message=response.message,
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Delete consumer")

    # ==================== Управление рабочими местами ====================

    async def get_all_workplaces(self) -> GetAllWorkplacesResponse:
        """
        Получить все рабочие места.

        Returns:
            GetAllWorkplacesResponse: Ответ со всеми рабочими местами
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_all_workplaces,
                    simulator_pb2.GetAllWorkplacesRequest(),
                )

                return GetAllWorkplacesResponse(
                    workplaces=[
                        self._proto_to_workplace(wp) for wp in response.workplaces
                    ],
                    total_count=response.total_count,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get all workplaces")

    async def create_workplace(self, request: CreateWorkplaceRequest) -> Workplace:
        """
        Создать новое рабочее место.

        Args:
            request: Запрос создания рабочего места

        Returns:
            Workplace: Созданное рабочее место
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.CreateWorkplaceRequest(
                    workplace_name=request.workplace_name,
                    required_speciality=request.required_speciality,
                    required_qualification=request.required_qualification,
                    required_equipment=request.required_equipment,
                    required_stages=request.required_stages,
                )

                response = await self._with_retry(
                    self.stub.create_workplace, proto_request
                )

                return self._proto_to_workplace(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Create workplace")

    async def update_workplace(self, request: UpdateWorkplaceRequest) -> Workplace:
        """
        Обновить рабочее место.

        Args:
            request: Запрос обновления рабочего места

        Returns:
            Workplace: Обновленное рабочее место
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.UpdateWorkplaceRequest(
                    workplace_id=request.workplace_id,
                    workplace_name=request.workplace_name,
                    required_speciality=request.required_speciality,
                    required_qualification=request.required_qualification,
                    required_equipment=request.required_equipment,
                    required_stages=request.required_stages,
                )

                response = await self._with_retry(
                    self.stub.update_workplace, proto_request
                )

                return self._proto_to_workplace(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Update workplace")

    async def delete_workplace(
        self, request: DeleteWorkplaceRequest
    ) -> simulator_pb2.SuccessResponse:
        """
        Удалить рабочее место.

        Args:
            request: Запрос удаления рабочего места

        Returns:
            SuccessResponse: Результат удаления
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.DeleteWorkplaceRequest(
                    workplace_id=request.workplace_id
                )

                response = await self._with_retry(
                    self.stub.delete_workplace, proto_request
                )

                return SuccessResponse(
                    success=response.success,
                    message=response.message,
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Delete workplace")

    # ==================== Управление картами процесса ====================

    async def get_process_graph(self, request: GetProcessGraphRequest) -> ProcessGraph:
        """
        Получить карту процесса.

        Args:
            request: Запрос получения карты процесса

        Returns:
            ProcessGraph: Карта процесса
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.GetProcessGraphRequest(
                    process_graph_id=request.process_graph_id
                )

                response = await self._with_retry(
                    self.stub.get_process_graph, proto_request
                )

                return self._proto_to_process_graph(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get process graph")

    # ==================== Вспомогательные методы ====================

    def _proto_to_supplier(self, proto_supplier) -> Supplier:
        """Конвертировать protobuf Supplier в Pydantic модель."""
        return Supplier(
            supplier_id=proto_supplier.supplier_id,
            name=proto_supplier.name,
            product_name=proto_supplier.product_name,
            material_type=proto_supplier.material_type,
            delivery_period=proto_supplier.delivery_period,
            special_delivery_period=proto_supplier.special_delivery_period,
            reliability=proto_supplier.reliability,
            product_quality=proto_supplier.product_quality,
            cost=proto_supplier.cost,
            special_delivery_cost=proto_supplier.special_delivery_cost,
        )

    def _proto_to_worker(self, proto_worker) -> Worker:
        """Конвертировать protobuf Worker в Pydantic модель."""
        return Worker(
            worker_id=proto_worker.worker_id,
            name=proto_worker.name,
            qualification=proto_worker.qualification,
            specialty=proto_worker.specialty,
            salary=proto_worker.salary,
        )

    def _proto_to_logist(self, proto_logist) -> Logist:
        """Конвертировать protobuf Logist в Pydantic модель."""
        return Logist(
            worker_id=proto_logist.worker_id,
            name=proto_logist.name,
            qualification=proto_logist.qualification,
            specialty=proto_logist.specialty,
            salary=proto_logist.salary,
            speed=proto_logist.speed,
            vehicle_type=proto_logist.vehicle_type,
        )

    def _proto_to_equipment(self, proto_equipment) -> Equipment:
        """Конвертировать protobuf Equipment в Pydantic модель."""
        return Equipment(
            equipment_id=proto_equipment.equipment_id,
            name=proto_equipment.name,
            equipment_type=proto_equipment.equipment_type,  # Добавлено поле equipment_type
            reliability=proto_equipment.reliability,
            maintenance_period=proto_equipment.maintenance_period,
            maintenance_cost=proto_equipment.maintenance_cost,
            cost=proto_equipment.cost,
            repair_cost=proto_equipment.repair_cost,
            repair_time=proto_equipment.repair_time,
        )

    def _proto_to_warehouse(self, proto_warehouse) -> Warehouse:
        """Конвертировать protobuf Warehouse в Pydantic модель."""
        return Warehouse(
            warehouse_id=proto_warehouse.warehouse_id,
            inventory_worker=(
                self._proto_to_worker(proto_warehouse.inventory_worker)
                if proto_warehouse.inventory_worker
                else None
            ),
            size=proto_warehouse.size,
            loading=proto_warehouse.loading,
            materials=dict(proto_warehouse.materials),
        )

    def _proto_to_consumer(self, proto_consumer) -> Consumer:
        """Конвертировать protobuf Consumer в Pydantic модель."""
        return Consumer(
            consumer_id=proto_consumer.consumer_id,
            name=proto_consumer.name,
            type=proto_consumer.type,
        )

    def _proto_to_tender(self, proto_tender) -> Tender:
        """Конвертировать protobuf Tender в Pydantic модель."""
        return Tender(
            tender_id=proto_tender.tender_id,
            consumer=self._proto_to_consumer(proto_tender.consumer),
            cost=proto_tender.cost,
            quantity_of_products=proto_tender.quantity_of_products,
            penalty_per_day=proto_tender.penalty_per_day,
            warranty_years=proto_tender.warranty_years,
            payment_form=proto_tender.payment_form,
        )

    def _proto_to_workplace(self, proto_workplace) -> Workplace:
        """Конвертировать protobuf Workplace в Pydantic модель."""
        return Workplace(
            workplace_id=proto_workplace.workplace_id,
            workplace_name=proto_workplace.workplace_name,
            required_speciality=proto_workplace.required_speciality,
            required_qualification=proto_workplace.required_qualification,
            required_equipment=proto_workplace.required_equipment,
            worker=(
                self._proto_to_worker(proto_workplace.worker)
                if proto_workplace.worker
                else None
            ),
            equipment=(
                self._proto_to_equipment(proto_workplace.equipment)
                if proto_workplace.equipment
                else None
            ),
            required_stages=list(proto_workplace.required_stages),
            is_start_node=proto_workplace.is_start_node,
            is_end_node=proto_workplace.is_end_node,
            next_workplace_ids=list(proto_workplace.next_workplace_ids),
        )

    def _proto_to_route(self, proto_route) -> Route:
        """Конвертировать protobuf Route в Pydantic модель."""
        return Route(
            length=proto_route.length,
            from_workplace=proto_route.from_workplace,
            to_workplace=proto_route.to_workplace,
        )

    def _proto_to_process_graph(self, proto_process_graph) -> ProcessGraph:
        """Конвертировать protobuf ProcessGraph в Pydantic модель."""
        return ProcessGraph(
            process_graph_id=proto_process_graph.process_graph_id,
            workplaces=[
                self._proto_to_workplace(wp) for wp in proto_process_graph.workplaces
            ],
            routes=[self._proto_to_route(r) for r in proto_process_graph.routes],
        )

    # ==================== Упрощенные методы для обратной совместимости ====================

    async def get_all_suppliers_simple(self) -> List[Supplier]:
        """Упрощенный метод получения поставщиков (для обратной совместимости)."""
        response = await self.get_all_suppliers()
        return response.suppliers

    async def get_all_workers_simple(self) -> List[Worker]:
        """Упрощенный метод получения работников (для обратной совместимости)."""
        response = await self.get_all_workers()
        return response.workers

    async def get_all_logists_simple(self) -> List[Logist]:
        """Упрощенный метод получения логистов (для обратной совместимости)."""
        response = await self.get_all_logists()
        return response.logists

    async def get_all_equipment_simple(self) -> List[Equipment]:
        """Упрощенный метод получения оборудования (для обратной совместимости)."""
        response = await self.get_all_equipment()
        return response.equipments

    async def get_all_tenders_simple(self) -> List[Tender]:
        """Упрощенный метод получения тендеров (для обратной совместимости)."""
        response = await self.get_all_tenders()
        return response.tenders

    async def get_all_consumers_simple(self) -> List[Consumer]:
        """Упрощенный метод получения заказчиков (для обратной совместимости)."""
        response = await self.get_all_consumers()
        return response.consumers

    async def get_all_workplaces_simple(self) -> List[Workplace]:
        """Упрощенный метод получения рабочих мест (для обратной совместимости)."""
        response = await self.get_all_workplaces()
        return response.workplaces

    # ==================== Справочные данные ====================

    # get_reference_data удален - его нет в proto
    # Используйте отдельные методы: get_available_defect_policies, get_available_improvements_list,
    # get_available_certifications, get_available_sales_strategies, get_available_material_types,
    # get_available_equipment_types, get_available_workplace_types

    async def get_material_types(self) -> "MaterialTypesResponse":
        """
        Получить типы материалов.

        Returns:
            MaterialTypesResponse: Типы материалов
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_material_types,
                    simulator_pb2.GetMaterialTypesRequest(),
                )
                from .models import MaterialTypesResponse

                return MaterialTypesResponse(
                    material_types=[
                        MaterialTypesResponse.MaterialType(
                            material_id=mt.material_id,
                            name=mt.name,
                            description=mt.description,
                            unit=mt.unit,
                            average_price=mt.average_price,
                        )
                        for mt in response.material_types
                    ],
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get material types")

    async def get_equipment_types(self) -> "EquipmentTypesResponse":
        """
        Получить типы оборудования.

        Returns:
            EquipmentTypesResponse: Типы оборудования
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_equipment_types,
                    simulator_pb2.GetEquipmentTypesRequest(),
                )
                from .models import EquipmentTypesResponse

                return EquipmentTypesResponse(
                    equipment_types=[
                        EquipmentTypesResponse.EquipmentType(
                            equipment_type_id=et.equipment_type_id,
                            name=et.name,
                            description=et.description,
                            base_reliability=et.base_reliability,
                            base_maintenance_cost=et.base_maintenance_cost,
                            base_cost=et.base_cost,
                            compatible_workplaces=list(et.compatible_workplaces),
                        )
                        for et in response.equipment_types
                    ],
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get equipment types")

    async def get_workplace_types(self) -> "WorkplaceTypesResponse":
        """
        Получить типы рабочих мест.

        Returns:
            WorkplaceTypesResponse: Типы рабочих мест
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_workplace_types,
                    simulator_pb2.GetWorkplaceTypesRequest(),
                )
                from .models import WorkplaceTypesResponse

                return WorkplaceTypesResponse(
                    workplace_types=[
                        WorkplaceTypesResponse.WorkplaceType(
                            workplace_type_id=wt.workplace_type_id,
                            name=wt.name,
                            description=wt.description,
                            required_specialty=wt.required_specialty,
                            required_qualification=wt.required_qualification,
                            compatible_equipment_types=list(
                                wt.compatible_equipment_types
                            ),
                        )
                        for wt in response.workplace_types
                    ],
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get workplace types")

    async def get_available_defect_policies(
        self,
    ) -> "DefectPoliciesListResponse":
        """
        Получить доступные политики работы с браком.

        Returns:
            DefectPoliciesListResponse: Список политик
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_available_defect_policies,
                    simulator_pb2.GetAvailableDefectPoliciesRequest(),
                )
                from .models import DefectPoliciesListResponse

                return DefectPoliciesListResponse(
                    policies=[
                        DefectPoliciesListResponse.DefectPolicyOption(
                            id=p.id,
                            name=p.name,
                            description=p.description,
                            cost_multiplier=p.cost_multiplier,
                            quality_impact=p.quality_impact,
                            time_impact=p.time_impact,
                        )
                        for p in response.policies
                    ],
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available defect policies")

    async def get_available_improvements_list(
        self,
    ) -> "ImprovementsListResponse":
        """
        Получить список доступных улучшений.

        Returns:
            ImprovementsListResponse: Список улучшений
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_available_improvements_list,
                    simulator_pb2.GetAvailableImprovementsListRequest(),
                )
                from .models import ImprovementsListResponse

                return ImprovementsListResponse(
                    improvements=[
                        ImprovementsListResponse.ImprovementOption(
                            id=i.id,
                            name=i.name,
                            description=i.description,
                            implementation_cost=i.implementation_cost,
                            implementation_time_days=i.implementation_time_days,
                            efficiency_gain=i.efficiency_gain,
                            quality_improvement=i.quality_improvement,
                            cost_reduction=i.cost_reduction,
                        )
                        for i in response.improvements
                    ],
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available improvements list")

    async def get_available_certifications(
        self,
    ) -> "CertificationsListResponse":
        """
        Получить доступные сертификации.

        Returns:
            CertificationsListResponse: Список сертификаций
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_available_certifications,
                    simulator_pb2.GetAvailableCertificationsRequest(),
                )
                from .models import CertificationsListResponse

                return CertificationsListResponse(
                    certifications=[
                        CertificationsListResponse.CertificationOption(
                            id=c.id,
                            name=c.name,
                            description=c.description,
                            implementation_cost=c.implementation_cost,
                            implementation_time_days=c.implementation_time_days,
                            market_access_improvement=c.market_access_improvement,
                            quality_recognition=c.quality_recognition,
                            government_access=c.government_access,
                        )
                        for c in response.certifications
                    ],
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available certifications")

    async def get_available_sales_strategies(
        self,
    ) -> "SalesStrategiesListResponse":
        """
        Получить доступные стратегии продаж.

        Returns:
            SalesStrategiesListResponse: Список стратегий
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_available_sales_strategies,
                    simulator_pb2.GetAvailableSalesStrategiesRequest(),
                )
                from .models import SalesStrategiesListResponse

                return SalesStrategiesListResponse(
                    strategies=[
                        SalesStrategiesListResponse.SalesStrategyOption(
                            id=s.id,
                            name=s.name,
                            description=s.description,
                            growth_forecast=s.growth_forecast,
                            unit_cost=s.unit_cost,
                            market_impact=s.market_impact,
                            trend_direction=s.trend_direction,
                            compatible_product_models=list(s.compatible_product_models),
                        )
                        for s in response.strategies
                    ],
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available sales strategies")

    # ==================== LEAN IMPROVEMENT METHODS ====================

    async def create_lean_improvement(
        self, request: "CreateLeanImprovementRequest"
    ) -> "LeanImprovement":
        """
        Создать новое Lean улучшение.

        Args:
            request: Запрос создания улучшения

        Returns:
            LeanImprovement: Созданное улучшение
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.CreateLeanImprovementRequest(
                    name=request.name,
                    is_implemented=request.is_implemented,
                    implementation_cost=request.implementation_cost,
                    efficiency_gain=request.efficiency_gain,
                )
                response = await self._with_retry(
                    self.stub.create_lean_improvement, proto_request
                )

                return self._proto_to_lean_improvement(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Create lean improvement")

    async def update_lean_improvement(
        self, request: "UpdateLeanImprovementRequest"
    ) -> "LeanImprovement":
        """
        Обновить Lean улучшение.

        Args:
            request: Запрос обновления улучшения

        Returns:
            LeanImprovement: Обновленное улучшение
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.UpdateLeanImprovementRequest(
                    improvement_id=request.improvement_id,
                    name=request.name,
                    is_implemented=request.is_implemented,
                    implementation_cost=request.implementation_cost,
                    efficiency_gain=request.efficiency_gain,
                )
                response = await self._with_retry(
                    self.stub.update_lean_improvement, proto_request
                )

                return self._proto_to_lean_improvement(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Update lean improvement")

    async def delete_lean_improvement(
        self, request: "DeleteLeanImprovementRequest"
    ) -> simulator_pb2.SuccessResponse:
        """
        Удалить Lean улучшение.

        Args:
            request: Запрос удаления улучшения

        Returns:
            SuccessResponse: Результат удаления
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.DeleteLeanImprovementRequest(
                    improvement_id=request.improvement_id,
                )
                response = await self._with_retry(
                    self.stub.delete_lean_improvement, proto_request
                )

                return SuccessResponse(
                    success=response.success,
                    message=response.message,
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Delete lean improvement")

    async def get_all_lean_improvements(
        self, request: Optional["GetAllLeanImprovementsRequest"] = None
    ) -> "GetAllLeanImprovementsResponse":
        """
        Получить все Lean улучшения.

        Args:
            request: Запрос получения улучшений

        Returns:
            GetAllLeanImprovementsResponse: Ответ со всеми улучшениями
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                # Если request не передан, создаем пустой запрос
                if request is None:
                    from .models import GetAllLeanImprovementsRequest

                    request = GetAllLeanImprovementsRequest()
                proto_request = simulator_pb2.GetAllLeanImprovementsRequest()
                response = await self._with_retry(
                    self.stub.get_all_lean_improvements, proto_request
                )
                from .models import GetAllLeanImprovementsResponse

                return GetAllLeanImprovementsResponse(
                    improvements=[
                        self._proto_to_lean_improvement(i)
                        for i in response.improvements
                    ],
                    total_count=response.total_count,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get all lean improvements")

    async def get_available_lean_improvements(
        self, request: Optional["GetAvailableLeanImprovementsRequest"] = None
    ) -> "GetAvailableLeanImprovementsResponse":
        """
        Получить доступные Lean улучшения.

        Args:
            request: Запрос получения доступных улучшений (опционально, можно передать None)

        Returns:
            GetAvailableLeanImprovementsResponse: Ответ с доступными улучшениями
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_request = simulator_pb2.GetAvailableLeanImprovementsRequest()
                response = await self._with_retry(
                    self.stub.get_available_lean_improvements, proto_request
                )
                from .models import GetAvailableLeanImprovementsResponse

                return GetAvailableLeanImprovementsResponse(
                    improvements=[
                        self._proto_to_lean_improvement(i)
                        for i in response.improvements
                    ],
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available lean improvements")

    # ==================== REFERENCE DATA METHODS ====================

    async def get_available_material_types(self) -> "MaterialTypesResponse":
        """
        Получить доступные типы материалов.

        Returns:
            MaterialTypesResponse: Типы материалов
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_available_material_types,
                    simulator_pb2.GetMaterialTypesRequest(),
                )
                from .models import MaterialTypesResponse

                return MaterialTypesResponse(
                    material_types=list(response.material_types),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available material types")

    async def get_available_equipment_types(self) -> "EquipmentTypesResponse":
        """
        Получить доступные типы оборудования.

        Returns:
            EquipmentTypesResponse: Типы оборудования
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_available_equipment_types,
                    simulator_pb2.GetEquipmentTypesRequest(),
                )
                from .models import EquipmentTypesResponse

                return EquipmentTypesResponse(
                    equipment_types=list(response.equipment_types),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available equipment types")

    async def get_available_workplace_types(self) -> "WorkplaceTypesResponse":
        """
        Получить доступные типы рабочих мест.

        Returns:
            WorkplaceTypesResponse: Типы рабочих мест
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_available_workplace_types,
                    simulator_pb2.GetWorkplaceTypesRequest(),
                )
                from .models import WorkplaceTypesResponse

                return WorkplaceTypesResponse(
                    workplace_types=list(response.workplace_types),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available workplace types")

    async def get_available_defect_policies(self) -> "DefectPoliciesListResponse":
        """
        Получить доступные политики работы с браком.

        Returns:
            DefectPoliciesListResponse: Политики работы с браком
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_available_defect_policies,
                    simulator_pb2.GetAvailableDefectPoliciesRequest(),
                )
                from .models import DefectPoliciesListResponse

                return DefectPoliciesListResponse(
                    policies=list(response.policies),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available defect policies")

    async def get_available_improvements_list(self) -> "ImprovementsListResponse":
        """
        Получить список доступных улучшений.

        Returns:
            ImprovementsListResponse: Список улучшений
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_available_improvements_list,
                    simulator_pb2.GetAvailableImprovementsListRequest(),
                )
                from .models import ImprovementsListResponse

                return ImprovementsListResponse(
                    improvements=list(response.improvements),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available improvements list")

    async def get_available_certifications(self) -> "CertificationsListResponse":
        """
        Получить доступные сертификации.

        Returns:
            CertificationsListResponse: Список сертификаций
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_available_certifications,
                    simulator_pb2.GetAvailableCertificationsRequest(),
                )
                from .models import CertificationsListResponse

                return CertificationsListResponse(
                    certifications=list(response.certifications),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available certifications")

    async def get_available_sales_strategies(self) -> "SalesStrategiesListResponse":
        """
        Получить доступные стратегии продаж.

        Returns:
            SalesStrategiesListResponse: Список стратегий
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_available_sales_strategies,
                    simulator_pb2.GetAvailableSalesStrategiesRequest(),
                )
                from .models import SalesStrategiesListResponse

                return SalesStrategiesListResponse(
                    strategies=list(response.strategies),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available sales strategies")

    # ==================== PROTO CONVERSION METHODS ====================

    def _proto_to_lean_improvement(self, proto_improvement):
        """Конвертировать protobuf LeanImprovement в Pydantic модель."""
        from .models import LeanImprovement

        return LeanImprovement(
            improvement_id=proto_improvement.improvement_id,
            name=proto_improvement.name,
            is_implemented=proto_improvement.is_implemented,
            implementation_cost=proto_improvement.implementation_cost,
            efficiency_gain=proto_improvement.efficiency_gain,
        )
