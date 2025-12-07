import asyncio
from typing import Optional, List, Dict, Any, Union
import logging

from .simulation_client import AsyncSimulationClient
from .database_client import AsyncDatabaseClient
from .models import *
from .exceptions import *

logger = logging.getLogger(__name__)


class AsyncUnifiedClient:
    """
    Объединенный клиент для работы с обоими сервисами.

    Фасад, который скрывает сложность работы с двумя разными сервисами.

    Пример использования:
    ```python
    async with AsyncUnifiedClient(
        sim_host="localhost",
        sim_port=50051,
        db_host="localhost",
        db_port=50052
    ) as client:
        # Получаем ресурсы из базы
        suppliers_response = await client.get_all_suppliers()
        logists_response = await client.get_all_logists()

        # Создаем и настраиваем симуляцию
        simulation_config = await client.create_simulation()
        await client.configure_simulation(
            simulation_id=simulation_config.simulation_id,
            logist_id=logists_response.logists[0].worker_id if logists_response.logists else None,
            supplier_ids=[s.supplier_id for s in suppliers_response.suppliers[:2]]
        )

        # Запускаем симуляцию и получаем полный ответ
        response = await client.run_simulation(simulation_config.simulation_id)
        results = response.simulation.results
        print(f"Прибыль: {results.profit:,} ₽")
    ```
    """

    def __init__(
        self,
        sim_host: str = "localhost",
        sim_port: int = 50051,
        db_host: str = "localhost",
        db_port: int = 50052,
        max_retries: int = 3,
        timeout: float = 30.0,
        rate_limit: Optional[float] = None,
        enable_logging: bool = True,
    ):
        """
        Инициализация объединенного клиента.

        Args:
            sim_host: Хост сервиса симуляции
            sim_port: Порт сервиса симуляции
            db_host: Хост сервиса базы данных
            db_port: Порт сервиса базы данных
            max_retries: Максимальное количество повторных попыток
            timeout: Таймаут операций
            rate_limit: Ограничение запросов
            enable_logging: Включить логирование
        """
        self.sim_client = AsyncSimulationClient(
            host=sim_host,
            port=sim_port,
            max_retries=max_retries,
            timeout=timeout,
            rate_limit=rate_limit,
            enable_logging=enable_logging,
        )

        self.db_client = AsyncDatabaseClient(
            host=db_host,
            port=db_port,
            max_retries=max_retries,
            timeout=timeout,
            rate_limit=rate_limit,
            enable_logging=enable_logging,
        )

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        """Подключиться к обоим сервисам."""
        logger.info("Connecting to services...")

        # Подключаемся параллельно к обоим сервисам
        await asyncio.gather(self.sim_client.connect(), self.db_client.connect())

        logger.info("Connected to all services")

    async def close(self):
        """Закрыть соединения с обоими сервисами."""
        logger.info("Closing connections...")

        await asyncio.gather(
            self.sim_client.close(),
            self.db_client.close(),
            return_exceptions=True,  # Закрываем оба, даже если один упал
        )

        logger.info("All connections closed")

    async def ping(self) -> Dict[str, bool]:
        """
        Проверить доступность всех сервисов.

        Returns:
            Dict: Статус каждого сервиса
        """
        results = await asyncio.gather(
            self.sim_client.ping(), self.db_client.ping(), return_exceptions=True
        )

        return {
            "simulation_service": isinstance(results[0], bool) and results[0],
            "database_service": isinstance(results[1], bool) and results[1],
        }

    # ==================== Прокси-методы для SimulationService ====================

    async def create_simulation(self) -> SimulationConfig:
        """
        Создать новую симуляцию.

        Returns:
            SimulationConfig: Конфигурация созданной симуляции
        """
        return await self.sim_client.create_simulation()

    async def get_simulation(self, simulation_id: str) -> SimulationResponse:
        """
        Получить информацию о симуляции.

        Args:
            simulation_id: ID симуляции

        Returns:
            SimulationResponse: Полный ответ с симуляцией
        """
        return await self.sim_client.get_simulation(simulation_id)

    async def get_simulation_as_dict(self, simulation_id: str) -> Dict[str, Any]:
        """
        Получить информацию о симуляции в виде словаря.

        Args:
            simulation_id: ID симуляции

        Returns:
            Dict: Информация о симуляции
        """
        return await self.sim_client.get_simulation_as_dict(simulation_id)

    async def run_simulation(self, simulation_id: str) -> SimulationResponse:
        """
        Запустить симуляцию.

        Args:
            simulation_id: ID симуляции

        Returns:
            SimulationResponse: Полный ответ с результатами
        """
        return await self.sim_client.run_simulation(simulation_id)

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
        return await self.sim_client.run_simulation_and_get_results(simulation_id)

    async def set_logist(
        self, simulation_id: str, worker_id: str
    ) -> SimulationResponse:
        """
        Назначить логиста.

        Args:
            simulation_id: ID симуляции
            worker_id: ID работника-логиста

        Returns:
            SimulationResponse: Обновленная симуляция
        """
        return await self.sim_client.set_logist(simulation_id, worker_id)

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
        return await self.sim_client.add_supplier(simulation_id, supplier_id, is_backup)

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
        return await self.sim_client.delete_supplier(simulation_id, supplier_id)

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
        return await self.sim_client.set_warehouse_worker(
            simulation_id, worker_id, warehouse_type
        )

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
        return await self.sim_client.increase_warehouse_size(
            simulation_id, warehouse_type, size
        )

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
        return await self.sim_client.set_worker_on_workplace(
            simulation_id, worker_id, workplace_id
        )

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
        return await self.sim_client.set_equipment_on_workplace(
            simulation_id, workplace_id, equipment_id
        )

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
        return await self.sim_client.unset_worker_on_workplace(simulation_id, worker_id)

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
        return await self.sim_client.unset_equipment_on_workplace(
            simulation_id, workplace_id
        )

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
        return await self.sim_client.add_tender(simulation_id, tender_id)

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
        return await self.sim_client.delete_tender(simulation_id, tender_id)

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
        return await self.sim_client.set_dealing_with_defects(simulation_id, policy)

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
        return await self.sim_client.set_certification(simulation_id, has_certification)

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
        return await self.sim_client.add_production_improvement(
            simulation_id, improvement
        )

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
        return await self.sim_client.delete_production_improvement(
            simulation_id, improvement
        )

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
        return await self.sim_client.set_sales_strategy(simulation_id, strategy)

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
        return await self.sim_client.add_process_route(
            simulation_id, length, from_workplace, to_workplace
        )

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
        return await self.sim_client.delete_process_route(
            simulation_id, from_workplace, to_workplace
        )

    # ==================== Прокси-методы для DatabaseManager ====================

    async def get_all_suppliers(self) -> GetAllSuppliersResponse:
        """
        Получить всех поставщиков.

        Returns:
            GetAllSuppliersResponse: Ответ со всеми поставщиками
        """
        return await self.db_client.get_all_suppliers()

    async def create_supplier(self, request: CreateSupplierRequest) -> Supplier:
        """
        Создать нового поставщика.

        Args:
            request: Запрос создания поставщика

        Returns:
            Supplier: Созданный поставщик
        """
        return await self.db_client.create_supplier(request)

    async def update_supplier(self, request: UpdateSupplierRequest) -> Supplier:
        """
        Обновить поставщика.

        Args:
            request: Запрос обновления поставщика

        Returns:
            Supplier: Обновленный поставщик
        """
        return await self.db_client.update_supplier(request)

    async def delete_supplier(self, request: DeleteSupplierRequest) -> SuccessResponse:
        """
        Удалить поставщика.

        Args:
            request: Запрос удаления поставщика

        Returns:
            SuccessResponse: Результат удаления
        """
        return await self.db_client.delete_supplier(request)

    async def get_all_workers(self) -> GetAllWorkersResponse:
        """
        Получить всех работников.

        Returns:
            GetAllWorkersResponse: Ответ со всеми работниками
        """
        return await self.db_client.get_all_workers()

    async def create_worker(self, request: CreateWorkerRequest) -> Worker:
        """
        Создать нового работника.

        Args:
            request: Запрос создания работника

        Returns:
            Worker: Созданный работник
        """
        return await self.db_client.create_worker(request)

    async def update_worker(self, request: UpdateWorkerRequest) -> Worker:
        """
        Обновить работника.

        Args:
            request: Запрос обновления работника

        Returns:
            Worker: Обновленный работник
        """
        return await self.db_client.update_worker(request)

    async def delete_worker(self, request: DeleteWorkerRequest) -> SuccessResponse:
        """
        Удалить работника.

        Args:
            request: Запрос удаления работника

        Returns:
            SuccessResponse: Результат удаления
        """
        return await self.db_client.delete_worker(request)

    async def get_all_logists(self) -> GetAllLogistsResponse:
        """
        Получить всех логистов.

        Returns:
            GetAllLogistsResponse: Ответ со всеми логистами
        """
        return await self.db_client.get_all_logists()

    async def create_logist(self, request: CreateLogistRequest) -> Logist:
        """
        Создать нового логиста.

        Args:
            request: Запрос создания логиста

        Returns:
            Logist: Созданный логист
        """
        return await self.db_client.create_logist(request)

    async def update_logist(self, request: UpdateLogistRequest) -> Logist:
        """
        Обновить логиста.

        Args:
            request: Запрос обновления логиста

        Returns:
            Logist: Обновленный логиста
        """
        return await self.db_client.update_logist(request)

    async def delete_logist(self, request: DeleteLogistRequest) -> SuccessResponse:
        """
        Удалить логиста.

        Args:
            request: Запрос удаления логиста

        Returns:
            SuccessResponse: Результат удаления
        """
        return await self.db_client.delete_logist(request)

    async def get_all_equipment(self) -> GetAllEquipmentResponse:
        """
        Получить всё оборудование.

        Returns:
            GetAllEquipmentResponse: Ответ со всем оборудованием
        """
        return await self.db_client.get_all_equipment()

    async def create_equipment(self, request: CreateEquipmentRequest) -> Equipment:
        """
        Создать новое оборудование.

        Args:
            request: Запрос создания оборудования

        Returns:
            Equipment: Созданное оборудование
        """
        return await self.db_client.create_equipment(request)

    async def update_equipment(self, request: UpdateEquipmentRequest) -> Equipment:
        """
        Обновить оборудование.

        Args:
            request: Запрос обновления оборудования

        Returns:
            Equipment: Обновленное оборудование
        """
        return await self.db_client.update_equipment(request)

    async def delete_equipment(
        self, request: DeleteEquipmentRequest
    ) -> SuccessResponse:
        """
        Удалить оборудование.

        Args:
            request: Запрос удаления оборудования

        Returns:
            SuccessResponse: Результат удаления
        """
        return await self.db_client.delete_equipment(request)

    async def get_all_tenders(self) -> GetAllTendersResponse:
        """
        Получить все тендеры.

        Returns:
            GetAllTendersResponse: Ответ со всеми тендерами
        """
        return await self.db_client.get_all_tenders()

    async def create_tender(self, request: CreateTenderRequest) -> Tender:
        """
        Создать новый тендер.

        Args:
            request: Запрос создания тендера

        Returns:
            Tender: Созданный тендер
        """
        return await self.db_client.create_tender(request)

    async def update_tender(self, request: UpdateTenderRequest) -> Tender:
        """
        Обновить тендер.

        Args:
            request: Запрос обновления тендера

        Returns:
            Tender: Обновленный тендер
        """
        return await self.db_client.update_tender(request)

    async def delete_tender(self, request: DeleteTenderRequest) -> SuccessResponse:
        """
        Удалить тендер.

        Args:
            request: Запрос удаления тендера

        Returns:
            SuccessResponse: Результат удаления
        """
        return await self.db_client.delete_tender(request)

    async def get_warehouse(self, request: GetWarehouseRequest) -> Warehouse:
        """
        Получить информацию о складе.

        Args:
            request: Запрос получения склада

        Returns:
            Warehouse: Модель склада
        """
        return await self.db_client.get_warehouse(request)

    async def get_all_consumers(self) -> GetAllConsumersResponse:
        """
        Получить всех заказчиков.

        Returns:
            GetAllConsumersResponse: Ответ со всеми заказчиками
        """
        return await self.db_client.get_all_consumers()

    async def create_consumer(self, request: CreateConsumerRequest) -> Consumer:
        """
        Создать нового заказчика.

        Args:
            request: Запрос создания заказчика

        Returns:
            Consumer: Созданный заказчик
        """
        return await self.db_client.create_consumer(request)

    async def update_consumer(self, request: UpdateConsumerRequest) -> Consumer:
        """
        Обновить заказчика.

        Args:
            request: Запрос обновления заказчика

        Returns:
            Consumer: Обновленный заказчик
        """
        return await self.db_client.update_consumer(request)

    async def delete_consumer(self, request: DeleteConsumerRequest) -> SuccessResponse:
        """
        Удалить заказчика.

        Args:
            request: Запрос удаления заказчика

        Returns:
            SuccessResponse: Результат удаления
        """
        return await self.db_client.delete_consumer(request)

    async def get_all_workplaces(self) -> GetAllWorkplacesResponse:
        """
        Получить все рабочие места.

        Returns:
            GetAllWorkplacesResponse: Ответ со всеми рабочими местами
        """
        return await self.db_client.get_all_workplaces()

    async def create_workplace(self, request: CreateWorkplaceRequest) -> Workplace:
        """
        Создать новое рабочее место.

        Args:
            request: Запрос создания рабочего места

        Returns:
            Workplace: Созданное рабочее место
        """
        return await self.db_client.create_workplace(request)

    async def update_workplace(self, request: UpdateWorkplaceRequest) -> Workplace:
        """
        Обновить рабочее место.

        Args:
            request: Запрос обновления рабочего места

        Returns:
            Workplace: Обновленное рабочее место
        """
        return await self.db_client.update_workplace(request)

    async def delete_workplace(
        self, request: DeleteWorkplaceRequest
    ) -> SuccessResponse:
        """
        Удалить рабочее место.

        Args:
            request: Запрос удаления рабочего места

        Returns:
            SuccessResponse: Результат удаления
        """
        return await self.db_client.delete_workplace(request)

    async def get_process_graph(self, request: GetProcessGraphRequest) -> ProcessGraph:
        """
        Получить карту процесса.

        Args:
            request: Запрос получения карты процесса

        Returns:
            ProcessGraph: Карта процесса
        """
        return await self.db_client.get_process_graph(request)

    # ==================== Упрощенные методы для обратной совместимости ====================

    async def get_all_suppliers_simple(self) -> List[Supplier]:
        """Упрощенный метод получения поставщиков."""
        response = await self.get_all_suppliers()
        return response.suppliers

    async def get_all_workers_simple(self) -> List[Worker]:
        """Упрощенный метод получения работников."""
        response = await self.get_all_workers()
        return response.workers

    async def get_all_logists_simple(self) -> List[Logist]:
        """Упрощенный метод получения логистов."""
        response = await self.get_all_logists()
        return response.logists

    async def get_all_equipment_simple(self) -> List[Equipment]:
        """Упрощенный метод получения оборудования."""
        response = await self.get_all_equipment()
        return response.equipments

    async def get_all_tenders_simple(self) -> List[Tender]:
        """Упрощенный метод получения тендеров."""
        response = await self.get_all_tenders()
        return response.tenders

    async def get_all_consumers_simple(self) -> List[Consumer]:
        """Упрощенный метод получения заказчиков."""
        response = await self.get_all_consumers()
        return response.consumers

    async def get_all_workplaces_simple(self) -> List[Workplace]:
        """Упрощенный метод получения рабочих мест."""
        response = await self.get_all_workplaces()
        return response.workplaces

    # ==================== Комбинированные методы ====================

    async def configure_simulation(
        self,
        simulation_id: str,
        logist_id: Optional[str] = None,
        supplier_ids: Optional[List[str]] = None,
        backup_supplier_ids: Optional[List[str]] = None,
        equipment_assignments: Optional[Dict[str, str]] = None,
        tender_ids: Optional[List[str]] = None,
        dealing_with_defects: Optional[str] = None,
        has_certification: Optional[bool] = None,
        production_improvements: Optional[List[str]] = None,
        sales_strategy: Optional[str] = None,
    ) -> List[Union[SimulationResponse, Exception]]:
        """
        Комплексная настройка симуляции.

        Args:
            simulation_id: ID симуляции
            logist_id: ID логиста
            supplier_ids: Список ID основных поставщиков
            backup_supplier_ids: Список ID запасных поставщиков
            equipment_assignments: {workplace_id: equipment_id}
            tender_ids: Список ID тендеров
            dealing_with_defects: Политика работы с браком
            has_certification: Есть ли сертификация
            production_improvements: Список улучшений производства
            sales_strategy: Стратегия продаж

        Returns:
            List[Union[SimulationResponse, Exception]]: Результаты всех операций
        """
        tasks = []

        # Настройка логиста
        if logist_id:
            tasks.append(self.set_logist(simulation_id, logist_id))

        # Настройка поставщиков
        if supplier_ids:
            for supplier_id in supplier_ids:
                tasks.append(self.add_supplier(simulation_id, supplier_id, False))

        if backup_supplier_ids:
            for supplier_id in backup_supplier_ids:
                tasks.append(self.add_supplier(simulation_id, supplier_id, True))

        # Настройка оборудования
        if equipment_assignments:
            for workplace_id, equipment_id in equipment_assignments.items():
                tasks.append(
                    self.set_equipment_on_workplace(
                        simulation_id, workplace_id, equipment_id
                    )
                )

        # Настройка тендеров
        if tender_ids:
            for tender_id in tender_ids:
                tasks.append(self.add_tender(simulation_id, tender_id))

        # Дополнительные настройки
        if dealing_with_defects:
            tasks.append(
                self.set_dealing_with_defects(simulation_id, dealing_with_defects)
            )

        if has_certification is not None:
            tasks.append(self.set_certification(simulation_id, has_certification))

        if production_improvements:
            for improvement in production_improvements:
                tasks.append(
                    self.add_production_improvement(simulation_id, improvement)
                )

        if sales_strategy:
            tasks.append(self.set_sales_strategy(simulation_id, sales_strategy))

        # Выполняем все задачи параллельно
        if tasks:
            return await asyncio.gather(*tasks, return_exceptions=True)

        return []

    async def configure_simulation_and_check(
        self,
        simulation_id: str,
        logist_id: Optional[str] = None,
        supplier_ids: Optional[List[str]] = None,
        backup_supplier_ids: Optional[List[str]] = None,
        equipment_assignments: Optional[Dict[str, str]] = None,
        tender_ids: Optional[List[str]] = None,
        dealing_with_defects: Optional[str] = None,
        has_certification: Optional[bool] = None,
        production_improvements: Optional[List[str]] = None,
        sales_strategy: Optional[str] = None,
    ) -> bool:
        """
        Комплексная настройка симуляции с проверкой результатов.

        Args:
            simulation_id: ID симуляции
            logist_id: ID логиста
            supplier_ids: Список ID основных поставщиков
            backup_supplier_ids: Список ID запасных поставщиков
            equipment_assignments: {workplace_id: equipment_id}
            tender_ids: Список ID тендеров
            dealing_with_defects: Политика работы с браком
            has_certification: Есть ли сертификация
            production_improvements: Список улучшений производства
            sales_strategy: Стратегия продаж

        Returns:
            bool: True если все настройки применены успешно
        """
        results = await self.configure_simulation(
            simulation_id=simulation_id,
            logist_id=logist_id,
            supplier_ids=supplier_ids,
            backup_supplier_ids=backup_supplier_ids,
            equipment_assignments=equipment_assignments,
            tender_ids=tender_ids,
            dealing_with_defects=dealing_with_defects,
            has_certification=has_certification,
            production_improvements=production_improvements,
            sales_strategy=sales_strategy,
        )

        # Проверяем результаты
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        error_count = len(results) - success_count

        if error_count > 0:
            logger.warning(f"Configured {success_count} out of {len(results)} settings")

        return error_count == 0

    async def run_complete_scenario(
        self, config: Optional[Dict[str, Any]] = None
    ) -> SimulationResponse:
        """
        Запустить полный сценарий: создание, настройка и запуск симуляции.

        Args:
            config: Конфигурация симуляции

        Returns:
            SimulationResponse: Полный ответ с результатами
        """
        config = config or {}

        # 1. Создаем симуляцию
        simulation_config = await self.create_simulation()
        simulation_id = simulation_config.simulation_id

        # 2. Настраиваем симуляцию
        await self.configure_simulation_and_check(
            simulation_id=simulation_id,
            logist_id=config.get("logist_id"),
            supplier_ids=config.get("supplier_ids"),
            backup_supplier_ids=config.get("backup_supplier_ids"),
            equipment_assignments=config.get("equipment_assignments"),
            tender_ids=config.get("tender_ids"),
            dealing_with_defects=config.get("dealing_with_defects"),
            has_certification=config.get("has_certification"),
            production_improvements=config.get("production_improvements"),
            sales_strategy=config.get("sales_strategy"),
        )

        # 3. Запускаем симуляцию
        return await self.run_simulation(simulation_id)

    async def get_available_resources(self) -> Dict[str, Any]:
        """
        Получить все доступные ресурсы параллельно.

        Returns:
            Dict: Все ресурсы
        """
        tasks = {
            "suppliers": self.get_all_suppliers(),
            "workers": self.get_all_workers(),
            "logists": self.get_all_logists(),
            "equipment": self.get_all_equipment(),
            "tenders": self.get_all_tenders(),
            "consumers": self.get_all_consumers(),
            "workplaces": self.get_all_workplaces(),
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        response_dict = {}
        for key, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                response_dict[key] = {
                    "error": str(result),
                    "items": [],
                    "total_count": 0,
                }
            else:
                response_dict[key] = {
                    "items": getattr(result, key, []),
                    "total_count": getattr(result, "total_count", 0),
                }

        return response_dict

    async def get_available_resources_simple(self) -> Dict[str, List]:
        """
        Получить все доступные ресурсы параллельно (упрощенная версия).

        Returns:
            Dict: Все ресурсы в виде списков
        """
        resources = await self.get_available_resources()

        return {
            "suppliers": resources["suppliers"]["items"],
            "workers": resources["workers"]["items"],
            "logists": resources["logists"]["items"],
            "equipment": resources["equipment"]["items"],
            "tenders": resources["tenders"]["items"],
            "consumers": resources["consumers"]["items"],
            "workplaces": resources["workplaces"]["items"],
        }

    async def create_and_configure_simulation(
        self,
        logist_id: Optional[str] = None,
        supplier_ids: Optional[List[str]] = None,
        backup_supplier_ids: Optional[List[str]] = None,
        equipment_assignments: Optional[Dict[str, str]] = None,
        tender_ids: Optional[List[str]] = None,
        dealing_with_defects: Optional[str] = None,
        has_certification: Optional[bool] = None,
        production_improvements: Optional[List[str]] = None,
        sales_strategy: Optional[str] = None,
    ) -> SimulationConfig:
        """
        Создать и настроить симуляцию за один шаг.

        Returns:
            SimulationConfig: Конфигурация созданной симуляции
        """
        # Создаем симуляцию
        simulation_config = await self.create_simulation()

        # Настраиваем симуляцию
        await self.configure_simulation_and_check(
            simulation_id=simulation_config.simulation_id,
            logist_id=logist_id,
            supplier_ids=supplier_ids,
            backup_supplier_ids=backup_supplier_ids,
            equipment_assignments=equipment_assignments,
            tender_ids=tender_ids,
            dealing_with_defects=dealing_with_defects,
            has_certification=has_certification,
            production_improvements=production_improvements,
            sales_strategy=sales_strategy,
        )

        return simulation_config

    async def create_complete_scenario(
        self, config: Optional[Dict[str, Any]] = None
    ) -> SimulationResponse:
        """
        Создать, настроить и запустить полный сценарий.

        Args:
            config: Конфигурация сценария

        Returns:
            SimulationResponse: Полный ответ с результатами
        """
        config = config or {}

        # Создаем и настраиваем симуляцию
        simulation_config = await self.create_and_configure_simulation(
            logist_id=config.get("logist_id"),
            supplier_ids=config.get("supplier_ids"),
            backup_supplier_ids=config.get("backup_supplier_ids"),
            equipment_assignments=config.get("equipment_assignments"),
            tender_ids=config.get("tender_ids"),
            dealing_with_defects=config.get("dealing_with_defects"),
            has_certification=config.get("has_certification"),
            production_improvements=config.get("production_improvements"),
            sales_strategy=config.get("sales_strategy"),
        )

        # Запускаем симуляцию
        return await self.run_simulation(simulation_config.simulation_id)
