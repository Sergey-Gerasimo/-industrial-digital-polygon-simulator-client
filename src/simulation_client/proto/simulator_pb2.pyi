from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DistributionStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DISTRIBUTION_STRATEGY_UNSPECIFIED: _ClassVar[DistributionStrategy]
    DISTRIBUTION_STRATEGY_BALANCED: _ClassVar[DistributionStrategy]
    DISTRIBUTION_STRATEGY_EFFICIENT: _ClassVar[DistributionStrategy]
    DISTRIBUTION_STRATEGY_CUSTOM: _ClassVar[DistributionStrategy]
    DISTRIBUTION_STRATEGY_PRIORITY_BASED: _ClassVar[DistributionStrategy]

class WarehouseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WAREHOUSE_TYPE_UNSPECIFIED: _ClassVar[WarehouseType]
    WAREHOUSE_TYPE_MATERIALS: _ClassVar[WarehouseType]
    WAREHOUSE_TYPE_PRODUCTS: _ClassVar[WarehouseType]
DISTRIBUTION_STRATEGY_UNSPECIFIED: DistributionStrategy
DISTRIBUTION_STRATEGY_BALANCED: DistributionStrategy
DISTRIBUTION_STRATEGY_EFFICIENT: DistributionStrategy
DISTRIBUTION_STRATEGY_CUSTOM: DistributionStrategy
DISTRIBUTION_STRATEGY_PRIORITY_BASED: DistributionStrategy
WAREHOUSE_TYPE_UNSPECIFIED: WarehouseType
WAREHOUSE_TYPE_MATERIALS: WarehouseType
WAREHOUSE_TYPE_PRODUCTS: WarehouseType

class Supplier(_message.Message):
    __slots__ = ("supplier_id", "name", "product_name", "material_type", "delivery_period", "special_delivery_period", "reliability", "product_quality", "cost", "special_delivery_cost")
    SUPPLIER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_DELIVERY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_QUALITY_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_DELIVERY_COST_FIELD_NUMBER: _ClassVar[int]
    supplier_id: str
    name: str
    product_name: str
    material_type: str
    delivery_period: int
    special_delivery_period: int
    reliability: float
    product_quality: float
    cost: int
    special_delivery_cost: int
    def __init__(self, supplier_id: _Optional[str] = ..., name: _Optional[str] = ..., product_name: _Optional[str] = ..., material_type: _Optional[str] = ..., delivery_period: _Optional[int] = ..., special_delivery_period: _Optional[int] = ..., reliability: _Optional[float] = ..., product_quality: _Optional[float] = ..., cost: _Optional[int] = ..., special_delivery_cost: _Optional[int] = ...) -> None: ...

class Warehouse(_message.Message):
    __slots__ = ("warehouse_id", "inventory_worker", "size", "loading", "materials")
    class MaterialsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    WAREHOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_WORKER_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    LOADING_FIELD_NUMBER: _ClassVar[int]
    MATERIALS_FIELD_NUMBER: _ClassVar[int]
    warehouse_id: str
    inventory_worker: Worker
    size: int
    loading: int
    materials: _containers.ScalarMap[str, int]
    def __init__(self, warehouse_id: _Optional[str] = ..., inventory_worker: _Optional[_Union[Worker, _Mapping]] = ..., size: _Optional[int] = ..., loading: _Optional[int] = ..., materials: _Optional[_Mapping[str, int]] = ...) -> None: ...

class Worker(_message.Message):
    __slots__ = ("worker_id", "name", "qualification", "specialty", "salary")
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    SPECIALTY_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    name: str
    qualification: int
    specialty: str
    salary: int
    def __init__(self, worker_id: _Optional[str] = ..., name: _Optional[str] = ..., qualification: _Optional[int] = ..., specialty: _Optional[str] = ..., salary: _Optional[int] = ...) -> None: ...

class Logist(_message.Message):
    __slots__ = ("worker_id", "name", "qualification", "specialty", "salary", "speed", "vehicle_type")
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    SPECIALTY_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    name: str
    qualification: int
    specialty: str
    salary: int
    speed: int
    vehicle_type: str
    def __init__(self, worker_id: _Optional[str] = ..., name: _Optional[str] = ..., qualification: _Optional[int] = ..., specialty: _Optional[str] = ..., salary: _Optional[int] = ..., speed: _Optional[int] = ..., vehicle_type: _Optional[str] = ...) -> None: ...

class Equipment(_message.Message):
    __slots__ = ("equipment_id", "name", "equipment_type", "reliability", "maintenance_period", "maintenance_cost", "cost", "repair_cost", "repair_time")
    EQUIPMENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_COST_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_COST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_TIME_FIELD_NUMBER: _ClassVar[int]
    equipment_id: str
    name: str
    equipment_type: str
    reliability: float
    maintenance_period: int
    maintenance_cost: int
    cost: int
    repair_cost: int
    repair_time: int
    def __init__(self, equipment_id: _Optional[str] = ..., name: _Optional[str] = ..., equipment_type: _Optional[str] = ..., reliability: _Optional[float] = ..., maintenance_period: _Optional[int] = ..., maintenance_cost: _Optional[int] = ..., cost: _Optional[int] = ..., repair_cost: _Optional[int] = ..., repair_time: _Optional[int] = ...) -> None: ...

class Workplace(_message.Message):
    __slots__ = ("workplace_id", "workplace_name", "required_speciality", "required_qualification", "required_equipment", "worker", "equipment", "required_stages", "is_start_node", "is_end_node", "next_workplace_ids")
    WORKPLACE_ID_FIELD_NUMBER: _ClassVar[int]
    WORKPLACE_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_SPECIALITY_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_EQUIPMENT_FIELD_NUMBER: _ClassVar[int]
    WORKER_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENT_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_STAGES_FIELD_NUMBER: _ClassVar[int]
    IS_START_NODE_FIELD_NUMBER: _ClassVar[int]
    IS_END_NODE_FIELD_NUMBER: _ClassVar[int]
    NEXT_WORKPLACE_IDS_FIELD_NUMBER: _ClassVar[int]
    workplace_id: str
    workplace_name: str
    required_speciality: str
    required_qualification: int
    required_equipment: str
    worker: Worker
    equipment: Equipment
    required_stages: _containers.RepeatedScalarFieldContainer[str]
    is_start_node: bool
    is_end_node: bool
    next_workplace_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, workplace_id: _Optional[str] = ..., workplace_name: _Optional[str] = ..., required_speciality: _Optional[str] = ..., required_qualification: _Optional[int] = ..., required_equipment: _Optional[str] = ..., worker: _Optional[_Union[Worker, _Mapping]] = ..., equipment: _Optional[_Union[Equipment, _Mapping]] = ..., required_stages: _Optional[_Iterable[str]] = ..., is_start_node: bool = ..., is_end_node: bool = ..., next_workplace_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class Route(_message.Message):
    __slots__ = ("length", "from_workplace", "to_workplace")
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    FROM_WORKPLACE_FIELD_NUMBER: _ClassVar[int]
    TO_WORKPLACE_FIELD_NUMBER: _ClassVar[int]
    length: int
    from_workplace: str
    to_workplace: str
    def __init__(self, length: _Optional[int] = ..., from_workplace: _Optional[str] = ..., to_workplace: _Optional[str] = ...) -> None: ...

class ProcessGraph(_message.Message):
    __slots__ = ("process_graph_id", "workplaces", "routes")
    PROCESS_GRAPH_ID_FIELD_NUMBER: _ClassVar[int]
    WORKPLACES_FIELD_NUMBER: _ClassVar[int]
    ROUTES_FIELD_NUMBER: _ClassVar[int]
    process_graph_id: str
    workplaces: _containers.RepeatedCompositeFieldContainer[Workplace]
    routes: _containers.RepeatedCompositeFieldContainer[Route]
    def __init__(self, process_graph_id: _Optional[str] = ..., workplaces: _Optional[_Iterable[_Union[Workplace, _Mapping]]] = ..., routes: _Optional[_Iterable[_Union[Route, _Mapping]]] = ...) -> None: ...

class Consumer(_message.Message):
    __slots__ = ("consumer_id", "name", "type")
    CONSUMER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    consumer_id: str
    name: str
    type: str
    def __init__(self, consumer_id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class Tender(_message.Message):
    __slots__ = ("tender_id", "consumer", "cost", "quantity_of_products", "penalty_per_day", "warranty_years", "payment_form")
    TENDER_ID_FIELD_NUMBER: _ClassVar[int]
    CONSUMER_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_OF_PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    PENALTY_PER_DAY_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_YEARS_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_FORM_FIELD_NUMBER: _ClassVar[int]
    tender_id: str
    consumer: Consumer
    cost: int
    quantity_of_products: int
    penalty_per_day: int
    warranty_years: int
    payment_form: str
    def __init__(self, tender_id: _Optional[str] = ..., consumer: _Optional[_Union[Consumer, _Mapping]] = ..., cost: _Optional[int] = ..., quantity_of_products: _Optional[int] = ..., penalty_per_day: _Optional[int] = ..., warranty_years: _Optional[int] = ..., payment_form: _Optional[str] = ...) -> None: ...

class SimulationParameters(_message.Message):
    __slots__ = ("logist", "suppliers", "backup_suppliers", "materials_warehouse", "product_warehouse", "processes", "tenders", "dealing_with_defects", "production_improvements", "sales_strategy", "production_schedule", "certifications", "lean_improvements", "distribution_strategy", "step", "capital")
    LOGIST_FIELD_NUMBER: _ClassVar[int]
    SUPPLIERS_FIELD_NUMBER: _ClassVar[int]
    BACKUP_SUPPLIERS_FIELD_NUMBER: _ClassVar[int]
    MATERIALS_WAREHOUSE_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_WAREHOUSE_FIELD_NUMBER: _ClassVar[int]
    PROCESSES_FIELD_NUMBER: _ClassVar[int]
    TENDERS_FIELD_NUMBER: _ClassVar[int]
    DEALING_WITH_DEFECTS_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_IMPROVEMENTS_FIELD_NUMBER: _ClassVar[int]
    SALES_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    CERTIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    LEAN_IMPROVEMENTS_FIELD_NUMBER: _ClassVar[int]
    DISTRIBUTION_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    CAPITAL_FIELD_NUMBER: _ClassVar[int]
    logist: Logist
    suppliers: _containers.RepeatedCompositeFieldContainer[Supplier]
    backup_suppliers: _containers.RepeatedCompositeFieldContainer[Supplier]
    materials_warehouse: Warehouse
    product_warehouse: Warehouse
    processes: ProcessGraph
    tenders: _containers.RepeatedCompositeFieldContainer[Tender]
    dealing_with_defects: str
    production_improvements: _containers.RepeatedCompositeFieldContainer[LeanImprovement]
    sales_strategy: str
    production_schedule: ProductionSchedule
    certifications: _containers.RepeatedCompositeFieldContainer[Certification]
    lean_improvements: _containers.RepeatedCompositeFieldContainer[LeanImprovement]
    distribution_strategy: DistributionStrategy
    step: int
    capital: int
    def __init__(self, logist: _Optional[_Union[Logist, _Mapping]] = ..., suppliers: _Optional[_Iterable[_Union[Supplier, _Mapping]]] = ..., backup_suppliers: _Optional[_Iterable[_Union[Supplier, _Mapping]]] = ..., materials_warehouse: _Optional[_Union[Warehouse, _Mapping]] = ..., product_warehouse: _Optional[_Union[Warehouse, _Mapping]] = ..., processes: _Optional[_Union[ProcessGraph, _Mapping]] = ..., tenders: _Optional[_Iterable[_Union[Tender, _Mapping]]] = ..., dealing_with_defects: _Optional[str] = ..., production_improvements: _Optional[_Iterable[_Union[LeanImprovement, _Mapping]]] = ..., sales_strategy: _Optional[str] = ..., production_schedule: _Optional[_Union[ProductionSchedule, _Mapping]] = ..., certifications: _Optional[_Iterable[_Union[Certification, _Mapping]]] = ..., lean_improvements: _Optional[_Iterable[_Union[LeanImprovement, _Mapping]]] = ..., distribution_strategy: _Optional[_Union[DistributionStrategy, str]] = ..., step: _Optional[int] = ..., capital: _Optional[int] = ...) -> None: ...

class SimulationResults(_message.Message):
    __slots__ = ("profit", "cost", "profitability", "factory_metrics", "production_metrics", "quality_metrics", "engineering_metrics", "commercial_metrics", "procurement_metrics", "step")
    PROFIT_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    PROFITABILITY_FIELD_NUMBER: _ClassVar[int]
    FACTORY_METRICS_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_METRICS_FIELD_NUMBER: _ClassVar[int]
    QUALITY_METRICS_FIELD_NUMBER: _ClassVar[int]
    ENGINEERING_METRICS_FIELD_NUMBER: _ClassVar[int]
    COMMERCIAL_METRICS_FIELD_NUMBER: _ClassVar[int]
    PROCUREMENT_METRICS_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    profit: int
    cost: int
    profitability: float
    factory_metrics: FactoryMetrics
    production_metrics: ProductionMetrics
    quality_metrics: QualityMetrics
    engineering_metrics: EngineeringMetrics
    commercial_metrics: CommercialMetrics
    procurement_metrics: ProcurementMetrics
    step: int
    def __init__(self, profit: _Optional[int] = ..., cost: _Optional[int] = ..., profitability: _Optional[float] = ..., factory_metrics: _Optional[_Union[FactoryMetrics, _Mapping]] = ..., production_metrics: _Optional[_Union[ProductionMetrics, _Mapping]] = ..., quality_metrics: _Optional[_Union[QualityMetrics, _Mapping]] = ..., engineering_metrics: _Optional[_Union[EngineeringMetrics, _Mapping]] = ..., commercial_metrics: _Optional[_Union[CommercialMetrics, _Mapping]] = ..., procurement_metrics: _Optional[_Union[ProcurementMetrics, _Mapping]] = ..., step: _Optional[int] = ...) -> None: ...

class Simulation(_message.Message):
    __slots__ = ("capital", "simulation_id", "parameters", "results", "room_id", "is_completed")
    CAPITAL_FIELD_NUMBER: _ClassVar[int]
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    IS_COMPLETED_FIELD_NUMBER: _ClassVar[int]
    capital: int
    simulation_id: str
    parameters: _containers.RepeatedCompositeFieldContainer[SimulationParameters]
    results: _containers.RepeatedCompositeFieldContainer[SimulationResults]
    room_id: str
    is_completed: bool
    def __init__(self, capital: _Optional[int] = ..., simulation_id: _Optional[str] = ..., parameters: _Optional[_Iterable[_Union[SimulationParameters, _Mapping]]] = ..., results: _Optional[_Iterable[_Union[SimulationResults, _Mapping]]] = ..., room_id: _Optional[str] = ..., is_completed: bool = ...) -> None: ...

class FactoryMetrics(_message.Message):
    __slots__ = ("profitability", "on_time_delivery_rate", "oee", "warehouse_metrics", "total_procurement_cost", "defect_rate")
    class WarehouseMetricsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: WarehouseMetrics
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[WarehouseMetrics, _Mapping]] = ...) -> None: ...
    PROFITABILITY_FIELD_NUMBER: _ClassVar[int]
    ON_TIME_DELIVERY_RATE_FIELD_NUMBER: _ClassVar[int]
    OEE_FIELD_NUMBER: _ClassVar[int]
    WAREHOUSE_METRICS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PROCUREMENT_COST_FIELD_NUMBER: _ClassVar[int]
    DEFECT_RATE_FIELD_NUMBER: _ClassVar[int]
    profitability: float
    on_time_delivery_rate: float
    oee: float
    warehouse_metrics: _containers.MessageMap[str, WarehouseMetrics]
    total_procurement_cost: int
    defect_rate: float
    def __init__(self, profitability: _Optional[float] = ..., on_time_delivery_rate: _Optional[float] = ..., oee: _Optional[float] = ..., warehouse_metrics: _Optional[_Mapping[str, WarehouseMetrics]] = ..., total_procurement_cost: _Optional[int] = ..., defect_rate: _Optional[float] = ...) -> None: ...

class WarehouseMetrics(_message.Message):
    __slots__ = ("fill_level", "current_load", "max_capacity", "material_levels", "load_over_time", "max_capacity_over_time")
    class MaterialLevelsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    FILL_LEVEL_FIELD_NUMBER: _ClassVar[int]
    CURRENT_LOAD_FIELD_NUMBER: _ClassVar[int]
    MAX_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_LEVELS_FIELD_NUMBER: _ClassVar[int]
    LOAD_OVER_TIME_FIELD_NUMBER: _ClassVar[int]
    MAX_CAPACITY_OVER_TIME_FIELD_NUMBER: _ClassVar[int]
    fill_level: float
    current_load: int
    max_capacity: int
    material_levels: _containers.ScalarMap[str, int]
    load_over_time: _containers.RepeatedScalarFieldContainer[int]
    max_capacity_over_time: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, fill_level: _Optional[float] = ..., current_load: _Optional[int] = ..., max_capacity: _Optional[int] = ..., material_levels: _Optional[_Mapping[str, int]] = ..., load_over_time: _Optional[_Iterable[int]] = ..., max_capacity_over_time: _Optional[_Iterable[int]] = ...) -> None: ...

class ProductionMetrics(_message.Message):
    __slots__ = ("monthly_productivity", "average_equipment_utilization", "wip_count", "finished_goods_count", "material_reserves")
    class MonthlyProductivity(_message.Message):
        __slots__ = ("month", "units_produced")
        MONTH_FIELD_NUMBER: _ClassVar[int]
        UNITS_PRODUCED_FIELD_NUMBER: _ClassVar[int]
        month: str
        units_produced: int
        def __init__(self, month: _Optional[str] = ..., units_produced: _Optional[int] = ...) -> None: ...
    class MaterialReservesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    MONTHLY_PRODUCTIVITY_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_EQUIPMENT_UTILIZATION_FIELD_NUMBER: _ClassVar[int]
    WIP_COUNT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_GOODS_COUNT_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_RESERVES_FIELD_NUMBER: _ClassVar[int]
    monthly_productivity: _containers.RepeatedCompositeFieldContainer[ProductionMetrics.MonthlyProductivity]
    average_equipment_utilization: float
    wip_count: int
    finished_goods_count: int
    material_reserves: _containers.ScalarMap[str, int]
    def __init__(self, monthly_productivity: _Optional[_Iterable[_Union[ProductionMetrics.MonthlyProductivity, _Mapping]]] = ..., average_equipment_utilization: _Optional[float] = ..., wip_count: _Optional[int] = ..., finished_goods_count: _Optional[int] = ..., material_reserves: _Optional[_Mapping[str, int]] = ...) -> None: ...

class QualityMetrics(_message.Message):
    __slots__ = ("defect_percentage", "good_output_percentage", "defect_causes", "average_material_quality", "average_supplier_failure_probability", "procurement_volume")
    class DefectCause(_message.Message):
        __slots__ = ("cause", "count", "percentage")
        CAUSE_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
        cause: str
        count: int
        percentage: float
        def __init__(self, cause: _Optional[str] = ..., count: _Optional[int] = ..., percentage: _Optional[float] = ...) -> None: ...
    DEFECT_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    GOOD_OUTPUT_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    DEFECT_CAUSES_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_MATERIAL_QUALITY_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_SUPPLIER_FAILURE_PROBABILITY_FIELD_NUMBER: _ClassVar[int]
    PROCUREMENT_VOLUME_FIELD_NUMBER: _ClassVar[int]
    defect_percentage: float
    good_output_percentage: float
    defect_causes: _containers.RepeatedCompositeFieldContainer[QualityMetrics.DefectCause]
    average_material_quality: float
    average_supplier_failure_probability: float
    procurement_volume: int
    def __init__(self, defect_percentage: _Optional[float] = ..., good_output_percentage: _Optional[float] = ..., defect_causes: _Optional[_Iterable[_Union[QualityMetrics.DefectCause, _Mapping]]] = ..., average_material_quality: _Optional[float] = ..., average_supplier_failure_probability: _Optional[float] = ..., procurement_volume: _Optional[int] = ...) -> None: ...

class EngineeringMetrics(_message.Message):
    __slots__ = ("operation_timings", "downtime_records", "defect_analysis")
    class OperationTiming(_message.Message):
        __slots__ = ("operation_name", "cycle_time", "takt_time", "timing_cost")
        OPERATION_NAME_FIELD_NUMBER: _ClassVar[int]
        CYCLE_TIME_FIELD_NUMBER: _ClassVar[int]
        TAKT_TIME_FIELD_NUMBER: _ClassVar[int]
        TIMING_COST_FIELD_NUMBER: _ClassVar[int]
        operation_name: str
        cycle_time: int
        takt_time: int
        timing_cost: int
        def __init__(self, operation_name: _Optional[str] = ..., cycle_time: _Optional[int] = ..., takt_time: _Optional[int] = ..., timing_cost: _Optional[int] = ...) -> None: ...
    class DowntimeRecord(_message.Message):
        __slots__ = ("cause", "total_minutes", "average_per_shift")
        CAUSE_FIELD_NUMBER: _ClassVar[int]
        TOTAL_MINUTES_FIELD_NUMBER: _ClassVar[int]
        AVERAGE_PER_SHIFT_FIELD_NUMBER: _ClassVar[int]
        cause: str
        total_minutes: int
        average_per_shift: float
        def __init__(self, cause: _Optional[str] = ..., total_minutes: _Optional[int] = ..., average_per_shift: _Optional[float] = ...) -> None: ...
    class DefectAnalysis(_message.Message):
        __slots__ = ("defect_type", "count", "percentage", "cumulative_percentage")
        DEFECT_TYPE_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
        CUMULATIVE_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
        defect_type: str
        count: int
        percentage: float
        cumulative_percentage: float
        def __init__(self, defect_type: _Optional[str] = ..., count: _Optional[int] = ..., percentage: _Optional[float] = ..., cumulative_percentage: _Optional[float] = ...) -> None: ...
    OPERATION_TIMINGS_FIELD_NUMBER: _ClassVar[int]
    DOWNTIME_RECORDS_FIELD_NUMBER: _ClassVar[int]
    DEFECT_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    operation_timings: _containers.RepeatedCompositeFieldContainer[EngineeringMetrics.OperationTiming]
    downtime_records: _containers.RepeatedCompositeFieldContainer[EngineeringMetrics.DowntimeRecord]
    defect_analysis: _containers.RepeatedCompositeFieldContainer[EngineeringMetrics.DefectAnalysis]
    def __init__(self, operation_timings: _Optional[_Iterable[_Union[EngineeringMetrics.OperationTiming, _Mapping]]] = ..., downtime_records: _Optional[_Iterable[_Union[EngineeringMetrics.DowntimeRecord, _Mapping]]] = ..., defect_analysis: _Optional[_Iterable[_Union[EngineeringMetrics.DefectAnalysis, _Mapping]]] = ...) -> None: ...

class CommercialMetrics(_message.Message):
    __slots__ = ("yearly_revenues", "tender_revenue_plan", "total_payments", "total_receipts", "sales_forecast", "strategy_costs", "tender_graph", "project_profitabilities", "on_time_completed_orders")
    class YearlyRevenue(_message.Message):
        __slots__ = ("year", "revenue")
        YEAR_FIELD_NUMBER: _ClassVar[int]
        REVENUE_FIELD_NUMBER: _ClassVar[int]
        year: int
        revenue: int
        def __init__(self, year: _Optional[int] = ..., revenue: _Optional[int] = ...) -> None: ...
    class SalesForecastEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: float
        def __init__(self, key: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...
    class StrategyCostsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    class TenderGraphPoint(_message.Message):
        __slots__ = ("strategy", "unit_size", "is_mastered")
        STRATEGY_FIELD_NUMBER: _ClassVar[int]
        UNIT_SIZE_FIELD_NUMBER: _ClassVar[int]
        IS_MASTERED_FIELD_NUMBER: _ClassVar[int]
        strategy: str
        unit_size: str
        is_mastered: bool
        def __init__(self, strategy: _Optional[str] = ..., unit_size: _Optional[str] = ..., is_mastered: bool = ...) -> None: ...
    class ProjectProfitability(_message.Message):
        __slots__ = ("project_name", "profitability")
        PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
        PROFITABILITY_FIELD_NUMBER: _ClassVar[int]
        project_name: str
        profitability: float
        def __init__(self, project_name: _Optional[str] = ..., profitability: _Optional[float] = ...) -> None: ...
    YEARLY_REVENUES_FIELD_NUMBER: _ClassVar[int]
    TENDER_REVENUE_PLAN_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PAYMENTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_RECEIPTS_FIELD_NUMBER: _ClassVar[int]
    SALES_FORECAST_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_COSTS_FIELD_NUMBER: _ClassVar[int]
    TENDER_GRAPH_FIELD_NUMBER: _ClassVar[int]
    PROJECT_PROFITABILITIES_FIELD_NUMBER: _ClassVar[int]
    ON_TIME_COMPLETED_ORDERS_FIELD_NUMBER: _ClassVar[int]
    yearly_revenues: _containers.RepeatedCompositeFieldContainer[CommercialMetrics.YearlyRevenue]
    tender_revenue_plan: int
    total_payments: int
    total_receipts: int
    sales_forecast: _containers.ScalarMap[str, float]
    strategy_costs: _containers.ScalarMap[str, int]
    tender_graph: _containers.RepeatedCompositeFieldContainer[CommercialMetrics.TenderGraphPoint]
    project_profitabilities: _containers.RepeatedCompositeFieldContainer[CommercialMetrics.ProjectProfitability]
    on_time_completed_orders: int
    def __init__(self, yearly_revenues: _Optional[_Iterable[_Union[CommercialMetrics.YearlyRevenue, _Mapping]]] = ..., tender_revenue_plan: _Optional[int] = ..., total_payments: _Optional[int] = ..., total_receipts: _Optional[int] = ..., sales_forecast: _Optional[_Mapping[str, float]] = ..., strategy_costs: _Optional[_Mapping[str, int]] = ..., tender_graph: _Optional[_Iterable[_Union[CommercialMetrics.TenderGraphPoint, _Mapping]]] = ..., project_profitabilities: _Optional[_Iterable[_Union[CommercialMetrics.ProjectProfitability, _Mapping]]] = ..., on_time_completed_orders: _Optional[int] = ...) -> None: ...

class ProcurementMetrics(_message.Message):
    __slots__ = ("supplier_performances", "total_procurement_value")
    class SupplierPerformance(_message.Message):
        __slots__ = ("supplier_id", "delivered_quantity", "projected_defect_rate", "planned_reliability", "actual_reliability", "planned_cost", "actual_cost", "actual_defect_count")
        SUPPLIER_ID_FIELD_NUMBER: _ClassVar[int]
        DELIVERED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
        PROJECTED_DEFECT_RATE_FIELD_NUMBER: _ClassVar[int]
        PLANNED_RELIABILITY_FIELD_NUMBER: _ClassVar[int]
        ACTUAL_RELIABILITY_FIELD_NUMBER: _ClassVar[int]
        PLANNED_COST_FIELD_NUMBER: _ClassVar[int]
        ACTUAL_COST_FIELD_NUMBER: _ClassVar[int]
        ACTUAL_DEFECT_COUNT_FIELD_NUMBER: _ClassVar[int]
        supplier_id: str
        delivered_quantity: int
        projected_defect_rate: float
        planned_reliability: float
        actual_reliability: float
        planned_cost: int
        actual_cost: int
        actual_defect_count: int
        def __init__(self, supplier_id: _Optional[str] = ..., delivered_quantity: _Optional[int] = ..., projected_defect_rate: _Optional[float] = ..., planned_reliability: _Optional[float] = ..., actual_reliability: _Optional[float] = ..., planned_cost: _Optional[int] = ..., actual_cost: _Optional[int] = ..., actual_defect_count: _Optional[int] = ...) -> None: ...
    SUPPLIER_PERFORMANCES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PROCUREMENT_VALUE_FIELD_NUMBER: _ClassVar[int]
    supplier_performances: _containers.RepeatedCompositeFieldContainer[ProcurementMetrics.SupplierPerformance]
    total_procurement_value: int
    def __init__(self, supplier_performances: _Optional[_Iterable[_Union[ProcurementMetrics.SupplierPerformance, _Mapping]]] = ..., total_procurement_value: _Optional[int] = ...) -> None: ...

class ProductionPlanRow(_message.Message):
    __slots__ = ("tender_id", "product_name", "priority", "plan_date", "dse", "short_set", "dse_name", "planned_quantity", "actual_quantity", "remaining_to_produce", "provision_status", "note", "planned_completion_date", "cost_breakdown", "order_number")
    TENDER_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    PLAN_DATE_FIELD_NUMBER: _ClassVar[int]
    DSE_FIELD_NUMBER: _ClassVar[int]
    SHORT_SET_FIELD_NUMBER: _ClassVar[int]
    DSE_NAME_FIELD_NUMBER: _ClassVar[int]
    PLANNED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    ACTUAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    REMAINING_TO_PRODUCE_FIELD_NUMBER: _ClassVar[int]
    PROVISION_STATUS_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    PLANNED_COMPLETION_DATE_FIELD_NUMBER: _ClassVar[int]
    COST_BREAKDOWN_FIELD_NUMBER: _ClassVar[int]
    ORDER_NUMBER_FIELD_NUMBER: _ClassVar[int]
    tender_id: str
    product_name: str
    priority: int
    plan_date: str
    dse: str
    short_set: str
    dse_name: str
    planned_quantity: int
    actual_quantity: int
    remaining_to_produce: int
    provision_status: str
    note: str
    planned_completion_date: str
    cost_breakdown: str
    order_number: str
    def __init__(self, tender_id: _Optional[str] = ..., product_name: _Optional[str] = ..., priority: _Optional[int] = ..., plan_date: _Optional[str] = ..., dse: _Optional[str] = ..., short_set: _Optional[str] = ..., dse_name: _Optional[str] = ..., planned_quantity: _Optional[int] = ..., actual_quantity: _Optional[int] = ..., remaining_to_produce: _Optional[int] = ..., provision_status: _Optional[str] = ..., note: _Optional[str] = ..., planned_completion_date: _Optional[str] = ..., cost_breakdown: _Optional[str] = ..., order_number: _Optional[str] = ...) -> None: ...

class ProductionSchedule(_message.Message):
    __slots__ = ("rows",)
    ROWS_FIELD_NUMBER: _ClassVar[int]
    rows: _containers.RepeatedCompositeFieldContainer[ProductionPlanRow]
    def __init__(self, rows: _Optional[_Iterable[_Union[ProductionPlanRow, _Mapping]]] = ...) -> None: ...

class UnplannedRepair(_message.Message):
    __slots__ = ("repairs", "total_repair_cost")
    class RepairRecord(_message.Message):
        __slots__ = ("month", "repair_cost", "equipment_id", "reason")
        MONTH_FIELD_NUMBER: _ClassVar[int]
        REPAIR_COST_FIELD_NUMBER: _ClassVar[int]
        EQUIPMENT_ID_FIELD_NUMBER: _ClassVar[int]
        REASON_FIELD_NUMBER: _ClassVar[int]
        month: str
        repair_cost: int
        equipment_id: str
        reason: str
        def __init__(self, month: _Optional[str] = ..., repair_cost: _Optional[int] = ..., equipment_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...
    REPAIRS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_REPAIR_COST_FIELD_NUMBER: _ClassVar[int]
    repairs: _containers.RepeatedCompositeFieldContainer[UnplannedRepair.RepairRecord]
    total_repair_cost: int
    def __init__(self, repairs: _Optional[_Iterable[_Union[UnplannedRepair.RepairRecord, _Mapping]]] = ..., total_repair_cost: _Optional[int] = ...) -> None: ...

class RequiredMaterial(_message.Message):
    __slots__ = ("material_id", "name", "has_contracted_supplier", "required_quantity", "current_stock")
    MATERIAL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HAS_CONTRACTED_SUPPLIER_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CURRENT_STOCK_FIELD_NUMBER: _ClassVar[int]
    material_id: str
    name: str
    has_contracted_supplier: bool
    required_quantity: int
    current_stock: int
    def __init__(self, material_id: _Optional[str] = ..., name: _Optional[str] = ..., has_contracted_supplier: bool = ..., required_quantity: _Optional[int] = ..., current_stock: _Optional[int] = ...) -> None: ...

class Certification(_message.Message):
    __slots__ = ("certificate_type", "is_obtained", "implementation_cost", "implementation_time_days")
    CERTIFICATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_OBTAINED_FIELD_NUMBER: _ClassVar[int]
    IMPLEMENTATION_COST_FIELD_NUMBER: _ClassVar[int]
    IMPLEMENTATION_TIME_DAYS_FIELD_NUMBER: _ClassVar[int]
    certificate_type: str
    is_obtained: bool
    implementation_cost: int
    implementation_time_days: int
    def __init__(self, certificate_type: _Optional[str] = ..., is_obtained: bool = ..., implementation_cost: _Optional[int] = ..., implementation_time_days: _Optional[int] = ...) -> None: ...

class LeanImprovement(_message.Message):
    __slots__ = ("improvement_id", "name", "is_implemented", "implementation_cost", "efficiency_gain")
    IMPROVEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_IMPLEMENTED_FIELD_NUMBER: _ClassVar[int]
    IMPLEMENTATION_COST_FIELD_NUMBER: _ClassVar[int]
    EFFICIENCY_GAIN_FIELD_NUMBER: _ClassVar[int]
    improvement_id: str
    name: str
    is_implemented: bool
    implementation_cost: int
    efficiency_gain: float
    def __init__(self, improvement_id: _Optional[str] = ..., name: _Optional[str] = ..., is_implemented: bool = ..., implementation_cost: _Optional[int] = ..., efficiency_gain: _Optional[float] = ...) -> None: ...

class WarehouseLoadChart(_message.Message):
    __slots__ = ("data_points", "warehouse_id")
    class LoadPoint(_message.Message):
        __slots__ = ("timestamp", "load", "max_capacity")
        TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
        LOAD_FIELD_NUMBER: _ClassVar[int]
        MAX_CAPACITY_FIELD_NUMBER: _ClassVar[int]
        timestamp: str
        load: int
        max_capacity: int
        def __init__(self, timestamp: _Optional[str] = ..., load: _Optional[int] = ..., max_capacity: _Optional[int] = ...) -> None: ...
    DATA_POINTS_FIELD_NUMBER: _ClassVar[int]
    WAREHOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    data_points: _containers.RepeatedCompositeFieldContainer[WarehouseLoadChart.LoadPoint]
    warehouse_id: str
    def __init__(self, data_points: _Optional[_Iterable[_Union[WarehouseLoadChart.LoadPoint, _Mapping]]] = ..., warehouse_id: _Optional[str] = ...) -> None: ...

class OperationTimingChart(_message.Message):
    __slots__ = ("timing_data", "chart_type")
    class TimingData(_message.Message):
        __slots__ = ("process_name", "cycle_time", "takt_time", "timing_cost")
        PROCESS_NAME_FIELD_NUMBER: _ClassVar[int]
        CYCLE_TIME_FIELD_NUMBER: _ClassVar[int]
        TAKT_TIME_FIELD_NUMBER: _ClassVar[int]
        TIMING_COST_FIELD_NUMBER: _ClassVar[int]
        process_name: str
        cycle_time: int
        takt_time: int
        timing_cost: int
        def __init__(self, process_name: _Optional[str] = ..., cycle_time: _Optional[int] = ..., takt_time: _Optional[int] = ..., timing_cost: _Optional[int] = ...) -> None: ...
    TIMING_DATA_FIELD_NUMBER: _ClassVar[int]
    CHART_TYPE_FIELD_NUMBER: _ClassVar[int]
    timing_data: _containers.RepeatedCompositeFieldContainer[OperationTimingChart.TimingData]
    chart_type: str
    def __init__(self, timing_data: _Optional[_Iterable[_Union[OperationTimingChart.TimingData, _Mapping]]] = ..., chart_type: _Optional[str] = ...) -> None: ...

class DowntimeChart(_message.Message):
    __slots__ = ("downtime_data", "chart_type")
    class DowntimeData(_message.Message):
        __slots__ = ("process_name", "cause", "downtime_minutes")
        PROCESS_NAME_FIELD_NUMBER: _ClassVar[int]
        CAUSE_FIELD_NUMBER: _ClassVar[int]
        DOWNTIME_MINUTES_FIELD_NUMBER: _ClassVar[int]
        process_name: str
        cause: str
        downtime_minutes: int
        def __init__(self, process_name: _Optional[str] = ..., cause: _Optional[str] = ..., downtime_minutes: _Optional[int] = ...) -> None: ...
    DOWNTIME_DATA_FIELD_NUMBER: _ClassVar[int]
    CHART_TYPE_FIELD_NUMBER: _ClassVar[int]
    downtime_data: _containers.RepeatedCompositeFieldContainer[DowntimeChart.DowntimeData]
    chart_type: str
    def __init__(self, downtime_data: _Optional[_Iterable[_Union[DowntimeChart.DowntimeData, _Mapping]]] = ..., chart_type: _Optional[str] = ...) -> None: ...

class ModelMasteryChart(_message.Message):
    __slots__ = ("model_points",)
    class ModelPoint(_message.Message):
        __slots__ = ("strategy", "unit_size", "is_mastered", "model_name")
        STRATEGY_FIELD_NUMBER: _ClassVar[int]
        UNIT_SIZE_FIELD_NUMBER: _ClassVar[int]
        IS_MASTERED_FIELD_NUMBER: _ClassVar[int]
        MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
        strategy: str
        unit_size: str
        is_mastered: bool
        model_name: str
        def __init__(self, strategy: _Optional[str] = ..., unit_size: _Optional[str] = ..., is_mastered: bool = ..., model_name: _Optional[str] = ...) -> None: ...
    MODEL_POINTS_FIELD_NUMBER: _ClassVar[int]
    model_points: _containers.RepeatedCompositeFieldContainer[ModelMasteryChart.ModelPoint]
    def __init__(self, model_points: _Optional[_Iterable[_Union[ModelMasteryChart.ModelPoint, _Mapping]]] = ...) -> None: ...

class ProjectProfitabilityChart(_message.Message):
    __slots__ = ("projects", "chart_type")
    class ProjectData(_message.Message):
        __slots__ = ("project_name", "profitability")
        PROJECT_NAME_FIELD_NUMBER: _ClassVar[int]
        PROFITABILITY_FIELD_NUMBER: _ClassVar[int]
        project_name: str
        profitability: float
        def __init__(self, project_name: _Optional[str] = ..., profitability: _Optional[float] = ...) -> None: ...
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    CHART_TYPE_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[ProjectProfitabilityChart.ProjectData]
    chart_type: str
    def __init__(self, projects: _Optional[_Iterable[_Union[ProjectProfitabilityChart.ProjectData, _Mapping]]] = ..., chart_type: _Optional[str] = ...) -> None: ...

class GetAvailableDefectPoliciesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DefectPoliciesListResponse(_message.Message):
    __slots__ = ("policies", "timestamp")
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    policies: _containers.RepeatedScalarFieldContainer[str]
    timestamp: str
    def __init__(self, policies: _Optional[_Iterable[str]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetAvailableImprovementsListRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ImprovementsListResponse(_message.Message):
    __slots__ = ("improvements", "timestamp")
    IMPROVEMENTS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    improvements: _containers.RepeatedScalarFieldContainer[str]
    timestamp: str
    def __init__(self, improvements: _Optional[_Iterable[str]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetAvailableCertificationsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CertificationsListResponse(_message.Message):
    __slots__ = ("certifications", "timestamp")
    CERTIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    certifications: _containers.RepeatedScalarFieldContainer[str]
    timestamp: str
    def __init__(self, certifications: _Optional[_Iterable[str]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetAvailableSalesStrategiesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SalesStrategiesListResponse(_message.Message):
    __slots__ = ("strategies", "timestamp")
    STRATEGIES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    strategies: _containers.RepeatedScalarFieldContainer[str]
    timestamp: str
    def __init__(self, strategies: _Optional[_Iterable[str]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetMaterialTypesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MaterialTypesResponse(_message.Message):
    __slots__ = ("material_types", "timestamp")
    MATERIAL_TYPES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    material_types: _containers.RepeatedScalarFieldContainer[str]
    timestamp: str
    def __init__(self, material_types: _Optional[_Iterable[str]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetEquipmentTypesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EquipmentTypesResponse(_message.Message):
    __slots__ = ("equipment_types", "timestamp")
    EQUIPMENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    equipment_types: _containers.RepeatedScalarFieldContainer[str]
    timestamp: str
    def __init__(self, equipment_types: _Optional[_Iterable[str]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetWorkplaceTypesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WorkplaceTypesResponse(_message.Message):
    __slots__ = ("workplace_types", "timestamp")
    WORKPLACE_TYPES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    workplace_types: _containers.RepeatedScalarFieldContainer[str]
    timestamp: str
    def __init__(self, workplace_types: _Optional[_Iterable[str]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetAvailableDealingWithDefectsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAvailableLeanImprovementsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateLeanImprovementRequest(_message.Message):
    __slots__ = ("name", "is_implemented", "implementation_cost", "efficiency_gain")
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_IMPLEMENTED_FIELD_NUMBER: _ClassVar[int]
    IMPLEMENTATION_COST_FIELD_NUMBER: _ClassVar[int]
    EFFICIENCY_GAIN_FIELD_NUMBER: _ClassVar[int]
    name: str
    is_implemented: bool
    implementation_cost: int
    efficiency_gain: float
    def __init__(self, name: _Optional[str] = ..., is_implemented: bool = ..., implementation_cost: _Optional[int] = ..., efficiency_gain: _Optional[float] = ...) -> None: ...

class UpdateLeanImprovementRequest(_message.Message):
    __slots__ = ("improvement_id", "name", "is_implemented", "implementation_cost", "efficiency_gain")
    IMPROVEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_IMPLEMENTED_FIELD_NUMBER: _ClassVar[int]
    IMPLEMENTATION_COST_FIELD_NUMBER: _ClassVar[int]
    EFFICIENCY_GAIN_FIELD_NUMBER: _ClassVar[int]
    improvement_id: str
    name: str
    is_implemented: bool
    implementation_cost: int
    efficiency_gain: float
    def __init__(self, improvement_id: _Optional[str] = ..., name: _Optional[str] = ..., is_implemented: bool = ..., implementation_cost: _Optional[int] = ..., efficiency_gain: _Optional[float] = ...) -> None: ...

class DeleteLeanImprovementRequest(_message.Message):
    __slots__ = ("improvement_id",)
    IMPROVEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    improvement_id: str
    def __init__(self, improvement_id: _Optional[str] = ...) -> None: ...

class GetAllLeanImprovementsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllLeanImprovementsResponse(_message.Message):
    __slots__ = ("improvements", "total_count")
    IMPROVEMENTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    improvements: _containers.RepeatedCompositeFieldContainer[LeanImprovement]
    total_count: int
    def __init__(self, improvements: _Optional[_Iterable[_Union[LeanImprovement, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetAvailableLeanImprovementsResponse(_message.Message):
    __slots__ = ("improvements", "timestamp")
    IMPROVEMENTS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    improvements: _containers.RepeatedCompositeFieldContainer[LeanImprovement]
    timestamp: str
    def __init__(self, improvements: _Optional[_Iterable[_Union[LeanImprovement, _Mapping]]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class UpdateProcessGraphRequest(_message.Message):
    __slots__ = ("simulation_id", "process_graph")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    PROCESS_GRAPH_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    process_graph: ProcessGraph
    def __init__(self, simulation_id: _Optional[str] = ..., process_graph: _Optional[_Union[ProcessGraph, _Mapping]] = ...) -> None: ...

class SetProductionPlanRowRequest(_message.Message):
    __slots__ = ("simulation_id", "row")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    ROW_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    row: ProductionPlanRow
    def __init__(self, simulation_id: _Optional[str] = ..., row: _Optional[_Union[ProductionPlanRow, _Mapping]] = ...) -> None: ...

class SimulationResponse(_message.Message):
    __slots__ = ("simulations", "timestamp")
    SIMULATIONS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    simulations: Simulation
    timestamp: str
    def __init__(self, simulations: _Optional[_Union[Simulation, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetSimulationRequest(_message.Message):
    __slots__ = ("simulation_id",)
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    def __init__(self, simulation_id: _Optional[str] = ...) -> None: ...

class SetLogistRequest(_message.Message):
    __slots__ = ("simulation_id", "worker_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    worker_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., worker_id: _Optional[str] = ...) -> None: ...

class AddSupplierRequest(_message.Message):
    __slots__ = ("simulation_id", "supplier_id", "is_backup")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPPLIER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_BACKUP_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    supplier_id: str
    is_backup: bool
    def __init__(self, simulation_id: _Optional[str] = ..., supplier_id: _Optional[str] = ..., is_backup: bool = ...) -> None: ...

class SetWarehouseInventoryWorkerRequest(_message.Message):
    __slots__ = ("simulation_id", "worker_id", "warehouse_type")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    WAREHOUSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    worker_id: str
    warehouse_type: WarehouseType
    def __init__(self, simulation_id: _Optional[str] = ..., worker_id: _Optional[str] = ..., warehouse_type: _Optional[_Union[WarehouseType, str]] = ...) -> None: ...

class IncreaseWarehouseSizeRequest(_message.Message):
    __slots__ = ("simulation_id", "warehouse_type", "size")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WAREHOUSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    warehouse_type: WarehouseType
    size: int
    def __init__(self, simulation_id: _Optional[str] = ..., warehouse_type: _Optional[_Union[WarehouseType, str]] = ..., size: _Optional[int] = ...) -> None: ...

class AddTenderRequest(_message.Message):
    __slots__ = ("simulation_id", "tender_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    TENDER_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    tender_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., tender_id: _Optional[str] = ...) -> None: ...

class RemoveTenderRequest(_message.Message):
    __slots__ = ("simulation_id", "tender_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    TENDER_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    tender_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., tender_id: _Optional[str] = ...) -> None: ...

class SetDealingWithDefectsRequest(_message.Message):
    __slots__ = ("simulation_id", "dealing_with_defects")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    DEALING_WITH_DEFECTS_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    dealing_with_defects: str
    def __init__(self, simulation_id: _Optional[str] = ..., dealing_with_defects: _Optional[str] = ...) -> None: ...

class DeleteSupplierRequest(_message.Message):
    __slots__ = ("simulation_id", "supplier_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPPLIER_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    supplier_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., supplier_id: _Optional[str] = ...) -> None: ...

class RunSimulationRequest(_message.Message):
    __slots__ = ("simulation_id",)
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    def __init__(self, simulation_id: _Optional[str] = ...) -> None: ...

class SetWorkerOnWorkerplaceRequest(_message.Message):
    __slots__ = ("simulation_id", "worker_id", "workplace_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    WORKPLACE_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    worker_id: str
    workplace_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., worker_id: _Optional[str] = ..., workplace_id: _Optional[str] = ...) -> None: ...

class UnSetWorkerOnWorkerplaceRequest(_message.Message):
    __slots__ = ("simulation_id", "worker_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    worker_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., worker_id: _Optional[str] = ...) -> None: ...

class CreateSimulationRquest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SuccessResponse(_message.Message):
    __slots__ = ("success", "message", "timestamp")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    timestamp: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class CreateSupplierRequest(_message.Message):
    __slots__ = ("name", "product_name", "material_type", "delivery_period", "special_delivery_period", "reliability", "product_quality", "cost", "special_delivery_cost")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_DELIVERY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_QUALITY_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_DELIVERY_COST_FIELD_NUMBER: _ClassVar[int]
    name: str
    product_name: str
    material_type: str
    delivery_period: int
    special_delivery_period: int
    reliability: float
    product_quality: float
    cost: int
    special_delivery_cost: int
    def __init__(self, name: _Optional[str] = ..., product_name: _Optional[str] = ..., material_type: _Optional[str] = ..., delivery_period: _Optional[int] = ..., special_delivery_period: _Optional[int] = ..., reliability: _Optional[float] = ..., product_quality: _Optional[float] = ..., cost: _Optional[int] = ..., special_delivery_cost: _Optional[int] = ...) -> None: ...

class UpdateSupplierRequest(_message.Message):
    __slots__ = ("supplier_id", "name", "product_name", "material_type", "delivery_period", "special_delivery_period", "reliability", "product_quality", "cost", "special_delivery_cost")
    SUPPLIER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_DELIVERY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_QUALITY_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_DELIVERY_COST_FIELD_NUMBER: _ClassVar[int]
    supplier_id: str
    name: str
    product_name: str
    material_type: str
    delivery_period: int
    special_delivery_period: int
    reliability: float
    product_quality: float
    cost: int
    special_delivery_cost: int
    def __init__(self, supplier_id: _Optional[str] = ..., name: _Optional[str] = ..., product_name: _Optional[str] = ..., material_type: _Optional[str] = ..., delivery_period: _Optional[int] = ..., special_delivery_period: _Optional[int] = ..., reliability: _Optional[float] = ..., product_quality: _Optional[float] = ..., cost: _Optional[int] = ..., special_delivery_cost: _Optional[int] = ...) -> None: ...

class GetAllSuppliersResponse(_message.Message):
    __slots__ = ("suppliers", "total_count")
    SUPPLIERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    suppliers: _containers.RepeatedCompositeFieldContainer[Supplier]
    total_count: int
    def __init__(self, suppliers: _Optional[_Iterable[_Union[Supplier, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetWarehouseRequest(_message.Message):
    __slots__ = ("warehouse_id",)
    WAREHOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    warehouse_id: str
    def __init__(self, warehouse_id: _Optional[str] = ...) -> None: ...

class CreateWorkerRequest(_message.Message):
    __slots__ = ("name", "qualification", "specialty", "salary")
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    SPECIALTY_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    name: str
    qualification: int
    specialty: str
    salary: int
    def __init__(self, name: _Optional[str] = ..., qualification: _Optional[int] = ..., specialty: _Optional[str] = ..., salary: _Optional[int] = ...) -> None: ...

class UpdateWorkerRequest(_message.Message):
    __slots__ = ("worker_id", "name", "qualification", "specialty", "salary")
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    SPECIALTY_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    name: str
    qualification: int
    specialty: str
    salary: int
    def __init__(self, worker_id: _Optional[str] = ..., name: _Optional[str] = ..., qualification: _Optional[int] = ..., specialty: _Optional[str] = ..., salary: _Optional[int] = ...) -> None: ...

class DeleteWorkerRequest(_message.Message):
    __slots__ = ("worker_id",)
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    def __init__(self, worker_id: _Optional[str] = ...) -> None: ...

class GetAllWorkersResponse(_message.Message):
    __slots__ = ("workers", "total_count")
    WORKERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    workers: _containers.RepeatedCompositeFieldContainer[Worker]
    total_count: int
    def __init__(self, workers: _Optional[_Iterable[_Union[Worker, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class CreateLogistRequest(_message.Message):
    __slots__ = ("name", "qualification", "specialty", "salary", "speed", "vehicle_type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    SPECIALTY_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    qualification: int
    specialty: str
    salary: int
    speed: int
    vehicle_type: str
    def __init__(self, name: _Optional[str] = ..., qualification: _Optional[int] = ..., specialty: _Optional[str] = ..., salary: _Optional[int] = ..., speed: _Optional[int] = ..., vehicle_type: _Optional[str] = ...) -> None: ...

class UpdateLogistRequest(_message.Message):
    __slots__ = ("worker_id", "name", "qualification", "specialty", "salary", "speed", "vehicle_type")
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    SPECIALTY_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    name: str
    qualification: int
    specialty: str
    salary: int
    speed: int
    vehicle_type: str
    def __init__(self, worker_id: _Optional[str] = ..., name: _Optional[str] = ..., qualification: _Optional[int] = ..., specialty: _Optional[str] = ..., salary: _Optional[int] = ..., speed: _Optional[int] = ..., vehicle_type: _Optional[str] = ...) -> None: ...

class DeleteLogistRequest(_message.Message):
    __slots__ = ("worker_id",)
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    def __init__(self, worker_id: _Optional[str] = ...) -> None: ...

class GetAllLogistsResponse(_message.Message):
    __slots__ = ("logists", "total_count")
    LOGISTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    logists: _containers.RepeatedCompositeFieldContainer[Logist]
    total_count: int
    def __init__(self, logists: _Optional[_Iterable[_Union[Logist, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class CreateWorkplaceRequest(_message.Message):
    __slots__ = ("workplace_name", "required_speciality", "required_qualification", "required_equipment", "required_stages")
    WORKPLACE_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_SPECIALITY_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_EQUIPMENT_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_STAGES_FIELD_NUMBER: _ClassVar[int]
    workplace_name: str
    required_speciality: str
    required_qualification: int
    required_equipment: str
    required_stages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, workplace_name: _Optional[str] = ..., required_speciality: _Optional[str] = ..., required_qualification: _Optional[int] = ..., required_equipment: _Optional[str] = ..., required_stages: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateWorkplaceRequest(_message.Message):
    __slots__ = ("workplace_id", "workplace_name", "required_speciality", "required_qualification", "required_equipment", "required_stages")
    WORKPLACE_ID_FIELD_NUMBER: _ClassVar[int]
    WORKPLACE_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_SPECIALITY_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_EQUIPMENT_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_STAGES_FIELD_NUMBER: _ClassVar[int]
    workplace_id: str
    workplace_name: str
    required_speciality: str
    required_qualification: int
    required_equipment: str
    required_stages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, workplace_id: _Optional[str] = ..., workplace_name: _Optional[str] = ..., required_speciality: _Optional[str] = ..., required_qualification: _Optional[int] = ..., required_equipment: _Optional[str] = ..., required_stages: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteWorkplaceRequest(_message.Message):
    __slots__ = ("workplace_id",)
    WORKPLACE_ID_FIELD_NUMBER: _ClassVar[int]
    workplace_id: str
    def __init__(self, workplace_id: _Optional[str] = ...) -> None: ...

class GetAllWorkplacesResponse(_message.Message):
    __slots__ = ("workplaces", "total_count")
    WORKPLACES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    workplaces: _containers.RepeatedCompositeFieldContainer[Workplace]
    total_count: int
    def __init__(self, workplaces: _Optional[_Iterable[_Union[Workplace, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetProcessGraphRequest(_message.Message):
    __slots__ = ("process_graph_id",)
    PROCESS_GRAPH_ID_FIELD_NUMBER: _ClassVar[int]
    process_graph_id: str
    def __init__(self, process_graph_id: _Optional[str] = ...) -> None: ...

class CreateConsumerRequest(_message.Message):
    __slots__ = ("name", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class UpdateConsumerRequest(_message.Message):
    __slots__ = ("consumer_id", "name", "type")
    CONSUMER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    consumer_id: str
    name: str
    type: str
    def __init__(self, consumer_id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class DeleteConsumerRequest(_message.Message):
    __slots__ = ("consumer_id",)
    CONSUMER_ID_FIELD_NUMBER: _ClassVar[int]
    consumer_id: str
    def __init__(self, consumer_id: _Optional[str] = ...) -> None: ...

class GetAllConsumersResponse(_message.Message):
    __slots__ = ("consumers", "total_count")
    CONSUMERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    consumers: _containers.RepeatedCompositeFieldContainer[Consumer]
    total_count: int
    def __init__(self, consumers: _Optional[_Iterable[_Union[Consumer, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class CreateTenderRequest(_message.Message):
    __slots__ = ("consumer_id", "cost", "quantity_of_products", "penalty_per_day", "warranty_years", "payment_form")
    CONSUMER_ID_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_OF_PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    PENALTY_PER_DAY_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_YEARS_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_FORM_FIELD_NUMBER: _ClassVar[int]
    consumer_id: str
    cost: int
    quantity_of_products: int
    penalty_per_day: int
    warranty_years: int
    payment_form: str
    def __init__(self, consumer_id: _Optional[str] = ..., cost: _Optional[int] = ..., quantity_of_products: _Optional[int] = ..., penalty_per_day: _Optional[int] = ..., warranty_years: _Optional[int] = ..., payment_form: _Optional[str] = ...) -> None: ...

class UpdateTenderRequest(_message.Message):
    __slots__ = ("tender_id", "consumer_id", "cost", "quantity_of_products", "penalty_per_day", "warranty_years", "payment_form")
    TENDER_ID_FIELD_NUMBER: _ClassVar[int]
    CONSUMER_ID_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_OF_PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    PENALTY_PER_DAY_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_YEARS_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_FORM_FIELD_NUMBER: _ClassVar[int]
    tender_id: str
    consumer_id: str
    cost: int
    quantity_of_products: int
    penalty_per_day: int
    warranty_years: int
    payment_form: str
    def __init__(self, tender_id: _Optional[str] = ..., consumer_id: _Optional[str] = ..., cost: _Optional[int] = ..., quantity_of_products: _Optional[int] = ..., penalty_per_day: _Optional[int] = ..., warranty_years: _Optional[int] = ..., payment_form: _Optional[str] = ...) -> None: ...

class DeleteTenderRequest(_message.Message):
    __slots__ = ("tender_id",)
    TENDER_ID_FIELD_NUMBER: _ClassVar[int]
    tender_id: str
    def __init__(self, tender_id: _Optional[str] = ...) -> None: ...

class GetAllTendersResponse(_message.Message):
    __slots__ = ("tenders", "total_count")
    TENDERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    tenders: _containers.RepeatedCompositeFieldContainer[Tender]
    total_count: int
    def __init__(self, tenders: _Optional[_Iterable[_Union[Tender, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetAllSuppliersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllWorkersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllLogistsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllWorkplacesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllConsumersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllTendersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PingRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateEquipmentRequest(_message.Message):
    __slots__ = ("name", "equipment_type", "reliability", "maintenance_period", "maintenance_cost", "cost", "repair_cost", "repair_time")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_COST_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_COST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_TIME_FIELD_NUMBER: _ClassVar[int]
    name: str
    equipment_type: str
    reliability: float
    maintenance_period: int
    maintenance_cost: int
    cost: int
    repair_cost: int
    repair_time: int
    def __init__(self, name: _Optional[str] = ..., equipment_type: _Optional[str] = ..., reliability: _Optional[float] = ..., maintenance_period: _Optional[int] = ..., maintenance_cost: _Optional[int] = ..., cost: _Optional[int] = ..., repair_cost: _Optional[int] = ..., repair_time: _Optional[int] = ...) -> None: ...

class UpdateEquipmentRequest(_message.Message):
    __slots__ = ("equipment_id", "name", "equipment_type", "reliability", "maintenance_period", "maintenance_cost", "cost", "repair_cost", "repair_time")
    EQUIPMENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_COST_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_COST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_TIME_FIELD_NUMBER: _ClassVar[int]
    equipment_id: str
    name: str
    equipment_type: str
    reliability: float
    maintenance_period: int
    maintenance_cost: int
    cost: int
    repair_cost: int
    repair_time: int
    def __init__(self, equipment_id: _Optional[str] = ..., name: _Optional[str] = ..., equipment_type: _Optional[str] = ..., reliability: _Optional[float] = ..., maintenance_period: _Optional[int] = ..., maintenance_cost: _Optional[int] = ..., cost: _Optional[int] = ..., repair_cost: _Optional[int] = ..., repair_time: _Optional[int] = ...) -> None: ...

class DeleteEquipmentRequest(_message.Message):
    __slots__ = ("equipment_id",)
    EQUIPMENT_ID_FIELD_NUMBER: _ClassVar[int]
    equipment_id: str
    def __init__(self, equipment_id: _Optional[str] = ...) -> None: ...

class GetAllEquipmentRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllEquipmentResopnse(_message.Message):
    __slots__ = ("equipments", "total_count")
    EQUIPMENTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    equipments: _containers.RepeatedCompositeFieldContainer[Equipment]
    total_count: int
    def __init__(self, equipments: _Optional[_Iterable[_Union[Equipment, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetMetricsRequest(_message.Message):
    __slots__ = ("simulation_id", "step")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    step: int
    def __init__(self, simulation_id: _Optional[str] = ..., step: _Optional[int] = ...) -> None: ...

class FactoryMetricsResponse(_message.Message):
    __slots__ = ("metrics", "timestamp")
    METRICS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    metrics: FactoryMetrics
    timestamp: str
    def __init__(self, metrics: _Optional[_Union[FactoryMetrics, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class ProductionMetricsResponse(_message.Message):
    __slots__ = ("metrics", "unplanned_repairs", "timestamp")
    METRICS_FIELD_NUMBER: _ClassVar[int]
    UNPLANNED_REPAIRS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    metrics: ProductionMetrics
    unplanned_repairs: UnplannedRepair
    timestamp: str
    def __init__(self, metrics: _Optional[_Union[ProductionMetrics, _Mapping]] = ..., unplanned_repairs: _Optional[_Union[UnplannedRepair, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class QualityMetricsResponse(_message.Message):
    __slots__ = ("metrics", "timestamp")
    METRICS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    metrics: QualityMetrics
    timestamp: str
    def __init__(self, metrics: _Optional[_Union[QualityMetrics, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class EngineeringMetricsResponse(_message.Message):
    __slots__ = ("metrics", "operation_timing_chart", "downtime_chart", "timestamp")
    METRICS_FIELD_NUMBER: _ClassVar[int]
    OPERATION_TIMING_CHART_FIELD_NUMBER: _ClassVar[int]
    DOWNTIME_CHART_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    metrics: EngineeringMetrics
    operation_timing_chart: OperationTimingChart
    downtime_chart: DowntimeChart
    timestamp: str
    def __init__(self, metrics: _Optional[_Union[EngineeringMetrics, _Mapping]] = ..., operation_timing_chart: _Optional[_Union[OperationTimingChart, _Mapping]] = ..., downtime_chart: _Optional[_Union[DowntimeChart, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class CommercialMetricsResponse(_message.Message):
    __slots__ = ("metrics", "model_mastery_chart", "project_profitability_chart", "timestamp")
    METRICS_FIELD_NUMBER: _ClassVar[int]
    MODEL_MASTERY_CHART_FIELD_NUMBER: _ClassVar[int]
    PROJECT_PROFITABILITY_CHART_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    metrics: CommercialMetrics
    model_mastery_chart: ModelMasteryChart
    project_profitability_chart: ProjectProfitabilityChart
    timestamp: str
    def __init__(self, metrics: _Optional[_Union[CommercialMetrics, _Mapping]] = ..., model_mastery_chart: _Optional[_Union[ModelMasteryChart, _Mapping]] = ..., project_profitability_chart: _Optional[_Union[ProjectProfitabilityChart, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class ProcurementMetricsResponse(_message.Message):
    __slots__ = ("metrics", "timestamp")
    METRICS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    metrics: ProcurementMetrics
    timestamp: str
    def __init__(self, metrics: _Optional[_Union[ProcurementMetrics, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetProductionScheduleRequest(_message.Message):
    __slots__ = ("simulation_id",)
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    def __init__(self, simulation_id: _Optional[str] = ...) -> None: ...

class ProductionScheduleResponse(_message.Message):
    __slots__ = ("schedule", "timestamp")
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    schedule: ProductionSchedule
    timestamp: str
    def __init__(self, schedule: _Optional[_Union[ProductionSchedule, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetWorkshopPlanRequest(_message.Message):
    __slots__ = ("simulation_id",)
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    def __init__(self, simulation_id: _Optional[str] = ...) -> None: ...

class WorkshopPlanResponse(_message.Message):
    __slots__ = ("workshop_plan", "timestamp")
    WORKSHOP_PLAN_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    workshop_plan: ProcessGraph
    timestamp: str
    def __init__(self, workshop_plan: _Optional[_Union[ProcessGraph, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetUnplannedRepairRequest(_message.Message):
    __slots__ = ("simulation_id",)
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    def __init__(self, simulation_id: _Optional[str] = ...) -> None: ...

class UnplannedRepairResponse(_message.Message):
    __slots__ = ("unplanned_repair", "timestamp")
    UNPLANNED_REPAIR_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    unplanned_repair: UnplannedRepair
    timestamp: str
    def __init__(self, unplanned_repair: _Optional[_Union[UnplannedRepair, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetWarehouseLoadChartRequest(_message.Message):
    __slots__ = ("simulation_id", "warehouse_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WAREHOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    warehouse_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., warehouse_id: _Optional[str] = ...) -> None: ...

class WarehouseLoadChartResponse(_message.Message):
    __slots__ = ("chart", "timestamp")
    CHART_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    chart: WarehouseLoadChart
    timestamp: str
    def __init__(self, chart: _Optional[_Union[WarehouseLoadChart, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class SetQualityInspectionRequest(_message.Message):
    __slots__ = ("simulation_id", "supplier_id", "inspection_enabled")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPPLIER_ID_FIELD_NUMBER: _ClassVar[int]
    INSPECTION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    supplier_id: str
    inspection_enabled: bool
    def __init__(self, simulation_id: _Optional[str] = ..., supplier_id: _Optional[str] = ..., inspection_enabled: bool = ...) -> None: ...

class SetDeliveryPeriodRequest(_message.Message):
    __slots__ = ("simulation_id", "supplier_id", "delivery_period_days")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPPLIER_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_PERIOD_DAYS_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    supplier_id: str
    delivery_period_days: int
    def __init__(self, simulation_id: _Optional[str] = ..., supplier_id: _Optional[str] = ..., delivery_period_days: _Optional[int] = ...) -> None: ...

class SetEquipmentMaintenanceIntervalRequest(_message.Message):
    __slots__ = ("simulation_id", "equipment_id", "interval_days")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENT_ID_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_DAYS_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    equipment_id: str
    interval_days: int
    def __init__(self, simulation_id: _Optional[str] = ..., equipment_id: _Optional[str] = ..., interval_days: _Optional[int] = ...) -> None: ...

class SetCertificationStatusRequest(_message.Message):
    __slots__ = ("simulation_id", "certificate_type", "is_obtained")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    CERTIFICATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_OBTAINED_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    certificate_type: str
    is_obtained: bool
    def __init__(self, simulation_id: _Optional[str] = ..., certificate_type: _Optional[str] = ..., is_obtained: bool = ...) -> None: ...

class SetLeanImprovementStatusRequest(_message.Message):
    __slots__ = ("simulation_id", "name", "is_implemented")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_IMPLEMENTED_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    name: str
    is_implemented: bool
    def __init__(self, simulation_id: _Optional[str] = ..., name: _Optional[str] = ..., is_implemented: bool = ...) -> None: ...

class SetSalesStrategyRequest(_message.Message):
    __slots__ = ("simulation_id", "strategy")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    strategy: str
    def __init__(self, simulation_id: _Optional[str] = ..., strategy: _Optional[str] = ...) -> None: ...

class GetRequiredMaterialsRequest(_message.Message):
    __slots__ = ("simulation_id",)
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    def __init__(self, simulation_id: _Optional[str] = ...) -> None: ...

class RequiredMaterialsResponse(_message.Message):
    __slots__ = ("materials", "timestamp")
    MATERIALS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    materials: _containers.RepeatedCompositeFieldContainer[RequiredMaterial]
    timestamp: str
    def __init__(self, materials: _Optional[_Iterable[_Union[RequiredMaterial, _Mapping]]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetAvailableImprovementsRequest(_message.Message):
    __slots__ = ("simulation_id",)
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    def __init__(self, simulation_id: _Optional[str] = ...) -> None: ...

class AvailableImprovementsResponse(_message.Message):
    __slots__ = ("improvements", "timestamp")
    IMPROVEMENTS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    improvements: _containers.RepeatedCompositeFieldContainer[LeanImprovement]
    timestamp: str
    def __init__(self, improvements: _Optional[_Iterable[_Union[LeanImprovement, _Mapping]]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetDefectPoliciesRequest(_message.Message):
    __slots__ = ("simulation_id",)
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    def __init__(self, simulation_id: _Optional[str] = ...) -> None: ...

class DefectPoliciesResponse(_message.Message):
    __slots__ = ("available_policies", "current_policy", "timestamp")
    AVAILABLE_POLICIES_FIELD_NUMBER: _ClassVar[int]
    CURRENT_POLICY_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    available_policies: _containers.RepeatedScalarFieldContainer[str]
    current_policy: str
    timestamp: str
    def __init__(self, available_policies: _Optional[_Iterable[str]] = ..., current_policy: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetAllMetricsRequest(_message.Message):
    __slots__ = ("simulation_id", "step")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    step: int
    def __init__(self, simulation_id: _Optional[str] = ..., step: _Optional[int] = ...) -> None: ...

class AllMetricsResponse(_message.Message):
    __slots__ = ("factory", "production", "quality", "engineering", "commercial", "procurement", "timestamp")
    FACTORY_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    ENGINEERING_FIELD_NUMBER: _ClassVar[int]
    COMMERCIAL_FIELD_NUMBER: _ClassVar[int]
    PROCUREMENT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    factory: FactoryMetrics
    production: ProductionMetrics
    quality: QualityMetrics
    engineering: EngineeringMetrics
    commercial: CommercialMetrics
    procurement: ProcurementMetrics
    timestamp: str
    def __init__(self, factory: _Optional[_Union[FactoryMetrics, _Mapping]] = ..., production: _Optional[_Union[ProductionMetrics, _Mapping]] = ..., quality: _Optional[_Union[QualityMetrics, _Mapping]] = ..., engineering: _Optional[_Union[EngineeringMetrics, _Mapping]] = ..., commercial: _Optional[_Union[CommercialMetrics, _Mapping]] = ..., procurement: _Optional[_Union[ProcurementMetrics, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class ValidateConfigurationRequest(_message.Message):
    __slots__ = ("simulation_id",)
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    def __init__(self, simulation_id: _Optional[str] = ...) -> None: ...

class ValidationResponse(_message.Message):
    __slots__ = ("is_valid", "errors", "warnings", "timestamp")
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    errors: _containers.RepeatedScalarFieldContainer[str]
    warnings: _containers.RepeatedScalarFieldContainer[str]
    timestamp: str
    def __init__(self, is_valid: bool = ..., errors: _Optional[_Iterable[str]] = ..., warnings: _Optional[_Iterable[str]] = ..., timestamp: _Optional[str] = ...) -> None: ...
