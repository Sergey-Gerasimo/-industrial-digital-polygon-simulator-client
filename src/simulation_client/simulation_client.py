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

    # ==================== Управление картой процесса (Инженеринг) ====================

    async def configure_workplace_in_graph(
        self,
        simulation_id: str,
        workplace_id: str,
        workplace_type: str,
        worker_id: Optional[str] = None,
        equipment_id: Optional[str] = None,
        is_start_node: bool = False,
        is_end_node: bool = False,
        next_workplace_ids: Optional[List[str]] = None,
    ) -> SimulationResponse:
        """
        Настроить рабочее место в графе процесса.

        Args:
            simulation_id: ID симуляции
            workplace_id: ID рабочего места
            workplace_type: Тип рабочего места
            worker_id: ID работника (опционально)
            equipment_id: ID оборудования (опционально)
            is_start_node: Является ли начальным узлом
            is_end_node: Является ли конечным узлом
            next_workplace_ids: Список следующих рабочих мест

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.ConfigureWorkplaceInGraphRequest(
                    simulation_id=simulation_id,
                    workplace_id=workplace_id,
                    workplace_type=workplace_type,
                    worker_id=worker_id or "",
                    equipment_id=equipment_id or "",
                    is_start_node=is_start_node,
                    is_end_node=is_end_node,
                    next_workplace_ids=next_workplace_ids or [],
                )
                response = await self._with_retry(
                    self.stub.configure_workplace_in_graph, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Configure workplace in graph")

    async def remove_workplace_from_graph(
        self, simulation_id: str, workplace_id: str
    ) -> SimulationResponse:
        """
        Удалить рабочее место из графа процесса.

        Args:
            simulation_id: ID симуляции
            workplace_id: ID рабочего места

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.RemoveWorkplaceFromGraphRequest(
                    simulation_id=simulation_id, workplace_id=workplace_id
                )
                response = await self._with_retry(
                    self.stub.remove_workplace_from_graph, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Remove workplace from graph")

    async def set_workplace_as_start_node(
        self, simulation_id: str, workplace_id: str
    ) -> SimulationResponse:
        """
        Установить рабочее место как начальный узел.

        Args:
            simulation_id: ID симуляции
            workplace_id: ID рабочего места

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.SetWorkplaceAsStartNodeRequest(
                    simulation_id=simulation_id, workplace_id=workplace_id
                )
                response = await self._with_retry(
                    self.stub.set_workplace_as_start_node, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Set workplace as start node")

    async def set_workplace_as_end_node(
        self, simulation_id: str, workplace_id: str
    ) -> SimulationResponse:
        """
        Установить рабочее место как конечный узел.

        Args:
            simulation_id: ID симуляции
            workplace_id: ID рабочего места

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.SetWorkplaceAsEndNodeRequest(
                    simulation_id=simulation_id, workplace_id=workplace_id
                )
                response = await self._with_retry(
                    self.stub.set_workplace_as_end_node, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Set workplace as end node")

    async def update_process_graph(
        self, simulation_id: str, process_graph: ProcessGraph
    ) -> SimulationResponse:
        """
        Обновить граф процесса.

        Args:
            simulation_id: ID симуляции
            process_graph: Граф процесса

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                # Конвертируем ProcessGraph в protobuf
                proto_graph = simulator_pb2.ProcessGraph(
                    process_graph_id=process_graph.process_graph_id,
                    workplaces=[
                        self._workplace_to_proto(wp) for wp in process_graph.workplaces
                    ],
                    routes=[self._route_to_proto(r) for r in process_graph.routes],
                )
                request = simulator_pb2.UpdateProcessGraphRequest(
                    simulation_id=simulation_id, process_graph=proto_graph
                )
                response = await self._with_retry(
                    self.stub.update_process_graph, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Update process graph")

    # ==================== Распределение производственного плана (Производство) ====================

    async def distribute_production_plan(
        self,
        simulation_id: str,
        strategy: DistributionStrategy,
        auto_assign_workers: bool = False,
        auto_assign_equipment: bool = False,
    ) -> "ProductionPlanDistributionResponse":
        """
        Распределить производственный план.

        Args:
            simulation_id: ID симуляции
            strategy: Стратегия распределения
            auto_assign_workers: Автоматически назначать работников
            auto_assign_equipment: Автоматически назначать оборудование

        Returns:
            ProductionPlanDistributionResponse: Результат распределения
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                # Конвертируем DistributionStrategy в protobuf enum
                proto_strategy = self._distribution_strategy_to_proto(strategy)
                request = simulator_pb2.DistributeProductionPlanRequest(
                    simulation_id=simulation_id,
                    strategy=proto_strategy,
                    auto_assign_workers=auto_assign_workers,
                    auto_assign_equipment=auto_assign_equipment,
                )
                response = await self._with_retry(
                    self.stub.distribute_production_plan, request
                )
                return ProductionPlanDistributionResponse(
                    assignments=[
                        self._proto_to_production_plan_assignment(a)
                        for a in response.assignments
                    ],
                    efficiency_score=response.efficiency_score,
                    total_assigned_quantity=response.total_assigned_quantity,
                    warnings=list(response.warnings),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Distribute production plan")

    async def get_production_plan_distribution(
        self, simulation_id: str
    ) -> "ProductionPlanDistributionResponse":
        """
        Получить распределение производственного плана.

        Args:
            simulation_id: ID симуляции

        Returns:
            ProductionPlanDistributionResponse: Распределение плана
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetProductionPlanDistributionRequest(
                    simulation_id=simulation_id
                )
                response = await self._with_retry(
                    self.stub.get_production_plan_distribution, request
                )
                return ProductionPlanDistributionResponse(
                    assignments=[
                        self._proto_to_production_plan_assignment(a)
                        for a in response.assignments
                    ],
                    efficiency_score=response.efficiency_score,
                    total_assigned_quantity=response.total_assigned_quantity,
                    warnings=list(response.warnings),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get production plan distribution")

    async def update_production_assignment(
        self, simulation_id: str, assignment: "ProductionPlanAssignment"
    ) -> SimulationResponse:
        """
        Обновить назначение производства.

        Args:
            simulation_id: ID симуляции
            assignment: Назначение производства

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_assignment = simulator_pb2.ProductionPlanAssignment(
                    schedule_item_id=assignment.schedule_item_id,
                    workplace_id=assignment.workplace_id,
                    assigned_quantity=assignment.assigned_quantity,
                    assigned_worker_id=assignment.assigned_worker_id,
                    assigned_equipment_id=assignment.assigned_equipment_id,
                    completion_percentage=assignment.completion_percentage,
                )
                request = simulator_pb2.UpdateProductionAssignmentRequest(
                    simulation_id=simulation_id, assignment=proto_assignment
                )
                response = await self._with_retry(
                    self.stub.update_production_assignment, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Update production assignment")

    async def update_workshop_plan(
        self, simulation_id: str, workshop_plan: "WorkshopPlan"
    ) -> SimulationResponse:
        """
        Обновить план цеха.

        Args:
            simulation_id: ID симуляции
            workshop_plan: План цеха

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_plan = self._workshop_plan_to_proto(workshop_plan)
                request = simulator_pb2.UpdateWorkshopPlanRequest(
                    simulation_id=simulation_id, workshop_plan=proto_plan
                )
                response = await self._with_retry(
                    self.stub.update_workshop_plan, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Update workshop plan")

    # ==================== Методы получения метрик и данных ====================

    async def run_simulation_step(
        self, simulation_id: str, step_count: int = 1
    ) -> "SimulationStepResponse":
        """
        Запустить шаг симуляции.

        Args:
            simulation_id: ID симуляции
            step_count: Количество шагов

        Returns:
            SimulationStepResponse: Результат шага
        """
        try:
            async with self._timeout_context(self.timeout * 2):
                await self._rate_limit()
                request = simulator_pb2.RunSimulationStepRequest(
                    simulation_id=simulation_id, step_count=step_count
                )
                response = await self._with_retry(
                    self.stub.run_simulation_step, request
                )
                from .models import SimulationStepResponse

                return SimulationStepResponse(
                    simulation=self._proto_to_simulation(response.simulation),
                    factory_metrics=(
                        self._proto_to_factory_metrics(response.factory_metrics)
                        if response.factory_metrics
                        else None
                    ),
                    production_metrics=(
                        self._proto_to_production_metrics(response.production_metrics)
                        if response.production_metrics
                        else None
                    ),
                    quality_metrics=(
                        self._proto_to_quality_metrics(response.quality_metrics)
                        if response.quality_metrics
                        else None
                    ),
                    engineering_metrics=(
                        self._proto_to_engineering_metrics(response.engineering_metrics)
                        if response.engineering_metrics
                        else None
                    ),
                    commercial_metrics=(
                        self._proto_to_commercial_metrics(response.commercial_metrics)
                        if response.commercial_metrics
                        else None
                    ),
                    procurement_metrics=(
                        self._proto_to_procurement_metrics(response.procurement_metrics)
                        if response.procurement_metrics
                        else None
                    ),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Run simulation step")

    async def get_factory_metrics(
        self, simulation_id: str, step: Optional[int] = None
    ) -> "FactoryMetricsResponse":
        """
        Получить метрики завода.

        Args:
            simulation_id: ID симуляции
            step: Номер шага (опционально)

        Returns:
            FactoryMetricsResponse: Метрики завода
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetMetricsRequest(
                    simulation_id=simulation_id, step=step if step else None
                )
                response = await self._with_retry(
                    self.stub.get_factory_metrics, request
                )
                from .models import FactoryMetricsResponse

                return FactoryMetricsResponse(
                    metrics=self._proto_to_factory_metrics(response.metrics),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get factory metrics")

    async def get_production_metrics(
        self, simulation_id: str, step: Optional[int] = None
    ) -> "ProductionMetricsResponse":
        """
        Получить метрики производства.

        Args:
            simulation_id: ID симуляции
            step: Номер шага (опционально)

        Returns:
            ProductionMetricsResponse: Метрики производства
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetMetricsRequest(
                    simulation_id=simulation_id, step=step if step else None
                )
                response = await self._with_retry(
                    self.stub.get_production_metrics, request
                )
                from .models import ProductionMetricsResponse, UnplannedRepair

                return ProductionMetricsResponse(
                    metrics=self._proto_to_production_metrics(response.metrics),
                    unplanned_repairs=(
                        self._proto_to_unplanned_repair(response.unplanned_repairs)
                        if response.unplanned_repairs
                        else None
                    ),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get production metrics")

    async def get_quality_metrics(
        self, simulation_id: str, step: Optional[int] = None
    ) -> "QualityMetricsResponse":
        """
        Получить метрики качества.

        Args:
            simulation_id: ID симуляции
            step: Номер шага (опционально)

        Returns:
            QualityMetricsResponse: Метрики качества
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetMetricsRequest(
                    simulation_id=simulation_id, step=step if step else None
                )
                response = await self._with_retry(
                    self.stub.get_quality_metrics, request
                )
                from .models import QualityMetricsResponse

                return QualityMetricsResponse(
                    metrics=self._proto_to_quality_metrics(response.metrics),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get quality metrics")

    async def get_engineering_metrics(
        self, simulation_id: str, step: Optional[int] = None
    ) -> "EngineeringMetricsResponse":
        """
        Получить метрики инженерии.

        Args:
            simulation_id: ID симуляции
            step: Номер шага (опционально)

        Returns:
            EngineeringMetricsResponse: Метрики инженерии
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetMetricsRequest(
                    simulation_id=simulation_id, step=step if step else None
                )
                response = await self._with_retry(
                    self.stub.get_engineering_metrics, request
                )
                from .models import EngineeringMetricsResponse

                return EngineeringMetricsResponse(
                    metrics=self._proto_to_engineering_metrics(response.metrics),
                    operation_timing_chart=(
                        self._proto_to_operation_timing_chart(
                            response.operation_timing_chart
                        )
                        if response.operation_timing_chart
                        else None
                    ),
                    downtime_chart=(
                        self._proto_to_downtime_chart(response.downtime_chart)
                        if response.downtime_chart
                        else None
                    ),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get engineering metrics")

    async def get_commercial_metrics(
        self, simulation_id: str, step: Optional[int] = None
    ) -> "CommercialMetricsResponse":
        """
        Получить метрики коммерции.

        Args:
            simulation_id: ID симуляции
            step: Номер шага (опционально)

        Returns:
            CommercialMetricsResponse: Метрики коммерции
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetMetricsRequest(
                    simulation_id=simulation_id, step=step if step else None
                )
                response = await self._with_retry(
                    self.stub.get_commercial_metrics, request
                )
                from .models import CommercialMetricsResponse

                return CommercialMetricsResponse(
                    metrics=self._proto_to_commercial_metrics(response.metrics),
                    model_mastery_chart=(
                        self._proto_to_model_mastery_chart(response.model_mastery_chart)
                        if response.model_mastery_chart
                        else None
                    ),
                    project_profitability_chart=(
                        self._proto_to_project_profitability_chart(
                            response.project_profitability_chart
                        )
                        if response.project_profitability_chart
                        else None
                    ),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get commercial metrics")

    async def get_procurement_metrics(
        self, simulation_id: str, step: Optional[int] = None
    ) -> "ProcurementMetricsResponse":
        """
        Получить метрики закупок.

        Args:
            simulation_id: ID симуляции
            step: Номер шага (опционально)

        Returns:
            ProcurementMetricsResponse: Метрики закупок
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetMetricsRequest(
                    simulation_id=simulation_id, step=step if step else None
                )
                response = await self._with_retry(
                    self.stub.get_procurement_metrics, request
                )
                from .models import ProcurementMetricsResponse

                return ProcurementMetricsResponse(
                    metrics=self._proto_to_procurement_metrics(response.metrics),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get procurement metrics")

    async def get_all_metrics(self, simulation_id: str) -> "AllMetricsResponse":
        """
        Получить все метрики.

        Args:
            simulation_id: ID симуляции

        Returns:
            AllMetricsResponse: Все метрики
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetAllMetricsRequest(
                    simulation_id=simulation_id
                )
                response = await self._with_retry(self.stub.get_all_metrics, request)
                from .models import AllMetricsResponse

                return AllMetricsResponse(
                    factory=(
                        self._proto_to_factory_metrics(response.factory)
                        if response.factory
                        else None
                    ),
                    production=(
                        self._proto_to_production_metrics(response.production)
                        if response.production
                        else None
                    ),
                    quality=(
                        self._proto_to_quality_metrics(response.quality)
                        if response.quality
                        else None
                    ),
                    engineering=(
                        self._proto_to_engineering_metrics(response.engineering)
                        if response.engineering
                        else None
                    ),
                    commercial=(
                        self._proto_to_commercial_metrics(response.commercial)
                        if response.commercial
                        else None
                    ),
                    procurement=(
                        self._proto_to_procurement_metrics(response.procurement)
                        if response.procurement
                        else None
                    ),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get all metrics")

    async def get_production_schedule(
        self, simulation_id: str
    ) -> "ProductionScheduleResponse":
        """
        Получить производственный план.

        Args:
            simulation_id: ID симуляции

        Returns:
            ProductionScheduleResponse: Производственный план
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetProductionScheduleRequest(
                    simulation_id=simulation_id
                )
                response = await self._with_retry(
                    self.stub.get_production_schedule, request
                )
                from .models import ProductionScheduleResponse

                return ProductionScheduleResponse(
                    schedule=self._proto_to_production_schedule(response.schedule),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get production schedule")

    async def update_production_schedule(
        self, simulation_id: str, schedule: "ProductionSchedule"
    ) -> SimulationResponse:
        """
        Обновить производственный план.

        Args:
            simulation_id: ID симуляции
            schedule: Производственный план

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_schedule = self._production_schedule_to_proto(schedule)
                request = simulator_pb2.UpdateProductionScheduleRequest(
                    simulation_id=simulation_id, schedule=proto_schedule
                )
                response = await self._with_retry(
                    self.stub.update_production_schedule, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Update production schedule")

    async def get_workshop_plan(self, simulation_id: str) -> "WorkshopPlanResponse":
        """
        Получить план цеха.

        Args:
            simulation_id: ID симуляции

        Returns:
            WorkshopPlanResponse: План цеха
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetWorkshopPlanRequest(
                    simulation_id=simulation_id
                )
                response = await self._with_retry(self.stub.get_workshop_plan, request)
                from .models import WorkshopPlanResponse

                return WorkshopPlanResponse(
                    workshop_plan=self._proto_to_workshop_plan(response.workshop_plan),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get workshop plan")

    async def get_unplanned_repair(
        self, simulation_id: str
    ) -> "UnplannedRepairResponse":
        """
        Получить внеплановые ремонты.

        Args:
            simulation_id: ID симуляции

        Returns:
            UnplannedRepairResponse: Внеплановые ремонты
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetUnplannedRepairRequest(
                    simulation_id=simulation_id
                )
                response = await self._with_retry(
                    self.stub.get_unplanned_repair, request
                )
                from .models import UnplannedRepairResponse

                return UnplannedRepairResponse(
                    unplanned_repair=self._proto_to_unplanned_repair(
                        response.unplanned_repair
                    ),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get unplanned repair")

    async def get_warehouse_load_chart(
        self, simulation_id: str, warehouse_id: str
    ) -> "WarehouseLoadChartResponse":
        """
        Получить график загрузки склада.

        Args:
            simulation_id: ID симуляции
            warehouse_id: ID склада

        Returns:
            WarehouseLoadChartResponse: График загрузки
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetWarehouseLoadChartRequest(
                    simulation_id=simulation_id, warehouse_id=warehouse_id
                )
                response = await self._with_retry(
                    self.stub.get_warehouse_load_chart, request
                )
                from .models import WarehouseLoadChartResponse, WarehouseLoadChart

                return WarehouseLoadChartResponse(
                    chart=WarehouseLoadChart(
                        data_points=[
                            WarehouseLoadChart.LoadPoint(
                                timestamp=dp.timestamp,
                                load=dp.load,
                                max_capacity=dp.max_capacity,
                            )
                            for dp in response.chart.data_points
                        ],
                        warehouse_id=response.chart.warehouse_id,
                    ),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get warehouse load chart")

    async def get_required_materials(
        self, simulation_id: str
    ) -> "RequiredMaterialsResponse":
        """
        Получить требуемые материалы.

        Args:
            simulation_id: ID симуляции

        Returns:
            RequiredMaterialsResponse: Требуемые материалы
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetRequiredMaterialsRequest(
                    simulation_id=simulation_id
                )
                response = await self._with_retry(
                    self.stub.get_required_materials, request
                )
                from .models import RequiredMaterialsResponse, RequiredMaterial

                return RequiredMaterialsResponse(
                    materials=[
                        RequiredMaterial(
                            material_id=m.material_id,
                            name=m.name,
                            has_contracted_supplier=m.has_contracted_supplier,
                            required_quantity=m.required_quantity,
                            current_stock=m.current_stock,
                        )
                        for m in response.materials
                    ],
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get required materials")

    async def get_available_improvements(
        self, simulation_id: str
    ) -> "AvailableImprovementsResponse":
        """
        Получить доступные улучшения.

        Args:
            simulation_id: ID симуляции

        Returns:
            AvailableImprovementsResponse: Доступные улучшения
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetAvailableImprovementsRequest(
                    simulation_id=simulation_id
                )
                response = await self._with_retry(
                    self.stub.get_available_improvements, request
                )
                from .models import AvailableImprovementsResponse

                return AvailableImprovementsResponse(
                    improvements=[
                        self._proto_to_lean_improvement(imp)
                        for imp in response.improvements
                    ],
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get available improvements")

    async def get_defect_policies(self, simulation_id: str) -> "DefectPoliciesResponse":
        """
        Получить политики работы с браком.

        Args:
            simulation_id: ID симуляции

        Returns:
            DefectPoliciesResponse: Политики работы с браком
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetDefectPoliciesRequest(
                    simulation_id=simulation_id
                )
                response = await self._with_retry(
                    self.stub.get_defect_policies, request
                )
                from .models import DefectPoliciesResponse

                return DefectPoliciesResponse(
                    available_policies=list(response.available_policies),
                    current_policy=response.current_policy,
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get defect policies")

    async def get_simulation_history(
        self, simulation_id: str
    ) -> "SimulationHistoryResponse":
        """
        Получить историю симуляции.

        Args:
            simulation_id: ID симуляции

        Returns:
            SimulationHistoryResponse: История симуляции
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetSimulationHistoryRequest(
                    simulation_id=simulation_id
                )
                response = await self._with_retry(
                    self.stub.get_simulation_history, request
                )
                from .models import SimulationHistoryResponse, SimulationStepResponse

                return SimulationHistoryResponse(
                    steps=[
                        SimulationStepResponse(
                            simulation=self._proto_to_simulation(step.simulation),
                            factory_metrics=(
                                self._proto_to_factory_metrics(step.factory_metrics)
                                if step.factory_metrics
                                else None
                            ),
                            production_metrics=(
                                self._proto_to_production_metrics(
                                    step.production_metrics
                                )
                                if step.production_metrics
                                else None
                            ),
                            quality_metrics=(
                                self._proto_to_quality_metrics(step.quality_metrics)
                                if step.quality_metrics
                                else None
                            ),
                            engineering_metrics=(
                                self._proto_to_engineering_metrics(
                                    step.engineering_metrics
                                )
                                if step.engineering_metrics
                                else None
                            ),
                            commercial_metrics=(
                                self._proto_to_commercial_metrics(
                                    step.commercial_metrics
                                )
                                if step.commercial_metrics
                                else None
                            ),
                            procurement_metrics=(
                                self._proto_to_procurement_metrics(
                                    step.procurement_metrics
                                )
                                if step.procurement_metrics
                                else None
                            ),
                            timestamp=step.timestamp,
                        )
                        for step in response.steps
                    ],
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get simulation history")

    async def validate_configuration(self, simulation_id: str) -> "ValidationResponse":
        """
        Валидировать конфигурацию симуляции.

        Args:
            simulation_id: ID симуляции

        Returns:
            ValidationResponse: Результат валидации
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.ValidateConfigurationRequest(
                    simulation_id=simulation_id
                )
                response = await self._with_retry(
                    self.stub.validate_configuration, request
                )
                from .models import ValidationResponse

                return ValidationResponse(
                    is_valid=response.is_valid,
                    errors=list(response.errors),
                    warnings=list(response.warnings),
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Validate configuration")

    async def set_quality_inspection(
        self,
        simulation_id: str,
        material_id: str,
        inspection: "QualityInspection",
    ) -> SimulationResponse:
        """
        Установить контроль качества.

        Args:
            simulation_id: ID симуляции
            material_id: ID материала
            inspection: Контроль качества

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_inspection = simulator_pb2.QualityInspection(
                    material_id=inspection.material_id,
                    inspection_enabled=inspection.inspection_enabled,
                    inspection_strictness=inspection.inspection_strictness,
                )
                request = simulator_pb2.SetQualityInspectionRequest(
                    simulation_id=simulation_id,
                    material_id=material_id,
                    inspection=proto_inspection,
                )
                response = await self._with_retry(
                    self.stub.set_quality_inspection, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Set quality inspection")

    async def set_delivery_schedule(
        self,
        simulation_id: str,
        supplier_id: str,
        schedule: "DeliverySchedule",
    ) -> SimulationResponse:
        """
        Установить график поставок.

        Args:
            simulation_id: ID симуляции
            supplier_id: ID поставщика
            schedule: График поставок

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                proto_schedule = simulator_pb2.DeliverySchedule(
                    supplier_id=schedule.supplier_id,
                    delivery_period_days=schedule.delivery_period_days,
                    is_express_delivery=schedule.is_express_delivery,
                )
                request = simulator_pb2.SetDeliveryScheduleRequest(
                    simulation_id=simulation_id,
                    supplier_id=supplier_id,
                    schedule=proto_schedule,
                )
                response = await self._with_retry(
                    self.stub.set_delivery_schedule, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Set delivery schedule")

    async def set_equipment_maintenance_interval(
        self, simulation_id: str, equipment_id: str, interval_days: int
    ) -> SimulationResponse:
        """
        Установить интервал обслуживания оборудования.

        Args:
            simulation_id: ID симуляции
            equipment_id: ID оборудования
            interval_days: Интервал в днях

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.SetEquipmentMaintenanceIntervalRequest(
                    simulation_id=simulation_id,
                    equipment_id=equipment_id,
                    interval_days=interval_days,
                )
                response = await self._with_retry(
                    self.stub.set_equipment_maintenance_interval, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Set equipment maintenance interval")

    async def set_certification_status(
        self, simulation_id: str, certificate_type: str, is_obtained: bool
    ) -> SimulationResponse:
        """
        Установить статус сертификации.

        Args:
            simulation_id: ID симуляции
            certificate_type: Тип сертификации
            is_obtained: Получена ли сертификация

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.SetCertificationStatusRequest(
                    simulation_id=simulation_id,
                    certificate_type=certificate_type,
                    is_obtained=is_obtained,
                )
                response = await self._with_retry(
                    self.stub.set_certification_status, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Set certification status")

    async def set_lean_improvement_status(
        self, simulation_id: str, improvement_id: str, is_implemented: bool
    ) -> SimulationResponse:
        """
        Установить статус улучшения Lean.

        Args:
            simulation_id: ID симуляции
            improvement_id: ID улучшения
            is_implemented: Реализовано ли улучшение

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.SetLeanImprovementStatusRequest(
                    simulation_id=simulation_id,
                    improvement_id=improvement_id,
                    is_implemented=is_implemented,
                )
                response = await self._with_retry(
                    self.stub.set_lean_improvement_status, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Set lean improvement status")

    async def set_sales_strategy_with_details(
        self,
        simulation_id: str,
        strategy: str,
        growth_forecast: float = 0.0,
        unit_cost: int = 0,
        market_impact: str = "",
        trend_direction: str = "",
    ) -> SimulationResponse:
        """
        Установить стратегию продаж с деталями.

        Args:
            simulation_id: ID симуляции
            strategy: Стратегия продаж
            growth_forecast: Прогноз роста
            unit_cost: Стоимость единицы
            market_impact: Влияние на рынок
            trend_direction: Направление тренда

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.SetSalesStrategyWithDetailsRequest(
                    simulation_id=simulation_id,
                    strategy=strategy,
                    growth_forecast=growth_forecast,
                    unit_cost=unit_cost,
                    market_impact=market_impact,
                    trend_direction=trend_direction,
                )
                response = await self._with_retry(
                    self.stub.set_sales_strategy_with_details, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Set sales strategy with details")

    async def get_reference_data(self, data_type: str = "") -> "ReferenceDataResponse":
        """
        Получить справочные данные.

        Args:
            data_type: Тип данных (опционально)

        Returns:
            ReferenceDataResponse: Справочные данные
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetReferenceDataRequest(data_type=data_type)
                response = await self._with_retry(self.stub.get_reference_data, request)
                from .models import ReferenceDataResponse

                return ReferenceDataResponse(
                    sales_strategies=[
                        ReferenceDataResponse.SalesStrategyItem(
                            id=item.id,
                            name=item.name,
                            description=item.description,
                            growth_forecast=item.growth_forecast,
                            unit_cost=item.unit_cost,
                            market_impact=item.market_impact,
                            trend_direction=item.trend_direction,
                        )
                        for item in response.sales_strategies
                    ],
                    defect_policies=[
                        ReferenceDataResponse.DefectPolicyItem(
                            id=item.id, name=item.name, description=item.description
                        )
                        for item in response.defect_policies
                    ],
                    certifications=[
                        ReferenceDataResponse.CertificationItem(
                            id=item.id,
                            name=item.name,
                            description=item.description,
                            implementation_cost=item.implementation_cost,
                            implementation_time_days=item.implementation_time_days,
                        )
                        for item in response.certifications
                    ],
                    improvements=[
                        ReferenceDataResponse.ImprovementItem(
                            id=item.id,
                            name=item.name,
                            description=item.description,
                            implementation_cost=item.implementation_cost,
                            efficiency_gain=item.efficiency_gain,
                        )
                        for item in response.improvements
                    ],
                    company_types=[
                        ReferenceDataResponse.CompanyTypeItem(
                            id=item.id, name=item.name, description=item.description
                        )
                        for item in response.company_types
                    ],
                    specialties=[
                        ReferenceDataResponse.SpecialtyItem(
                            id=item.id, name=item.name, description=item.description
                        )
                        for item in response.specialties
                    ],
                    vehicle_types=[
                        ReferenceDataResponse.VehicleTypeItem(
                            id=item.id,
                            name=item.name,
                            description=item.description,
                            speed_modifier=item.speed_modifier,
                        )
                        for item in response.vehicle_types
                    ],
                    unit_sizes=[
                        ReferenceDataResponse.UnitSizeItem(
                            id=item.id, name=item.name, description=item.description
                        )
                        for item in response.unit_sizes
                    ],
                    product_models=[
                        ReferenceDataResponse.ProductModelItem(
                            id=item.id,
                            name=item.name,
                            description=item.description,
                            unit_size=item.unit_size,
                        )
                        for item in response.product_models
                    ],
                    payment_forms=[
                        ReferenceDataResponse.PaymentFormItem(
                            id=item.id, name=item.name, description=item.description
                        )
                        for item in response.payment_forms
                    ],
                    workplace_types=[
                        ReferenceDataResponse.WorkplaceTypeItem(
                            id=item.id,
                            name=item.name,
                            description=item.description,
                            required_specialty=item.required_specialty,
                            required_qualification=item.required_qualification,
                            compatible_equipment=list(item.compatible_equipment),
                        )
                        for item in response.workplace_types
                    ],
                    timestamp=response.timestamp,
                )

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get reference data")

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
            room_id=proto_simulation.room_id,
            is_completed=proto_simulation.is_completed,
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
            quality_inspections=(
                {
                    k: self._proto_to_quality_inspection(v)
                    for k, v in proto_params.quality_inspections.items()
                }
                if proto_params.quality_inspections
                else {}
            ),
            delivery_schedules=(
                {
                    k: self._proto_to_delivery_schedule(v)
                    for k, v in proto_params.delivery_schedules.items()
                }
                if proto_params.delivery_schedules
                else {}
            ),
            equipment_maintenance_intervals=(
                dict(proto_params.equipment_maintenance_intervals)
                if proto_params.equipment_maintenance_intervals
                else {}
            ),
            spaghetti_diagram=(
                self._proto_to_spaghetti_diagram(proto_params.spaghetti_diagram)
                if proto_params.spaghetti_diagram
                else None
            ),
            production_schedule=(
                self._proto_to_production_schedule(proto_params.production_schedule)
                if proto_params.production_schedule
                else None
            ),
            sales_growth_forecast=proto_params.sales_growth_forecast,
            unit_production_cost=proto_params.unit_production_cost,
            certifications=(
                [self._proto_to_certification(c) for c in proto_params.certifications]
                if proto_params.certifications
                else []
            ),
            lean_improvements=(
                [
                    self._proto_to_lean_improvement(li)
                    for li in proto_params.lean_improvements
                ]
                if proto_params.lean_improvements
                else []
            ),
            production_assignments=(
                {
                    k: self._proto_to_production_plan_assignment(v)
                    for k, v in proto_params.production_assignments.items()
                }
                if proto_params.production_assignments
                else {}
            ),
            distribution_strategy=self._proto_to_distribution_strategy(
                proto_params.distribution_strategy
            ),
            workshop_plan=(
                self._proto_to_workshop_plan(proto_params.workshop_plan)
                if proto_params.workshop_plan
                else None
            ),
        )

    def _proto_to_simulation_results(self, proto_results):
        """Конвертировать protobuf SimulationResults в Pydantic модель."""
        if not proto_results:
            return None

        return SimulationResults(
            profit=proto_results.profit,
            cost=proto_results.cost,
            profitability=proto_results.profitability,
            factory_metrics=(
                self._proto_to_factory_metrics(proto_results.factory_metrics)
                if proto_results.factory_metrics
                else None
            ),
            production_metrics=(
                self._proto_to_production_metrics(proto_results.production_metrics)
                if proto_results.production_metrics
                else None
            ),
            quality_metrics=(
                self._proto_to_quality_metrics(proto_results.quality_metrics)
                if proto_results.quality_metrics
                else None
            ),
            engineering_metrics=(
                self._proto_to_engineering_metrics(proto_results.engineering_metrics)
                if proto_results.engineering_metrics
                else None
            ),
            commercial_metrics=(
                self._proto_to_commercial_metrics(proto_results.commercial_metrics)
                if proto_results.commercial_metrics
                else None
            ),
            procurement_metrics=(
                self._proto_to_procurement_metrics(proto_results.procurement_metrics)
                if proto_results.procurement_metrics
                else None
            ),
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
            penalty_per_day=proto_tender.penalty_per_day,
            warranty_years=proto_tender.warranty_years,
            payment_form=proto_tender.payment_form,
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
            is_start_node=proto_workplace.is_start_node,
            is_end_node=proto_workplace.is_end_node,
            next_workplace_ids=list(proto_workplace.next_workplace_ids),
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

    def _distribution_strategy_to_proto(self, strategy: DistributionStrategy) -> int:
        """Конвертировать DistributionStrategy в protobuf enum значение."""
        if strategy == DistributionStrategy.DISTRIBUTION_STRATEGY_BALANCED:
            return simulator_pb2.DISTRIBUTION_STRATEGY_BALANCED
        elif strategy == DistributionStrategy.DISTRIBUTION_STRATEGY_EFFICIENT:
            return simulator_pb2.DISTRIBUTION_STRATEGY_EFFICIENT
        elif strategy == DistributionStrategy.DISTRIBUTION_STRATEGY_CUSTOM:
            return simulator_pb2.DISTRIBUTION_STRATEGY_CUSTOM
        elif strategy == DistributionStrategy.DISTRIBUTION_STRATEGY_PRIORITY_BASED:
            return simulator_pb2.DISTRIBUTION_STRATEGY_PRIORITY_BASED
        else:
            return simulator_pb2.DISTRIBUTION_STRATEGY_UNSPECIFIED

    def _workplace_to_proto(self, workplace: Workplace):
        """Конвертировать Workplace в protobuf."""
        return simulator_pb2.Workplace(
            workplace_id=workplace.workplace_id,
            workplace_name=workplace.workplace_name,
            required_speciality=workplace.required_speciality,
            required_qualification=workplace.required_qualification,
            worker=(
                self._worker_to_proto(workplace.worker) if workplace.worker else None
            ),
            equipment=(
                self._equipment_to_proto(workplace.equipment)
                if workplace.equipment
                else None
            ),
            required_stages=workplace.required_stages,
            is_start_node=workplace.is_start_node,
            is_end_node=workplace.is_end_node,
            next_workplace_ids=workplace.next_workplace_ids,
        )

    def _worker_to_proto(self, worker: Worker):
        """Конвертировать Worker в protobuf."""
        return simulator_pb2.Worker(
            worker_id=worker.worker_id,
            name=worker.name,
            qualification=worker.qualification,
            specialty=worker.specialty,
            salary=worker.salary,
        )

    def _equipment_to_proto(self, equipment: Equipment):
        """Конвертировать Equipment в protobuf."""
        return simulator_pb2.Equipment(
            equipment_id=equipment.equipment_id,
            name=equipment.name,
            reliability=equipment.reliability,
            maintenance_period=equipment.maintenance_period,
            maintenance_cost=equipment.maintenance_cost,
            cost=equipment.cost,
            repair_cost=equipment.repair_cost,
            repair_time=equipment.repair_time,
        )

    def _route_to_proto(self, route: Route):
        """Конвертировать Route в protobuf."""
        return simulator_pb2.Route(
            length=route.length,
            from_workplace=route.from_workplace,
            to_workplace=route.to_workplace,
        )

    def _workshop_plan_to_proto(self, workshop_plan: "WorkshopPlan"):
        """Конвертировать WorkshopPlan в protobuf."""
        from .models import WorkshopPlan

        return simulator_pb2.WorkshopPlan(
            workplace_nodes=[
                simulator_pb2.WorkshopPlan.WorkplaceNode(
                    workplace_id=node.workplace_id,
                    assigned_worker=(
                        self._worker_to_proto(node.assigned_worker)
                        if node.assigned_worker
                        else None
                    ),
                    assigned_equipment=(
                        self._equipment_to_proto(node.assigned_equipment)
                        if node.assigned_equipment
                        else None
                    ),
                    maintenance_interval=node.maintenance_interval,
                    is_start_node=node.is_start_node,
                    is_end_node=node.is_end_node,
                    assigned_schedule_items=node.assigned_schedule_items,
                    max_capacity_per_day=node.max_capacity_per_day,
                    current_utilization=node.current_utilization,
                )
                for node in workshop_plan.workplace_nodes
            ],
            logistic_routes=[
                self._route_to_proto(r) for r in workshop_plan.logistic_routes
            ],
            production_schedule_id=workshop_plan.production_schedule_id,
        )

    def _proto_to_production_plan_assignment(self, proto_assignment):
        """Конвертировать protobuf ProductionPlanAssignment в Pydantic модель."""
        from .models import ProductionPlanAssignment

        return ProductionPlanAssignment(
            schedule_item_id=proto_assignment.schedule_item_id,
            workplace_id=proto_assignment.workplace_id,
            assigned_quantity=proto_assignment.assigned_quantity,
            assigned_worker_id=proto_assignment.assigned_worker_id,
            assigned_equipment_id=proto_assignment.assigned_equipment_id,
            completion_percentage=proto_assignment.completion_percentage,
        )

    def _proto_to_factory_metrics(self, proto_metrics):
        """Конвертировать protobuf FactoryMetrics в Pydantic модель."""
        from .models import FactoryMetrics, WarehouseMetrics

        return FactoryMetrics(
            profitability=proto_metrics.profitability,
            on_time_delivery_rate=proto_metrics.on_time_delivery_rate,
            oee=proto_metrics.oee,
            warehouse_metrics={
                k: WarehouseMetrics(
                    fill_level=v.fill_level,
                    current_load=v.current_load,
                    max_capacity=v.max_capacity,
                    material_levels=dict(v.material_levels),
                )
                for k, v in proto_metrics.warehouse_metrics.items()
            },
            total_procurement_cost=proto_metrics.total_procurement_cost,
            defect_rate=proto_metrics.defect_rate,
        )

    def _proto_to_production_metrics(self, proto_metrics):
        """Конвертировать protobuf ProductionMetrics в Pydantic модель."""
        from .models import ProductionMetrics

        return ProductionMetrics(
            monthly_productivity=[
                ProductionMetrics.MonthlyProductivity(
                    month=mp.month, units_produced=mp.units_produced
                )
                for mp in proto_metrics.monthly_productivity
            ],
            average_equipment_utilization=proto_metrics.average_equipment_utilization,
            wip_count=proto_metrics.wip_count,
            finished_goods_count=proto_metrics.finished_goods_count,
            material_reserves=dict(proto_metrics.material_reserves),
        )

    def _proto_to_quality_metrics(self, proto_metrics):
        """Конвертировать protobuf QualityMetrics в Pydantic модель."""
        from .models import QualityMetrics

        return QualityMetrics(
            defect_percentage=proto_metrics.defect_percentage,
            good_output_percentage=proto_metrics.good_output_percentage,
            defect_causes=[
                QualityMetrics.DefectCause(
                    cause=dc.cause, count=dc.count, percentage=dc.percentage
                )
                for dc in proto_metrics.defect_causes
            ],
            average_material_quality=proto_metrics.average_material_quality,
            average_supplier_failure_probability=proto_metrics.average_supplier_failure_probability,
            procurement_volume=proto_metrics.procurement_volume,
        )

    def _proto_to_engineering_metrics(self, proto_metrics):
        """Конвертировать protobuf EngineeringMetrics в Pydantic модель."""
        from .models import EngineeringMetrics

        return EngineeringMetrics(
            operation_timings=[
                EngineeringMetrics.OperationTiming(
                    operation_name=ot.operation_name,
                    cycle_time=ot.cycle_time,
                    takt_time=ot.takt_time,
                    timing_cost=ot.timing_cost,
                )
                for ot in proto_metrics.operation_timings
            ],
            downtime_records=[
                EngineeringMetrics.DowntimeRecord(
                    cause=dr.cause,
                    total_minutes=dr.total_minutes,
                    average_per_shift=dr.average_per_shift,
                )
                for dr in proto_metrics.downtime_records
            ],
            defect_analysis=[
                EngineeringMetrics.DefectAnalysis(
                    defect_type=da.defect_type,
                    count=da.count,
                    percentage=da.percentage,
                    cumulative_percentage=da.cumulative_percentage,
                )
                for da in proto_metrics.defect_analysis
            ],
        )

    def _proto_to_commercial_metrics(self, proto_metrics):
        """Конвертировать protobuf CommercialMetrics в Pydantic модель."""
        from .models import CommercialMetrics

        return CommercialMetrics(
            yearly_revenues=[
                CommercialMetrics.YearlyRevenue(year=yr.year, revenue=yr.revenue)
                for yr in proto_metrics.yearly_revenues
            ],
            tender_revenue_plan=proto_metrics.tender_revenue_plan,
            total_payments=proto_metrics.total_payments,
            total_receipts=proto_metrics.total_receipts,
            sales_forecast=dict(proto_metrics.sales_forecast),
            strategy_costs=dict(proto_metrics.strategy_costs),
            tender_graph=[
                CommercialMetrics.TenderGraphPoint(
                    strategy=tgp.strategy,
                    unit_size=tgp.unit_size,
                    is_mastered=tgp.is_mastered,
                )
                for tgp in proto_metrics.tender_graph
            ],
            project_profitabilities=[
                CommercialMetrics.ProjectProfitability(
                    project_name=pp.project_name, profitability=pp.profitability
                )
                for pp in proto_metrics.project_profitabilities
            ],
            on_time_completed_orders=proto_metrics.on_time_completed_orders,
        )

    def _proto_to_procurement_metrics(self, proto_metrics):
        """Конвертировать protobuf ProcurementMetrics в Pydantic модель."""
        from .models import ProcurementMetrics

        return ProcurementMetrics(
            supplier_performances=[
                ProcurementMetrics.SupplierPerformance(
                    supplier_id=sp.supplier_id,
                    delivered_quantity=sp.delivered_quantity,
                    projected_defect_rate=sp.projected_defect_rate,
                    planned_reliability=sp.planned_reliability,
                    actual_reliability=sp.actual_reliability,
                    planned_cost=sp.planned_cost,
                    actual_cost=sp.actual_cost,
                    actual_defect_count=sp.actual_defect_count,
                )
                for sp in proto_metrics.supplier_performances
            ],
            total_procurement_value=proto_metrics.total_procurement_value,
        )

    def _proto_to_unplanned_repair(self, proto_repair):
        """Конвертировать protobuf UnplannedRepair в Pydantic модель."""
        from .models import UnplannedRepair

        return UnplannedRepair(
            repairs=[
                UnplannedRepair.RepairRecord(
                    month=r.month,
                    repair_cost=r.repair_cost,
                    equipment_id=r.equipment_id,
                    reason=r.reason,
                )
                for r in proto_repair.repairs
            ],
            total_repair_cost=proto_repair.total_repair_cost,
        )

    def _proto_to_operation_timing_chart(self, proto_chart):
        """Конвертировать protobuf OperationTimingChart в Pydantic модель."""
        from .models import OperationTimingChart

        return OperationTimingChart(
            timing_data=[
                OperationTimingChart.TimingData(
                    process_name=td.process_name,
                    cycle_time=td.cycle_time,
                    takt_time=td.takt_time,
                    timing_cost=td.timing_cost,
                )
                for td in proto_chart.timing_data
            ],
            chart_type=proto_chart.chart_type,
        )

    def _proto_to_downtime_chart(self, proto_chart):
        """Конвертировать protobuf DowntimeChart в Pydantic модель."""
        from .models import DowntimeChart

        return DowntimeChart(
            downtime_data=[
                DowntimeChart.DowntimeData(
                    process_name=dd.process_name,
                    cause=dd.cause,
                    downtime_minutes=dd.downtime_minutes,
                )
                for dd in proto_chart.downtime_data
            ],
            chart_type=proto_chart.chart_type,
        )

    def _proto_to_model_mastery_chart(self, proto_chart):
        """Конвертировать protobuf ModelMasteryChart в Pydantic модель."""
        from .models import ModelMasteryChart

        return ModelMasteryChart(
            model_points=[
                ModelMasteryChart.ModelPoint(
                    strategy=mp.strategy,
                    unit_size=mp.unit_size,
                    is_mastered=mp.is_mastered,
                    model_name=mp.model_name,
                )
                for mp in proto_chart.model_points
            ]
        )

    def _proto_to_project_profitability_chart(self, proto_chart):
        """Конвертировать protobuf ProjectProfitabilityChart в Pydantic модель."""
        from .models import ProjectProfitabilityChart

        return ProjectProfitabilityChart(
            projects=[
                ProjectProfitabilityChart.ProjectData(
                    project_name=p.project_name, profitability=p.profitability
                )
                for p in proto_chart.projects
            ],
            chart_type=proto_chart.chart_type,
        )

    def _proto_to_quality_inspection(self, proto_inspection):
        """Конвертировать protobuf QualityInspection в Pydantic модель."""
        from .models import QualityInspection

        return QualityInspection(
            material_id=proto_inspection.material_id,
            inspection_enabled=proto_inspection.inspection_enabled,
            inspection_strictness=proto_inspection.inspection_strictness,
        )

    def _proto_to_delivery_schedule(self, proto_schedule):
        """Конвертировать protobuf DeliverySchedule в Pydantic модель."""
        from .models import DeliverySchedule

        return DeliverySchedule(
            supplier_id=proto_schedule.supplier_id,
            delivery_period_days=proto_schedule.delivery_period_days,
            is_express_delivery=proto_schedule.is_express_delivery,
        )

    def _proto_to_certification(self, proto_cert):
        """Конвертировать protobuf Certification в Pydantic модель."""
        from .models import Certification

        return Certification(
            certificate_type=proto_cert.certificate_type,
            is_obtained=proto_cert.is_obtained,
            implementation_cost=proto_cert.implementation_cost,
            implementation_time_days=proto_cert.implementation_time_days,
        )

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

    def _proto_to_spaghetti_diagram(self, proto_diagram):
        """Конвертировать protobuf SpaghettiDiagram в Pydantic модель."""
        from .models import SpaghettiDiagram

        return SpaghettiDiagram(
            workplace_details=[
                SpaghettiDiagram.WorkplaceDetail(
                    workplace_id=wd.workplace_id,
                    assigned_worker=(
                        self._proto_to_worker(wd.assigned_worker)
                        if wd.assigned_worker
                        else None
                    ),
                    assigned_equipment=(
                        self._proto_to_equipment(wd.assigned_equipment)
                        if wd.assigned_equipment
                        else None
                    ),
                    maintenance_interval=wd.maintenance_interval,
                )
                for wd in proto_diagram.workplace_details
            ],
            logistic_routes=[
                self._proto_to_route(r) for r in proto_diagram.logistic_routes
            ],
        )

    def _proto_to_production_schedule(self, proto_schedule):
        """Конвертировать protobuf ProductionSchedule в Pydantic модель."""
        from .models import ProductionSchedule

        return ProductionSchedule(
            schedule_items=[
                ProductionSchedule.ScheduleItem(
                    item_id=si.item_id,
                    priority=si.priority,
                    plan_number=si.plan_number,
                    plan_date=si.plan_date,
                    product_name=si.product_name,
                    planned_quantity=si.planned_quantity,
                    actual_quantity=si.actual_quantity,
                    remaining_to_produce=si.remaining_to_produce,
                    planned_completion_date=si.planned_completion_date,
                    order_number=si.order_number,
                    tender_id=si.tender_id,
                )
                for si in proto_schedule.schedule_items
            ]
        )

    def _production_schedule_to_proto(self, schedule: "ProductionSchedule"):
        """Конвертировать ProductionSchedule в protobuf."""
        from .models import ProductionSchedule

        return simulator_pb2.ProductionSchedule(
            schedule_items=[
                simulator_pb2.ProductionSchedule.ScheduleItem(
                    item_id=si.item_id,
                    priority=si.priority,
                    plan_number=si.plan_number,
                    plan_date=si.plan_date,
                    product_name=si.product_name,
                    planned_quantity=si.planned_quantity,
                    actual_quantity=si.actual_quantity,
                    remaining_to_produce=si.remaining_to_produce,
                    planned_completion_date=si.planned_completion_date,
                    order_number=si.order_number,
                    tender_id=si.tender_id,
                )
                for si in schedule.schedule_items
            ]
        )

    def _proto_to_workshop_plan(self, proto_plan):
        """Конвертировать protobuf WorkshopPlan в Pydantic модель."""
        from .models import WorkshopPlan

        return WorkshopPlan(
            workplace_nodes=[
                WorkshopPlan.WorkplaceNode(
                    workplace_id=wn.workplace_id,
                    assigned_worker=(
                        self._proto_to_worker(wn.assigned_worker)
                        if wn.assigned_worker
                        else None
                    ),
                    assigned_equipment=(
                        self._proto_to_equipment(wn.assigned_equipment)
                        if wn.assigned_equipment
                        else None
                    ),
                    maintenance_interval=wn.maintenance_interval,
                    is_start_node=wn.is_start_node,
                    is_end_node=wn.is_end_node,
                    assigned_schedule_items=list(wn.assigned_schedule_items),
                    max_capacity_per_day=wn.max_capacity_per_day,
                    current_utilization=wn.current_utilization,
                )
                for wn in proto_plan.workplace_nodes
            ],
            logistic_routes=[
                self._proto_to_route(r) for r in proto_plan.logistic_routes
            ],
            production_schedule_id=proto_plan.production_schedule_id,
        )

    def _proto_to_distribution_strategy(self, proto_strategy):
        """Конвертировать protobuf DistributionStrategy enum в Pydantic модель."""
        if proto_strategy == simulator_pb2.DISTRIBUTION_STRATEGY_BALANCED:
            return DistributionStrategy.DISTRIBUTION_STRATEGY_BALANCED
        elif proto_strategy == simulator_pb2.DISTRIBUTION_STRATEGY_EFFICIENT:
            return DistributionStrategy.DISTRIBUTION_STRATEGY_EFFICIENT
        elif proto_strategy == simulator_pb2.DISTRIBUTION_STRATEGY_CUSTOM:
            return DistributionStrategy.DISTRIBUTION_STRATEGY_CUSTOM
        elif proto_strategy == simulator_pb2.DISTRIBUTION_STRATEGY_PRIORITY_BASED:
            return DistributionStrategy.DISTRIBUTION_STRATEGY_PRIORITY_BASED
        else:
            return DistributionStrategy.DISTRIBUTION_STRATEGY_UNSPECIFIED
