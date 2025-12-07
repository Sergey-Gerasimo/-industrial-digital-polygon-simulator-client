import asyncio
import grpc
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from .base_client import AsyncBaseClient
from .proto import simulator_pb2
from .proto import simulator_pb2_grpc
from .models import *
from .exceptions import *
from .utils import proto_to_dict

logger = logging.getLogger(__name__)


class AsyncSimulationClient(AsyncBaseClient):
    """
    Асинхронный клиент для SimulationService.

    Работает на порту 50051 (или другом указанном порту).

    Пример использования:
    ```python
    async with AsyncSimulationClient("localhost", 50051) as client:
        simulation = await client.create_simulation()
        await client.set_logist(simulation.simulation_id, "logist_123")
        results = await client.run_simulation(simulation.simulation_id)
    ```
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 50051,  # 👈 Порт для SimulationService
        max_retries: int = 3,
        timeout: float = 30.0,
        rate_limit: Optional[float] = None,
        enable_logging: bool = True,
    ):
        super().__init__(host, port, max_retries, timeout, rate_limit, enable_logging)
        self.stub = None

    async def connect(self):
        """Подключиться к серверу SimulationService."""
        try:
            self.channel = await self._create_channel()
            self.stub = simulator_pb2_grpc.SimulationServiceStub(self.channel)

            # Проверяем соединение
            if await self.ping():
                logger.info(
                    f"Connected to SimulationService at {self.host}:{self.port}"
                )
            else:
                raise ConnectionError(
                    f"Cannot connect to SimulationService at {self.host}:{self.port}"
                )

        except Exception as e:
            logger.error(f"Failed to connect to SimulationService: {e}")
            raise ConnectionError(f"Connection to SimulationService failed: {e}")

    async def close(self):
        """Закрыть соединение."""
        if self.channel:
            await self.channel.close()
            logger.info("Disconnected from SimulationService")

    async def ping(self) -> bool:
        """
        Проверить доступность SimulationService.

        Returns:
            bool: True если сервер доступен
        """
        try:
            async with self._timeout_context(5.0):  # Короткий таймаут для ping
                await self._rate_limit()
                response = await self.stub.ping(simulator_pb2.PingRequest())
                return response.success
        except Exception as e:
            logger.warning(f"Ping to SimulationService failed: {e}")
            return False

    # ==================== Основные операции симуляции ====================

    async def create_simulation(self) -> SimulationConfig:
        """
        Создать новую симуляцию.

        Returns:
            SimulationConfig: Конфигурация созданной симуляции
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.create_simulation, simulator_pb2.CreateSimulationRquest()
                )

                sim = response.simulation
                return SimulationConfig(
                    simulation_id=sim.simulation_id, capital=sim.capital
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Create simulation")

    async def get_simulation(self, simulation_id: str) -> SimulationResponse:
        """
        Получить информацию о симуляции.

        Args:
            simulation_id: ID симуляции

        Returns:
            SimulationResponse: Полный ответ с симуляцией
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_simulation,
                    simulator_pb2.GetSimulationRequest(simulation_id=simulation_id),
                )
                return SimulationResponse(
                    simulation=Simulation(
                        capital=response.simulation.capital,
                        step=response.simulation.step,
                        simulation_id=response.simulation.simulation_id,
                        parameters=self._proto_to_simulation_parameters(
                            response.simulation.parameters
                        ),
                        results=self._proto_to_simulation_results(
                            response.simulation.results
                        ),
                    ),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get simulation")

    async def get_simulation_as_dict(self, simulation_id: str) -> Dict[str, Any]:
        """
        Получить информацию о симуляции в виде словаря.

        Args:
            simulation_id: ID симуляции

        Returns:
            Dict: Информация о симуляции
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_simulation,
                    simulator_pb2.GetSimulationRequest(simulation_id=simulation_id),
                )
                return proto_to_dict(response.simulation)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get simulation")

    async def run_simulation(self, simulation_id: str) -> SimulationResponse:
        """
        Запустить симуляцию.

        Args:
            simulation_id: ID симуляции

        Returns:
            SimulationResponse: Полный ответ с результатами
        """
        try:
            async with self._timeout_context(
                self.timeout * 3
            ):  # Дольше для запуска симуляции
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.run_simulation,
                    simulator_pb2.RunSimulationRequest(simulation_id=simulation_id),
                )

                return SimulationResponse(
                    simulation=Simulation(
                        capital=response.simulation.capital,
                        step=response.simulation.step,
                        simulation_id=response.simulation.simulation_id,
                        parameters=self._proto_to_simulation_parameters(
                            response.simulation.parameters
                        ),
                        results=self._proto_to_simulation_results(
                            response.simulation.results
                        ),
                    ),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Run simulation")

    async def run_simulation_and_get_results(
        self, simulation_id: str
    ) -> SimulationResults:
        """
        Запустить симуляцию и получить только результаты.

        Args:
            simulation_id: ID симуляции

        Returns:
            SimulationResults: Результаты симуляции
        """
        try:
            async with self._timeout_context(self.timeout * 3):
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.run_simulation,
                    simulator_pb2.RunSimulationRequest(simulation_id=simulation_id),
                )

                return SimulationResults(
                    profit=response.simulation.results.profit,
                    cost=response.simulation.results.cost,
                    profitability=response.simulation.results.profitability,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Run simulation")

    # ==================== Управление логистами ====================

    async def set_logist(
        self, simulation_id: str, worker_id: str
    ) -> SimulationResponse:
        """
        Назначить логиста для симуляции.

        Args:
            simulation_id: ID симуляции
            worker_id: ID работника-логиста

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.set_logist,
                    simulator_pb2.SetLogistRequest(
                        simulation_id=simulation_id, worker_id=worker_id
                    ),
                )
                logger.info(f"Set logist {worker_id} for simulation {simulation_id}")
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to set logist {worker_id}: {e}")
            raise self._handle_grpc_error(e, "Set logist")

    # ==================== Управление поставщиками ====================

    async def add_supplier(
        self, simulation_id: str, supplier_id: str, is_backup: bool = False
    ) -> SimulationResponse:
        """
        Добавить поставщика в симуляцию.

        Args:
            simulation_id: ID симуляции
            supplier_id: ID поставщика
            is_backup: Является ли запасным поставщиком

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.add_supplier,
                    simulator_pb2.AddSupplierRequest(
                        simulation_id=simulation_id,
                        supplier_id=supplier_id,
                        is_backup=is_backup,
                    ),
                )
                logger.info(
                    f"Added supplier {supplier_id} to simulation {simulation_id}"
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to add supplier {supplier_id}: {e}")
            raise self._handle_grpc_error(e, "Add supplier")

    async def delete_supplier(
        self, simulation_id: str, supplier_id: str
    ) -> SimulationResponse:
        """
        Удалить поставщика из симуляции.

        Args:
            simulation_id: ID симуляции
            supplier_id: ID поставщика

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.delete_supplier,
                    simulator_pb2.DeleteSupplierRequest(
                        simulation_id=simulation_id, supplier_id=supplier_id
                    ),
                )
                logger.info(
                    f"Deleted supplier {supplier_id} from simulation {simulation_id}"
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to delete supplier {supplier_id}: {e}")
            raise self._handle_grpc_error(e, "Delete supplier")

    # ==================== Управление складом ====================

    async def set_warehouse_worker(
        self, simulation_id: str, worker_id: str, warehouse_type: WarehouseType
    ) -> SimulationResponse:
        """
        Назначить работника на склад.

        Args:
            simulation_id: ID симуляции
            worker_id: ID работника
            warehouse_type: Тип склада

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.set_warehouse_inventory_worker,
                    simulator_pb2.SetWarehouseInventoryWorkerRequest(
                        simulation_id=simulation_id,
                        worker_id=worker_id,
                        warehouse_type=self._warehouse_type_to_proto(warehouse_type),
                    ),
                )
                logger.info(
                    f"Set worker {worker_id} on {warehouse_type.value} warehouse"
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to set warehouse worker {worker_id}: {e}")
            raise self._handle_grpc_error(e, "Set warehouse worker")

    async def increase_warehouse_size(
        self, simulation_id: str, warehouse_type: WarehouseType, size: int
    ) -> SimulationResponse:
        """
        Увеличить размер склада.

        Args:
            simulation_id: ID симуляции
            warehouse_type: Тип склада
            size: На сколько увеличить

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.increase_warehouse_size,
                    simulator_pb2.IncreaseWarehouseSizeRequest(
                        simulation_id=simulation_id,
                        warehouse_type=self._warehouse_type_to_proto(warehouse_type),
                        size=size,
                    ),
                )
                logger.info(
                    f"Increased {warehouse_type.value} warehouse size by {size}"
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to increase warehouse size: {e}")
            raise self._handle_grpc_error(e, "Increase warehouse size")

    # ==================== Управление рабочими местами ====================

    async def set_worker_on_workplace(
        self, simulation_id: str, worker_id: str, workplace_id: str
    ) -> SimulationResponse:
        """
        Назначить работника на рабочее место.

        Args:
            simulation_id: ID симуляции
            worker_id: ID работника
            workplace_id: ID рабочего места

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.set_worker_on_workerplace,
                    simulator_pb2.SetWorkerOnWorkerplaceRequest(
                        simulation_id=simulation_id,
                        worker_id=worker_id,
                        workplace_id=workplace_id,
                    ),
                )
                logger.info(f"Set worker {worker_id} on workplace {workplace_id}")
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to set worker on workplace: {e}")
            raise self._handle_grpc_error(e, "Set worker on workplace")

    async def set_equipment_on_workplace(
        self, simulation_id: str, workplace_id: str, equipment_id: str
    ) -> SimulationResponse:
        """
        Установить оборудование на рабочее место.

        Args:
            simulation_id: ID симуляции
            workplace_id: ID рабочего места
            equipment_id: ID оборудования

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.set_equipment_on_workplace,
                    simulator_pb2.SetEquipmentOnWorkplaceRequst(
                        simulation_id=simulation_id,
                        workplace_id=workplace_id,
                        equipment_id=equipment_id,
                    ),
                )
                logger.info(f"Set equipment {equipment_id} on workplace {workplace_id}")
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to set equipment on workplace: {e}")
            raise self._handle_grpc_error(e, "Set equipment on workplace")

    async def unset_worker_on_workplace(
        self, simulation_id: str, worker_id: str
    ) -> SimulationResponse:
        """
        Снять работника с рабочего места.

        Args:
            simulation_id: ID симуляции
            worker_id: ID работника

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.unset_worker_on_workerplace,
                    simulator_pb2.UnSetWorkerOnWorkerplaceRequest(
                        simulation_id=simulation_id, worker_id=worker_id
                    ),
                )
                logger.info(f"Unset worker {worker_id} from workplace")
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to unset worker from workplace: {e}")
            raise self._handle_grpc_error(e, "Unset worker from workplace")

    async def unset_equipment_on_workplace(
        self, simulation_id: str, workplace_id: str
    ) -> SimulationResponse:
        """
        Снять оборудование с рабочего места.

        Args:
            simulation_id: ID симуляции
            workplace_id: ID рабочего места

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.unset_equipment_on_workplace,
                    simulator_pb2.UnSetEquipmentOnWorkplaceRequst(
                        simulation_id=simulation_id, workplace_id=workplace_id
                    ),
                )
                logger.info(f"Unset equipment from workplace {workplace_id}")
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to unset equipment from workplace: {e}")
            raise self._handle_grpc_error(e, "Unset equipment from workplace")

    # ==================== Управление тендерами ====================

    async def add_tender(
        self, simulation_id: str, tender_id: str
    ) -> SimulationResponse:
        """
        Добавить тендер в симуляцию.

        Args:
            simulation_id: ID симуляции
            tender_id: ID тендера

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.add_tender,
                    simulator_pb2.AddTenderRequest(
                        simulation_id=simulation_id, tender_id=tender_id
                    ),
                )
                logger.info(f"Added tender {tender_id} to simulation {simulation_id}")
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to add tender {tender_id}: {e}")
            raise self._handle_grpc_error(e, "Add tender")

    async def delete_tender(
        self, simulation_id: str, tender_id: str
    ) -> SimulationResponse:
        """
        Удалить тендер из симуляции.

        Args:
            simulation_id: ID симуляции
            tender_id: ID тендера

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.delete_tender,
                    simulator_pb2.RemoveTenderRequest(
                        simulation_id=simulation_id, tender_id=tender_id
                    ),
                )
                logger.info(
                    f"Deleted tender {tender_id} from simulation {simulation_id}"
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to delete tender {tender_id}: {e}")
            raise self._handle_grpc_error(e, "Delete tender")

    # ==================== Дополнительные настройки ====================

    async def set_dealing_with_defects(
        self, simulation_id: str, policy: str
    ) -> SimulationResponse:
        """
        Установить политику работы с браком.

        Args:
            simulation_id: ID симуляции
            policy: Политика работы с браком

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.set_dealing_with_defects,
                    simulator_pb2.SetDealingWithDefectsRequest(
                        simulation_id=simulation_id, dealing_with_defects=policy
                    ),
                )
                logger.info(
                    f"Set defects policy to {policy} for simulation {simulation_id}"
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to set defects policy: {e}")
            raise self._handle_grpc_error(e, "Set dealing with defects")

    async def set_certification(
        self, simulation_id: str, has_certification: bool
    ) -> SimulationResponse:
        """
        Установить наличие сертификации.

        Args:
            simulation_id: ID симуляции
            has_certification: Есть ли сертификация

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.set_has_certification,
                    simulator_pb2.SetHasCertificationRequest(
                        simulation_id=simulation_id, has_certification=has_certification
                    ),
                )
                status = "with" if has_certification else "without"
                logger.info(f"Set simulation {simulation_id} {status} certification")
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to set certification: {e}")
            raise self._handle_grpc_error(e, "Set certification")

    async def add_production_improvement(
        self, simulation_id: str, improvement: str
    ) -> SimulationResponse:
        """
        Добавить улучшение производства.

        Args:
            simulation_id: ID симуляции
            improvement: Улучшение производства

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.add_production_improvement,
                    simulator_pb2.AddProductionImprovementRequest(
                        simulation_id=simulation_id, production_improvement=improvement
                    ),
                )
                logger.info(
                    f"Added improvement {improvement} to simulation {simulation_id}"
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to add production improvement: {e}")
            raise self._handle_grpc_error(e, "Add production improvement")

    async def delete_production_improvement(
        self, simulation_id: str, improvement: str
    ) -> SimulationResponse:
        """
        Удалить улучшение производства.

        Args:
            simulation_id: ID симуляции
            improvement: Улучшение производства

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.delete_production_improvement,
                    simulator_pb2.DeleteProductionImprovementRequest(
                        simulation_id=simulation_id, production_improvement=improvement
                    ),
                )
                logger.info(
                    f"Deleted improvement {improvement} from simulation {simulation_id}"
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to delete production improvement: {e}")
            raise self._handle_grpc_error(e, "Delete production improvement")

    async def set_sales_strategy(
        self, simulation_id: str, strategy: str
    ) -> SimulationResponse:
        """
        Установить стратегию продаж.

        Args:
            simulation_id: ID симуляции
            strategy: Стратегия продаж

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.set_sales_strategy,
                    simulator_pb2.SetSalesStrategyRequest(
                        simulation_id=simulation_id, sales_strategy=strategy
                    ),
                )
                logger.info(
                    f"Set sales strategy to {strategy} for simulation {simulation_id}"
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to set sales strategy: {e}")
            raise self._handle_grpc_error(e, "Set sales strategy")

    # ==================== Управление маршрутами процесса ====================

    async def add_process_route(
        self, simulation_id: str, length: int, from_workplace: str, to_workplace: str
    ) -> SimulationResponse:
        """
        Добавить маршрут процесса.

        Args:
            simulation_id: ID симуляции
            length: Длина маршрута
            from_workplace: ID начального рабочего места
            to_workplace: ID конечного рабочего места

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.add_process_rote,
                    simulator_pb2.AddProcessRouteRequest(
                        simulation_id=simulation_id,
                        length=length,
                        from_workplace=from_workplace,
                        to_workplace=to_workplace,
                    ),
                )
                logger.info(
                    f"Added process route from {from_workplace} to {to_workplace}"
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to add process route: {e}")
            raise self._handle_grpc_error(e, "Add process route")

    async def delete_process_route(
        self, simulation_id: str, from_workplace: str, to_workplace: str
    ) -> SimulationResponse:
        """
        Удалить маршрут процесса.

        Args:
            simulation_id: ID симуляции
            from_workplace: ID начального рабочего места
            to_workplace: ID конечного рабочего места

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.delete_process_rote,
                    simulator_pb2.DeleteProcesRouteRequest(
                        simulation_id=simulation_id,
                        from_workplace=from_workplace,
                        to_workplace=to_workplace,
                    ),
                )
                logger.info(
                    f"Deleted process route from {from_workplace} to {to_workplace}"
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to delete process route: {e}")
            raise self._handle_grpc_error(e, "Delete process route")

    # ==================== Вспомогательные методы ====================

    def _warehouse_type_to_proto(self, warehouse_type: WarehouseType) -> int:
        """Конвертировать WarehouseType в protobuf enum значение."""
        if warehouse_type == WarehouseType.WAREHOUSE_TYPE_MATERIALS:
            return simulator_pb2.WAREHOUSE_TYPE_MATERIALS
        elif warehouse_type == WarehouseType.WAREHOUSE_TYPE_PRODUCTS:
            return simulator_pb2.WAREHOUSE_TYPE_PRODUCTS
        else:
            return simulator_pb2.WAREHOUSE_TYPE_UNSPECIFIED

    def _proto_to_simulation_response(self, response) -> SimulationResponse:
        """Конвертировать protobuf SimulationResponse в Pydantic модель."""
        return SimulationResponse(
            simulation=self._proto_to_simulation(response.simulation),
            timestamp=response.timestamp,
        )

    def _proto_to_simulation(self, proto_simulation) -> Simulation:
        """Конвертировать protobuf Simulation в Pydantic модель."""
        return Simulation(
            capital=proto_simulation.capital,
            step=proto_simulation.step,
            simulation_id=proto_simulation.simulation_id,
            parameters=self._proto_to_simulation_parameters(
                proto_simulation.parameters
            ),
            results=self._proto_to_simulation_results(proto_simulation.results),
        )

    def _proto_to_simulation_parameters(self, proto_params):
        """Конвертировать protobuf SimulationParameters в Pydantic модель."""
        if not proto_params:
            return None

        return SimulationParameters(
            logist=(
                self._proto_to_logist(proto_params.logist)
                if proto_params.logist
                else None
            ),
            suppliers=[self._proto_to_supplier(s) for s in proto_params.suppliers],
            backup_suppliers=[
                self._proto_to_supplier(s) for s in proto_params.backup_suppliers
            ],
            materials_warehouse=(
                self._proto_to_warehouse(proto_params.materials_warehouse)
                if proto_params.materials_warehouse
                else None
            ),
            product_warehouse=(
                self._proto_to_warehouse(proto_params.product_warehouse)
                if proto_params.product_warehouse
                else None
            ),
            processes=(
                self._proto_to_process_graph(proto_params.processes)
                if proto_params.processes
                else None
            ),
            tenders=[self._proto_to_tender(t) for t in proto_params.tenders],
            dealing_with_defects=proto_params.dealing_with_defects,
            has_certification=proto_params.has_certification,
            production_improvements=list(proto_params.production_improvements),
            sales_strategy=proto_params.sales_strategy,
        )

    def _proto_to_simulation_results(self, proto_results):
        """Конвертировать protobuf SimulationResults в Pydantic модель."""
        if not proto_results:
            return None

        return SimulationResults(
            profit=proto_results.profit,
            cost=proto_results.cost,
            profitability=proto_results.profitability,
        )

    def _proto_to_supplier(self, proto_supplier):
        """Конвертировать protobuf Supplier в Pydantic модель."""
        return Supplier(
            supplier_id=proto_supplier.supplier_id,
            name=proto_supplier.name,
            product_name=proto_supplier.product_name,
            delivery_period=proto_supplier.delivery_period,
            special_delivery_period=proto_supplier.special_delivery_period,
            reliability=proto_supplier.reliability,
            product_quality=proto_supplier.product_quality,
            cost=proto_supplier.cost,
            special_delivery_cost=proto_supplier.special_delivery_cost,
        )

    def _proto_to_worker(self, proto_worker):
        """Конвертировать protobuf Worker в Pydantic модель."""
        return Worker(
            worker_id=proto_worker.worker_id,
            name=proto_worker.name,
            qualification=proto_worker.qualification,
            specialty=proto_worker.specialty,
            salary=proto_worker.salary,
        )

    def _proto_to_logist(self, proto_logist):
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

    def _proto_to_equipment(self, proto_equipment):
        """Конвертировать protobuf Equipment в Pydantic модель."""
        return Equipment(
            equipment_id=proto_equipment.equipment_id,
            name=proto_equipment.name,
            reliability=proto_equipment.reliability,
            maintenance_period=proto_equipment.maintenance_period,
            maintenance_cost=proto_equipment.maintenance_cost,
            cost=proto_equipment.cost,
            repair_cost=proto_equipment.repair_cost,
            repair_time=proto_equipment.repair_time,
        )

    def _proto_to_warehouse(self, proto_warehouse):
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

    def _proto_to_tender(self, proto_tender):
        """Конвертировать protobuf Tender в Pydantic модель."""
        return Tender(
            tender_id=proto_tender.tender_id,
            consumer=self._proto_to_consumer(proto_tender.consumer),
            cost=proto_tender.cost,
            quantity_of_products=proto_tender.quantity_of_products,
        )

    def _proto_to_consumer(self, proto_consumer):
        """Конвертировать protobuf Consumer в Pydantic модель."""
        return Consumer(
            consumer_id=proto_consumer.consumer_id,
            name=proto_consumer.name,
            type=proto_consumer.type,
        )

    def _proto_to_workplace(self, proto_workplace):
        """Конвертировать protobuf Workplace в Pydantic модель."""
        return Workplace(
            workplace_id=proto_workplace.workplace_id,
            workplace_name=proto_workplace.workplace_name,
            required_speciality=proto_workplace.required_speciality,
            required_qualification=proto_workplace.required_qualification,
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
        )

    def _proto_to_route(self, proto_route):
        """Конвертировать protobuf Route в Pydantic модель."""
        return Route(
            length=proto_route.length,
            from_workplace=proto_route.from_workplace,
            to_workplace=proto_route.to_workplace,
        )

    def _proto_to_process_graph(self, proto_process_graph):
        """Конвертировать protobuf ProcessGraph в Pydantic модель."""
        return ProcessGraph(
            process_graph_id=proto_process_graph.process_graph_id,
            workplaces=[
                self._proto_to_workplace(wp) for wp in proto_process_graph.workplaces
            ],
            routes=[self._proto_to_route(r) for r in proto_process_graph.routes],
        )
