from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime
import uuid


# ==================== ENUMS ====================


class WarehouseType(str, Enum):
    """Типы складов - точное соответствие protobuf."""

    WAREHOUSE_TYPE_UNSPECIFIED = "WAREHOUSE_TYPE_UNSPECIFIED"
    WAREHOUSE_TYPE_MATERIALS = "WAREHOUSE_TYPE_MATERIALS"
    WAREHOUSE_TYPE_PRODUCTS = "WAREHOUSE_TYPE_PRODUCTS"


# ==================== DATA MODELS (основные сущности) ====================


class Supplier(BaseModel):
    """Поставщик - точное соответствие protobuf Supplier."""

    supplier_id: str
    name: str
    product_name: str
    delivery_period: int
    special_delivery_period: int
    reliability: float
    product_quality: float
    cost: int
    special_delivery_cost: int

    model_config = ConfigDict(from_attributes=True)


class Worker(BaseModel):
    """Работник - точное соответствие protobuf Worker."""

    worker_id: str
    name: str
    qualification: int
    specialty: str
    salary: int

    model_config = ConfigDict(from_attributes=True)


class Logist(BaseModel):
    """Логист - точное соответствие protobuf Logist."""

    worker_id: str
    name: str
    qualification: int
    specialty: str
    salary: int
    speed: int
    vehicle_type: str

    model_config = ConfigDict(from_attributes=True)


class Equipment(BaseModel):
    """Оборудование - точное соответствие protobuf Equipment."""

    equipment_id: str
    name: str
    reliability: float
    maintenance_period: int
    maintenance_cost: int
    cost: int
    repair_cost: int
    repair_time: int

    model_config = ConfigDict(from_attributes=True)


class Workplace(BaseModel):
    """Рабочее место - точное соответствие protobuf Workplace."""

    workplace_id: str
    workplace_name: str
    required_speciality: str
    required_qualification: int
    worker: Optional["Worker"] = None
    equipment: Optional["Equipment"] = None
    required_stages: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class Route(BaseModel):
    """Маршрут - точное соответствие protobuf Route."""

    length: int
    from_workplace: str
    to_workplace: str

    model_config = ConfigDict(from_attributes=True)


class ProcessGraph(BaseModel):
    """Карта процесса - точное соответствие protobuf ProcessGraph."""

    process_graph_id: str
    workplaces: List[Workplace] = Field(default_factory=list)
    routes: List[Route] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class Consumer(BaseModel):
    """Заказчик - точное соответствие protobuf Consumer."""

    consumer_id: str
    name: str
    type: str  # гос./не гос.

    model_config = ConfigDict(from_attributes=True)


class Tender(BaseModel):
    """Тендер - точное соответствие protobuf Tender."""

    tender_id: str
    consumer: Consumer
    cost: int
    quantity_of_products: int

    model_config = ConfigDict(from_attributes=True)


class Warehouse(BaseModel):
    """Склад - точное соответствие protobuf Warehouse."""

    warehouse_id: str
    inventory_worker: Optional[Worker] = None
    size: int
    loading: int
    materials: Dict[str, int] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

    @property
    def available_space(self) -> int:
        """Доступное место на складе."""
        return max(0, self.size - self.loading)


class SimulationParameters(BaseModel):
    """Параметры симуляции - точное соответствие protobuf SimulationParameters."""

    logist: Optional[Logist] = None
    suppliers: List[Supplier] = Field(default_factory=list)
    backup_suppliers: List[Supplier] = Field(default_factory=list)
    materials_warehouse: Optional[Warehouse] = None
    product_warehouse: Optional[Warehouse] = None
    processes: Optional[ProcessGraph] = None
    tenders: List[Tender] = Field(default_factory=list)
    dealing_with_defects: str = ""
    has_certification: bool = False
    production_improvements: List[str] = Field(default_factory=list)
    sales_strategy: str = ""

    model_config = ConfigDict(from_attributes=True)


class SimulationResults(BaseModel):
    """Результаты симуляции - точное соответствие protobuf SimulationResults."""

    profit: int
    cost: int
    profitability: float

    model_config = ConfigDict(from_attributes=True)

    @property
    def roi(self) -> float:
        """Return on Investment (в процентах)."""
        if self.cost == 0:
            return 0.0
        return (self.profit / self.cost) * 100

    @property
    def net_profit(self) -> int:
        """Чистая прибыль."""
        return self.profit - self.cost


class Simulation(BaseModel):
    """Симуляция - точное соответствие protobuf Simulation."""

    capital: int
    step: int
    simulation_id: str
    parameters: Optional[SimulationParameters] = None
    results: Optional[SimulationResults] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== RESPONSE MODELS (ответы сервисов) ====================


class SimulationResponse(BaseModel):
    """Ответ симуляции - точное соответствие protobuf SimulationResponse."""

    simulation: Simulation
    timestamp: str  # ISO формат

    model_config = ConfigDict(from_attributes=True)


class SuccessResponse(BaseModel):
    """Успешный ответ - точное соответствие protobuf SuccessResponse."""

    success: bool
    message: str
    timestamp: str  # ISO формат

    model_config = ConfigDict(from_attributes=True)


class GetAllSuppliersResponse(BaseModel):
    """Ответ со всеми поставщиками - точное соответствие protobuf."""

    suppliers: List[Supplier] = Field(default_factory=list)
    total_count: int

    model_config = ConfigDict(from_attributes=True)


class GetAllWorkersResponse(BaseModel):
    """Ответ со всеми работниками - точное соответствие protobuf."""

    workers: List[Worker] = Field(default_factory=list)
    total_count: int

    model_config = ConfigDict(from_attributes=True)


class GetAllLogistsResponse(BaseModel):
    """Ответ со всеми логистами - точное соответствие protobuf."""

    logists: List[Logist] = Field(default_factory=list)
    total_count: int

    model_config = ConfigDict(from_attributes=True)


class GetAllWorkplacesResponse(BaseModel):
    """Ответ со всеми рабочими местами - точное соответствие protobuf."""

    workplaces: List[Workplace] = Field(default_factory=list)
    total_count: int

    model_config = ConfigDict(from_attributes=True)


class GetAllConsumersResponse(BaseModel):
    """Ответ со всеми заказчиками - точное соответствие protobuf."""

    consumers: List[Consumer] = Field(default_factory=list)
    total_count: int

    model_config = ConfigDict(from_attributes=True)


class GetAllTendersResponse(BaseModel):
    """Ответ со всеми тендерами - точное соответствие protobuf."""

    tenders: List[Tender] = Field(default_factory=list)
    total_count: int

    model_config = ConfigDict(from_attributes=True)


class GetAllEquipmentResponse(BaseModel):
    """Ответ со всем оборудованием - точное соответствие protobuf GetAllEquipmentResopnse."""

    equipments: List[Equipment] = Field(default_factory=list)
    total_count: int

    model_config = ConfigDict(from_attributes=True)


# ==================== REQUEST MODELS (запросы к сервисам) ====================


class GetSimulationRequest(BaseModel):
    """Запрос получения симуляции - точное соответствие protobuf."""

    simulation_id: str

    model_config = ConfigDict(from_attributes=True)


class SetLogistRequest(BaseModel):
    """Запрос установки логиста - точное соответствие protobuf."""

    simulation_id: str
    worker_id: str

    model_config = ConfigDict(from_attributes=True)


class AddSupplierRequest(BaseModel):
    """Запрос добавления поставщика - точное соответствие protobuf."""

    simulation_id: str
    supplier_id: str
    is_backup: bool

    model_config = ConfigDict(from_attributes=True)


class SetWarehouseInventoryWorkerRequest(BaseModel):
    """Запрос установки работника на склад - точное соответствие protobuf."""

    simulation_id: str
    worker_id: str
    warehouse_type: WarehouseType

    model_config = ConfigDict(from_attributes=True)


class IncreaseWarehouseSizeRequest(BaseModel):
    """Запрос увеличения размера склада - точное соответствие protobuf."""

    simulation_id: str
    warehouse_type: WarehouseType
    size: int

    model_config = ConfigDict(from_attributes=True)


class AddTenderRequest(BaseModel):
    """Запрос добавления тендера - точное соответствие protobuf."""

    simulation_id: str
    tender_id: str

    model_config = ConfigDict(from_attributes=True)


class RemoveTenderRequest(BaseModel):
    """Запрос удаления тендера - точное соответствие protobuf."""

    simulation_id: str
    tender_id: str

    model_config = ConfigDict(from_attributes=True)


class SetDealingWithDefectsRequest(BaseModel):
    """Запрос установки политики работы с браком - точное соответствие protobuf."""

    simulation_id: str
    dealing_with_defects: str

    model_config = ConfigDict(from_attributes=True)


class SetHasCertificationRequest(BaseModel):
    """Запрос установки сертификации - точное соответствие protobuf."""

    simulation_id: str
    has_certification: bool

    model_config = ConfigDict(from_attributes=True)


class DeleteSupplierRequest(BaseModel):
    """Запрос удаления поставщика - точное соответствие protobuf."""

    simulation_id: str
    supplier_id: str

    model_config = ConfigDict(from_attributes=True)


class AddProductionImprovementRequest(BaseModel):
    """Запрос добавления улучшения производства - точное соответствие protobuf."""

    simulation_id: str
    production_improvement: str

    model_config = ConfigDict(from_attributes=True)


class DeleteProductionImprovementRequest(BaseModel):
    """Запрос удаления улучшения производства - точное соответствие protobuf."""

    simulation_id: str
    production_improvement: str

    model_config = ConfigDict(from_attributes=True)


class SetSalesStrategyRequest(BaseModel):
    """Запрос установки стратегии продаж - точное соответствие protobuf."""

    simulation_id: str
    sales_strategy: str

    model_config = ConfigDict(from_attributes=True)


class RunSimulationRequest(BaseModel):
    """Запрос запуска симуляции - точное соответствие protobuf."""

    simulation_id: str

    model_config = ConfigDict(from_attributes=True)


class AddProcessRouteRequest(BaseModel):
    """Запрос добавления маршрута процесса - точное соответствие protobuf."""

    simulation_id: str
    length: int
    from_workplace: str
    to_workplace: str

    model_config = ConfigDict(from_attributes=True)


class DeleteProcessRouteRequest(BaseModel):
    """Запрос удаления маршрута процесса - точное соответствие protobuf DeleteProcesRouteRequest."""

    simulation_id: str
    from_workplace: str
    to_workplace: str

    model_config = ConfigDict(from_attributes=True)


class SetWorkerOnWorkplaceRequest(BaseModel):
    """Запрос установки работника на рабочее место - точное соответствие protobuf SetWorkerOnWorkerplaceRequest."""

    simulation_id: str
    worker_id: str
    workplace_id: str

    model_config = ConfigDict(from_attributes=True)


class UnSetWorkerOnWorkplaceRequest(BaseModel):
    """Запрос снятия работника с рабочего места - точное соответствие protobuf UnSetWorkerOnWorkerplaceRequest."""

    simulation_id: str
    worker_id: str

    model_config = ConfigDict(from_attributes=True)


class SetEquipmentOnWorkplaceRequest(BaseModel):
    """Запрос установки оборудования на рабочее место - точное соответствие protobuf SetEquipmentOnWorkplaceRequst."""

    simulation_id: str
    workplace_id: str
    equipment_id: str

    model_config = ConfigDict(from_attributes=True)


class UnSetEquipmentOnWorkplaceRequest(BaseModel):
    """Запрос снятия оборудования с рабочего места - точное соответствие protobuf UnSetEquipmentOnWorkplaceRequst."""

    simulation_id: str
    workplace_id: str

    model_config = ConfigDict(from_attributes=True)


class CreateSimulationRequest(BaseModel):
    """Запрос создания симуляции - точное соответствие protobuf CreateSimulationRquest."""

    # Пустой запрос, как в protobuf
    pass


class PingRequest(BaseModel):
    """Запрос ping - точное соответствие protobuf."""

    # Пустой запрос, как в protobuf
    pass


# ==================== DATABASE REQUEST MODELS ====================


class CreateSupplierRequest(BaseModel):
    """Запрос создания поставщика - точное соответствие protobuf."""

    name: str
    product_name: str
    delivery_period: int
    special_delivery_period: int
    reliability: float
    product_quality: float
    cost: int
    special_delivery_cost: int

    model_config = ConfigDict(from_attributes=True)


class UpdateSupplierRequest(BaseModel):
    """Запрос обновления поставщика - точное соответствие protobuf."""

    supplier_id: str
    name: str
    product_name: str
    delivery_period: int
    special_delivery_period: int
    reliability: float
    product_quality: float
    cost: int
    special_delivery_cost: int

    model_config = ConfigDict(from_attributes=True)


class GetWarehouseRequest(BaseModel):
    """Запрос получения склада - точное соответствие protobuf."""

    warehouse_id: str

    model_config = ConfigDict(from_attributes=True)


class CreateWorkerRequest(BaseModel):
    """Запрос создания работника - точное соответствие protobuf."""

    name: str
    qualification: int
    specialty: str
    salary: int

    model_config = ConfigDict(from_attributes=True)


class UpdateWorkerRequest(BaseModel):
    """Запрос обновления работника - точное соответствие protobuf."""

    worker_id: str
    name: str
    qualification: int
    specialty: str
    salary: int

    model_config = ConfigDict(from_attributes=True)


class DeleteWorkerRequest(BaseModel):
    """Запрос удаления работника - точное соответствие protobuf."""

    worker_id: str

    model_config = ConfigDict(from_attributes=True)


class CreateLogistRequest(BaseModel):
    """Запрос создания логиста - точное соответствие protobuf."""

    name: str
    qualification: int
    specialty: str
    salary: int
    speed: int
    vehicle_type: str

    model_config = ConfigDict(from_attributes=True)


class UpdateLogistRequest(BaseModel):
    """Запрос обновления логиста - точное соответствие protobuf."""

    worker_id: str
    name: str
    qualification: int
    specialty: str
    salary: int
    speed: int
    vehicle_type: str

    model_config = ConfigDict(from_attributes=True)


class DeleteLogistRequest(BaseModel):
    """Запрос удаления логиста - точное соответствие protobuf."""

    worker_id: str

    model_config = ConfigDict(from_attributes=True)


class CreateWorkplaceRequest(BaseModel):
    """Запрос создания рабочего места - точное соответствие protobuf."""

    workplace_name: str
    required_speciality: str
    required_qualification: int
    worker_id: str
    required_stages: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UpdateWorkplaceRequest(BaseModel):
    """Запрос обновления рабочего места - точное соответствие protobuf."""

    workplace_id: str
    workplace_name: str
    required_speciality: str
    required_qualification: int
    worker_id: str
    required_stages: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DeleteWorkplaceRequest(BaseModel):
    """Запрос удаления рабочего места - точное соответствие protobuf."""

    workplace_id: str

    model_config = ConfigDict(from_attributes=True)


class GetProcessGraphRequest(BaseModel):
    """Запрос получения карты процесса - точное соответствие protobuf."""

    process_graph_id: str

    model_config = ConfigDict(from_attributes=True)


class CreateConsumerRequest(BaseModel):
    """Запрос создания заказчика - точное соответствие protobuf."""

    name: str
    type: str

    model_config = ConfigDict(from_attributes=True)


class UpdateConsumerRequest(BaseModel):
    """Запрос обновления заказчика - точное соответствие protobuf."""

    consumer_id: str
    name: str
    type: str

    model_config = ConfigDict(from_attributes=True)


class DeleteConsumerRequest(BaseModel):
    """Запрос удаления заказчика - точное соответствие protobuf."""

    consumer_id: str

    model_config = ConfigDict(from_attributes=True)


class CreateTenderRequest(BaseModel):
    """Запрос создания тендера - точное соответствие protobuf."""

    consumer_id: str
    cost: int
    quantity_of_products: int

    model_config = ConfigDict(from_attributes=True)


class UpdateTenderRequest(BaseModel):
    """Запрос обновления тендера - точное соответствие protobuf."""

    tender_id: str
    consumer_id: str
    cost: int
    quantity_of_products: int

    model_config = ConfigDict(from_attributes=True)


class DeleteTenderRequest(BaseModel):
    """Запрос удаления тендера - точное соответствие protobuf."""

    tender_id: str

    model_config = ConfigDict(from_attributes=True)


class GetAllSuppliersRequest(BaseModel):
    """Запрос всех поставщиков - точное соответствие protobuf."""

    # Пустой запрос, как в protobuf
    pass


class GetAllWorkersRequest(BaseModel):
    """Запрос всех работников - точное соответствие protobuf."""

    # Пустой запрос, как в protobuf
    pass


class GetAllLogistsRequest(BaseModel):
    """Запрос всех логистов - точное соответствие protobuf."""

    # Пустой запрос, как в protobuf
    pass


class GetAllWorkplacesRequest(BaseModel):
    """Запрос всех рабочих мест - точное соответствие protobuf."""

    # Пустой запрос, как в protobuf
    pass


class GetAllConsumersRequest(BaseModel):
    """Запрос всех заказчиков - точное соответствие protobuf."""

    # Пустой запрос, как в protobuf
    pass


class GetAllTendersRequest(BaseModel):
    """Запрос всех тендеров - точное соответствие protobuf."""

    # Пустой запрос, как в protobuf
    pass


class CreateEquipmentRequest(BaseModel):
    """Запрос создания оборудования - точное соответствие protobuf."""

    name: str
    reliability: float
    maintenance_period: int
    maintenance_cost: int
    cost: int
    repair_cost: int
    repair_time: int

    model_config = ConfigDict(from_attributes=True)


class UpdateEquipmentRequest(BaseModel):
    """Запрос обновления оборудования - точное соответствие protobuf."""

    equipment_id: str
    name: str
    reliability: float
    maintenance_period: int
    maintenance_cost: int
    cost: int
    repair_cost: int
    repair_time: int

    model_config = ConfigDict(from_attributes=True)


class DeleteEquipmentRequest(BaseModel):
    """Запрос удаления оборудования - точное соответствие protobuf."""

    equipment_id: str

    model_config = ConfigDict(from_attributes=True)


class GetAllEquipmentRequest(BaseModel):
    """Запрос всего оборудования - точное соответствие protobuf."""

    # Пустой запрос, как в protobuf
    pass


# ==================== HELPER MODELS (для удобства) ====================


class SimulationConfig(BaseModel):
    """Упрощенная конфигурация симуляции для клиента."""

    simulation_id: str
    capital: Optional[int] = None
    logist_id: Optional[str] = None
    supplier_ids: List[str] = Field(default_factory=list)
    backup_supplier_ids: List[str] = Field(default_factory=list)
    equipment_assignments: Dict[str, str] = Field(
        default_factory=dict
    )  # workplace_id: equipment_id
    tender_ids: List[str] = Field(default_factory=list)
    dealing_with_defects: str = "standard"
    has_certification: bool = False
    production_improvements: List[str] = Field(default_factory=list)
    sales_strategy: str = "standard"

    model_config = ConfigDict(from_attributes=True)


class ExtendedSimulationResults(SimulationResults):
    """Расширенные результаты симуляции с дополнительными полями."""

    capital: Optional[int] = None
    step: Optional[int] = None
    timestamp: Optional[datetime] = None

    @property
    def roi_percentage(self) -> float:
        """ROI в процентах."""
        if self.cost == 0:
            return 0.0
        return (self.profit / self.cost) * 100


# ==================== TYPE ALIASES ====================

SupplierList = List[Supplier]
WorkerList = List[Worker]
LogistList = List[Logist]
EquipmentList = List[Equipment]
TenderList = List[Tender]
ConsumerList = List[Consumer]
WorkplaceList = List[Workplace]


# ==================== EXPORTS ====================

__all__ = [
    # Enums
    "WarehouseType",
    # Data Models
    "Supplier",
    "Worker",
    "Logist",
    "Equipment",
    "Workplace",
    "Route",
    "ProcessGraph",
    "Consumer",
    "Tender",
    "Warehouse",
    "SimulationParameters",
    "SimulationResults",
    "Simulation",
    # Response Models
    "SimulationResponse",
    "SuccessResponse",
    "GetAllSuppliersResponse",
    "GetAllWorkersResponse",
    "GetAllLogistsResponse",
    "GetAllWorkplacesResponse",
    "GetAllConsumersResponse",
    "GetAllTendersResponse",
    "GetAllEquipmentResponse",
    # Request Models (SimulationService)
    "GetSimulationRequest",
    "SetLogistRequest",
    "AddSupplierRequest",
    "SetWarehouseInventoryWorkerRequest",
    "IncreaseWarehouseSizeRequest",
    "AddTenderRequest",
    "RemoveTenderRequest",
    "SetDealingWithDefectsRequest",
    "SetHasCertificationRequest",
    "DeleteSupplierRequest",
    "AddProductionImprovementRequest",
    "DeleteProductionImprovementRequest",
    "SetSalesStrategyRequest",
    "RunSimulationRequest",
    "AddProcessRouteRequest",
    "DeleteProcessRouteRequest",
    "SetWorkerOnWorkplaceRequest",
    "UnSetWorkerOnWorkplaceRequest",
    "SetEquipmentOnWorkplaceRequest",
    "UnSetEquipmentOnWorkplaceRequest",
    "CreateSimulationRequest",
    "PingRequest",
    # Request Models (DatabaseManager)
    "CreateSupplierRequest",
    "UpdateSupplierRequest",
    "GetWarehouseRequest",
    "CreateWorkerRequest",
    "UpdateWorkerRequest",
    "DeleteWorkerRequest",
    "CreateLogistRequest",
    "UpdateLogistRequest",
    "DeleteLogistRequest",
    "CreateWorkplaceRequest",
    "UpdateWorkplaceRequest",
    "DeleteWorkplaceRequest",
    "GetProcessGraphRequest",
    "CreateConsumerRequest",
    "UpdateConsumerRequest",
    "DeleteConsumerRequest",
    "CreateTenderRequest",
    "UpdateTenderRequest",
    "DeleteTenderRequest",
    "GetAllSuppliersRequest",
    "GetAllWorkersRequest",
    "GetAllLogistsRequest",
    "GetAllWorkplacesRequest",
    "GetAllConsumersRequest",
    "GetAllTendersRequest",
    "CreateEquipmentRequest",
    "UpdateEquipmentRequest",
    "DeleteEquipmentRequest",
    "GetAllEquipmentRequest",
    # Helper Models
    "SimulationConfig",
    "ExtendedSimulationResults",
    # Type Aliases
    "SupplierList",
    "WorkerList",
    "LogistList",
    "EquipmentList",
    "TenderList",
    "ConsumerList",
    "WorkplaceList",
]
