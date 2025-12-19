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

    def _create_stub(self, channel: grpc.aio.Channel):
        """Создать stub для SimulationService."""
        return simulator_pb2_grpc.SimulationServiceStub(channel)

    def _get_service_name(self) -> str:
        """Получить имя сервиса для логирования."""
        return "SimulationService"

    def _parse_ping_response(self, response) -> bool:
        """Парсить ответ ping для SimulationService."""
        # PingResponse имеет поле success напрямую, не нужно конвертировать через SimulationResponse
        return response.success

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

                # SimulationResponse содержит поле simulations (множественное число) согласно proto
                # Но поле называется simulations, хотя обычно это один объект Simulation
                if hasattr(response, "simulations") and response.simulations:
                    sim = response.simulations
                elif hasattr(response, "simulation") and response.simulation:
                    sim = response.simulation
                else:
                    # Если структура ответа другая, пробуем получить напрямую
                    sim = response
                    if not hasattr(sim, "simulation_id"):
                        raise ValueError(
                            f"Unexpected response structure from create_simulation: {type(response)}, fields: {dir(response)}"
                        )

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
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get simulation")

    async def get_simulation_as_dict(self, simulation_id: str) -> Dict[str, Any]:
        """
        Получить информацию о симуляции в виде словаря.

        DEPRECATED: Используйте get_simulation() и конвертируйте в словарь самостоятельно.

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
                # Используем simulations вместо simulation согласно proto
                sim = (
                    response.simulations
                    if hasattr(response, "simulations")
                    else response.simulation
                )
                return proto_to_dict(sim)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get simulation")

    async def run_simulation(
        self, simulation_id: str
    ) -> simulator_pb2.SimulationResponse:
        """
        Запустить симуляцию.

        Args:
            simulation_id: ID симуляции

        Returns:
            SimulationResponse: Protobuf ответ с результатами
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
                return self._proto_to_simulation_response(response)

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
                # Используем simulations вместо simulation согласно proto
                sim = (
                    response.simulations
                    if hasattr(response, "simulations")
                    else response.simulation
                )
                if sim.results:
                    return self._proto_to_simulation_results(sim.results[-1])
                return None

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
    ) -> simulator_pb2.SimulationResponse:
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
    ) -> simulator_pb2.SimulationResponse:
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
    ) -> simulator_pb2.SimulationResponse:
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
    ) -> simulator_pb2.SimulationResponse:
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
    ) -> simulator_pb2.SimulationResponse:
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

    # set_equipment_on_workplace удален - его нет в proto файле
    # Используйте update_process_graph для изменения графа процесса

    async def unset_worker_on_workplace(
        self, simulation_id: str, worker_id: str
    ) -> simulator_pb2.SimulationResponse:
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

    # unset_equipment_on_workplace удален - его нет в proto файле
    # Используйте update_process_graph для изменения графа процесса

    # ==================== Управление тендерами ====================

    async def add_tender(
        self, simulation_id: str, tender_id: str
    ) -> simulator_pb2.SimulationResponse:
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
    ) -> simulator_pb2.SimulationResponse:
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
    ) -> simulator_pb2.SimulationResponse:
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

    # set_certification удален - используйте set_certification_status вместо него

    # add_production_improvement и delete_production_improvement удалены - их нет в proto
    # Используйте set_lean_improvement_status для управления улучшениями

    async def set_sales_strategy(
        self, simulation_id: str, strategy: str
    ) -> simulator_pb2.SimulationResponse:
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
                        simulation_id=simulation_id,
                        strategy=strategy,  # Исправлено: strategy вместо sales_strategy
                    ),
                )
                logger.info(
                    f"Set sales strategy to {strategy} for simulation {simulation_id}"
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            logger.error(f"Failed to set sales strategy: {e}")
            raise self._handle_grpc_error(e, "Set sales strategy")

    # add_process_route, delete_process_route, configure_workplace_in_graph,
    # remove_workplace_from_graph, set_workplace_as_start_node, set_workplace_as_end_node
    # удалены - их нет в proto
    # Используйте update_process_graph для всех изменений графа процесса

    async def update_process_graph(
        self, simulation_id: str, process_graph: ProcessGraph
    ) -> simulator_pb2.SimulationResponse:
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

    # distribute_production_plan и get_production_plan_distribution удалены - их нет в proto
    # Используйте SetProductionPlanRowRequest для установки строк производственного плана

    # update_production_assignment и update_workshop_plan удалены - их нет в proto
    # Используйте SetProductionPlanRowRequest для обновления производственного плана
    # Используйте UpdateProcessGraphRequest для обновления графа процесса (workshop plan)

    # ==================== Методы получения метрик и данных ====================

    # run_simulation_step удален - его нет в proto
    # Используйте run_simulation для запуска полной симуляции

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
                return self._proto_to_all_metrics_response(response)

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
                return self._proto_to_production_schedule_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get production schedule")

    # update_production_schedule удален - его нет в proto
    # Используйте set_production_plan_row для обновления отдельных строк плана

    async def get_workshop_plan(
        self, simulation_id: str
    ) -> simulator_pb2.WorkshopPlanResponse:
        """
        Получить план цеха.

        Args:
            simulation_id: ID симуляции

        Returns:
            WorkshopPlanResponse: Protobuf ответ с планом цеха
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetWorkshopPlanRequest(
                    simulation_id=simulation_id
                )
                response = await self._with_retry(self.stub.get_workshop_plan, request)
                return self._proto_to_workshop_plan_response(response)

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
                return self._proto_to_unplanned_repair_response(response)

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
                return self._proto_to_warehouse_load_chart_response(response)

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
                return self._proto_to_required_materials_response(response)

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
                return self._proto_to_available_improvements_response(response)

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
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Get defect policies")

    # get_simulation_history удален - его нет в proto
    # Используйте get_simulation для получения текущего состояния симуляции

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
                return self._proto_to_validation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Validate configuration")

    async def set_quality_inspection(
        self,
        simulation_id: str,
        supplier_id: str,
        inspection_enabled: bool,
    ) -> SimulationResponse:
        """
        Установить контроль качества для поставщика.

        Args:
            simulation_id: ID симуляции
            supplier_id: ID поставщика
            inspection_enabled: Включить/выключить контроль качества

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.SetQualityInspectionRequest(
                    simulation_id=simulation_id,
                    supplier_id=supplier_id,
                    inspection_enabled=inspection_enabled,
                )
                response = await self._with_retry(
                    self.stub.set_quality_inspection, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Set quality inspection")

    # Старый set_delivery_period удален - дубликат, правильная версия ниже (строка 3490)

    async def set_equipment_maintenance_interval(
        self, simulation_id: str, equipment_id: str, interval_days: int
    ) -> simulator_pb2.SimulationResponse:
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
    ) -> simulator_pb2.SimulationResponse:
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
        self, simulation_id: str, name: str, is_implemented: bool
    ) -> SimulationResponse:
        """
        Установить статус улучшения Lean.

        Args:
            simulation_id: ID симуляции
            name: Название улучшения (не ID!)
            is_implemented: Реализовано ли улучшение

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.SetLeanImprovementStatusRequest(
                    simulation_id=simulation_id,
                    name=name,
                    is_implemented=is_implemented,
                )
                response = await self._with_retry(
                    self.stub.set_lean_improvement_status, request
                )
                return self._proto_to_simulation_response(response)

        except grpc.RpcError as e:
            self._handle_grpc_error(e, "Set lean improvement status")

    # set_sales_strategy_with_details удален - его нет в proto
    # Используйте set_sales_strategy для установки стратегии продаж

    # get_reference_data удален - его нет в proto
    # Используйте отдельные методы: get_available_defect_policies, get_available_improvements_list,
    # get_available_certifications, get_available_sales_strategies, get_material_types,
    # get_equipment_types, get_workplace_types

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

    async def _get_step_from_simulation(self, simulation_id: str) -> int:
        """
        Получить step из симуляции.

        Args:
            simulation_id: ID симуляции

        Returns:
            int: step симуляции (>= 1) или 1, если не удалось получить/step=0
        """
        try:
            sim_response = await self.get_simulation(simulation_id)
            # В сервисе step по факту обязателен: на сервере часто используется `if request.step:`,
            # и при step=0 он считается "не передан" (falsy), что приводит к падению.
            # Поэтому гарантируем step >= 1.
            return (
                sim_response.simulations.step
                if sim_response.simulations.step > 0
                else 1
            )
        except Exception as e:
            logger.warning(
                f"Failed to get step from simulation {simulation_id}: {e}, using step=1"
            )
            return 1

    def _proto_to_simulation_response(self, response) -> SimulationResponse:
        """Конвертировать protobuf SimulationResponse в Pydantic модель."""
        # В proto файле поле называется simulations (множественное число)
        sim = (
            response.simulations
            if hasattr(response, "simulations")
            else response.simulation
        )
        return SimulationResponse(
            simulations=self._proto_to_simulation(sim),
            timestamp=response.timestamp,
        )

    def _proto_to_simulation(self, proto_simulation) -> Simulation:
        """Конвертировать protobuf Simulation в Pydantic модель."""
        # step может отсутствовать в proto, используем значение по умолчанию
        step = getattr(proto_simulation, "step", 0)
        if step == 0:
            # Попробуем взять step из последнего результата или параметров, если он там присутствует
            if proto_simulation.results:
                step = getattr(proto_simulation.results[-1], "step", 0)
            elif proto_simulation.parameters:
                step = getattr(proto_simulation.parameters[-1], "step", 0)

        return Simulation(
            capital=proto_simulation.capital,
            step=step,
            simulation_id=proto_simulation.simulation_id,
            parameters=[
                self._proto_to_simulation_parameters(p)
                for p in proto_simulation.parameters
            ],
            results=[
                self._proto_to_simulation_results(r) for r in proto_simulation.results
            ],
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
            production_improvements=[
                self._proto_to_lean_improvement(li)
                for li in proto_params.production_improvements
            ],
            sales_strategy=proto_params.sales_strategy,
            production_schedule=(
                self._proto_to_production_schedule(proto_params.production_schedule)
                if proto_params.production_schedule
                else None
            ),
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
            distribution_strategy=(
                self._proto_to_distribution_strategy(proto_params.distribution_strategy)
                if hasattr(proto_params, "distribution_strategy")
                and proto_params.distribution_strategy
                else DistributionStrategy.DISTRIBUTION_STRATEGY_UNSPECIFIED
            ),
            step=getattr(proto_params, "step", 0),
            capital=getattr(proto_params, "capital", 0),
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
            step=getattr(proto_results, "step", 0),
        )

    def _proto_to_supplier(self, proto_supplier):
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
            quality_inspection=bool(
                getattr(proto_supplier, "quality_inspection_enabled", False)
            ),
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
            equipment_type=proto_equipment.equipment_type,  # Добавлено поле equipment_type
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
            x=proto_workplace.x if proto_workplace.HasField("x") else None,
            y=proto_workplace.y if proto_workplace.HasField("y") else None,
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
        kwargs = dict(
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

        if workplace.x is not None:
            kwargs["x"] = workplace.x
        if workplace.y is not None:
            kwargs["y"] = workplace.y

        return simulator_pb2.Workplace(**kwargs)

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

    def _process_graph_to_proto(self, process_graph: "ProcessGraph"):
        """Конвертировать ProcessGraph в protobuf ProcessGraph.

        Клиент может передать как Pydantic-модель, так и обычный dict
        (например, из вебсокета). Чтобы избежать AttributeError при доступе
        к полям, приводим вход к ProcessGraph через Pydantic.
        """
        if isinstance(process_graph, dict):
            process_graph = ProcessGraph.model_validate(process_graph)

        return simulator_pb2.ProcessGraph(
            process_graph_id=process_graph.process_graph_id,
            workplaces=[
                self._workplace_to_proto(wp) for wp in process_graph.workplaces
            ],
            routes=[self._route_to_proto(r) for r in process_graph.routes],
        )

    # _workshop_plan_to_proto удален - WorkshopPlan нет в proto
    # WorkshopPlanResponse использует ProcessGraph согласно proto

    # _proto_to_production_plan_assignment удален - ProductionPlanAssignment нет в proto

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

    # _proto_to_quality_inspection и _proto_to_delivery_schedule удалены - их нет в proto

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

    # Старые версии _proto_to_spaghetti_diagram, _proto_to_production_schedule,
    # _production_schedule_to_proto и _proto_to_workshop_plan удалены
    # Правильные версии определены ниже (строки 3414+)

    # ==================== NEW METHODS FOR UPDATED PROTO ====================

    async def update_process_graph(
        self, simulation_id: str, process_graph: "ProcessGraph"
    ) -> simulator_pb2.SimulationResponse:
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
                response = await self._with_retry(
                    self.stub.update_process_graph,
                    simulator_pb2.UpdateProcessGraphRequest(
                        simulation_id=simulation_id,
                        process_graph=self._process_graph_to_proto(process_graph),
                    ),
                )

                return self._proto_to_simulation_response(response)

        except Exception as e:
            logger.error(f"Failed to update process graph: {e}")
            raise

    async def set_production_plan_row(
        self, simulation_id: str, row: "ProductionPlanRow"
    ) -> SimulationResponse:
        """
        Установить строку производственного плана.

        Args:
            simulation_id: ID симуляции
            row: Строка производственного плана

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.set_production_plan_row,
                    simulator_pb2.SetProductionPlanRowRequest(
                        simulation_id=simulation_id,
                        row=self._production_plan_row_to_proto(row),
                    ),
                )

                return self._proto_to_simulation_response(response)

        except Exception as e:
            logger.error(f"Failed to set production plan row: {e}")
            raise

    async def get_factory_metrics(
        self, simulation_id: str, step: int = 1
    ) -> "FactoryMetricsResponse":
        """
        Получить метрики завода.

        Args:
            simulation_id: ID симуляции
            step: Шаг симуляции (опционально)

        Returns:
            FactoryMetricsResponse: Метрики завода
        """
        # Сервер требует step как обязательный аргумент, даже если в proto он опциональный
        # Если step не передан, получаем его из симуляции или используем 0
        # ВАЖНО: получаем step ДО _timeout_context, чтобы избежать конфликтов с вложенными контекстами

        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetMetricsRequest(
                    simulation_id=simulation_id, step=step
                )
                response = await self._with_retry(
                    self.stub.get_factory_metrics,
                    request,
                )

                return self._proto_to_factory_metrics_response(response)

        except Exception as e:
            logger.error(f"Failed to get factory metrics: {e}")
            raise

    async def get_production_metrics(
        self, simulation_id: str, step: int = 1
    ) -> "ProductionMetricsResponse":
        """
        Получить метрики производства.

        Args:
            simulation_id: ID симуляции
            step: Шаг симуляции (опционально)

        Returns:
            ProductionMetricsResponse: Метрики производства
        """
        # Сервер требует step как обязательный аргумент, даже если в proto он опциональный
        # Если step не передан, получаем его из симуляции или используем 0
        # ВАЖНО: получаем step ДО _timeout_context, чтобы избежать конфликтов с вложенными контекстами

        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetMetricsRequest(
                    simulation_id=simulation_id, step=step
                )
                response = await self._with_retry(
                    self.stub.get_production_metrics,
                    request,
                )

                return self._proto_to_production_metrics_response(response)

        except Exception as e:
            logger.error(f"Failed to get production metrics: {e}")
            raise

    async def get_quality_metrics(
        self, simulation_id: str, step: int = 1
    ) -> "QualityMetricsResponse":
        """
        Получить метрики качества.

        Args:
            simulation_id: ID симуляции
            step: Шаг симуляции (опционально)

        Returns:
            QualityMetricsResponse: Метрики качества
        """
        # Сервер требует step как обязательный аргумент, даже если в proto он опциональный
        # Если step не передан, получаем его из симуляции или используем 0
        # ВАЖНО: получаем step ДО _timeout_context, чтобы избежать конфликтов с вложенными контекстами

        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetMetricsRequest(
                    simulation_id=simulation_id, step=step
                )
                response = await self._with_retry(
                    self.stub.get_quality_metrics,
                    request,
                )

                return self._proto_to_quality_metrics_response(response)

        except Exception as e:
            logger.error(f"Failed to get quality metrics: {e}")
            raise

    async def get_engineering_metrics(
        self, simulation_id: str, step: int = 1
    ) -> "EngineeringMetricsResponse":
        """
        Получить метрики инженерии.

        Args:
            simulation_id: ID симуляции
            step: Шаг симуляции (опционально)

        Returns:
            EngineeringMetricsResponse: Метрики инженерии
        """
        # Сервер требует step как обязательный аргумент, даже если в proto он опциональный
        # Если step не передан, получаем его из симуляции или используем 0
        # ВАЖНО: получаем step ДО _timeout_context, чтобы избежать конфликтов с вложенными контекстами

        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetMetricsRequest(
                    simulation_id=simulation_id, step=step
                )
                response = await self._with_retry(
                    self.stub.get_engineering_metrics,
                    request,
                )

                return self._proto_to_engineering_metrics_response(response)

        except Exception as e:
            logger.error(f"Failed to get engineering metrics: {e}")
            raise

    async def get_commercial_metrics(
        self, simulation_id: str, step: int = 1
    ) -> "CommercialMetricsResponse":
        """
        Получить коммерческие метрики.

        Args:
            simulation_id: ID симуляции
            step: Шаг симуляции (опционально)

        Returns:
            CommercialMetricsResponse: Коммерческие метрики
        """
        # Сервер требует step как обязательный аргумент, даже если в proto он опциональный
        # Если step не передан, получаем его из симуляции или используем 0
        # ВАЖНО: получаем step ДО _timeout_context, чтобы избежать конфликтов с вложенными контекстами

        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetMetricsRequest(
                    simulation_id=simulation_id, step=step
                )
                response = await self._with_retry(
                    self.stub.get_commercial_metrics,
                    request,
                )

                return self._proto_to_commercial_metrics_response(response)

        except Exception as e:
            logger.error(f"Failed to get commercial metrics: {e}")
            raise

    async def get_procurement_metrics(
        self, simulation_id: str, step: int = 1
    ) -> "ProcurementMetricsResponse":
        """
        Получить метрики закупок.

        Args:
            simulation_id: ID симуляции
            step: Шаг симуляции (опционально)

        Returns:
            ProcurementMetricsResponse: Метрики закупок
        """
        # Сервер требует step как обязательный аргумент, даже если в proto он опциональный
        # Если step не передан, получаем его из симуляции или используем 0
        # ВАЖНО: получаем step ДО _timeout_context, чтобы избежать конфликтов с вложенными контекстами

        try:
            async with self._timeout_context():
                await self._rate_limit()
                request = simulator_pb2.GetMetricsRequest(
                    simulation_id=simulation_id, step=step
                )
                response = await self._with_retry(
                    self.stub.get_procurement_metrics,
                    request,
                )

                return self._proto_to_procurement_metrics_response(response)

        except Exception as e:
            logger.error(f"Failed to get procurement metrics: {e}")
            raise

    async def get_all_metrics(
        self, simulation_id: str, step: int = 1
    ) -> "AllMetricsResponse":
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
                response = await self._with_retry(
                    self.stub.get_all_metrics,
                    simulator_pb2.GetAllMetricsRequest(
                        simulation_id=simulation_id, step=step
                    ),
                )

                return self._proto_to_all_metrics_response(response)

        except Exception as e:
            logger.error(f"Failed to get all metrics: {e}")
            raise

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
                response = await self._with_retry(
                    self.stub.get_production_schedule,
                    simulator_pb2.GetProductionScheduleRequest(
                        simulation_id=simulation_id
                    ),
                )

                return self._proto_to_production_schedule_response(response)

        except Exception as e:
            logger.error(f"Failed to get production schedule: {e}")
            raise

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
                response = await self._with_retry(
                    self.stub.get_workshop_plan,
                    simulator_pb2.GetWorkshopPlanRequest(simulation_id=simulation_id),
                )

                return self._proto_to_workshop_plan_response(response)

        except Exception as e:
            logger.error(f"Failed to get workshop plan: {e}")
            raise

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
                response = await self._with_retry(
                    self.stub.get_unplanned_repair,
                    simulator_pb2.GetUnplannedRepairRequest(
                        simulation_id=simulation_id
                    ),
                )

                return self._proto_to_unplanned_repair_response(response)

        except Exception as e:
            logger.error(f"Failed to get unplanned repair: {e}")
            raise

    async def get_warehouse_load_chart(
        self, simulation_id: str, warehouse_id: str
    ) -> "WarehouseLoadChartResponse":
        """
        Получить график загрузки склада.

        Args:
            simulation_id: ID симуляции
            warehouse_id: ID склада

        Returns:
            WarehouseLoadChartResponse: График загрузки склада
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_warehouse_load_chart,
                    simulator_pb2.GetWarehouseLoadChartRequest(
                        simulation_id=simulation_id, warehouse_id=warehouse_id
                    ),
                )

                return self._proto_to_warehouse_load_chart_response(response)

        except Exception as e:
            logger.error(f"Failed to get warehouse load chart: {e}")
            raise

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
                response = await self._with_retry(
                    self.stub.get_required_materials,
                    simulator_pb2.GetRequiredMaterialsRequest(
                        simulation_id=simulation_id
                    ),
                )

                return self._proto_to_required_materials_response(response)

        except Exception as e:
            logger.error(f"Failed to get required materials: {e}")
            raise

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
                response = await self._with_retry(
                    self.stub.get_available_improvements,
                    simulator_pb2.GetAvailableImprovementsRequest(
                        simulation_id=simulation_id
                    ),
                )

                return self._proto_to_available_improvements_response(response)

        except Exception as e:
            logger.error(f"Failed to get available improvements: {e}")
            raise

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
                response = await self._with_retry(
                    self.stub.get_defect_policies,
                    simulator_pb2.GetDefectPoliciesRequest(simulation_id=simulation_id),
                )

                return self._proto_to_defect_policies_response(response)

        except Exception as e:
            logger.error(f"Failed to get defect policies: {e}")
            raise

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
                response = await self._with_retry(
                    self.stub.validate_configuration,
                    simulator_pb2.ValidateConfigurationRequest(
                        simulation_id=simulation_id
                    ),
                )

                return self._proto_to_validation_response(response)

        except Exception as e:
            logger.error(f"Failed to validate configuration: {e}")
            raise

    async def set_quality_inspection(
        self, simulation_id: str, supplier_id: str, inspection_enabled: bool = True
    ) -> simulator_pb2.SimulationResponse:
        """
        Установить контроль качества.

        Args:
            simulation_id: ID симуляции
            supplier_id: ID поставщика
            inspection_enabled: Включить контроль качества

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.set_quality_inspection,
                    simulator_pb2.SetQualityInspectionRequest(
                        simulation_id=simulation_id,
                        supplier_id=supplier_id,
                        inspection_enabled=inspection_enabled,
                    ),
                )

                return self._proto_to_simulation_response(response)

        except Exception as e:
            logger.error(f"Failed to set quality inspection: {e}")
            raise

    async def set_delivery_period(
        self, simulation_id: str, supplier_id: str, delivery_period_days: int
    ) -> simulator_pb2.SimulationResponse:
        """
        Установить период поставок.

        Args:
            simulation_id: ID симуляции
            supplier_id: ID поставщика
            delivery_period_days: Период поставок в днях

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.set_delivery_period,
                    simulator_pb2.SetDeliveryPeriodRequest(
                        simulation_id=simulation_id,
                        supplier_id=supplier_id,
                        delivery_period_days=delivery_period_days,
                    ),
                )

                return self._proto_to_simulation_response(response)

        except Exception as e:
            logger.error(f"Failed to set delivery period: {e}")
            raise

    async def set_equipment_maintenance_interval(
        self, simulation_id: str, equipment_id: str, interval_days: int
    ) -> simulator_pb2.SimulationResponse:
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
                response = await self._with_retry(
                    self.stub.set_equipment_maintenance_interval,
                    simulator_pb2.SetEquipmentMaintenanceIntervalRequest(
                        simulation_id=simulation_id,
                        equipment_id=equipment_id,
                        interval_days=interval_days,
                    ),
                )

                return self._proto_to_simulation_response(response)

        except Exception as e:
            logger.error(f"Failed to set equipment maintenance interval: {e}")
            raise

    async def set_certification_status(
        self, simulation_id: str, certificate_type: str, is_obtained: bool = False
    ) -> simulator_pb2.SimulationResponse:
        """
        Установить статус сертификации.

        Args:
            simulation_id: ID симуляции
            certificate_type: Тип сертификата
            is_obtained: Получен ли сертификат

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.set_certification_status,
                    simulator_pb2.SetCertificationStatusRequest(
                        simulation_id=simulation_id,
                        certificate_type=certificate_type,
                        is_obtained=is_obtained,
                    ),
                )

                return self._proto_to_simulation_response(response)

        except Exception as e:
            logger.error(f"Failed to set certification status: {e}")
            raise

    async def set_lean_improvement_status(
        self, simulation_id: str, improvement_id: str, is_implemented: bool = False
    ) -> simulator_pb2.SimulationResponse:
        """
        Установить статус Lean улучшения.

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
                response = await self._with_retry(
                    self.stub.set_lean_improvement_status,
                    simulator_pb2.SetLeanImprovementStatusRequest(
                        simulation_id=simulation_id,
                        name=improvement_id,  # В proto используется name вместо improvement_id
                        is_implemented=is_implemented,
                    ),
                )

                return self._proto_to_simulation_response(response)

        except Exception as e:
            logger.error(f"Failed to set lean improvement status: {e}")
            raise

    # ==================== REFERENCE DATA METHODS ====================

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

                return self._proto_to_material_types_response(response)

        except Exception as e:
            logger.error(f"Failed to get material types: {e}")
            raise

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

                return self._proto_to_equipment_types_response(response)

        except Exception as e:
            logger.error(f"Failed to get equipment types: {e}")
            raise

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

                return self._proto_to_workplace_types_response(response)

        except Exception as e:
            logger.error(f"Failed to get workplace types: {e}")
            raise

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

                return self._proto_to_defect_policies_list_response(response)

        except Exception as e:
            logger.error(f"Failed to get available defect policies: {e}")
            raise

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

                return self._proto_to_improvements_list_response(response)

        except Exception as e:
            logger.error(f"Failed to get available improvements list: {e}")
            raise

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

                return self._proto_to_certifications_list_response(response)

        except Exception as e:
            logger.error(f"Failed to get available certifications: {e}")
            raise

    async def get_available_sales_strategies(self) -> "SalesStrategiesListResponse":
        """
        Получить доступные стратегии продаж.

        Returns:
            SalesStrategiesListResponse: Стратегии продаж
        """
        try:
            async with self._timeout_context():
                await self._rate_limit()
                response = await self._with_retry(
                    self.stub.get_available_sales_strategies,
                    simulator_pb2.GetAvailableSalesStrategiesRequest(),
                )

                return self._proto_to_sales_strategies_list_response(response)

        except Exception as e:
            logger.error(f"Failed to get available sales strategies: {e}")
            raise

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

    # ==================== NEW PROTO CONVERSION METHODS ====================

    def _proto_to_production_plan_row(self, proto_row):
        """Конвертировать protobuf ProductionPlanRow в Pydantic модель."""
        from .models import ProductionPlanRow

        return ProductionPlanRow(
            tender_id=proto_row.tender_id,
            product_name=proto_row.product_name,
            priority=proto_row.priority,
            plan_date=proto_row.plan_date,
            dse=proto_row.dse,
            short_set=proto_row.short_set,
            dse_name=proto_row.dse_name,
            planned_quantity=proto_row.planned_quantity,
            actual_quantity=proto_row.actual_quantity,
            remaining_to_produce=proto_row.remaining_to_produce,
            provision_status=proto_row.provision_status,
            note=proto_row.note,
            planned_completion_date=proto_row.planned_completion_date,
            cost_breakdown=proto_row.cost_breakdown,
            order_number=proto_row.order_number,
        )

    def _production_plan_row_to_proto(self, row: "ProductionPlanRow"):
        """Конвертировать ProductionPlanRow в protobuf."""
        return simulator_pb2.ProductionPlanRow(
            tender_id=row.tender_id,
            product_name=row.product_name,
            priority=row.priority,
            plan_date=row.plan_date,
            dse=row.dse,
            short_set=row.short_set,
            dse_name=row.dse_name,
            planned_quantity=row.planned_quantity,
            actual_quantity=row.actual_quantity,
            remaining_to_produce=row.remaining_to_produce,
            provision_status=row.provision_status,
            note=row.note,
            planned_completion_date=row.planned_completion_date,
            cost_breakdown=row.cost_breakdown,
            order_number=row.order_number,
        )

    def _proto_to_production_schedule(self, proto_schedule):
        """Конвертировать protobuf ProductionSchedule в Pydantic модель."""
        from .models import ProductionSchedule

        return ProductionSchedule(
            rows=[
                self._proto_to_production_plan_row(row) for row in proto_schedule.rows
            ]
        )

    def _production_schedule_to_proto(self, schedule: "ProductionSchedule"):
        """Конвертировать ProductionSchedule в protobuf."""
        return simulator_pb2.ProductionSchedule(
            rows=[self._production_plan_row_to_proto(row) for row in schedule.rows]
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

    def _proto_to_required_material(self, proto_material):
        """Конвертировать protobuf RequiredMaterial в Pydantic модель."""
        from .models import RequiredMaterial

        return RequiredMaterial(
            material_id=proto_material.material_id,
            name=proto_material.name,
            has_contracted_supplier=proto_material.has_contracted_supplier,
            required_quantity=proto_material.required_quantity,
            current_stock=proto_material.current_stock,
        )

    # ==================== METRICS CONVERSION METHODS ====================

    def _proto_to_monthly_productivity(self, proto_prod):
        """Конвертировать protobuf MonthlyProductivity в Pydantic модель."""
        from .models import MonthlyProductivity

        return MonthlyProductivity(
            month=proto_prod.month,
            units_produced=proto_prod.units_produced,
        )

    def _proto_to_warehouse_metrics(self, proto_metrics):
        """Конвертировать protobuf WarehouseMetrics в Pydantic модель."""
        from .models import WarehouseMetrics

        return WarehouseMetrics(
            fill_level=proto_metrics.fill_level,
            current_load=proto_metrics.current_load,
            max_capacity=proto_metrics.max_capacity,
            material_levels=dict(proto_metrics.material_levels),
            load_over_time=list(proto_metrics.load_over_time),
            max_capacity_over_time=list(proto_metrics.max_capacity_over_time),
        )

    def _proto_to_production_metrics(self, proto_metrics):
        """Конвертировать protobuf ProductionMetrics в Pydantic модель."""
        from .models import ProductionMetrics

        return ProductionMetrics(
            monthly_productivity=[
                self._proto_to_monthly_productivity(mp)
                for mp in proto_metrics.monthly_productivity
            ],
            average_equipment_utilization=proto_metrics.average_equipment_utilization,
            wip_count=proto_metrics.wip_count,
            finished_goods_count=proto_metrics.finished_goods_count,
            material_reserves=dict(proto_metrics.material_reserves),
        )

    def _proto_to_defect_cause(self, proto_cause):
        """Конвертировать protobuf DefectCause в Pydantic модель."""
        from .models import DefectCause

        return DefectCause(
            cause=proto_cause.cause,
            count=proto_cause.count,
            percentage=proto_cause.percentage,
        )

    def _proto_to_quality_metrics(self, proto_metrics):
        """Конвертировать protobuf QualityMetrics в Pydantic модель."""
        from .models import QualityMetrics

        return QualityMetrics(
            defect_percentage=proto_metrics.defect_percentage,
            good_output_percentage=proto_metrics.good_output_percentage,
            defect_causes=[
                self._proto_to_defect_cause(dc) for dc in proto_metrics.defect_causes
            ],
            average_material_quality=proto_metrics.average_material_quality,
            average_supplier_failure_probability=proto_metrics.average_supplier_failure_probability,
            procurement_volume=proto_metrics.procurement_volume,
        )

    def _proto_to_operation_timing(self, proto_timing):
        """Конвертировать protobuf OperationTiming в Pydantic модель."""
        from .models import OperationTiming

        return OperationTiming(
            operation_name=proto_timing.operation_name,
            cycle_time=proto_timing.cycle_time,
            takt_time=proto_timing.takt_time,
            timing_cost=proto_timing.timing_cost,
        )

    def _proto_to_downtime_record(self, proto_record):
        """Конвертировать protobuf DowntimeRecord в Pydantic модель."""
        from .models import DowntimeRecord

        return DowntimeRecord(
            cause=proto_record.cause,
            total_minutes=proto_record.total_minutes,
            average_per_shift=proto_record.average_per_shift,
        )

    def _proto_to_defect_analysis(self, proto_analysis):
        """Конвертировать protobuf DefectAnalysis в Pydantic модель."""
        from .models import DefectAnalysis

        return DefectAnalysis(
            defect_type=proto_analysis.defect_type,
            count=proto_analysis.count,
            percentage=proto_analysis.percentage,
            cumulative_percentage=proto_analysis.cumulative_percentage,
        )

    def _proto_to_engineering_metrics(self, proto_metrics):
        """Конвертировать protobuf EngineeringMetrics в Pydantic модель."""
        from .models import EngineeringMetrics

        return EngineeringMetrics(
            operation_timings=[
                self._proto_to_operation_timing(ot)
                for ot in proto_metrics.operation_timings
            ],
            downtime_records=[
                self._proto_to_downtime_record(dr)
                for dr in proto_metrics.downtime_records
            ],
            defect_analysis=[
                self._proto_to_defect_analysis(da)
                for da in proto_metrics.defect_analysis
            ],
        )

    def _proto_to_yearly_revenue(self, proto_revenue):
        """Конвертировать protobuf YearlyRevenue в Pydantic модель."""
        from .models import YearlyRevenue

        return YearlyRevenue(
            year=proto_revenue.year,
            revenue=proto_revenue.revenue,
        )

    def _proto_to_tender_graph_point(self, proto_point):
        """Конвертировать protobuf TenderGraphPoint в Pydantic модель."""
        from .models import TenderGraphPoint

        return TenderGraphPoint(
            strategy=proto_point.strategy,
            unit_size=proto_point.unit_size,
            is_mastered=proto_point.is_mastered,
        )

    def _proto_to_project_profitability(self, proto_profit):
        """Конвертировать protobuf ProjectProfitability в Pydantic модель."""
        from .models import ProjectProfitability

        return ProjectProfitability(
            project_name=proto_profit.project_name,
            profitability=proto_profit.profitability,
        )

    def _proto_to_commercial_metrics(self, proto_metrics):
        """Конвертировать protobuf CommercialMetrics в Pydantic модель."""
        from .models import CommercialMetrics

        return CommercialMetrics(
            yearly_revenues=[
                self._proto_to_yearly_revenue(yr)
                for yr in proto_metrics.yearly_revenues
            ],
            tender_revenue_plan=proto_metrics.tender_revenue_plan,
            total_payments=proto_metrics.total_payments,
            total_receipts=proto_metrics.total_receipts,
            sales_forecast=dict(proto_metrics.sales_forecast),
            strategy_costs=dict(proto_metrics.strategy_costs),
            tender_graph=[
                self._proto_to_tender_graph_point(tgp)
                for tgp in proto_metrics.tender_graph
            ],
            project_profitabilities=[
                self._proto_to_project_profitability(pp)
                for pp in proto_metrics.project_profitabilities
            ],
            on_time_completed_orders=proto_metrics.on_time_completed_orders,
        )

    def _proto_to_supplier_performance(self, proto_perf):
        """Конвертировать protobuf SupplierPerformance в Pydantic модель."""
        from .models import SupplierPerformance

        return SupplierPerformance(
            supplier_id=proto_perf.supplier_id,
            delivered_quantity=proto_perf.delivered_quantity,
            projected_defect_rate=proto_perf.projected_defect_rate,
            planned_reliability=proto_perf.planned_reliability,
            actual_reliability=proto_perf.actual_reliability,
            planned_cost=proto_perf.planned_cost,
            actual_cost=proto_perf.actual_cost,
            actual_defect_count=proto_perf.actual_defect_count,
        )

    def _proto_to_procurement_metrics(self, proto_metrics):
        """Конвертировать protobuf ProcurementMetrics в Pydantic модель."""
        from .models import ProcurementMetrics

        return ProcurementMetrics(
            supplier_performances=[
                self._proto_to_supplier_performance(sp)
                for sp in proto_metrics.supplier_performances
            ],
            total_procurement_value=proto_metrics.total_procurement_value,
        )

    def _proto_to_factory_metrics(self, proto_metrics):
        """Конвертировать protobuf FactoryMetrics в Pydantic модель."""
        from .models import FactoryMetrics

        return FactoryMetrics(
            profitability=proto_metrics.profitability,
            on_time_delivery_rate=proto_metrics.on_time_delivery_rate,
            oee=proto_metrics.oee,
            warehouse_metrics={
                warehouse_id: self._proto_to_warehouse_metrics(metrics)
                for warehouse_id, metrics in proto_metrics.warehouse_metrics.items()
            },
            total_procurement_cost=proto_metrics.total_procurement_cost,
            defect_rate=proto_metrics.defect_rate,
        )

    def _proto_to_repair_record(self, proto_record):
        """Конвертировать protobuf RepairRecord в Pydantic модель."""
        from .models import RepairRecord

        return RepairRecord(
            month=proto_record.month,
            repair_cost=proto_record.repair_cost,
            equipment_id=proto_record.equipment_id,
            reason=proto_record.reason,
        )

    def _proto_to_unplanned_repair(self, proto_repair):
        """Конвертировать protobuf UnplannedRepair в Pydantic модель."""
        from .models import UnplannedRepair

        return UnplannedRepair(
            repairs=[self._proto_to_repair_record(r) for r in proto_repair.repairs],
            total_repair_cost=proto_repair.total_repair_cost,
        )

    def _proto_to_load_point(self, proto_point):
        """Конвертировать protobuf LoadPoint в Pydantic модель."""
        from .models import LoadPoint

        return LoadPoint(
            timestamp=proto_point.timestamp,
            load=proto_point.load,
            max_capacity=proto_point.max_capacity,
        )

    def _proto_to_warehouse_load_chart(self, proto_chart):
        """Конвертировать protobuf WarehouseLoadChart в Pydantic модель."""
        from .models import WarehouseLoadChart

        return WarehouseLoadChart(
            data_points=[
                self._proto_to_load_point(dp) for dp in proto_chart.data_points
            ],
            warehouse_id=proto_chart.warehouse_id,
        )

    def _proto_to_timing_data(self, proto_data):
        """Конвертировать protobuf TimingData в Pydantic модель."""
        from .models import TimingData

        return TimingData(
            process_name=proto_data.process_name,
            cycle_time=proto_data.cycle_time,
            takt_time=proto_data.takt_time,
            timing_cost=proto_data.timing_cost,
        )

    def _proto_to_operation_timing_chart(self, proto_chart):
        """Конвертировать protobuf OperationTimingChart в Pydantic модель."""
        from .models import OperationTimingChart

        return OperationTimingChart(
            timing_data=[
                self._proto_to_timing_data(td) for td in proto_chart.timing_data
            ],
            chart_type=proto_chart.chart_type,
        )

    def _proto_to_downtime_data(self, proto_data):
        """Конвертировать protobuf DowntimeData в Pydantic модель."""
        from .models import DowntimeData

        return DowntimeData(
            process_name=proto_data.process_name,
            cause=proto_data.cause,
            downtime_minutes=proto_data.downtime_minutes,
        )

    def _proto_to_downtime_chart(self, proto_chart):
        """Конвертировать protobuf DowntimeChart в Pydantic модель."""
        from .models import DowntimeChart

        return DowntimeChart(
            downtime_data=[
                self._proto_to_downtime_data(dd) for dd in proto_chart.downtime_data
            ],
            chart_type=proto_chart.chart_type,
        )

    def _proto_to_model_point(self, proto_point):
        """Конвертировать protobuf ModelPoint в Pydantic модель."""
        from .models import ModelPoint

        return ModelPoint(
            strategy=proto_point.strategy,
            unit_size=proto_point.unit_size,
            is_mastered=proto_point.is_mastered,
            model_name=proto_point.model_name,
        )

    def _proto_to_model_mastery_chart(self, proto_chart):
        """Конвертировать protobuf ModelMasteryChart в Pydantic модель."""
        from .models import ModelMasteryChart

        return ModelMasteryChart(
            model_points=[
                self._proto_to_model_point(mp) for mp in proto_chart.model_points
            ]
        )

    def _proto_to_project_data(self, proto_data):
        """Конвертировать protobuf ProjectData в Pydantic модель."""
        from .models import ProjectData

        return ProjectData(
            project_name=proto_data.project_name,
            profitability=proto_data.profitability,
        )

    def _proto_to_project_profitability_chart(self, proto_chart):
        """Конвертировать protobuf ProjectProfitabilityChart в Pydantic модель."""
        from .models import ProjectProfitabilityChart

        return ProjectProfitabilityChart(
            projects=[self._proto_to_project_data(pd) for pd in proto_chart.projects],
            chart_type=proto_chart.chart_type,
        )

    # ==================== RESPONSE CONVERSION METHODS ====================

    def _proto_to_factory_metrics_response(self, proto_response):
        """Конвертировать protobuf FactoryMetricsResponse в Pydantic модель."""
        from .models import FactoryMetricsResponse

        return FactoryMetricsResponse(
            metrics=self._proto_to_factory_metrics(proto_response.metrics),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_production_metrics_response(self, proto_response):
        """Конвертировать protobuf ProductionMetricsResponse в Pydantic модель."""
        from .models import ProductionMetricsResponse

        return ProductionMetricsResponse(
            metrics=self._proto_to_production_metrics(proto_response.metrics),
            unplanned_repairs=(
                self._proto_to_unplanned_repair(proto_response.unplanned_repairs)
                if proto_response.unplanned_repairs
                else None
            ),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_quality_metrics_response(self, proto_response):
        """Конвертировать protobuf QualityMetricsResponse в Pydantic модель."""
        from .models import QualityMetricsResponse

        return QualityMetricsResponse(
            metrics=self._proto_to_quality_metrics(proto_response.metrics),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_engineering_metrics_response(self, proto_response):
        """Конвертировать protobuf EngineeringMetricsResponse в Pydantic модель."""
        from .models import EngineeringMetricsResponse

        return EngineeringMetricsResponse(
            metrics=self._proto_to_engineering_metrics(proto_response.metrics),
            operation_timing_chart=(
                self._proto_to_operation_timing_chart(
                    proto_response.operation_timing_chart
                )
                if proto_response.operation_timing_chart
                else None
            ),
            downtime_chart=(
                self._proto_to_downtime_chart(proto_response.downtime_chart)
                if proto_response.downtime_chart
                else None
            ),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_commercial_metrics_response(self, proto_response):
        """Конвертировать protobuf CommercialMetricsResponse в Pydantic модель."""
        from .models import CommercialMetricsResponse

        return CommercialMetricsResponse(
            metrics=self._proto_to_commercial_metrics(proto_response.metrics),
            model_mastery_chart=(
                self._proto_to_model_mastery_chart(proto_response.model_mastery_chart)
                if proto_response.model_mastery_chart
                else None
            ),
            project_profitability_chart=(
                self._proto_to_project_profitability_chart(
                    proto_response.project_profitability_chart
                )
                if proto_response.project_profitability_chart
                else None
            ),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_procurement_metrics_response(self, proto_response):
        """Конвертировать protobuf ProcurementMetricsResponse в Pydantic модель."""
        from .models import ProcurementMetricsResponse

        return ProcurementMetricsResponse(
            metrics=self._proto_to_procurement_metrics(proto_response.metrics),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_production_schedule_response(self, proto_response):
        """Конвертировать protobuf ProductionScheduleResponse в Pydantic модель."""
        from .models import ProductionScheduleResponse

        return ProductionScheduleResponse(
            schedule=self._proto_to_production_schedule(proto_response.schedule),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_workshop_plan_response(self, proto_response):
        """Конвертировать protobuf WorkshopPlanResponse в Pydantic модель."""
        from .models import WorkshopPlanResponse

        return WorkshopPlanResponse(
            workshop_plan=self._proto_to_process_graph(proto_response.workshop_plan),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_unplanned_repair_response(self, proto_response):
        """Конвертировать protobuf UnplannedRepairResponse в Pydantic модель."""
        from .models import UnplannedRepairResponse

        return UnplannedRepairResponse(
            unplanned_repair=self._proto_to_unplanned_repair(
                proto_response.unplanned_repair
            ),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_warehouse_load_chart_response(self, proto_response):
        """Конвертировать protobuf WarehouseLoadChartResponse в Pydantic модель."""
        from .models import WarehouseLoadChartResponse

        return WarehouseLoadChartResponse(
            chart=self._proto_to_warehouse_load_chart(proto_response.chart),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_required_materials_response(self, proto_response):
        """Конвертировать protobuf RequiredMaterialsResponse в Pydantic модель."""
        from .models import RequiredMaterialsResponse

        return RequiredMaterialsResponse(
            materials=[
                self._proto_to_required_material(m) for m in proto_response.materials
            ],
            timestamp=proto_response.timestamp,
        )

    def _proto_to_available_improvements_response(self, proto_response):
        """Конвертировать protobuf AvailableImprovementsResponse в Pydantic модель."""
        from .models import AvailableImprovementsResponse

        return AvailableImprovementsResponse(
            improvements=[
                self._proto_to_lean_improvement(i) for i in proto_response.improvements
            ],
            timestamp=proto_response.timestamp,
        )

    def _proto_to_defect_policies_response(self, proto_response):
        """Конвертировать protobuf DefectPoliciesResponse в Pydantic модель."""
        from .models import DefectPoliciesResponse

        return DefectPoliciesResponse(
            available_policies=list(proto_response.available_policies),
            current_policy=proto_response.current_policy,
            timestamp=proto_response.timestamp,
        )

    def _proto_to_all_metrics_response(self, proto_response):
        """Конвертировать protobuf AllMetricsResponse в Pydantic модель."""
        from .models import AllMetricsResponse

        return AllMetricsResponse(
            factory=self._proto_to_factory_metrics(proto_response.factory),
            production=self._proto_to_production_metrics(proto_response.production),
            quality=self._proto_to_quality_metrics(proto_response.quality),
            engineering=self._proto_to_engineering_metrics(proto_response.engineering),
            commercial=self._proto_to_commercial_metrics(proto_response.commercial),
            procurement=self._proto_to_procurement_metrics(proto_response.procurement),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_validation_response(self, proto_response):
        """Конвертировать protobuf ValidationResponse в Pydantic модель."""
        from .models import ValidationResponse

        return ValidationResponse(
            is_valid=proto_response.is_valid,
            errors=list(proto_response.errors),
            warnings=list(proto_response.warnings),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_material_types_response(self, proto_response):
        """Конвертировать protobuf MaterialTypesResponse в Pydantic модель."""
        from .models import MaterialTypesResponse

        return MaterialTypesResponse(
            material_types=list(proto_response.material_types),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_equipment_types_response(self, proto_response):
        """Конвертировать protobuf EquipmentTypesResponse в Pydantic модель."""
        from .models import EquipmentTypesResponse

        return EquipmentTypesResponse(
            equipment_types=list(proto_response.equipment_types),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_workplace_types_response(self, proto_response):
        """Конвертировать protobuf WorkplaceTypesResponse в Pydantic модель."""
        from .models import WorkplaceTypesResponse

        return WorkplaceTypesResponse(
            workplace_types=list(proto_response.workplace_types),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_defect_policies_list_response(self, proto_response):
        """Конвертировать protobuf DefectPoliciesListResponse в Pydantic модель."""
        from .models import DefectPoliciesListResponse

        return DefectPoliciesListResponse(
            policies=list(proto_response.policies),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_improvements_list_response(self, proto_response):
        """Конвертировать protobuf ImprovementsListResponse в Pydantic модель."""
        from .models import ImprovementsListResponse

        return ImprovementsListResponse(
            improvements=list(proto_response.improvements),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_certifications_list_response(self, proto_response):
        """Конвертировать protobuf CertificationsListResponse в Pydantic модель."""
        from .models import CertificationsListResponse

        return CertificationsListResponse(
            certifications=list(proto_response.certifications),
            timestamp=proto_response.timestamp,
        )

    def _proto_to_sales_strategies_list_response(self, proto_response):
        """Конвертировать protobuf SalesStrategiesListResponse в Pydantic модель."""
        from .models import SalesStrategiesListResponse

        return SalesStrategiesListResponse(
            strategies=list(proto_response.strategies),
            timestamp=proto_response.timestamp,
        )
