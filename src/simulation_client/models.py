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


class DistributionStrategy(str, Enum):
    """Стратегия распределения производственного плана - точное соответствие protobuf."""

    DISTRIBUTION_STRATEGY_UNSPECIFIED = "DISTRIBUTION_STRATEGY_UNSPECIFIED"
    DISTRIBUTION_STRATEGY_BALANCED = "DISTRIBUTION_STRATEGY_BALANCED"
    DISTRIBUTION_STRATEGY_EFFICIENT = "DISTRIBUTION_STRATEGY_EFFICIENT"
    DISTRIBUTION_STRATEGY_CUSTOM = "DISTRIBUTION_STRATEGY_CUSTOM"
    DISTRIBUTION_STRATEGY_PRIORITY_BASED = "DISTRIBUTION_STRATEGY_PRIORITY_BASED"


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
    is_start_node: bool = False
    is_end_node: bool = False
    next_workplace_ids: List[str] = Field(default_factory=list)

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
    penalty_per_day: int = 0
    warranty_years: int = 0
    payment_form: str = ""

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
    quality_inspections: Dict[str, "QualityInspection"] = Field(default_factory=dict)
    delivery_schedules: Dict[str, "DeliverySchedule"] = Field(default_factory=dict)
    equipment_maintenance_intervals: Dict[str, int] = Field(default_factory=dict)
    spaghetti_diagram: Optional["SpaghettiDiagram"] = None
    production_schedule: Optional["ProductionSchedule"] = None
    sales_growth_forecast: float = 0.0
    unit_production_cost: int = 0
    certifications: List["Certification"] = Field(default_factory=list)
    lean_improvements: List["LeanImprovement"] = Field(default_factory=list)
    production_assignments: Dict[str, "ProductionPlanAssignment"] = Field(
        default_factory=dict
    )
    distribution_strategy: DistributionStrategy = (
        DistributionStrategy.DISTRIBUTION_STRATEGY_UNSPECIFIED
    )
    workshop_plan: Optional["WorkshopPlan"] = None

    model_config = ConfigDict(from_attributes=True)


class SimulationResults(BaseModel):
    """Результаты симуляции - точное соответствие protobuf SimulationResults."""

    profit: int
    cost: int
    profitability: float
    factory_metrics: Optional["FactoryMetrics"] = None
    production_metrics: Optional["ProductionMetrics"] = None
    quality_metrics: Optional["QualityMetrics"] = None
    engineering_metrics: Optional["EngineeringMetrics"] = None
    commercial_metrics: Optional["CommercialMetrics"] = None
    procurement_metrics: Optional["ProcurementMetrics"] = None

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
    room_id: str = ""
    is_completed: bool = False

    model_config = ConfigDict(from_attributes=True)


# ==================== METRICS MODELS (модели метрик) ====================


class WarehouseMetrics(BaseModel):
    """Метрики склада - точное соответствие protobuf WarehouseMetrics."""

    fill_level: float = 0.0
    current_load: int = 0
    max_capacity: int = 0
    material_levels: Dict[str, int] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class FactoryMetrics(BaseModel):
    """Метрики завода - точное соответствие protobuf FactoryMetrics."""

    profitability: float = 0.0
    on_time_delivery_rate: float = 0.0
    oee: float = 0.0
    warehouse_metrics: Dict[str, WarehouseMetrics] = Field(default_factory=dict)
    total_procurement_cost: int = 0
    defect_rate: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class ProductionMetrics(BaseModel):
    """Метрики производства - точное соответствие protobuf ProductionMetrics."""

    class MonthlyProductivity(BaseModel):
        """Месячная производительность."""

        month: str = ""
        units_produced: int = 0

        model_config = ConfigDict(from_attributes=True)

    monthly_productivity: List[MonthlyProductivity] = Field(default_factory=list)
    average_equipment_utilization: float = 0.0
    wip_count: int = 0
    finished_goods_count: int = 0
    material_reserves: Dict[str, int] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class QualityMetrics(BaseModel):
    """Метрики качества - точное соответствие protobuf QualityMetrics."""

    class DefectCause(BaseModel):
        """Причина брака."""

        cause: str = ""
        count: int = 0
        percentage: float = 0.0

        model_config = ConfigDict(from_attributes=True)

    defect_percentage: float = 0.0
    good_output_percentage: float = 0.0
    defect_causes: List[DefectCause] = Field(default_factory=list)
    average_material_quality: float = 0.0
    average_supplier_failure_probability: float = 0.0
    procurement_volume: int = 0

    model_config = ConfigDict(from_attributes=True)


class EngineeringMetrics(BaseModel):
    """Метрики инженерии - точное соответствие protobuf EngineeringMetrics."""

    class OperationTiming(BaseModel):
        """Время операции."""

        operation_name: str = ""
        cycle_time: int = 0
        takt_time: int = 0
        timing_cost: int = 0

        model_config = ConfigDict(from_attributes=True)

    class DowntimeRecord(BaseModel):
        """Запись простоя."""

        cause: str = ""
        total_minutes: int = 0
        average_per_shift: float = 0.0

        model_config = ConfigDict(from_attributes=True)

    class DefectAnalysis(BaseModel):
        """Анализ брака."""

        defect_type: str = ""
        count: int = 0
        percentage: float = 0.0
        cumulative_percentage: float = 0.0

        model_config = ConfigDict(from_attributes=True)

    operation_timings: List[OperationTiming] = Field(default_factory=list)
    downtime_records: List[DowntimeRecord] = Field(default_factory=list)
    defect_analysis: List[DefectAnalysis] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CommercialMetrics(BaseModel):
    """Метрики коммерции - точное соответствие protobuf CommercialMetrics."""

    class YearlyRevenue(BaseModel):
        """Годовая выручка."""

        year: int = 0
        revenue: int = 0

        model_config = ConfigDict(from_attributes=True)

    class TenderGraphPoint(BaseModel):
        """Точка графика тендеров."""

        strategy: str = ""
        unit_size: str = ""
        is_mastered: bool = False

        model_config = ConfigDict(from_attributes=True)

    class ProjectProfitability(BaseModel):
        """Прибыльность проекта."""

        project_name: str = ""
        profitability: float = 0.0

        model_config = ConfigDict(from_attributes=True)

    yearly_revenues: List[YearlyRevenue] = Field(default_factory=list)
    tender_revenue_plan: int = 0
    total_payments: int = 0
    total_receipts: int = 0
    sales_forecast: Dict[str, float] = Field(default_factory=dict)
    strategy_costs: Dict[str, int] = Field(default_factory=dict)
    tender_graph: List[TenderGraphPoint] = Field(default_factory=list)
    project_profitabilities: List[ProjectProfitability] = Field(default_factory=list)
    on_time_completed_orders: int = 0

    model_config = ConfigDict(from_attributes=True)


class ProcurementMetrics(BaseModel):
    """Метрики закупок - точное соответствие protobuf ProcurementMetrics."""

    class SupplierPerformance(BaseModel):
        """Производительность поставщика."""

        supplier_id: str = ""
        delivered_quantity: int = 0
        projected_defect_rate: float = 0.0
        planned_reliability: float = 0.0
        actual_reliability: float = 0.0
        planned_cost: int = 0
        actual_cost: int = 0
        actual_defect_count: int = 0

        model_config = ConfigDict(from_attributes=True)

    supplier_performances: List[SupplierPerformance] = Field(default_factory=list)
    total_procurement_value: int = 0

    model_config = ConfigDict(from_attributes=True)


# ==================== PRODUCTION PLANNING MODELS ====================


class ProductionPlanAssignment(BaseModel):
    """Распределение производственного плана - точное соответствие protobuf ProductionPlanAssignment."""

    schedule_item_id: str = ""
    workplace_id: str = ""
    assigned_quantity: int = 0
    assigned_worker_id: str = ""
    assigned_equipment_id: str = ""
    completion_percentage: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class ProductionSchedule(BaseModel):
    """Объемно-календарный план - точное соответствие protobuf ProductionSchedule."""

    class ScheduleItem(BaseModel):
        """Элемент плана."""

        item_id: str = ""
        priority: int = 0
        plan_number: str = ""
        plan_date: str = ""
        product_name: str = ""
        planned_quantity: int = 0
        actual_quantity: int = 0
        remaining_to_produce: int = 0
        planned_completion_date: str = ""
        order_number: str = ""
        tender_id: str = ""

        model_config = ConfigDict(from_attributes=True)

    schedule_items: List[ScheduleItem] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class WorkshopPlan(BaseModel):
    """План цеха - точное соответствие protobuf WorkshopPlan."""

    class WorkplaceNode(BaseModel):
        """Узел рабочего места."""

        workplace_id: str = ""
        assigned_worker: Optional[Worker] = None
        assigned_equipment: Optional[Equipment] = None
        maintenance_interval: int = 0
        is_start_node: bool = False
        is_end_node: bool = False
        assigned_schedule_items: List[str] = Field(default_factory=list)
        max_capacity_per_day: int = 0
        current_utilization: float = 0.0

        model_config = ConfigDict(from_attributes=True)

    workplace_nodes: List[WorkplaceNode] = Field(default_factory=list)
    logistic_routes: List[Route] = Field(default_factory=list)
    production_schedule_id: str = ""

    model_config = ConfigDict(from_attributes=True)


class UnplannedRepair(BaseModel):
    """Внеплановый ремонт - точное соответствие protobuf UnplannedRepair."""

    class RepairRecord(BaseModel):
        """Запись ремонта."""

        month: str = ""
        repair_cost: int = 0
        equipment_id: str = ""
        reason: str = ""

        model_config = ConfigDict(from_attributes=True)

    repairs: List[RepairRecord] = Field(default_factory=list)
    total_repair_cost: int = 0

    model_config = ConfigDict(from_attributes=True)


class SpaghettiDiagram(BaseModel):
    """Спагетти-диаграмма - точное соответствие protobuf SpaghettiDiagram."""

    class WorkplaceDetail(BaseModel):
        """Детали рабочего места."""

        workplace_id: str = ""
        assigned_worker: Optional[Worker] = None
        assigned_equipment: Optional[Equipment] = None
        maintenance_interval: int = 0

        model_config = ConfigDict(from_attributes=True)

    workplace_details: List[WorkplaceDetail] = Field(default_factory=list)
    logistic_routes: List[Route] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RequiredMaterial(BaseModel):
    """Требуемый материал - точное соответствие protobuf RequiredMaterial."""

    material_id: str = ""
    name: str = ""
    has_contracted_supplier: bool = False
    required_quantity: int = 0
    current_stock: int = 0

    model_config = ConfigDict(from_attributes=True)


class QualityInspection(BaseModel):
    """Контроль качества - точное соответствие protobuf QualityInspection."""

    material_id: str = ""
    inspection_enabled: bool = False
    inspection_strictness: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class DeliverySchedule(BaseModel):
    """График поставок - точное соответствие protobuf DeliverySchedule."""

    supplier_id: str = ""
    delivery_period_days: int = 0
    is_express_delivery: bool = False

    model_config = ConfigDict(from_attributes=True)


class Certification(BaseModel):
    """Сертификация - точное соответствие protobuf Certification."""

    certificate_type: str = ""
    is_obtained: bool = False
    implementation_cost: int = 0
    implementation_time_days: int = 0

    model_config = ConfigDict(from_attributes=True)


class LeanImprovement(BaseModel):
    """Улучшение по методологии Lean - точное соответствие protobuf LeanImprovement."""

    improvement_id: str = ""
    name: str = ""
    is_implemented: bool = False
    implementation_cost: int = 0
    efficiency_gain: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class WarehouseLoadChart(BaseModel):
    """График загрузки склада - точное соответствие protobuf WarehouseLoadChart."""

    class LoadPoint(BaseModel):
        """Точка загрузки."""

        timestamp: str = ""
        load: int = 0
        max_capacity: int = 0

        model_config = ConfigDict(from_attributes=True)

    data_points: List[LoadPoint] = Field(default_factory=list)
    warehouse_id: str = ""

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


class ProductionPlanDistributionResponse(BaseModel):
    """Ответ распределения производственного плана - точное соответствие protobuf."""

    assignments: List[ProductionPlanAssignment] = Field(default_factory=list)
    efficiency_score: float = 0.0
    total_assigned_quantity: int = 0
    warnings: List[str] = Field(default_factory=list)
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class FactoryMetricsResponse(BaseModel):
    """Ответ метрик завода - точное соответствие protobuf."""

    metrics: FactoryMetrics
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class ProductionMetricsResponse(BaseModel):
    """Ответ метрик производства - точное соответствие protobuf."""

    metrics: ProductionMetrics
    unplanned_repairs: Optional[UnplannedRepair] = None
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class QualityMetricsResponse(BaseModel):
    """Ответ метрик качества - точное соответствие protobuf."""

    metrics: QualityMetrics
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class EngineeringMetricsResponse(BaseModel):
    """Ответ метрик инженерии - точное соответствие protobuf."""

    metrics: EngineeringMetrics
    operation_timing_chart: Optional["OperationTimingChart"] = None
    downtime_chart: Optional["DowntimeChart"] = None
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class CommercialMetricsResponse(BaseModel):
    """Ответ метрик коммерции - точное соответствие protobuf."""

    metrics: CommercialMetrics
    model_mastery_chart: Optional["ModelMasteryChart"] = None
    project_profitability_chart: Optional["ProjectProfitabilityChart"] = None
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class ProcurementMetricsResponse(BaseModel):
    """Ответ метрик закупок - точное соответствие protobuf."""

    metrics: ProcurementMetrics
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class ProductionScheduleResponse(BaseModel):
    """Ответ производственного плана - точное соответствие protobuf."""

    schedule: ProductionSchedule
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class WorkshopPlanResponse(BaseModel):
    """Ответ плана цеха - точное соответствие protobuf."""

    workshop_plan: WorkshopPlan
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class UnplannedRepairResponse(BaseModel):
    """Ответ внеплановых ремонтов - точное соответствие protobuf."""

    unplanned_repair: UnplannedRepair
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class WarehouseLoadChartResponse(BaseModel):
    """Ответ графика загрузки склада - точное соответствие protobuf."""

    chart: WarehouseLoadChart
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class RequiredMaterialsResponse(BaseModel):
    """Ответ требуемых материалов - точное соответствие protobuf."""

    materials: List[RequiredMaterial] = Field(default_factory=list)
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class AvailableImprovementsResponse(BaseModel):
    """Ответ доступных улучшений - точное соответствие protobuf."""

    improvements: List[LeanImprovement] = Field(default_factory=list)
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class DefectPoliciesResponse(BaseModel):
    """Ответ политик работы с браком - точное соответствие protobuf."""

    available_policies: List[str] = Field(default_factory=list)
    current_policy: str = ""
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class SimulationStepResponse(BaseModel):
    """Ответ шага симуляции - точное соответствие protobuf."""

    simulation: Simulation
    factory_metrics: Optional[FactoryMetrics] = None
    production_metrics: Optional[ProductionMetrics] = None
    quality_metrics: Optional[QualityMetrics] = None
    engineering_metrics: Optional[EngineeringMetrics] = None
    commercial_metrics: Optional[CommercialMetrics] = None
    procurement_metrics: Optional[ProcurementMetrics] = None
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class SimulationHistoryResponse(BaseModel):
    """Ответ истории симуляции - точное соответствие protobuf."""

    steps: List[SimulationStepResponse] = Field(default_factory=list)
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class AllMetricsResponse(BaseModel):
    """Ответ всех метрик - точное соответствие protobuf."""

    factory: Optional[FactoryMetrics] = None
    production: Optional[ProductionMetrics] = None
    quality: Optional[QualityMetrics] = None
    engineering: Optional[EngineeringMetrics] = None
    commercial: Optional[CommercialMetrics] = None
    procurement: Optional[ProcurementMetrics] = None
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class ValidationResponse(BaseModel):
    """Ответ валидации - точное соответствие protobuf."""

    is_valid: bool = False
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


# ==================== CHART MODELS ====================


class OperationTimingChart(BaseModel):
    """График времени операций - точное соответствие protobuf."""

    class TimingData(BaseModel):
        """Данные времени."""

        process_name: str = ""
        cycle_time: int = 0
        takt_time: int = 0
        timing_cost: int = 0

        model_config = ConfigDict(from_attributes=True)

    timing_data: List[TimingData] = Field(default_factory=list)
    chart_type: str = ""

    model_config = ConfigDict(from_attributes=True)


class DowntimeChart(BaseModel):
    """График простоев - точное соответствие protobuf."""

    class DowntimeData(BaseModel):
        """Данные простоя."""

        process_name: str = ""
        cause: str = ""
        downtime_minutes: int = 0

        model_config = ConfigDict(from_attributes=True)

    downtime_data: List[DowntimeData] = Field(default_factory=list)
    chart_type: str = ""

    model_config = ConfigDict(from_attributes=True)


class ModelMasteryChart(BaseModel):
    """График освоения моделей - точное соответствие protobuf."""

    class ModelPoint(BaseModel):
        """Точка модели."""

        strategy: str = ""
        unit_size: str = ""
        is_mastered: bool = False
        model_name: str = ""

        model_config = ConfigDict(from_attributes=True)

    model_points: List[ModelPoint] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProjectProfitabilityChart(BaseModel):
    """График прибыльности проектов - точное соответствие protobuf."""

    class ProjectData(BaseModel):
        """Данные проекта."""

        project_name: str = ""
        profitability: float = 0.0

        model_config = ConfigDict(from_attributes=True)

    projects: List[ProjectData] = Field(default_factory=list)
    chart_type: str = ""

    model_config = ConfigDict(from_attributes=True)


# ==================== REFERENCE DATA MODELS ====================


class ReferenceDataResponse(BaseModel):
    """Ответ справочных данных - точное соответствие protobuf."""

    class SalesStrategyItem(BaseModel):
        """Элемент стратегии продаж."""

        id: str = ""
        name: str = ""
        description: str = ""
        growth_forecast: float = 0.0
        unit_cost: int = 0
        market_impact: str = ""
        trend_direction: str = ""

        model_config = ConfigDict(from_attributes=True)

    class DefectPolicyItem(BaseModel):
        """Элемент политики работы с браком."""

        id: str = ""
        name: str = ""
        description: str = ""

        model_config = ConfigDict(from_attributes=True)

    class CertificationItem(BaseModel):
        """Элемент сертификации."""

        id: str = ""
        name: str = ""
        description: str = ""
        implementation_cost: int = 0
        implementation_time_days: int = 0

        model_config = ConfigDict(from_attributes=True)

    class ImprovementItem(BaseModel):
        """Элемент улучшения."""

        id: str = ""
        name: str = ""
        description: str = ""
        implementation_cost: int = 0
        efficiency_gain: float = 0.0

        model_config = ConfigDict(from_attributes=True)

    class CompanyTypeItem(BaseModel):
        """Элемент типа компании."""

        id: str = ""
        name: str = ""
        description: str = ""

        model_config = ConfigDict(from_attributes=True)

    class SpecialtyItem(BaseModel):
        """Элемент специальности."""

        id: str = ""
        name: str = ""
        description: str = ""

        model_config = ConfigDict(from_attributes=True)

    class VehicleTypeItem(BaseModel):
        """Элемент типа транспорта."""

        id: str = ""
        name: str = ""
        description: str = ""
        speed_modifier: int = 0

        model_config = ConfigDict(from_attributes=True)

    class UnitSizeItem(BaseModel):
        """Элемент размера единицы."""

        id: str = ""
        name: str = ""
        description: str = ""

        model_config = ConfigDict(from_attributes=True)

    class ProductModelItem(BaseModel):
        """Элемент модели продукта."""

        id: str = ""
        name: str = ""
        description: str = ""
        unit_size: str = ""

        model_config = ConfigDict(from_attributes=True)

    class PaymentFormItem(BaseModel):
        """Элемент формы оплаты."""

        id: str = ""
        name: str = ""
        description: str = ""

        model_config = ConfigDict(from_attributes=True)

    class WorkplaceTypeItem(BaseModel):
        """Элемент типа рабочего места."""

        id: str = ""
        name: str = ""
        description: str = ""
        required_specialty: str = ""
        required_qualification: int = 0
        compatible_equipment: List[str] = Field(default_factory=list)

        model_config = ConfigDict(from_attributes=True)

    sales_strategies: List[SalesStrategyItem] = Field(default_factory=list)
    defect_policies: List[DefectPolicyItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    improvements: List[ImprovementItem] = Field(default_factory=list)
    company_types: List[CompanyTypeItem] = Field(default_factory=list)
    specialties: List[SpecialtyItem] = Field(default_factory=list)
    vehicle_types: List[VehicleTypeItem] = Field(default_factory=list)
    unit_sizes: List[UnitSizeItem] = Field(default_factory=list)
    product_models: List[ProductModelItem] = Field(default_factory=list)
    payment_forms: List[PaymentFormItem] = Field(default_factory=list)
    workplace_types: List[WorkplaceTypeItem] = Field(default_factory=list)
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class DefectPoliciesListResponse(BaseModel):
    """Ответ списка политик работы с браком - точное соответствие protobuf."""

    class DefectPolicyOption(BaseModel):
        """Опция политики работы с браком."""

        id: str = ""
        name: str = ""
        description: str = ""
        cost_multiplier: float = 0.0
        quality_impact: float = 0.0
        time_impact: float = 0.0

        model_config = ConfigDict(from_attributes=True)

    policies: List[DefectPolicyOption] = Field(default_factory=list)
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class ImprovementsListResponse(BaseModel):
    """Ответ списка улучшений - точное соответствие protobuf."""

    class ImprovementOption(BaseModel):
        """Опция улучшения."""

        id: str = ""
        name: str = ""
        description: str = ""
        implementation_cost: int = 0
        implementation_time_days: int = 0
        efficiency_gain: float = 0.0
        quality_improvement: float = 0.0
        cost_reduction: float = 0.0

        model_config = ConfigDict(from_attributes=True)

    improvements: List[ImprovementOption] = Field(default_factory=list)
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class CertificationsListResponse(BaseModel):
    """Ответ списка сертификаций - точное соответствие protobuf."""

    class CertificationOption(BaseModel):
        """Опция сертификации."""

        id: str = ""
        name: str = ""
        description: str = ""
        implementation_cost: int = 0
        implementation_time_days: int = 0
        market_access_improvement: float = 0.0
        quality_recognition: float = 0.0
        government_access: float = 0.0

        model_config = ConfigDict(from_attributes=True)

    certifications: List[CertificationOption] = Field(default_factory=list)
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class SalesStrategiesListResponse(BaseModel):
    """Ответ списка стратегий продаж - точное соответствие protobuf."""

    class SalesStrategyOption(BaseModel):
        """Опция стратегии продаж."""

        id: str = ""
        name: str = ""
        description: str = ""
        growth_forecast: float = 0.0
        unit_cost: int = 0
        market_impact: str = ""
        trend_direction: str = ""
        compatible_product_models: List[str] = Field(default_factory=list)

        model_config = ConfigDict(from_attributes=True)

    strategies: List[SalesStrategyOption] = Field(default_factory=list)
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class MaterialTypesResponse(BaseModel):
    """Ответ типов материалов - точное соответствие protobuf."""

    class MaterialType(BaseModel):
        """Тип материала."""

        material_id: str = ""
        name: str = ""
        description: str = ""
        unit: str = ""
        average_price: int = 0

        model_config = ConfigDict(from_attributes=True)

    material_types: List[MaterialType] = Field(default_factory=list)
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class EquipmentTypesResponse(BaseModel):
    """Ответ типов оборудования - точное соответствие protobuf."""

    class EquipmentType(BaseModel):
        """Тип оборудования."""

        equipment_type_id: str = ""
        name: str = ""
        description: str = ""
        base_reliability: float = 0.0
        base_maintenance_cost: int = 0
        base_cost: int = 0
        compatible_workplaces: List[str] = Field(default_factory=list)

        model_config = ConfigDict(from_attributes=True)

    equipment_types: List[EquipmentType] = Field(default_factory=list)
    timestamp: str = ""

    model_config = ConfigDict(from_attributes=True)


class WorkplaceTypesResponse(BaseModel):
    """Ответ типов рабочих мест - точное соответствие protobuf."""

    class WorkplaceType(BaseModel):
        """Тип рабочего места."""

        workplace_type_id: str = ""
        name: str = ""
        description: str = ""
        required_specialty: str = ""
        required_qualification: int = 0
        compatible_equipment_types: List[str] = Field(default_factory=list)

        model_config = ConfigDict(from_attributes=True)

    workplace_types: List[WorkplaceType] = Field(default_factory=list)
    timestamp: str = ""

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


class ConfigureWorkplaceInGraphRequest(BaseModel):
    """Запрос настройки рабочего места в графе - точное соответствие protobuf."""

    simulation_id: str
    workplace_id: str
    workplace_type: str
    worker_id: Optional[str] = None
    equipment_id: Optional[str] = None
    is_start_node: bool = False
    is_end_node: bool = False
    next_workplace_ids: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RemoveWorkplaceFromGraphRequest(BaseModel):
    """Запрос удаления рабочего места из графа - точное соответствие protobuf."""

    simulation_id: str
    workplace_id: str

    model_config = ConfigDict(from_attributes=True)


class SetWorkplaceAsStartNodeRequest(BaseModel):
    """Запрос установки рабочего места как начального узла - точное соответствие protobuf."""

    simulation_id: str
    workplace_id: str

    model_config = ConfigDict(from_attributes=True)


class SetWorkplaceAsEndNodeRequest(BaseModel):
    """Запрос установки рабочего места как конечного узла - точное соответствие protobuf."""

    simulation_id: str
    workplace_id: str

    model_config = ConfigDict(from_attributes=True)


class UpdateProcessGraphRequest(BaseModel):
    """Запрос обновления графа процесса - точное соответствие protobuf."""

    simulation_id: str
    process_graph: ProcessGraph

    model_config = ConfigDict(from_attributes=True)


class DistributeProductionPlanRequest(BaseModel):
    """Запрос распределения производственного плана - точное соответствие protobuf."""

    simulation_id: str
    strategy: DistributionStrategy
    auto_assign_workers: bool = False
    auto_assign_equipment: bool = False

    model_config = ConfigDict(from_attributes=True)


class GetProductionPlanDistributionRequest(BaseModel):
    """Запрос получения распределения производственного плана - точное соответствие protobuf."""

    simulation_id: str

    model_config = ConfigDict(from_attributes=True)


class UpdateProductionAssignmentRequest(BaseModel):
    """Запрос обновления назначения производства - точное соответствие protobuf."""

    simulation_id: str
    assignment: ProductionPlanAssignment

    model_config = ConfigDict(from_attributes=True)


class UpdateWorkshopPlanRequest(BaseModel):
    """Запрос обновления плана цеха - точное соответствие protobuf."""

    simulation_id: str
    workshop_plan: WorkshopPlan

    model_config = ConfigDict(from_attributes=True)


class GetMetricsRequest(BaseModel):
    """Запрос получения метрик - точное соответствие protobuf."""

    simulation_id: str
    step: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class GetProductionScheduleRequest(BaseModel):
    """Запрос получения производственного плана - точное соответствие protobuf."""

    simulation_id: str

    model_config = ConfigDict(from_attributes=True)


class UpdateProductionScheduleRequest(BaseModel):
    """Запрос обновления производственного плана - точное соответствие protobuf."""

    simulation_id: str
    schedule: ProductionSchedule

    model_config = ConfigDict(from_attributes=True)


class GetWorkshopPlanRequest(BaseModel):
    """Запрос получения плана цеха - точное соответствие protobuf."""

    simulation_id: str

    model_config = ConfigDict(from_attributes=True)


class GetUnplannedRepairRequest(BaseModel):
    """Запрос получения внеплановых ремонтов - точное соответствие protobuf."""

    simulation_id: str

    model_config = ConfigDict(from_attributes=True)


class GetWarehouseLoadChartRequest(BaseModel):
    """Запрос получения графика загрузки склада - точное соответствие protobuf."""

    simulation_id: str
    warehouse_id: str

    model_config = ConfigDict(from_attributes=True)


class SetQualityInspectionRequest(BaseModel):
    """Запрос установки контроля качества - точное соответствие protobuf."""

    simulation_id: str
    material_id: str
    inspection: QualityInspection

    model_config = ConfigDict(from_attributes=True)


class SetDeliveryScheduleRequest(BaseModel):
    """Запрос установки графика поставок - точное соответствие protobuf."""

    simulation_id: str
    supplier_id: str
    schedule: DeliverySchedule

    model_config = ConfigDict(from_attributes=True)


class SetEquipmentMaintenanceIntervalRequest(BaseModel):
    """Запрос установки интервала обслуживания оборудования - точное соответствие protobuf."""

    simulation_id: str
    equipment_id: str
    interval_days: int

    model_config = ConfigDict(from_attributes=True)


class SetCertificationStatusRequest(BaseModel):
    """Запрос установки статуса сертификации - точное соответствие protobuf."""

    simulation_id: str
    certificate_type: str
    is_obtained: bool

    model_config = ConfigDict(from_attributes=True)


class SetLeanImprovementStatusRequest(BaseModel):
    """Запрос установки статуса улучшения Lean - точное соответствие protobuf."""

    simulation_id: str
    improvement_id: str
    is_implemented: bool

    model_config = ConfigDict(from_attributes=True)


class SetSalesStrategyWithDetailsRequest(BaseModel):
    """Запрос установки стратегии продаж с деталями - точное соответствие protobuf."""

    simulation_id: str
    strategy: str
    growth_forecast: float = 0.0
    unit_cost: int = 0
    market_impact: str = ""
    trend_direction: str = ""

    model_config = ConfigDict(from_attributes=True)


class GetRequiredMaterialsRequest(BaseModel):
    """Запрос получения требуемых материалов - точное соответствие protobuf."""

    simulation_id: str

    model_config = ConfigDict(from_attributes=True)


class GetAvailableImprovementsRequest(BaseModel):
    """Запрос получения доступных улучшений - точное соответствие protobuf."""

    simulation_id: str

    model_config = ConfigDict(from_attributes=True)


class GetDefectPoliciesRequest(BaseModel):
    """Запрос получения политик работы с браком - точное соответствие protobuf."""

    simulation_id: str

    model_config = ConfigDict(from_attributes=True)


class RunSimulationStepRequest(BaseModel):
    """Запрос запуска шага симуляции - точное соответствие protobuf."""

    simulation_id: str
    step_count: int = 1

    model_config = ConfigDict(from_attributes=True)


class GetSimulationHistoryRequest(BaseModel):
    """Запрос получения истории симуляции - точное соответствие protobuf."""

    simulation_id: str

    model_config = ConfigDict(from_attributes=True)


class GetAllMetricsRequest(BaseModel):
    """Запрос получения всех метрик - точное соответствие protobuf."""

    simulation_id: str

    model_config = ConfigDict(from_attributes=True)


class ValidateConfigurationRequest(BaseModel):
    """Запрос валидации конфигурации - точное соответствие protobuf."""

    simulation_id: str

    model_config = ConfigDict(from_attributes=True)


class GetReferenceDataRequest(BaseModel):
    """Запрос получения справочных данных - точное соответствие protobuf."""

    data_type: str = ""

    model_config = ConfigDict(from_attributes=True)


class GetAvailableDefectPoliciesRequest(BaseModel):
    """Запрос получения доступных политик работы с браком - точное соответствие protobuf."""

    # Пустой запрос
    pass


class GetAvailableImprovementsListRequest(BaseModel):
    """Запрос получения списка доступных улучшений - точное соответствие protobuf."""

    # Пустой запрос
    pass


class GetAvailableCertificationsRequest(BaseModel):
    """Запрос получения доступных сертификаций - точное соответствие protobuf."""

    # Пустой запрос
    pass


class GetAvailableSalesStrategiesRequest(BaseModel):
    """Запрос получения доступных стратегий продаж - точное соответствие protobuf."""

    # Пустой запрос
    pass


class GetMaterialTypesRequest(BaseModel):
    """Запрос получения типов материалов - точное соответствие protobuf."""

    # Пустой запрос
    pass


class GetEquipmentTypesRequest(BaseModel):
    """Запрос получения типов оборудования - точное соответствие protobuf."""

    # Пустой запрос
    pass


class GetWorkplaceTypesRequest(BaseModel):
    """Запрос получения типов рабочих мест - точное соответствие protobuf."""

    # Пустой запрос
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
    penalty_per_day: int = 0
    warranty_years: int = 0
    payment_form: str = ""

    model_config = ConfigDict(from_attributes=True)


class UpdateTenderRequest(BaseModel):
    """Запрос обновления тендера - точное соответствие protobuf."""

    tender_id: str
    consumer_id: str
    cost: int
    quantity_of_products: int
    penalty_per_day: int = 0
    warranty_years: int = 0
    payment_form: str = ""

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
    "DistributionStrategy",
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
    # Metrics Models
    "FactoryMetrics",
    "WarehouseMetrics",
    "ProductionMetrics",
    "QualityMetrics",
    "EngineeringMetrics",
    "CommercialMetrics",
    "ProcurementMetrics",
    # Production Planning Models
    "ProductionPlanAssignment",
    "ProductionSchedule",
    "WorkshopPlan",
    "UnplannedRepair",
    "SpaghettiDiagram",
    "RequiredMaterial",
    "QualityInspection",
    "DeliverySchedule",
    "Certification",
    "LeanImprovement",
    "WarehouseLoadChart",
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
    "ProductionPlanDistributionResponse",
    "FactoryMetricsResponse",
    "ProductionMetricsResponse",
    "QualityMetricsResponse",
    "EngineeringMetricsResponse",
    "CommercialMetricsResponse",
    "ProcurementMetricsResponse",
    "ProductionScheduleResponse",
    "WorkshopPlanResponse",
    "UnplannedRepairResponse",
    "WarehouseLoadChartResponse",
    "RequiredMaterialsResponse",
    "AvailableImprovementsResponse",
    "DefectPoliciesResponse",
    "SimulationStepResponse",
    "SimulationHistoryResponse",
    "AllMetricsResponse",
    "ValidationResponse",
    # Chart Models
    "OperationTimingChart",
    "DowntimeChart",
    "ModelMasteryChart",
    "ProjectProfitabilityChart",
    # Reference Data Models
    "ReferenceDataResponse",
    "DefectPoliciesListResponse",
    "ImprovementsListResponse",
    "CertificationsListResponse",
    "SalesStrategiesListResponse",
    "MaterialTypesResponse",
    "EquipmentTypesResponse",
    "WorkplaceTypesResponse",
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
    # New Request Models (SimulationService)
    "ConfigureWorkplaceInGraphRequest",
    "RemoveWorkplaceFromGraphRequest",
    "SetWorkplaceAsStartNodeRequest",
    "SetWorkplaceAsEndNodeRequest",
    "UpdateProcessGraphRequest",
    "DistributeProductionPlanRequest",
    "GetProductionPlanDistributionRequest",
    "UpdateProductionAssignmentRequest",
    "UpdateWorkshopPlanRequest",
    "GetMetricsRequest",
    "GetProductionScheduleRequest",
    "UpdateProductionScheduleRequest",
    "GetWorkshopPlanRequest",
    "GetUnplannedRepairRequest",
    "GetWarehouseLoadChartRequest",
    "SetQualityInspectionRequest",
    "SetDeliveryScheduleRequest",
    "SetEquipmentMaintenanceIntervalRequest",
    "SetCertificationStatusRequest",
    "SetLeanImprovementStatusRequest",
    "SetSalesStrategyWithDetailsRequest",
    "GetRequiredMaterialsRequest",
    "GetAvailableImprovementsRequest",
    "GetDefectPoliciesRequest",
    "RunSimulationStepRequest",
    "GetSimulationHistoryRequest",
    "GetAllMetricsRequest",
    "ValidateConfigurationRequest",
    "GetReferenceDataRequest",
    "GetAvailableDefectPoliciesRequest",
    "GetAvailableImprovementsListRequest",
    "GetAvailableCertificationsRequest",
    "GetAvailableSalesStrategiesRequest",
    "GetMaterialTypesRequest",
    "GetEquipmentTypesRequest",
    "GetWorkplaceTypesRequest",
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
